from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ecommerce_analytics_engine',
    default_args=default_args,
    description='Hourly generation, ingestion, and local dbt processing pipeline',
    schedule_interval='@hourly',
    catchup=False,
) as dag:

    # 1. Trigger the Python data script inside the project volume mount
    generate_mock_data = BashOperator(
        task_id='generate_mock_data',
        bash_command='python /opt/airflow/project_root/sample-data/generate-data.py',
    )

    # 2. Run dbt models to verify and transform fresh delta records
    dbt_run_transformations = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='cd /opt/airflow/project_root/dbt_transform && dbt run --profiles-dir /opt/airflow/project_root',
    )

    # 3. Test data qualities against constraints
    dbt_test_assertions = BashOperator(
        task_id='dbt_test_assertions',
        bash_command='cd /opt/airflow/project_root/dbt_transform && dbt test --profiles-dir /opt/airflow/project_root',
    )

    generate_mock_data >> dbt_run_transformations >> dbt_test_assertions
