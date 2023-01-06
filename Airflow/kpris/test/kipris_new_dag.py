from codecs import register_error
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context
from airflow.operators.python_operator import BranchPythonOperator

from datetime import datetime, timedelta
import redis
import pendulum

from pyFiles.kipris import Kipris

local_tz =pendulum.timezone('Asia/Seoul')

default_args={
    'depends_on_past':False,
    'start_date':datetime(2022,7,25,0,0, tzinfo=local_tz),
    'catchup':False,
    'retries':12,
    'retry_delay':timedelta(minutes=10),
    'provide_context':True
}

kipris=Kipris()

def init_date():
    redis_=redis.StrictRedis(host="192.168.0.13",port=6379,db=2)
    context=get_current_context()
    today_str=context["execution_date"].strftime('%Y%m%d')
    
    redis_.delete('work_date')
    redis_.sadd('work_date',today_str)
    
with DAG(
    dag_id='KIPRIS_API',
    default_args=default_args,
    max_active_runs=1,
    schedule_interval=timedelta(days=1)
) as dag:
    
    init=PythonOperator(
        task_id="init",
        python_callable=init_date,
        dag=dag
    )
    regit_union=PythonOperator(
        task_id="regit_union",
        python_callable=kipris.data_union,
        op_kwargs={'type_':'reg'},
        dag=dag        
    )
    regit_error=PythonOperator(
        task_id="regit_error",
        python_callable=kipris.error_working,
        dag=dag
    )
    reg_data_working = PythonOperator(
        task_id='reg_data_working',
        python_callable=kipris.data_working,
        dag=dag
    )
    
    init >> (regit_union, regit_error) >> reg_data_working