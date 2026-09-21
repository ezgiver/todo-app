import io
import json
from unittest.mock import patch
from urllib.error import URLError

import pytest


def test_requires_login(client):
    assert client.post('/api/assistant/next-step', json={'task': 'Start'}).status_code == 401


@pytest.mark.parametrize('body', [None, [], {}, {'task': 1}, {'task': ' '}, {'task': 'x' * 1001}])
def test_invalid_input(client, register_and_login, body):
    register_and_login()
    assert client.post('/api/assistant/next-step', json=body).status_code == 400


def test_suggestion_is_not_saved(client, register_and_login):
    register_and_login()
    response = io.BytesIO(json.dumps({'message': {'content': 'Write one sentence. Stop when saved.'}}).encode())
    with patch('app.services.ollama.urlopen', return_value=response) as call:
        result = client.post('/api/assistant/next-step', json={'task': ' Start my app '})
    assert result.status_code == 200
    assert result.json['step'] == 'Write one sentence. Stop when saved.'
    payload = json.loads(call.call_args.args[0].data)
    assert payload['messages'][-1]['content'] == 'Start my app'
    assert payload['stream'] is False
    assert client.get('/api/todos/').json == []


def test_offline(client, register_and_login):
    register_and_login()
    with patch('app.services.ollama.urlopen', side_effect=URLError('offline')):
        assert client.post('/api/assistant/next-step', json={'task': 'Start'}).status_code == 503


@pytest.mark.parametrize('response', [b'bad json', b'[]', b'{"message": {"content": ""}}', json.dumps({'message': {'content': 'x' * 256}}).encode()])
def test_bad_model_response(client, register_and_login, response):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=io.BytesIO(response)):
        assert client.post('/api/assistant/next-step', json={'task': 'Start'}).status_code == 503
