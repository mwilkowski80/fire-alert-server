import json
import logging
import pathlib
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Token(object):
    payload: str
    created_at: datetime

    def to_jsonable_dict(self):
        return {
            'payload': self.payload,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def from_jsonable_dict(dict_: dict) -> 'Token':
        return Token(
            payload=dict_['payload'],
            created_at=datetime.fromisoformat(dict_['created_at'])
        )


class TokenStorage(object):
    def update(self, token: Token) -> None:
        raise NotImplementedError()

    def get(self) -> Token:
        raise NotImplementedError()


class FileTokenStorage(TokenStorage):
    def __init__(self, path: pathlib.Path):
        self._path = path

    def update(self, token: Token) -> None:
        if not isinstance(token, Token):
            raise ValueError('You did not provide a token (instance of the Token class)')

        with open(self._path, 'w') as f:
            json.dump(token.to_jsonable_dict(), f)

    def get(self) -> Token:
        if self._path.exists():
            with open(self._path, 'r') as f:
                return Token.from_jsonable_dict(json.load(f))


import firebase_admin
from firebase_admin import messaging


class PushNotification(object):
    def __init__(self, token_storage: TokenStorage,
                 priority: str = 'high', ttl: int = 60):
        self._token_storage = token_storage
        self._log = logging.getLogger(f'{__name__}.{PushNotification.__name__}')
        self._priority = priority
        self._ttl = ttl
        self.maybe_init_firebase_app()

    def update_user_token(self, user_token: str):
        self._token_storage.update(
            Token(payload=user_token, created_at=datetime.utcnow()))

    def push(self, payload: dict):
        user_token = self._token_storage.get()
        message = messaging.Message(
            data=payload,
            token=user_token.payload,
            android=messaging.AndroidConfig(priority=self._priority, ttl=self._ttl),
        )
        response = messaging.send(message)
        self._log.info(f'Successfully sent alert: {response}')

    def maybe_init_firebase_app(self):
        try:
            firebase_admin.get_app()
        except:
            firebase_admin.initialize_app()
