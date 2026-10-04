"""Real HTTP authentication gates plus session and credential invariants."""
import json
from pathlib import Path
import re
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from sentinellab.web.auth import Auth, create_account, IDLE_SECONDS, ABSOLUTE_SECONDS
from sentinellab.web.server import LocalServer, main
from sentinellab.storage.database import initialize_database, import_events
from sentinellab.storage.alerts import save_detection, list_history
from sentinellab.storage.cases import case_history
from tests.integration import test_web as fixture

ROOT = Path(__file__).resolve().parents[2]
PASSWORD = 'Synthetic test password only 2026'

class AuthTests(unittest.TestCase):
    request = fixture.WebTests.request
    cleanup = fixture.WebTests.cleanup

    @classmethod
    def setUpClass(cls):
        cls.account_temp = tempfile.TemporaryDirectory()
        cls.account = Path(cls.account_temp.name) / 'account.json'
        create_account(cls.account, 'test_analyst', PASSWORD)

    @classmethod
    def tearDownClass(cls):
        cls.account_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'events.db'
        initialize_database(self.db)
        self.now = 100.0
        self.auth = Auth(self.account, clock=lambda:self.now)
        self.server = LocalServer(self.db, port=0, auth=self.auth)
        self.worker = Thread(target=self.server.serve_forever, kwargs={'poll_interval':0.01}, daemon=True)
        self.worker.start()
        self.addCleanup(self.cleanup)

    def post(self, path, data, *, cookie=None, token=None, **changes):
        headers = {'Origin':self.server.origin, 'X-SentinelLab-Token':token or self.server.token,
                   'Content-Type':'application/json'}
        if cookie: headers['Cookie'] = cookie
        headers.update(changes)
        return self.request('POST', path, data if isinstance(data,bytes) else json.dumps(data).encode(),headers)

    def login(self, **changes):
        return self.post('/api/login', {'username':'test_analyst','password':PASSWORD}, **changes)

    def signed_in(self):
        code,headers,body = self.login()
        self.assertEqual(code,200,body)
        cookie=headers['Set-Cookie'].split(';')[0]
        page=self.request('GET','/',headers={'Cookie':cookie})[2].decode()
        token=re.search(r'name="request-token" content="([0-9a-f]{64})"',page)[1]
        return cookie,token

    def test_anonymous_all_data_reads_and_writes_are_gated(self):
        before=self.db.read_bytes()
        page=self.request('GET','/')[2]
        self.assertIn(b'Sign in to SentinelLab',page)
        self.assertNotIn(b'Find login activity',page)
        for path in ('/api/summary','/api/events','/api/events/1','/api/alerts','/api/alerts/summary','/api/runs','/api/cases','/api/cases/1','/api/cases/1/history'):
            self.assertEqual(self.request('GET',path)[0],401,path)
        for path in ('/api/import','/api/detect','/api/cases','/api/cases/1/notes','/api/cases/1/state','/api/logout'):
            self.assertEqual(self.post(path,{})[0],401,path)
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(self.request('GET','/static/auth.js')[0],200)
        self.assertEqual(self.request('GET','/static/../auth.py')[0],404)

    def test_success_cookie_rotation_and_logout(self):
        code, headers, body=self.login()
        self.assertEqual(code,200)
        cookie=headers['Set-Cookie'].split(';')[0]
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        self.assertIn('SameSite=Strict',headers['Set-Cookie'])
        self.assertNotIn('Domain=',headers['Set-Cookie'])
        self.assertNotIn(PASSWORD.encode(),body)
        code,headers,_=self.login(cookie=cookie)
        rotated=headers['Set-Cookie'].split(';')[0]
        self.assertNotEqual(cookie,rotated)
        self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':cookie})[0],401)
        key=rotated.partition('=')[2]
        token=self.auth.get(key)['csrf']
        self.assertNotEqual(token,self.server.token)
        code,headers,_=self.post('/api/logout',{},cookie=rotated,token=token)
        self.assertEqual(code,200)
        self.assertIn('Max-Age=0',headers['Set-Cookie'])
        self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':rotated})[0],401)

    def test_bad_password_username_and_rate_limit(self):
        for i in range(5):
            data={'username':'unknown' if i%2 else 'test_analyst','password':'Wrong synthetic password'}
            code,_,body=self.post('/api/login',data)
            self.assertEqual(code,401)
            self.assertEqual(json.loads(body)['error'],'Username or password is incorrect.')
        self.assertEqual(self.login()[0],429)
        self.now+=60
        self.assertEqual(self.login()[0],200)

    def test_login_request_protections(self):
        # These checks reject headers before reading the body. Send an empty
        # body to avoid racing the server's early close with a discarded upload
        # on Windows; malformed JSON/body checks remain separate below.
        for changes in ({'Origin':'null'},{'Host':'foreign.invalid'},{'X-SentinelLab-Token':'wrong'},{'Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.post('/api/login', b'', **changes)[0],403)
        self.assertEqual(self.post('/api/login', b'', **{'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.post('/api/login',b'',**{'Content-Length':'4097'})[0],413)
        self.assertEqual(self.post('/api/login',b'',**{'Transfer-Encoding':'chunked'})[0],411)
        for data in (b'null',b'[]',b'{',b'\xff',b'{"username":"a","username":"b","password":"x"}',b'{"username":NaN,"password":"x"}',{},dict(username='test_analyst',password=1)):
            self.assertEqual(self.post('/api/login',data)[0],400)

    def test_authenticated_writes_need_session_token(self):
        cookie,token=self.signed_in()
        self.assertEqual(self.post('/api/logout',{},cookie=cookie)[0],403)
        self.assertEqual(self.post('/api/logout',{},cookie=cookie,token=token,Origin='null')[0],403)
        self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':cookie})[0],200)

    def test_server_uses_account_instead_of_spoofed_author(self):
        import_events(ROOT/'data/samples/day07_all_rules.jsonl',self.db)
        save_detection(self.db)
        alert=list_history(self.db)['items'][0]['alert_id']
        cookie,token=self.signed_in()
        self.assertEqual(self.post('/api/cases',dict(alert_id=alert,title='Review',author='forged'),cookie=cookie,token=token)[0],200)
        self.assertEqual(self.post('/api/cases/1/notes',dict(text='Synthetic observation',author='forged'),cookie=cookie,token=token)[0],200)
        self.assertEqual(self.post('/api/cases/1/state',dict(status='in_progress',disposition='undecided',reason='Reviewing',author='forged',expected_revision='2'),cookie=cookie,token=token)[0],200)
        self.assertEqual({a['author'] for a in case_history(self.db,1)['items']},{'test_analyst'})

    def test_idle_and_absolute_expiry_checked_server_side(self):
        cookie,_=self.signed_in()
        self.now+=IDLE_SECONDS
        self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':cookie})[0],401)
        cookie,_=self.signed_in()
        for _ in range(ABSOLUTE_SECONDS//300):
            self.now+=300
            result=self.request('GET','/api/summary',headers={'Cookie':cookie})[0]
        self.assertEqual(result,401)

    def test_duplicate_and_malformed_cookies_rejected(self):
        cookie,_=self.signed_in()
        for value in (cookie+'; '+cookie, cookie+'x','sentinellab=anything'):
            self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':value})[0],401)
        self.assertEqual(self.request('GET','/api/summary',headers={'Cookie':'other=value; '+cookie})[0],200)

    def test_bounded_sessions_verification_and_restart(self):
        with patch('sentinellab.web.auth.derive',return_value=self.auth.password_hash):
            for _ in range(10): self.assertEqual(self.auth.login('test_analyst',PASSWORD)[0],200)
            self.now+=61
            self.assertEqual(self.auth.login('test_analyst',PASSWORD)[0],429)
            self.auth.sessions.clear()
            self.auth.verifier.acquire()
            try: self.assertEqual(self.auth.login('test_analyst',PASSWORD)[0],429)
            finally: self.auth.verifier.release()
            code,key=self.auth.login('test_analyst',PASSWORD)
            self.assertEqual(code,200)
        self.assertIsNone(Auth(self.account).get(key))

    def test_account_is_hashed_salted_and_exclusive(self):
        data=json.loads(self.account.read_text())
        self.assertNotIn(PASSWORD,self.account.read_text())
        self.assertEqual(len(data['salt']),32)
        second=Path(self.temp.name)/'second.json'
        create_account(second,'test_analyst',PASSWORD)
        self.assertNotEqual(json.loads(second.read_text())['password_hash'],data['password_hash'])
        with self.assertRaises(FileExistsError): create_account(second,'test_analyst',PASSWORD)
        for username,password in [('bad name',PASSWORD),('valid','short')]:
            with self.assertRaises(ValueError): create_account(Path(self.temp.name)/'bad.json',username,password)

    def test_invalid_or_missing_account_fails_closed_without_database(self):
        for content in ('{}','[]','null','{"version":99}','x'*4097,
                        '['*1500+']'*1500, self.account.read_text().replace('{','{"version":1,',1)):
            path=Path(self.temp.name)/'invalid.json';path.write_text(content)
            with self.assertRaises(ValueError): Auth(path)
        with self.assertRaises(ValueError): LocalServer(self.db,0)
        missing=Path(self.temp.name)/'absent.db'
        self.assertEqual(main(['--database',str(missing),'--credentials',str(Path(self.temp.name)/'missing.json'),'--port','8779']),2)
        self.assertFalse(missing.exists())
