# dbt-airflow-etl-project

A containerized ETL pipeline that demonstrates Docker, dbt transformations, and Apache Airflow orchestration. This project generates synthetic eCommerce data, transforms it through dbt staging/marts layers for analytics, validates data quality, and persists results in a local DuckDB warehouse—all orchestrated hourly by Airflow.

## 📋 Table of Contents
- [Project Architecture](#-project-architecture)
- [Prerequisites](#-prerequisites)
- [Setup Instructions](#-setup-instructions)
- [Running the Project](#-running-the-project)
- [Understanding the Pipeline](#-understanding-the-pipeline)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ Project Architecture

### High-Level Workflow
```
Generate Mock Data → dbt Run Transformations → dbt Test Assertions
```

### Components

**1. Airflow Orchestration**
- Runs an hourly DAG: `ecommerce_analytics_engine`
- Orchestrates three sequential tasks:
  - Generate fresh synthetic eCommerce data
  - Execute dbt transformations
  - Validate data quality with dbt tests

**2. dbt Transformations**
- **Staging Layer** (`stg_orders.sql`): Deduplicates orders, normalizes status
- **Marts Layer** (`analytics_daily_sales.sql`): Aggregates daily sales metrics by order status

**3. Data Warehouse**
- Local DuckDB database (`local_warehouse.duckdb`)
- Stores raw and transformed analytics data

**4. Docker Containers**
- PostgreSQL 13 (Airflow metadata store)
- Airflow Webserver & Scheduler
- Custom Airflow image with dbt-core and dbt-duckdb

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** ([Install Docker](https://docs.docker.com/get-docker/))
- **Python 3.9+** (for local development, optional if using Docker only)
- **Git** (to clone/manage the repository)
- **4GB+ RAM** available for Docker containers
- **MacOS/Linux** (Windows requires WSL2)

---

## 🚀 Setup Instructions

### Step 1: Clone/Navigate to Project
```bash
cd /Users/nishantjain2088gmail.com/projects/git-repo/dbt-airflow-etl-project
```

### Step 2: Set Up Environment Variables (Optional for Local Development)

If running dbt locally (outside Docker), create/activate the Python virtual environment:

```bash
# Create virtual environment
python3 -m venv dag-etl.venv

# Activate (macOS/Linux)
source dag-etl.venv/bin/activate

# Or on Windows
dag-etl.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # If you have a requirements.txt
# OR manually install:
pip install dbt-core dbt-duckdb apache-airflow faker pandas
```

### Step 3: Configure dbt

The project uses DuckDB as the warehouse. Configuration is in `profiles.yml`:

```yaml
dbt_transform:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /opt/airflow/project_root/local_warehouse.duckdb
      threads: 4
```

**For local dbt runs**, update the path to your local database:
```yaml
path: ./local_warehouse.duckdb
```

### Step 4: Build & Start Docker Containers

From the project root, initialize Airflow:

```bash
# Navigate to Airflow directory
cd airflow

# Initialize Airflow database (first time only)
docker-compose up airflow-init

# Start all services (runs in background)
docker-compose up -d
```

**What this does:**
- Spins up PostgreSQL 13 (Airflow metadata)
- Starts Airflow Webserver (port 8080)
- Starts Airflow Scheduler (processes DAGs hourly)
- Mounts project root at `/opt/airflow/project_root` inside containers

### Step 5: Verify Services Are Running

```bash
# Check container status
docker-compose ps

# View logs for debugging
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
```

Expected output: All services should show `Up` status.

---

## 🎯 Running the Project

### Access Airflow Web UI

1. Open browser: **http://localhost:8080**
2. Login with credentials:
   - **Username:** `airflow`
   - **Password:** `airflow`

### Trigger the DAG Manually

1. In Airflow UI, find the DAG: **`ecommerce_analytics_engine`**
2. Click the **Play button** (▶️) to trigger a run
3. Monitor the DAG Run in real-time:
   - Click DAG name → Click the run
   - View task logs and status
   - Expected tasks: `generate_mock_data`, `dbt_run_transformations`, `dbt_test_assertions`

### Automatic Hourly Runs

The DAG runs automatically every hour. To disable:
1. Toggle DAG to **OFF** in Airflow UI, or
2. Modify `dag-pipeline.py` and change `schedule_interval='@hourly'` to `schedule_interval=None`

---

## 📊 Understanding the Pipeline

### 1. Generate Mock Data
**File:** `sample-data/generate-data.py`

Creates synthetic eCommerce dataset:
- **500 Users** with email and signup date
- **50 Products** across 5 categories (price range: $5-$500)
- **1000 Orders** with statuses: completed, returned, cancelled
- **Order Items** (1-3 line items per order)

Writes to: `local_warehouse.duckdb`

### 2. dbt Run Transformations
**File:** `dbt_transform/models/`

#### Staging Layer (`models/staging/stg_orders.sql`)
- **Input:** Raw orders table
- **Processing:** Deduplicate, normalize status field
- **Output:** `stg_orders` view

#### Marts Layer (`models/marts/analytics_daily_sales.sql`)
- **Input:** `stg_orders` + items
- **Processing:** Aggregate daily sales by order status, calculate gross revenue
- **Output:** `analytics_daily_sales` view (consumable analytics table)

### 3. dbt Test Assertions
**File:** `dbt_transform/models/staging/schema.yml`

Validates data quality:
- Not null constraints on key fields
- Unique constraints on primary keys
- Custom SQL tests

---

## 📁 Project Structure

```
dbt-airflow-etl-project/
├── airflow/                          # Docker & Airflow config
│   ├── docker-compose.yaml           # Multi-container setup
│   ├── Dockerfile                    # Custom Airflow image
│   ├── dags/
│   │   └── dag-pipeline.py           # DAG definition
│   ├── plugins/                      # Custom Airflow plugins
│   ├── logs/                         # Airflow task logs
│   └── config/
│
├── dbt_transform/                    # dbt project root
│   ├── dbt_project.yml               # dbt configuration
│   ├── profiles.yml                  # DuckDB warehouse config
│   ├── models/
│   │   ├── staging/
│   │   │   ├── schema.yml            # Data tests & documentation
│   │   │   └── stg_orders.sql        # Staging layer
│   │   └── marts/
│   │       └── analytics_daily_sales.sql  # Analytics layer
│   ├── target/                       # Compiled dbt artifacts
│   └── logs/
│
├── sample-data/
│   ├── generate-data.py              # Synthetic data generator
│   └── local_warehouse.duckdb        # DuckDB database (auto-created)
│
├── dag-etl.venv/                     # Python virtual environment
├── profiles.yml                      # dbt profile configuration
├── local_warehouse.duckdb            # Main warehouse (project root)
└── README.md                         # This file
```

---

## 🔧 Running dbt Locally (Optional)

If you want to run dbt outside the Docker container:

```bash
# Activate virtual environment
source dag-etl.venv/bin/activate

# Change to dbt project directory
cd dbt_transform

# Run transformations
dbt run

# Test data quality
dbt test

# Generate documentation
dbt docs generate

# Serve documentation
dbt docs serve
```

---

## 📝 Configuration Files

### `profiles.yml` - dbt Warehouse Connection
Defines how dbt connects to DuckDB:
```yaml
dbt_transform:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /opt/airflow/project_root/local_warehouse.duckdb
      threads: 4
```

### `dbt_project.yml` - dbt Project Metadata
```yaml
name: 'dbt_transform'
version: '1.0.0'
config-version: 2
```

### `airflow/docker-compose.yaml` - Container Setup
Defines PostgreSQL, Airflow Webserver, and Scheduler services with proper volumes and environment variables.

---

## 🐛 Troubleshooting

### Issue: Docker Containers Won't Start
```bash
# Check Docker daemon is running
docker --version

# View detailed error logs
docker-compose logs --tail=50

# Rebuild containers from scratch
docker-compose down -v
docker-compose up -d
```

### Issue: Airflow DAG Not Appearing
- Wait 30-60 seconds for scheduler to parse DAGs
- Check scheduler logs: `docker-compose logs airflow-scheduler`
- Verify DAG file at: `airflow/dags/dag-pipeline.py`

### Issue: dbt Compilation Errors
```bash
# Inside Docker container
docker exec -it dbt-airflow-etl-project-airflow-scheduler-1 bash

# Or locally (if using local venv)
cd dbt_transform
dbt debug  # Check dbt configuration
dbt parse  # Validate dbt project
```

### Issue: Database File Not Found
- Ensure `local_warehouse.duckdb` permissions are correct: `chmod 644 local_warehouse.duckdb`
- Verify path in `profiles.yml` matches actual location
- Check volume mounts in `docker-compose.yaml`

### Issue: Permission Denied Errors
```bash
# Fix file permissions
chmod -R 755 dbt_transform
chmod -R 755 sample-data
chmod -R 755 airflow
```

---

## 📚 Next Steps & Learning

- **Airflow Documentation:** [Apache Airflow Docs](https://airflow.apache.org/docs/)
- **dbt Documentation:** [dbt Docs](https://docs.getdbt.com/)
- **DuckDB Guide:** [DuckDB Docs](https://duckdb.org/docs/)

---

## 📝 Notes

- DAG runs **hourly** by default (can be modified in `dag-pipeline.py`)
- Mock data is regenerated with each DAG run (Faker creates new records)
- dbt models are materialized as **views** (change in `dbt_project.yml`)
- All logs are preserved in `airflow/logs/` and `dbt_transform/logs/`

---

**Happy Data Engineering! 🚀**
