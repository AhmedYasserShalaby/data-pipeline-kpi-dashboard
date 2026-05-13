# Quality Diagnosis And Remediation Plan

This report translates validation failures into operational diagnosis and remediation actions.

## Executive Diagnosis

- Total issues detected: **55**.
- Highest-risk table: **orders**.
- Main risk: dashboard KPIs can become misleading if invalid orders or orphaned facts are silently loaded.
- Control response: quarantine rejected rows, reconcile with source owners, and reload corrected records incrementally.

## Issue Diagnosis

| severity | table_name | issue_type                         | issue_count | root_cause                                                                               | remediation                                                                                                 |
| -------- | ---------- | ---------------------------------- | ----------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| High     | orders     | invalid_order_or_missing_dimension | 25          | Order rows were not safe to load because key quantity or dimension checks failed.        | Keep rejected rows visible, reconcile with order source owners, and reload corrected records incrementally. |
| High     | orders     | missing_foreign_key                | 13          | Fact rows reference dimension records that are absent from the trusted dimension export. | Add referential-integrity checks before load and quarantine orphaned records for source-owner review.       |
| High     | orders     | numeric_below_min                  | 12          | Operational values violated accepted business ranges.                                    | Validate entry rules at source and block negative/zero quantities before analytics ingestion.               |
| Medium   | orders     | duplicate_key                      | 2           | Source system or export process produced repeated business keys.                         | Deduplicate upstream exports, enforce unique constraints, and keep latest-record rules explicit.            |
| Medium   | returns    | invalid_return_or_missing_order    | 2           | Return records could not be matched to valid loaded orders.                              | Validate return/order relationships before finance reporting and investigate missing order references.      |
| Medium   | customers  | duplicate_key                      | 1           | Source system or export process produced repeated business keys.                         | Deduplicate upstream exports, enforce unique constraints, and keep latest-record rules explicit.            |

## Remediation Backlog

| priority | owner                 | action                                                                        | success_check                                            |
| -------- | --------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| P1       | Data engineering      | Block or quarantine invalid rows from `orders` before KPI export.             | No rejected rows enter trusted warehouse tables.         |
| P1       | Source system owner   | Fix missing dimension references and invalid quantities in source exports.    | Foreign-key and numeric-range issue counts trend down.   |
| P2       | Analytics engineering | Add KPI reconciliation checks to every dashboard-facing mart.                 | Warehouse totals equal dashboard export totals.          |
| P3       | Data governance       | Review data contracts monthly and add new accepted-value or freshness checks. | Contracts stay aligned with real source-system behavior. |

## Interview Talking Point

I did not stop at detecting bad data. I added a diagnosis layer that explains root causes, severity, and remediation actions so the pipeline behaves more like an operational data product.
