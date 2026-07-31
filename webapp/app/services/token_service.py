import base64
import os


class TokenService:
    def generate(self, length: int) -> str:
        token = base64.b64encode(os.urandom(64))[:length].decode("utf-8")
        self._tokens.append(token)
        return token

    def __init__(self) -> None:
        self._tokens: list[str] = []

    def list_paginated(self, page: int, page_size: int) -> tuple[list[str], int]:
        start = (page - 1) * page_size
        end = start + page_size
        return self._tokens[start:end], len(self._tokens)


token_service = TokenService()


def get_token_service() -> TokenService:
    return token_service
