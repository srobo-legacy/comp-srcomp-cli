
from nose.tools import raises
from datetime import timedelta

from sr.comp.cli.add_delay import parse_duration, BadDurationException

def test_bad_inputs():
    @raises(BadDurationException)
    def check(ts):
        parse_duration(ts)

    yield check, "nope"
    yield check, "now"
    yield check, "5dd"


def test_valid_inputs():
    def check(time_str, expected):
        td = parse_duration(time_str)
        assert expected == td

    yield check, "1m", timedelta(minutes = 1)
    yield check, "1s", timedelta(seconds = 1)
    yield check, "42", timedelta(seconds = 42)
    yield check, "42s", timedelta(seconds = 42)
    yield check, "1hr", timedelta(hours = 1)
