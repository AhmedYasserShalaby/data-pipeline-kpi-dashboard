from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ISSUE_COLUMNS = ["table_name", "issue_type", "row_reference", "column_name", "issue_detail"]


def load_contracts(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def validate_contracts(raw_tables: dict[str, pd.DataFrame], contracts: dict[str, Any]) -> pd.DataFrame:
    issues = []
    for table_name, frame in raw_tables.items():
        contract = contracts.get(table_name, {})
        _check_required_columns(table_name, frame, contract)
        issues.extend(_id_pattern_issues(table_name, frame, contract))
        issues.extend(_duplicate_key_issues(table_name, frame, contract))
        issues.extend(_date_issues(table_name, frame, contract))
        issues.extend(_numeric_range_issues(table_name, frame, contract))
        issues.extend(_allowed_value_issues(table_name, frame, contract))
        issues.extend(_foreign_key_issues(table_name, frame, contract, raw_tables))
    return pd.DataFrame(issues, columns=ISSUE_COLUMNS)


def _check_required_columns(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> None:
    missing = sorted(set(contract.get("required_columns", [])) - set(frame.columns))
    if missing:
        raise ValueError(f"{table_name} missing required columns: {', '.join(missing)}")


def _id_pattern_issues(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, str]]:
    column = contract.get("id_column")
    pattern = contract.get("id_pattern")
    if not column or not pattern or column not in frame.columns:
        return []
    invalid = ~frame[column].astype(str).str.match(pattern, case=False, na=False)
    return _issue_rows(frame[invalid], table_name, "invalid_id_format", column, f"Expected pattern {pattern}", column)


def _duplicate_key_issues(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, str]]:
    column = contract.get("unique_key")
    if not column or column not in frame.columns:
        return []
    normalized = _normalize(frame[column])
    duplicate = normalized.duplicated(keep="first")
    return _issue_rows(
        frame[duplicate], table_name, "duplicate_key", column, "Duplicate key removed during cleaning", column
    )


def _date_issues(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for column, rules in contract.get("date_columns", {}).items():
        if column not in frame.columns:
            continue
        parsed = _parse_dates(frame[column])
        invalid = parsed.isna()
        issues.extend(
            _issue_rows(
                frame[invalid],
                table_name,
                "invalid_date",
                column,
                "Date could not be parsed",
                contract.get("id_column"),
            )
        )
        min_date = pd.Timestamp(rules["min"]) if rules.get("min") else None
        max_date = pd.Timestamp(rules["max"]) if rules.get("max") else None
        if min_date is not None:
            below_min = parsed.notna() & (parsed < min_date)
            issues.extend(
                _issue_rows(
                    frame[below_min],
                    table_name,
                    "date_below_min",
                    column,
                    f"Date before {rules['min']}",
                    contract.get("id_column"),
                )
            )
        if max_date is not None:
            above_max = parsed.notna() & (parsed > max_date)
            issues.extend(
                _issue_rows(
                    frame[above_max],
                    table_name,
                    "date_above_max",
                    column,
                    f"Date after {rules['max']}",
                    contract.get("id_column"),
                )
            )
    return issues


def _numeric_range_issues(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for column, rules in contract.get("numeric_ranges", {}).items():
        if column not in frame.columns:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        invalid_numeric = values.isna()
        issues.extend(
            _issue_rows(
                frame[invalid_numeric],
                table_name,
                "invalid_numeric",
                column,
                "Value is not numeric",
                contract.get("id_column"),
            )
        )
        if "min" in rules:
            minimum = float(rules["min"])
            below = values <= minimum if rules.get("inclusive_min", True) is False else values < minimum
            issues.extend(
                _issue_rows(
                    frame[values.notna() & below],
                    table_name,
                    "numeric_below_min",
                    column,
                    f"Minimum {minimum}",
                    contract.get("id_column"),
                )
            )
        if "max" in rules:
            maximum = float(rules["max"])
            above = values >= maximum if rules.get("inclusive_max", True) is False else values > maximum
            issues.extend(
                _issue_rows(
                    frame[values.notna() & above],
                    table_name,
                    "numeric_above_max",
                    column,
                    f"Maximum {maximum}",
                    contract.get("id_column"),
                )
            )
    return issues


def _allowed_value_issues(table_name: str, frame: pd.DataFrame, contract: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for column, allowed_values in contract.get("allowed_values", {}).items():
        if column not in frame.columns:
            continue
        allowed = {str(value).strip().lower() for value in allowed_values}
        invalid = ~frame[column].fillna("").astype(str).str.strip().str.lower().isin(allowed)
        issues.extend(
            _issue_rows(
                frame[invalid],
                table_name,
                "invalid_allowed_value",
                column,
                f"Allowed: {', '.join(allowed_values)}",
                contract.get("id_column"),
            )
        )
    return issues


def _foreign_key_issues(
    table_name: str,
    frame: pd.DataFrame,
    contract: dict[str, Any],
    raw_tables: dict[str, pd.DataFrame],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for column, rules in contract.get("foreign_keys", {}).items():
        parent = raw_tables.get(rules["table"])
        parent_column = rules["column"]
        if column not in frame.columns or parent is None or parent_column not in parent.columns:
            continue
        values = _normalize(frame[column]) if rules.get("normalize") else frame[column].astype(str)
        parent_values = set(
            _normalize(parent[parent_column]) if rules.get("normalize") else parent[parent_column].astype(str)
        )
        missing = ~values.isin(parent_values)
        detail = f"Missing {rules['table']}.{parent_column}"
        issues.extend(
            _issue_rows(frame[missing], table_name, "missing_foreign_key", column, detail, contract.get("id_column"))
        )
    return issues


def _issue_rows(
    frame: pd.DataFrame,
    table_name: str,
    issue_type: str,
    column_name: str,
    issue_detail: str,
    reference_column: str | None,
) -> list[dict[str, str]]:
    if frame.empty:
        return []
    if reference_column and reference_column in frame.columns:
        references = frame[reference_column].astype(str)
    else:
        references = frame.index.astype(str)
    return [
        {
            "table_name": table_name,
            "issue_type": issue_type,
            "row_reference": reference,
            "column_name": column_name,
            "issue_detail": issue_detail,
        }
        for reference in references
    ]


def _normalize(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.upper()


def _parse_dates(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=False)
    fallback = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=True)
    return parsed.fillna(fallback)
