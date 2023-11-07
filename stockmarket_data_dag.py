from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
from packages import extract_stock_data
from packages import transform_stock_data
from packages import visualize

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 20),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'stockmarket_dag',
    default_args=default_args,
    description='Stock Market Analysis',
    schedule_interval=None,
)

extract_data = PythonOperator(
    task_id='extract_stock_data',
    python_callable=extract_stock_data,
    dag=dag, 
)

transform_data = PythonOperator(
    task_id='transform_stock_data',
    python_callable=transform_stock_data,
    dag=dag, 
)

visualize_data = PythonOperator(
    task_id='visualize_data',
    python_callable=visualize,
    dag=dag, 
)

extract_data >> transform_data >> visualize_data