import runpy
import sys
import urllib.request
from urllib.error import HTTPError, URLError

import health_check
import pytest


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return b'{"status": "ok"}'


def test_check_health_prints_response(mocker, capsys):
    urlopen = mocker.patch("health_check.urlopen", return_value=FakeResponse())

    result = health_check.check_health("http://localhost:8000/health")

    assert result == 0
    urlopen.assert_called_once_with("http://localhost:8000/health", timeout=5.0)
    assert capsys.readouterr().out == 'HTTP 200: {"status": "ok"}\n'


def test_check_health_returns_one_for_http_error(mocker, capsys):
    error = HTTPError("http://localhost:8000/health", 503, "Unavailable", {}, None)
    mocker.patch("health_check.urlopen", side_effect=error)

    result = health_check.check_health("http://localhost:8000/health")

    assert result == 1
    assert "HTTP 503 Unavailable" in capsys.readouterr().err


def test_check_health_returns_one_for_url_error(mocker, capsys):
    mocker.patch(
        "health_check.urlopen",
        side_effect=URLError("connection refused"),
    )

    result = health_check.check_health("http://localhost:8000/health")

    assert result == 1
    assert "connection refused" in capsys.readouterr().err


def test_main_uses_command_line_url(mocker):
    check_health = mocker.patch("health_check.check_health", return_value=7)
    mocker.patch.object(sys, "argv", ["health_check", "--url", "http://example.test"])

    assert health_check.main() == 7
    check_health.assert_called_once_with("http://example.test")


def test_script_entry_point_exits_with_health_result(mocker):
    mocker.patch.object(sys, "argv", ["health_check", "--url", "http://example.test"])
    mocker.patch.object(urllib.request, "urlopen", return_value=FakeResponse())

    with pytest.raises(SystemExit) as error:
        runpy.run_path("health_check.py", run_name="__main__")

    assert error.value.code == 0
