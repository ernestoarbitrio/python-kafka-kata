import subprocess
import sys


def test_producer_message_queue():
    result = subprocess.run(
        [sys.executable, "-m", "websitestats.producer", "--schedule", "0"],
        capture_output=True,
        text=True,
    )

    assert "Connection complete" in result.stdout
    assert "published successfully on demo-topic" in result.stdout


def test_producer_set_schedule_to_zero_if_param_is_invalid():
    result = subprocess.run(
        [sys.executable, "-m", "websitestats.producer", "--schedule", "a"],
        capture_output=True,
        text=True,
    )

    assert (
        "WARNING:producer:No valid scheduler option found, set to 0." in result.stdout
    )
