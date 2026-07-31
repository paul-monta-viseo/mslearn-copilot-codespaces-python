import health_check


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
