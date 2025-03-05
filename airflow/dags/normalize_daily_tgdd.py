import os
from datetime import datetime
from airflow import DAG
import json
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator

import logging
logging.basicConfig(level=logging.INFO)

with open('crawler/tgdd_crawler/tgdd_crawler/metadata.json', 'r') as f:
    metadata = json.load(f)
    ingest_id = metadata.get('last_mod', None)
    if ingest_id:
        ingest_id = ingest_id.replace("-", "")

def run_normalize_script():
    os.system('python spark_processing/pipeline/tgdd/normalize.py ' + ingest_id)

def run_normalize_common_script():
    os.system('python spark_processing/pipeline/tgdd/normalize_common.py ' + ingest_id)

def run_upsert_by_categories_script():
    os.system('python spark_processing/pipeline/tgdd/by_categories.py ' + ingest_id)


dag_normalize = DAG(
    'normalize_thegioididong_daily',
    description='Normalize Thegioididong daily',
    tags=['normalize', 'thegioididong', 'daily'],
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

normalize_task = PythonOperator(
    task_id='normalize',
    python_callable=run_normalize_script,
    dag=dag_normalize,
)

trigger_normalize_common = TriggerDagRunOperator(
    task_id='trigger_normalize_common',
    trigger_dag_id='normalize_common_thegioididong_daily',
    dag=dag_normalize,
)

trigger_upsert_by_categories = TriggerDagRunOperator(
    task_id='trigger_upsert_by_categories',
    trigger_dag_id='upsert_by_categories_thegioididong_daily',
    dag=dag_normalize,
)

dag_normalize_common = DAG(
    'normalize_common_thegioididong_daily',
    description='Normalize Common Thegioididong daily',
    tags=['normalize_common', 'thegioididong', 'daily'],
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

normalize_common_task = PythonOperator(
    task_id='normalize_common',
    python_callable=run_normalize_common_script,
    dag=dag_normalize_common,
)

dag_upsert_by_categories = DAG(
    'upsert_by_categories_thegioididong_daily',
    description='Upsert by Categories Thegioididong daily',
    tags=['upsert_by_categories', 'thegioididong', 'daily'],
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

upsert_by_categories_task = PythonOperator(
    task_id='upsert_by_categories',
    python_callable=run_upsert_by_categories_script,
    dag=dag_upsert_by_categories,
)

normalize_task >> trigger_normalize_common
normalize_task >> trigger_upsert_by_categories