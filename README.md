# Website stats through Kafka

<a href="https://github.com/ernestoarbitrio/python-kafka-kata/actions">
<img alt="CI" src="https://github.com/ernestoarbitrio/python-kafka-kata/workflows/CI/badge.svg?branch=main">
</a>

This is a kata on producing website statistics (e.g. reponse time, error code, etc...)
using `kafka-python` (https://pypi.org/project/kafka-python/).

The code included simulate a system that monitors website availability over the
network, produces metrics about this and passes these events through a
[Kafka](https://kafka.apache.org/) instance into a [PostgreSQL](https://www.postgresql.org/)
database.

The `kafka` and `postgres` serivces have been intanciated on [Aiven](https://aiven.io/).

## Run the example

First of all some configuration and secrets must be set. 

### Database Settings
```bash
export POSTGRES_HOST=db_host
export POSTGRES_PORT=db_port
export POSTGRES_DB_NAME=db_name
export POSTGRES_USER=db_user
export POSTGRES_PASSWORD=db_password
```

### Kafka Settings
```bash
export KAFKA_SERVICE_URI=url:port
export SSL_CA_FILE_PATH=/your/path/ca.pem
export SSL_CERTFILE_PATH=/your/path/service.cert
export SSL_KEYFILE_PATH=/your/path/service.key
```

### Load demo data
The following command will load demo data within the `websites` table. In practice, this way
we simulate the data entry of the website we wanna get the statistics.


**NOTE: The first time this script will create the database schema either.**
```bash
python -m websitestats.util load_demo_data
```

### Run test locally
Create a python virtual environment with your favourite venv (`pipenv`, `conda`, etc...) manager.

#### Install requirements
```bash
pip install -r requrements.txt
```

#### Run tests
```bash
pytest
```

### Run complete example

*NOTE: the `producer` and the `consumer` must be ran in 2 different bash
sessions and in each of those you must export the settings above.*

#### Producer
```bash
python -m websitestats.producer --schedule <n_seconds>
```
The `--schedule` parameter is mandatory and indicates the periodicity of
the producer job. For example `--schedule 3` means that the job will be run
scheduled each 3 seconds. I you wanna run the producer only once you must
specify `--schedule 0`.

#### Consumer
```bash
python -m websitestats.consumer
```