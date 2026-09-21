import io
import json
from unittest.mock import patch
from urllib.error import URLError
import pytest

STEP = {'action': 'Open the app', 'done_when': 'The task list is visible'}

def response(content, **overrides):
    return io.BytesIO(json.dumps({'done': True, 'done_reason': 'stop', 'message': {'content': content}, **overrides}).encode())

@pytest.mark.parametrize('count', [1, 3])
def test_valid(client, register_and_login, count):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=response(json.dumps({'steps': [STEP] * count}))) as call:
        r = client.post('/api/assistant/steps', json={'task': ' Start '})
    assert r.status_code == 200
    assert r.json == {'steps': [STEP] * count}
    payload = json.loads(call.call_args.args[0].data)
    assert payload['format']['properties']['steps']['maxItems'] == 3
    assert json.loads(payload['messages'][-1]['content']) == {'task': 'Start'}
    assert client.get('/api/todos/').json == []

@pytest.mark.parametrize('body', ['invalid', {'steps': []}, {'steps': [STEP] * 4}, {'steps': [{'action': 'x'}]}, {'steps': [{**STEP, 'extra': 'x'}]}, {'steps': [STEP], 'extra': True}, {'steps': [{**STEP, 'action': 4}]}, {'steps': [{**STEP, 'action': ' '}]}, {'steps': [{**STEP, 'done_when': 'x' * 121}]}])
def test_invalid_output(client, register_and_login, body):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=response(body if isinstance(body, str) else json.dumps(body))):
        assert client.post('/api/assistant/steps', json={'task': 'Start'}).status_code == 503

@pytest.mark.parametrize('metadata', [{'done': False}, {'done_reason': 'length'}])
def test_incomplete(client, register_and_login, metadata):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=response(json.dumps({'steps': [STEP]}), **metadata)):
        assert client.post('/api/assistant/steps', json={'task': 'Start'}).status_code == 503

@pytest.mark.parametrize('error', [URLError('offline'), TimeoutError()])
def test_failure(client, register_and_login, error):
    register_and_login()
    with patch('app.services.ollama.urlopen', side_effect=error):
        assert client.post('/api/assistant/steps', json={'task': 'Start'}).status_code == 503

def test_auth(client):
    assert client.post('/api/assistant/steps', json={'task': 'Start'}).status_code == 401

@pytest.mark.parametrize('body', [[], {}, {'task': ' '}, {'task': 3}, {'task': 'x' * 1001}])
def test_input(client, register_and_login, body):
    register_and_login()
    with patch('app.services.ollama.urlopen') as call:
        assert client.post('/api/assistant/steps', json=body).status_code == 400
        call.assert_not_called()

def test_trim_and_save(client, register_and_login):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=response(json.dumps({'steps': [{'action': ' a ', 'done_when': ' b '}]}))):
        assert client.post('/api/assistant/steps', json={'task': 'Start'}).json['steps'][0] == {'action': 'a', 'done_when': 'b'}
    title = 'a' * 120 + ' — Done when: ' + 'b' * 120
    assert len(title) <= 255
    r = client.post('/api/todos/', json={'title': title})
    assert r.status_code == 201
    assert r.json['title'] == title


@pytest.mark.parametrize('extra', [{'blocker': None}, {'blocker': 3}, {'blocker': 'x' * 1001}, {'available_minutes': True}, {'available_minutes': 0}, {'available_minutes': 121}, {'available_minutes': 1.5}, {'available_minutes': '20'}])
def test_invalid_context(client, register_and_login, extra):
    register_and_login()
    with patch('app.services.ollama.urlopen') as call:
        assert client.post('/api/assistant/steps', json={'task': 'Start', **extra}).status_code == 400
        call.assert_not_called()


def test_context_reaches_model(client, register_and_login):
    register_and_login()
    with patch('app.services.ollama.urlopen', return_value=response(json.dumps({'steps': [STEP]}))) as call:
        assert client.post('/api/assistant/steps', json={'task': 'Start', 'blocker': ' Too many choices ', 'available_minutes': 20}).status_code == 200
    payload = json.loads(call.call_args.args[0].data)
    assert json.loads(payload['messages'][-1]['content']) == {'task': 'Start', 'blocker': 'Too many choices', 'available_minutes': 20}
