import pathlib
from datetime import datetime

import pytest

from firealertserver.pushnotification import TokenStorage, FileTokenStorage, Token


def create_token_storage(tmp_path: pathlib.Path) -> TokenStorage:
    return FileTokenStorage(tmp_path / 'tokens.json')


def test_when_wrong_data_to_update_then_error(tmp_path):
    with pytest.raises(ValueError):
        create_token_storage(tmp_path).update(None)
    with pytest.raises(ValueError):
        create_token_storage(tmp_path).update({})


def test_when_empty_storage_then_get_returns_none(tmp_path):
    assert create_token_storage(tmp_path).get() is None
    assert create_token_storage(tmp_path).get() is None


def test_when_saved_token_then_load_it_from_token_storage(tmp_path):
    token = Token(payload='my_payload', created_at=datetime.now())
    create_token_storage(tmp_path).update(token)
    assert create_token_storage(tmp_path).get() == token


def test_when_saved_token_multiple_times_then_load_it_from_token_storage(tmp_path):
    created_at = datetime.now()
    token1 = Token(payload='my_payload', created_at=created_at)
    token2 = Token(payload='other_payload', created_at=created_at)
    token3 = Token(payload='my_payload', created_at=created_at)
    assert token1 != token2
    assert token1 == token3

    storage1 = create_token_storage(tmp_path)
    storage1.update(token1)
    assert storage1.get() == token1
    assert storage1.get() == token3

    storage1.update(token2)
    assert storage1.get() == token2

    storage2 = create_token_storage(tmp_path)
    assert storage2.get() == token2


def test_when_tested_empty_storage_then_we_can_test_it_again_later(tmp_path):
    assert create_token_storage(tmp_path).get() == None
    assert create_token_storage(tmp_path).get() == None
