import os
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
import logging

logging.basicConfig(level=logging.INFO)

dag = DAG(
    'crawl_thegioididong_full',
    description='Crawl Thegioididong full',
    tags=['crawl', 'thegioididong', 'full'],
    schedule_interval='@once',
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

run_spider_task = BashOperator(
    task_id='run_spider_task',
    bash_command=(
        'cd /app/crawler/tgdd_crawler/tgdd_crawler; '
        'scrapy crawl tgdd_crawler; '
    ),
    dag=dag,
)

run_spider_task
