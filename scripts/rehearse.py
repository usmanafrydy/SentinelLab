"""Check the full local workflow using synthetic data in a temporary folder."""
import http.client
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
from tempfile import TemporaryDirectory
from queue import Queue, Empty
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentinellab.web.auth import create_account


def worker(account, database):
    """Private worker closes on parent pipe EOF, including a parent crash."""
    from sentinellab.web.auth import Auth
    from sentinellab.web.server import LocalServer
    from sentinellab.storage.database import initialize_database
    with LocalServer(Path(database), 0, auth=Auth(Path(account))) as server:
        initialize_database(Path(database))
        thread = Thread(target=server.serve_forever, kwargs={'poll_interval':0.05})
        thread.start()
        try:
            print(json.dumps({'port':server.server_address[1]}), flush=True)
            sys.stdin.readline()
        finally:
            server.shutdown()
            thread.join(timeout=5)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def rehearse():
    checks = []
    with TemporaryDirectory(prefix='sentinellab-rehearsal-') as temporary:
        folder = Path(temporary)
        account, database = folder/'account.json', folder/'events.db'
        password = secrets.token_urlsafe(32)
        create_account(account, 'rehearsal_analyst', password)
        checks.append('Synthetic account created using account service')
        process = None
        cookie = token = ''
        port = None

        def request(method, path, data=None, kind='application/json', authenticated=True):
            headers = {}
            if authenticated and cookie:
                headers['Cookie'] = cookie
            if data is not None:
                headers.update({'Origin': f'http://127.0.0.1:{port}',
                                'X-SentinelLab-Token': token, 'Content-Type': kind})
                if not isinstance(data, bytes):
                    data = json.dumps(data).encode()
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
            try:
                connection.request(method, path, body=data, headers=headers)
                response = connection.getresponse()
                return response.status, dict(response.getheaders()), response.read()
            finally:
                connection.close()

        def post(path, body, kind='application/json'):
            status, _, raw = request('POST', path, body, kind)
            require(status == 200, 'Write failed at '+path)
            return json.loads(raw)

        def get(path):
            status, _, raw = request('GET', path)
            require(status == 200, 'Read failed at '+path)
            return json.loads(raw)

        def start():
            nonlocal process, port, cookie, token
            cookie = token = ''
            process = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), '--worker', str(account), str(database)], cwd=ROOT,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            ready = Queue()
            Thread(target=lambda: ready.put(process.stdout.readline()), daemon=True).start()
            try:
                line = ready.get(timeout=10)
            except Empty:
                raise RuntimeError('Server startup timed out') from None
            require(bool(line), 'Server process failed to start')
            port = json.loads(line)['port']
            status, _, raw = request('GET', '/login', authenticated=False)
            require(status == 200, 'Login page failed')
            token = re.search(rb'name="request-token" content="([0-9a-f]{64})"', raw)[1].decode()

        def stop():
            nonlocal process
            if process is not None:
                # EOF reaches the actual interpreter behind a Windows launcher.
                process.stdin.close()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    raise RuntimeError('Owned worker did not stop; cleanup is unverified') from None
                process.stdout.close()
                require(process.returncode == 0, 'Rehearsal worker did not exit cleanly')
                process = None

        def login():
            nonlocal cookie, token
            status, headers, _ = request('POST', '/api/login',
                                        {'username':'rehearsal_analyst', 'password':password},
                                        authenticated=False)
            require(status == 200, 'Synthetic sign-in failed')
            cookie = headers['Set-Cookie'].split(';')[0]
            status, _, raw = request('GET', '/')
            require(status == 200, 'Authenticated workspace failed')
            token = re.search(rb'name="request-token" content="([0-9a-f]{64})"', raw)[1].decode()

        try:
            start()
            require(request('GET','/api/summary',authenticated=False)[0] == 401, 'Anonymous access allowed')
            login()
            checks.append('Separate server process and authenticated workspace')
            sample = (ROOT/'data/samples/day07_all_rules.jsonl').read_bytes()
            imported = post('/api/import', sample, 'application/x-ndjson')
            require(imported['inserted'] == 16 and imported['rejected'] == 0, 'Sample import counts differ')
            repeated = post('/api/import', sample, 'application/x-ndjson')
            require(repeated['inserted'] == 0 and repeated['duplicates'] == 16, 'Import doubled evidence')
            checks.append('16 events imported; repeated upload adds zero events')
            post('/api/detect', b'rule=all', 'application/x-www-form-urlencoded')
            findings = get('/api/alerts')['items']
            require(len(findings) == 3 and {a['rule_id'] for a in findings} == {'R1','R2','R3'}, 'Rule findings differ')
            post('/api/detect', b'rule=all', 'application/x-www-form-urlencoded')
            require(get('/api/alerts')['total'] == 3 and get('/api/runs')['total'] == 2, 'Repeated save changed alert count')
            checks.append('Three saved rule findings; second run adds no duplicate alerts')
            alert = next(a for a in findings if a['rule_id'] == 'R3')
            created = post('/api/cases', {'alert_id':alert['alert_id'], 'title':'Synthetic setup rehearsal', 'author':'ignored'})
            case_id = created['case']['id']
            base = '/api/cases/'+case_id
            post(base+'/notes', {'text':'Synthetic review: alert needs context, not automatic proof.', 'author':'ignored'})
            post(base+'/state', {'status':'closed','disposition':'suspicious',
                                'reason':'Synthetic suspicious pattern retained for demonstration.',
                                'author':'ignored','expected_revision':'2'})
            case = get(base)
            require(case['revision'] == '3' and case['status'] == 'closed', 'Case transition failed')
            report = get(base+'/report?format=json&revision=3')
            require(len(report['actions']) == 3 and report['case']['revision'] == '3', 'Report history incomplete')
            require({a['author'] for a in report['actions']} == {'rehearsal_analyst'}, 'Report author is not session user')
            source_records = {line.decode() for line in sample.splitlines() if line.strip()}
            require(bool(report['evidence']) and all(e['original_record'] in source_records for e in report['evidence']), 'Original evidence differs')
            status, headers, raw = request('GET',base+'/report?format=markdown&revision=3')
            require(status == 200 and b'# SentinelLab investigation report' in raw
                    and 'attachment' in headers.get('Content-Disposition',''), 'Markdown attachment failed')
            checks.append('Case, session-authored note, decision and complete JSON/Markdown exports')
            old_cookie = cookie
            stop()
            start()
            cookie = old_cookie
            require(request('GET','/api/summary')[0] == 401, 'Restart retained an old session')
            cookie = ''
            login()
            require(get(base) == case, 'Restart changed saved case')
            require(get('/api/alerts')['total'] == 3, 'Restart lost alerts')
            post('/api/logout', {})
            require(request('GET','/api/summary')[0] == 401, 'Logout retained access')
            checks.append('Process restart preserves saved work; old sessions and logout are rejected')
        finally:
            stop()
    checks.append('Temporary account, database and files removed')
    return {'status':'passed','checks':checks,'python':sys.version.split()[0],
            'isolated_environment':sys.prefix != sys.base_prefix,
            'limits':['Synthetic HTTP workflow, not a browser usability audit.',
                      'Account service exercised; interactive hidden password entry is separate.',
                      'No fresh operating-system or production-deployment certification.']}


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--worker':
        worker(sys.argv[2], sys.argv[3])
        raise SystemExit(0)
    if len(sys.argv) != 1:
        raise SystemExit('Usage: python scripts/rehearse.py')
    try:
        print(json.dumps(rehearse(), indent=2))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print(json.dumps({'status':'failed','reason':str(error) if isinstance(error,RuntimeError) else 'Check Python capabilities, writable temporary storage and local server startup.'}))
        raise SystemExit(1)
