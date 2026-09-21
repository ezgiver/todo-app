"""Small local before/after experiment; human quality review is still required."""
import json
import subprocess
import time
from pathlib import Path
from app import create_app
from app.services.ollama import suggest_steps

BASELINE_REF = 'codex/structured-ai-steps'
baseline = {'__package__': 'app.services'}
exec(subprocess.check_output(['git', 'show', f'{BASELINE_REF}:backend/app/services/ollama.py'], text=True), baseline)
cases = [
    ('Do a 15 minute workout', 'I do not know which moves to choose', 15),
    ('Improve my technical skills', 'Too many things to learn; I have a Flask app connected to Ollama', 20),
    ('Cook a healthy and delicious meal', 'Choosing a recipe and getting groceries', None),
]
app = create_app('config.TestingConfig')
report = {'baseline_commit': subprocess.check_output(['git', 'rev-parse', BASELINE_REF], text=True).strip(), 'model': app.config['OLLAMA_MODEL'], 'settings': {'temperature': 0.2, 'num_predict': 512}, 'method': 'One run per case and version. Baseline sees task only; candidate also sees blocker/time. Combined prompt/context change, not an isolated prompt comparison. Human ratings pending.', 'cases': []}
with app.app_context():
    for task, blocker, minutes in cases:
        row = {'task': task, 'blocker': blocker, 'available_minutes': minutes}
        for name, run in [('baseline', lambda: baseline['suggest_steps'](task)), ('candidate', lambda: suggest_steps(task, blocker, minutes))]:
            start = time.monotonic()
            try:
                row[name] = {'result': run()}
            except Exception as exc:
                row[name] = {'error': str(exc)}
            row[name]['seconds'] = round(time.monotonic() - start, 2)
            print(task, name, json.dumps(row[name]), flush=True)
        report['cases'].append(row)
        Path('../evaluations/context-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
