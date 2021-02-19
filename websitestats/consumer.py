# encoding: utf-8

"""Provides consumer facilities for consuming website statistics on a kafka topic"""

import json
import logging
import sys

from kafka import KafkaConsumer

from .settings import Database as db
from .settings import consumer

logger = logging.getLogger("consumer")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class _StatsConsumer:
    """Stats consumer object."""

    def __init__(self, consumer: KafkaConsumer = consumer):
        """
        Parameters
        ----------
        consumer: KafkaConsumer
        """
        self._db = db()
        self._consumer = consumer

    def write_messages(self):
        """Consume the message from the topic and write a tuple into a DB table."""
        try:
            for msg in self._consumer:
                stats = json.loads(msg.value.decode("utf-8"))
                try:
                    self._db.query(
                        "INSERT INTO public.stats "
                        "(http_response_time, error_code, content, website_id) "
                        "VALUES (%s, %s, %s, %s);",
                        (
                            stats["time"],
                            stats["error_code"],
                            stats["page_content"],
                            stats["id"],
                        ),
                    )
                    logger.info(
                        f"Stats for {stats['url']} [time : {stats['time']}, "
                        f"error_code: {stats['error_code']}] has been saved."
                    )
                except Exception:
                    logger.error(f"Error: {stats['url']} not saved!!!")
                    pass
        except KeyboardInterrupt:
            consumer.commit()
            consumer.close()


def main():
    stats_consumer = _StatsConsumer(consumer)
    stats_consumer.write_messages()


if __name__ == "__main__":
    main()
