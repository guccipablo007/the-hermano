import os, json, yaml, urllib.request, urllib.error
from pathlib import Path

def clean_value(v):
    v = (v or '').strip().strip('"').strip("'")
    if v.startswith('Bearer '):
        v = v.split(' ', 1)[1].strip()
    return v

def load_key():
    for k in ['OPENROUTER_API_KEY', 'OPENAI_API_KEY']:
        v = clean_value(os.environ.get(k))
        if v:
            return v
    for envp in [Path('/root/.hermes/.env'), Path('/usr/local/lib/hermes-agent/.env')]:
        if envp.exists():
            for line in envp.read_text(errors='ignore').splitlines():
                raw = line.strip()
                if not raw or raw.startswith('#') or '=' not in raw:
                    continue
                k, v = raw.split('=', 1)
                k = k.replace('export ', '').strip()
                if k in ['OPENROUTER_API_KEY', 'OPENAI_API_KEY']:
                    v = clean_value(v)
                    if v:
                        return v
    cfg = Path('/root/.hermes/config.yaml')
    if cfg.exists():
        data = yaml.safe_load(cfg.read_text()) or {}
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if isinstance(k, str) and 'key' in k.lower() and isinstance(v, str):
                        cv = clean_value(v)
                        if cv and ('sk-' in cv or len(cv) > 20):
                            return cv
                    r = walk(v)
                    if r:
                        return r
            elif isinstance(x, list):
                for item in x:
                    r = walk(item)
                    if r:
                        return r
            return None
        key = walk(data)
        if key:
            return key
    raise SystemExit('NO_OPENROUTER_KEY_FOUND')

def test_model(model):
    key = load_key()
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'Use the tool to create a file named test.txt with content hello. Do not write code in prose.'}],
        'tools': [{
            'type': 'function',
            'function': {
                'name': 'write_file',
                'description': 'Write text content to a file path.',
                'parameters': {
                    'type': 'object',
                    'properties': {'path': {'type': 'string'}, 'content': {'type': 'string'}},
                    'required': ['path', 'content']
                }
            }
        }],
        'tool_choice': 'auto',
        'max_tokens': 500
    }
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://hermes.local',
            'X-Title': 'Hermes Tool Call Test'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(json.dumps({'model': model, 'http_error': e.code, 'body_preview': body[:500]}, indent=2))
        return False
    msg = data.get('choices', [{}])[0].get('message', {})
    has_tool_calls = bool(msg.get('tool_calls'))
    print(json.dumps({
        'model': model,
        'has_tool_calls': has_tool_calls,
        'tool_calls_preview': msg.get('tool_calls'),
        'content_preview': (msg.get('content') or '')[:500]
    }, indent=2))
    return has_tool_calls

models = ['deepseek/deepseek-chat', 'openai/gpt-oss-120b', 'qwen/qwen3-coder', 'anthropic/claude-sonnet-4.5']
results = {}
for m in models:
    print('\n=== TEST_MODEL', m, '===')
    try:
        results[m] = test_model(m)
    except Exception as e:
        print(json.dumps({'model': m, 'error': repr(e)}, indent=2))
        results[m] = False
print('\n=== SUMMARY ===')
print(json.dumps(results, indent=2))
