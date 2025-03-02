import os
from datetime import datetime
from airflow import DAG
import json
from airflow.operators.python import PythonOperator
import logging
logging.basicConfig(level=logging.INFO)

def run_script():
    # import os, sys
    # print(sys.path.append('/opt/'))
    with open('crawler/tgdd_crawler/tgdd_crawler/metadata.json', 'r') as f:
        metadata = json.load(f)
        ingest_id = metadata.get('last_mod', None)
        if ingest_id:
            ingest_id = ingest_id.replace("-", "")
            logging.info(ingest_id)
            os.system('python spark_processing/pipeline/tgdd/normalize.py ' + ingest_id)


dag = DAG(
    'normalize_thegioididong_daily',
    description='Normalize Thegioididong daily',
    tags=['normalize', 'thegioididong', 'daily'],
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

normalize_task = PythonOperator(
    task_id='normalize_task',
    python_callable=run_script,
    dag=dag,
)

normalize_task