# Engineering

## Ионов Артем группа 6231-010402D

### Лабораторная работа №1 "Базовый пайплайн работы с данными"

# Необходимый минимум для выполнения лабораторных работ:

Что было выполнено для начала:

1. Для начала был установлен клиент программы Docker Desktop по [ссылке](https://www.docker.com/products/docker-desktop/). Проведена настройка для запуска докера.
   
 ```
$ dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
 ```

 ```
$ dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
 ```
2. Для работы был выбран [VS Code](https://code.visualstudio.com/insiders/). Затем была проведена настройка, установка требуемых расширений для работы:

   * [ms-python.python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
   * [ms-toolsai.jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
   * [ms-vscode-remote.vscode-remote-extensionpack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
   * [ms-azuretools.vscode-docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

3. Клонирование репозитория. Склонировал себе [репозиторий](https://github.com/ssau-data-engineering/Prerequisites.git ) в заранее созданную папку GitHere.

 ```
git clone https://github.com/ssau-data-engineering/Prerequisites.git 
 ```
4. Далее, перед запуском контейнеров, была выполнена последовательнось команд:

```bash
    docker network create data-engineering-labs-network
```

Подготавливка к запуску **Apache airflow**

```bash
    docker compose -f docker-compose.airflow.yaml up airflow-init
```

Для запуска, `airflow` `nifi` `elasticsearch` `posgresql` `mlflow` использовались следующие, соответственно, команды.

```bash
    docker compose -f docker-compose.airflow.yaml up --build -d
```    
    
```bash
    docker compose -f docker-compose.nifi.yaml up --build -d
```    
    
```bash
    docker compose -f docker-compose.elasticsearch.yaml up --build -d
```    
    
```bash
    docker compose -f docker-compose.postgresql.yaml up --build -d
```

```bash
    docker compose -f docker-compose.mlflow.yaml up --build -d
```

5. Запущенные контейнеры в Docker

![image](https://github.com/user-attachments/assets/41eaed57-c69b-4a4a-aa2f-3ba4910b417f)

### Лабораторная работа №1 "Базовый пайплайн работы с данными"
## Реализация пайплайна

Используя DAG нужно реализовать пайплайн обработки данных, в файлах csv. Схема пайплайна:

![image](https://github.com/user-attachments/assets/f26f7781-7067-4e42-af33-2c73395d01ef)

Часть кода дага представлена ниже, полный [код](daglr1.py).

![image](https://github.com/user-attachments/assets/b8a26afd-3d38-4919-91f8-cca2afb4dc20)

etl_task_load: Загружает данные.
etl_task_clean: Очищает загруженные данные.
etl_task_process: Обрабатывает очищенные данные.

Все данные находятся в папке [data](https://github.com/sat4h/Lab-1-2024/tree/aea247556efc95ceaf28fddca0fbe6624d88fa8e/data).

## Airflow

Переходим в airflow... Здесь есть у нас уже dag (Я его уже запустил на этапе оформления отчета). Если его не получается найти, можно отсортировать по Owner.

![image](https://github.com/user-attachments/assets/b06e42d4-8719-47a6-b414-eb4813044f7a)

Здесь особых проблем не возникло, ошибки были на этапе "модернизации" кода так сказать.

![image](https://github.com/user-attachments/assets/02d9160d-f6ae-4b1b-b25e-82f12f92b0eb)

После того как все пройдет удачно, можно перейти в ElasticSearch.
![image](https://github.com/user-attachments/assets/400616d8-6f33-42ec-8f49-f74995281a0f)

## ElasticSearch
Все прошло успешно, переходим к созданию Index Pattern для wines.
![image](https://github.com/user-attachments/assets/d169582c-e690-430b-8f69-405fd4d7266d)

затем в консоли Dev Tools прописываем:

```
GET /wines/_search
{
  "query": {
    "match_all": {}
  }
}
```

![image](https://github.com/user-attachments/assets/331d61df-a14a-4ab5-9906-e8981a9adf4d)

И теперь в Dashboard можно построить график по полученным данным. На скрине построен график points/price

![image](https://github.com/user-attachments/assets/1f7b2d48-97fe-49bd-9419-a5df2cae303c)

## APACHE NIFI

В Apache Nifi был реализован пайплайн с помощью схемы. Для реализации пайплайна достаточно следующих процессоров:

GetFile

SplitRecord

QueryRecord

UpdateRecord

MergeContent

PutFile

PutElasticsearchHttp

Общая схема:

![image](https://github.com/user-attachments/assets/6042e4c7-56ba-4013-a4ef-272195ee0692)

Данные были загружены в nifi/data/

Параметры GetFile, установим так же input directory с данными.
![image](https://github.com/user-attachments/assets/09f908a1-4c17-40ce-b282-fcb97211088b)

А так же указать местоположение для нового файла в PutFile

![image](https://github.com/user-attachments/assets/095714ff-2649-424b-ac3f-c1ff6cb0872c)

А вот и мои любимые ошибки, их было очень много, пришлось искать помощь ._.

![image](https://github.com/user-attachments/assets/1497446b-e991-494c-a364-96bc693f5f40)

 - Очень много проблем с переполнением памяти
 - То Nifi просто не работал после перезагрузки, он вроде запущен, но localhost не отвечал
 - Nifi зависал очень часто
 - Трудности были с обработкой строк
 - 
   Ну и вообще интерфейс мне не очень понравился.
Рестартим --> Запускаем пайплайн Рестартим --> Запускаем пайплайн --> Рестартим --> Запускаем пайплайн, дожидаемся окончания работы, мой долгожданный файл оказался в /data/data2. Пайплайн сохранил [здесь](

Могу сказать, что Apache Nifi мне вообще не понравился, лучше с кодом повозиться :)
