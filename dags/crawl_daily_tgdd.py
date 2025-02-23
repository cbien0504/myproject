import os
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
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

run_spider_task = BashOperator(
    task_id='run_spider_task',
    bash_command=(
        'cd /opt/airflow/crawler/tgdd_crawler/tgdd_crawler; '
        'scrapy crawl my_spider -a daily=true; '
    ),
    dag=dag,
)

run_spider_task
