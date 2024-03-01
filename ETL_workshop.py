import pymysql
import pandas as pd
import requests
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.utils.dates import days_ago


mysql_connection = 'mysql_default'   # ตั้งค่า mysql connection ในหน้า Airflow web UI
conversion_rate_api = 'https://r2de2-workshop-vmftiryt6q-ts.a.run.app/usd_thb_conversion_rate'

# path ที่ใช้ในการเก็บไฟล์
transaction_path = '/home/airflow/gcs/data/transaction.csv'
conversion_rate_path = '/home/airflow/gcs/data/conversion_rate.csv'
result_path = '/home/airflow/gcs/data/result.csv'


def get_data_from_mysql(transaction_path):

    # ใช้ HookOperator ในการเชื่อมต่อกับ database
    mysqlserver = MySqlHook(mysql_connection)
    
    # Query ข้อมูลจาก database แล้วเก็บเป็น pandas DataFrame
    audible_data = mysqlserver.get_pandas_df(sql='SELECT * FROM audible_data')
    audible_transaction = mysqlserver.get_pandas_df(sql='SELECT * FROM audible_transaction')

    # join 2 ตารางเข้าด้วยกัน
    df = audible_transaction.merge(audible_data, how='left', left_on='book_id', right_on='Book_ID')

    # save ไฟล์ไปเก็บไว้ใน GCS
    df.to_csv(transaction_path, index=False)
    print(f'Output to {transaction_path}')


def get_conversion_rate(conversion_rate_path):
    # ดึงข้อมูล conversion rate ด้วยการ get api
    r = requests.get(conversion_rate_api)
    conversion_rate = r.json()
    conversion_rate_df = pd.DataFrame(conversion_rate)

    # เปลี่ยนชื่อ col เป็น date แล้วเซฟไฟล์ CSV ไปเก็บใน GCS
    conversion_rate_df = conversion_rate_df.reset_index().rename(columns={'index': 'date'})
    conversion_rate_df.to_csv(conversion_rate_path, index=False)
    print(f'Output to {conversion_rate_path}')


def get_result(transaction_path, conversion_rate_path, result_path):
    # อ่านจากไฟล์จาก GCS
    transaction = pd.read_csv(transaction_path)
    conversion_rate = pd.read_csv(conversion_rate_path)

    transaction['date'] = transaction['timestamp']
    transaction['date'] = pd.to_datetime(transaction['date']).dt.date
    conversion_rate['date'] = pd.to_datetime(conversion_rate['date']).dt.date

    # join 2 DataFrame
    final_df = transaction.merge(conversion_rate, how='left', on='date')
    
    #แปลงหน่วยราคาให้เป็น float
    final_df['Price'] = final_df.apply(lambda x: x['Price'].replace('$',''), axis=1)
    final_df['Price'] = final_df['Price'].astype(float)

    #แปลงราคาให้เป็น THB
    final_df['THBPrice'] = final_df['Price'] * final_df['conversion_rate']
    final_df = final_df.drop(['date', 'book_id'], axis=1)

    # save ไฟล์ CSV
    final_df.to_csv(result_path, index=False)
    print(f'Output to {result_path}')


with DAG(
    'ETL_workshop',
    start_date=days_ago(1),
    schedule_interval='@once',
    tags=['workshop']
) as dag:

    
    t1 = PythonOperator(
        task_id = 'get_data_from_mysql',
        python_callable = get_data_from_mysql,
        op_kwargs={
            'transaction_path': transaction_path,
        },
    )

    t2 = PythonOperator(
        task_id='get_conversion_rate',
        python_callable=get_conversion_rate,
        op_kwargs={
            'conversion_rate_path': conversion_rate_path,
        },
    )

    t3 = PythonOperator(
        task_id = 'get_result',
        python_callable = get_result,
        op_kwargs={
            'transaction_path': transaction_path,
            'conversion_rate_path': conversion_rate_path,
            'result_path' : result_path,
        },
    )

    [t1, t2] >> t3
