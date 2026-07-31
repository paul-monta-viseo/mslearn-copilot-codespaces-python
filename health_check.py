"""Check the application's health endpoint."""

import argparse
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_HEALTH_URL = "http://localhost:8000/health"


def check_health(url: str, timeout: float = 5.0) -> int:
    """Request the health endpoint, print its result, and return an exit code."""
    try:
        with urlopen(url, timeout=timeout) as response:
            result = response.read().decode("utf-8")
            print(f"HTTP {response.status}: {result}")
            return 0
    except HTTPError as error:
        print(f"Health check failed: HTTP {error.code} {error.reason}", file=sys.stderr)
    except URLError as error:
        print(f"Health check failed: {error.reason}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.getenv("HEALTH_URL", DEFAULT_HEALTH_URL),
        help="Health endpoint URL (default: %(default)s)",
    )
    args = parser.parse_args()
    return check_health(args.url)


if __name__ == "__main__":
    raise SystemExit(main())
