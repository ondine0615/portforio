import os
from datetime import datetime

from airflow.operators.bash import BashOperator
from airflow import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.operators.python import PythonOperator

from all_new_twitch import Twitch


default_args={
    
    "start_date": datetime(2022,8,1)
}

twitch = Twitch()

with DAG(
    dag_id="twitch_emotions_log",
    default_args=default_args,
    schedule_interval='@daily',
    tags=["twitch"],
    catchup=False) as dag:
    
    #table 생성
    create_table= SqliteOperator( 
        task_id="create_table",
        sqlite_conn_id="db_sqlite",
        sql='''
            CREATE TABLE IF NOT EXISTS result3 (
                emotes TEXT PRIMARY KEY,
                total_sum INTEGER
            )
        '''
    )
    
    extract = PythonOperator(
        task_id = 'extract',
        python_callable= extract_from_website
    )
    count_one = PythonOperator(
        task_id = 'count_one',
        python_callable=emotion_count_one
    )
    count_all=PythonOperator(
        task_id = 'count_all',
        python_callable=emotion_count_all
    )
    concat_csv = PythonOperator(
        task_id='concat_csv',
        python_callable=concat_all_csv
    )
    
    store_csv=BashOperator(
    task_id="store_csv",
    bash_command='echo -e ".separator ","\n.import /home/ondine0615/workplace/chat-log/csv/df_sum.csv result3" | sqlite3 /home/ondine0615/workplace/chat-log/csv/result.db'
    )
    
    create_table >> extract >> count_one >> concat_csv >> store_csv