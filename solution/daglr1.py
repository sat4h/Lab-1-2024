from airflow import DAG
from airflow.operators.python import PythonOperator
from elasticsearch import Elasticsearch
from datetime import datetime
import pandas as pd
import numpy as np
import uuid
import os

# Параметры по умолчанию для DAG
default_args = {
    'owner': 'sat4h',
    'start_date': datetime(2024, 1, 2),
}

dag = DAG(
    'all_in_one',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,  # Здесь можно задать интервал расписания, если необходимо
)

def load_data():
    all_data = []
    # Загружаем данные из CSV файлов по частям
    for i in range(26):
        chunk = pd.read_csv(f"/opt/airflow/data/chunk{i}.csv")
        all_data.append(chunk)

    # Объединяем все загруженные данные в один DataFrame
    result_df = pd.concat(all_data, ignore_index=True)
    result_df.to_csv('/opt/airflow/data/temp_data.csv', index=False)  # Сохраняем во временный файл

def clean_data():
    # Загружаем временные данные
    dataframe = pd.read_csv('/opt/airflow/data/temp_data.csv')
    # Удаляем строки с пустыми значениями в указанных столбцах
    filtered_df = dataframe.dropna(subset=['designation', 'region_1'])
    filtered_df.to_csv('/opt/airflow/data/cleaned_data.csv', index=False)  # Сохраняем очищенные данные

def process_data():
    # Загружаем очищенные данные
    dataframe = pd.read_csv('/opt/airflow/data/cleaned_data.csv')
    # Заменяем NaN в столбце 'price' на 0 и удаляем столбец 'id'
    dataframe['price'].fillna(0, inplace=True)
    dataframe.drop(columns=['id'], inplace=True)
    
    # Сохраняем окончательные данные
    dataframe.to_csv('/opt/airflow/data/data.csv', index=False)

# Задача для загрузки данных
etl_task_load = PythonOperator(
    task_id='etl_task_load',
    python_callable=load_data,
    dag=dag
)

# Задача для очистки данных
etl_task_clean = PythonOperator(
    task_id='etl_task_clean',
    python_callable=clean_data,
    dag=dag
)

# Задача для обработки данных
etl_task_process = PythonOperator(
    task_id='etl_task_process',
    python_callable=process_data,
    dag=dag
)

def index_data_to_elasticsearch():
    es = Elasticsearch("http://elasticsearch-kibana:9200")
    data_to_index = pd.read_csv('/opt/airflow/data/data.csv')
    
    # Заменяем все NaN на пустую строку для всех столбцов
    data_to_index.fillna('', inplace=True)

    # Индексируем каждый документ в Elasticsearch
    for _, row in data_to_index.iterrows():
        document_id = str(uuid.uuid4())
        document = row.to_dict()

        # Индексируем документ в Elasticsearch
        es.index(index="wines", id=document_id, body=document)
        print(document)  # Логируем документ для отладки

# Задача для загрузки данных в Elasticsearch
load_task = PythonOperator(
    task_id='load_task',
    python_callable=index_data_to_elasticsearch,
    dag=dag
)

# Определяем зависимости между задачами
etl_task_load >> etl_task_clean >> etl_task_process >> load_task
