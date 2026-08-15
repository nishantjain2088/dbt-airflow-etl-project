FROM apache/airflow:2.7.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir \
    "duckdb==1.5.5" \
    "dbt-core==1.12.0" \
    "dbt-duckdb==1.10.1" \
    "pandas" \
    "faker"
