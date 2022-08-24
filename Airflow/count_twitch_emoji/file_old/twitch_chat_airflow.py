import os
from datetime import datetime

from airflow.operators.bash import BashOperator
from airflow import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator


default_args={
    
    "start_date": datetime(2022,1,1)
}


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
    #chat log를 가지고 오기 위한 정보 수집과 text 파일로 내려받기
    extract_=BashOperator(
        task_id="extract_from_website",
        bash_command="python3 /home/ondine0615/airflow/dags/dag_py/extract_from_website.py"
    )
    #전처리
    make_csv=BashOperator(
        task_id='text_to_csv',
        bash_command="python3 /home/ondine0615/airflow/dags/dag_py/emotion_count_all.py"
    )
    # 
    concat_csv=BashOperator(
        task_id='concat_csv',
        bash_command="python3 /home/ondine0615/airflow/dags/dag_py/concat_csv.py"
    ) # 저장 
    store_csv=BashOperator(
        task_id="store_csv",
        bash_command='echo -e ".separator ","\n.import /home/ondine0615/workplace/chat-log/csv/df_sum.csv result3" | sqlite3 /home/ondine0615/workplace/chat-log/csv/result.db'
    )
    
    create_table >> extract_ >> make_csv >> concat_csv >> store_csv