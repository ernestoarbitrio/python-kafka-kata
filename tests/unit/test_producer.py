from unittest import mock
from unittest.mock import patch

import pytest
from kafka import KafkaProducer
from psycopg2.extras import RealDictRow

from websitestats.producer import _StatsExtractor, _StatsProducer

from ..mockserver import get_free_port, start_mock_server
from ..unitutil import method_mock, property_mock


class Describe_StatsProducer:
    @patch("websitestats.producer.producer")
    def test_produce_message(self, KafkaProducerMock):
        stats_producer = _StatsProducer()
        stats_producer._publish_message(KafkaProducerMock, "topic", "data")

        KafkaProducerMock.send.assert_called_once()

    @patch("websitestats.producer.producer")
    def test_verify_produce_message(self, KafkaProducerMock):
        stats_producer = _StatsProducer()
        stats_producer._publish_message(KafkaProducerMock, "topic", "data")

        args = KafkaProducerMock.send.call_args

        assert args[0] == ("topic",)
        assert args[1] == {"value": b"data"}

    @mock.patch("websitestats.producer._StatsExtractor.from_url")
    def test_producer_flush(self, mock_extractor, request):
        mock_obj = mock.MagicMock()
        mock_obj.value = KafkaProducer
        stats_producer = _StatsProducer(mock_obj)
        _website_list = property_mock(request, _StatsProducer, "_website_list")
        _publish_message = method_mock(
            request, _StatsProducer, "_publish_message", autospec=True
        )
        mock_extractor.return_value = [0.0, None, "foo"]
        _website_list.return_value = [
            RealDictRow(
                [
                    ("id", 4),
                    ("name", "python website"),
                    ("url", "https://www.python.org"),
                ]
            ),
        ]

        stats_producer.flush()

        assert _publish_message.called
        assert _publish_message.call_args_list == [
            mock.call(
                mock_obj,
                "demo-topic",
                value='{"id": 4, "url": "https://www.python.org", "time": 0.0, '
                '"error_code": null, "page_content": "foo"}',
            )
        ]

    @patch("psycopg2.connect")
    def it_knows_its_website_list(self, mock_connect):
        expected = [
            RealDictRow(
                [
                    ("id", 4),
                    ("name", "python website"),
                    ("url", "https://www.python.org"),
                ]
            ),
            RealDictRow(
                [
                    ("id", 5),
                    ("name", "foo"),
                    ("url", "https://www.foo.bar"),
                ]
            ),
        ]
        # Mocking DB connection
        mock_con = mock_connect.return_value
        mock_cur = mock_con.cursor.return_value
        mock_cur.fetchall.return_value = expected
        stats_producer = _StatsProducer()

        website_list = stats_producer._website_list

        assert website_list == expected


class Describe_StatsExtractor:
    @classmethod
    def setup_class(cls):
        cls.mock_server_port = get_free_port()
        start_mock_server(cls.mock_server_port)

    @pytest.fixture
    def regex_patched(self, monkeypatch):
        regexp = ["<title>(.*)</title>"]
        monkeypatch.setattr("websitestats.producer.REGEX_PATTERNS", regexp)
        return regexp

    def test_extract_statistic_from_url(self, regex_patched):
        base_url = "http://localhost:{port}/data/".format(port=self.mock_server_port)

        _, error_code, page_content = _StatsExtractor.from_url(base_url)

        assert error_code is None
        assert page_content == "hello world"

    def but_it_return_service_unavailable_when_url_is_worng(self):
        base_url = "http://localhost:{port}".format(port=self.mock_server_port)

        _, error_code, page_content = _StatsExtractor.from_url(base_url)

        assert error_code == 503
        assert page_content == ""

    def and_it_collect_statistics_even_if_a_conn_error_occuerred(self):
        time_, error_code, page_content = _StatsExtractor.from_url("www.foo.bar")

        assert error_code == 503
        assert time_ == 0.0
        assert page_content is None
