from unittest import mock

from websitestats.consumer import _StatsConsumer


class Describe_StatsConsumer:
    @mock.patch("websitestats.consumer.db")
    def test_consume_messages(self, mock_db):
        mock_db.return_value = mock.MagicMock()
        mock_obj = mock.MagicMock()
        mock_obj.value = (
            b'{"time":1, "error_code": 0, "page_content":"a", "id":2, '
            b'"url": "www.foo.bar"}'
        )
        stats_consumer = _StatsConsumer([mock_obj])

        stats_consumer.write_messages()

        assert mock_db.return_value.query.called
        assert mock_db.return_value.query.call_args_list == [
            mock.call(
                "INSERT INTO public.stats (http_response_time, error_code, content, "
                "website_id) VALUES (%s, %s, %s, %s);",
                (1, 0, "a", 2),
            )
        ]
