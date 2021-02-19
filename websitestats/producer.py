# coding: utf-8

"""Provides producer facilities for publishing website statistics on a kafka topic"""

import argparse
import json
import logging
import random
import re
import sys
import time
import typing as t

import requests
from kafka import KafkaProducer
from psycopg2.extras import RealDictRow

from .scheduler import StatsScheduler
from .settings import REGEX_PATTERNS, TOPIC
from .settings import Database as db
from .settings import producer

logger = logging.getLogger("producer")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

serializable = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]


class _StatsExtractor:
    """Extractor object for the websites statistics."""

    def __init__(self, url: str):
        self._url = url

    @classmethod
    def from_url(cls, url: str) -> t.Tuple[float, int, t.Union[str, None]]:
        """Extract the website statistic using pytthon requests.

        Parameters
        ----------
        url : str
            The url from which extract the statistics

        Return
        ------
        time_, error_code, page_content: (float, int, str or None)
            Response time in seconds, http error code, extracted page content.
        """
        url = url if url.startswith("http") else f"http://{url}"
        try:
            request = requests.get(url)
            time_ = request.elapsed.total_seconds()
            error_code = request.status_code if not request.ok else None
            # --- The page_content contains the text that matches one (chose randomly)
            # --- of the regexp pattern defined in the REGEX_PATTERNS constant.
            page_content = "--".join(
                re.findall(random.choice(REGEX_PATTERNS), request.text, re.IGNORECASE)
            )
        except requests.exceptions.ConnectionError:
            # --- In case of a ConnectionError, the stats are hardcoded to simulate a
            # --- service unavailable error.
            time_ = 0.0
            error_code = 503
            page_content = None
        return time_, error_code, page_content


class _StatsProducer:
    """Producer object class.

    Automatically instanciate the DB object and get the KakfaProducer directly from the
    settings to have it available and the object creation.
    """

    def __init__(self, producer: KafkaProducer = producer):
        """
        Parameters
        ----------
        producer: KafkaProducer
        """
        self._producer = producer
        self._db = db()

    def flush(self) -> None:
        """Publish all the message on the kafka topic given the website list.

        Iterates over the website list and extract the stats via the _StatsExtractor
        object.
        """
        for website in self._website_list:
            url = website.get("url")
            time_, error_code, page_content = _StatsExtractor.from_url(url)
            message = {
                "id": website.get("id"),
                "url": url,
                "time": time_,
                "error_code": error_code,
                "page_content": page_content,
            }
            self._publish_message(self._producer, TOPIC, value=json.dumps(message))

    @staticmethod
    def _publish_message(
        producer_instance: KafkaProducer, topic_name: str, value: serializable
    ) -> None:
        """Publish a single message on the kafka topic.

        Parameters
        ----------
        producer_instance : KafkaProducer
            The Kafka Producer instance to use as producer for the kafka topic
        topic_name: str
            The kafka topic name where publish the message
        value: serializable
            A serializable object that wraps the message to be sent
        """
        try:
            value_bytes = bytes(value, encoding="utf-8")
            producer_instance.send(topic_name, value=value_bytes)
            producer_instance.flush()
            logger.info(
                f"Stats for {json.loads(value)['url']} published "
                f"successfully on {topic_name}."
            )
        except Exception as ex:
            logger.error(f"Exception in publishing message: {str(ex)}")

    @property
    def _website_list(self) -> t.List[RealDictRow]:
        """List of all the websites row fount in the related DB table."""
        websites = self._db.query("SELECT * FROM websites;")
        return websites.fetchall()


def main():
    stats_producer = _StatsProducer()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schedule",
        help="Every N seconds you wanna run the producer. (0 only once)",
    )
    args = parser.parse_args()
    try:
        n_seconds = int(args.schedule)
    except (TypeError, ValueError):
        logger.warning("No valid scheduler option found, set to 0.")
        n_seconds = 0
    if n_seconds != 0:
        scheduler = StatsScheduler()
        scheduler.every(n_seconds).seconds.do(stats_producer.flush)
        logger.info(f"Job scheduled every {n_seconds} seconds.")
        while True:
            scheduler.run_pending()
            time.sleep(1)
    stats_producer.flush()


if __name__ == "__main__":
    main()
