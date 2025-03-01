import os
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator

import logging

logging.basicConfig(level=logging.INFO)

dag = DAG(
    'crawl_thegioididong_daily',
    description='Crawl Thegioididong daily',
    tags=['crawl', 'thegioididong', 'daily'],
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

crawl = BashOperator(
    task_id='crawl',
    bash_command=(
        'cd /opt/airflow/crawler/tgdd_crawler/tgdd_crawler; '
        'scrapy crawl tgdd_crawler -a daily=true; '
    ),
    dag=dag,
)

trigger_normalize = TriggerDagRunOperator(
    task_id='trigger_normalize',
    trigger_dag_id='normalize_thegioididong_daily',
    dag=dag,
)

crawl >> trigger_normalize
