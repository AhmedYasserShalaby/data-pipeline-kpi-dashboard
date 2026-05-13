from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


DEFAULT_ARGS = {
    "owner": "ahmed-yasser",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="retail_kpi_pipeline",
    default_args=DEFAULT_ARGS,
    description="Run the retail ETL pipeline, analytics models, KPI exports, and validation checks.",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["portfolio", "data-engineering", "retail-kpi"],
) as dag:
    generate_data = BashOperator(
        task_id="generate_demo_data",
        bash_command="retail-kpi generate-data",
    )

    validate_contracts = BashOperator(
        task_id="validate_contracts",
        bash_command="retail-kpi validate-contracts",
    )

    run_pipeline = BashOperator(
        task_id="run_full_pipeline",
        bash_command="retail-kpi run-pipeline --mode full",
    )

    build_models = BashOperator(
        task_id="build_analytics_models",
        bash_command="retail-kpi run-models",
    )

    export_kpis = BashOperator(
        task_id="export_kpi_files",
        bash_command="retail-kpi run-kpis",
    )

    generate_data >> validate_contracts >> run_pipeline >> build_models >> export_kpis
