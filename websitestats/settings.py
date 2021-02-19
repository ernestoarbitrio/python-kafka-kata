import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from psycopg2.extras import RealDictCursor

from . import config

REGEX_PATTERNS = ["<title>(.*)</title>", "href=['\"]?([^'\" >]+)"]


# ------------------ DB Settings ------------------

db_params = config("postgresql")


class Database:
    """Database object helper."""

    def __init__(self):
        self.connection = psycopg2.connect(**db_params)
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def query(self, *args):
        """Execute the query through the psycopg2 cursor and return itself for the
        results fetching."""
        self.cursor.execute(*args)
        self.connection.commit()
        return self.cursor

    def close(self):
        """Close DB conncetion"""
        self.cursor.close()
        self.connection.close()


# ------------------ Kafka Settings ------------------

kafka_consumer_params = config("kafka-consumer")
consumer = KafkaConsumer("demo-topic", **kafka_consumer_params)

kafka_producer_params = config("kafka-producer")
producer = KafkaProducer(**kafka_producer_params)

TOPIC = config("kafka-topic").get("name", "demo-topic")
