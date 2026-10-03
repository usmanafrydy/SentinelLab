"""Single-account local password verification and in-memory sessions."""
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import secrets
from threading import Lock
import time

N = 131072
MAX_MEMORY = 256 * 1024 * 1024
IDLE_SECONDS = 15 * 60
ABSOLUTE_SECONDS = 8 * 60 * 60


def password_bytes(password):
    if not isinstance(password, str) or not 15 <= len(password) <= 128:
        raise ValueError('Use a password of 15 to 128 characters.')
    raw = password.encode('utf-8')
    if len(raw) > 512:
        raise ValueError('Password is too long in UTF-8.')
    return raw


def derive(password, salt):
    return hashlib.scrypt(password_bytes(password), salt=salt, n=N, r=8, p=1, dklen=64, maxmem=MAX_MEMORY)


def create_account(path, username, password):
    if not isinstance(username, str) or re.fullmatch(r'[A-Za-z0-9_.-]{3,40}', username) is None:
        raise ValueError('Username needs 3 to 40 letters, digits, underscores, dots or hyphens.')
    salt = secrets.token_bytes(16)
    record = dict(version=1, username=username, salt=salt.hex(), password_hash=derive(password, salt).hex())
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids silently replacing an existing account.
    with path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream)
    try:
        path.chmod(0o600)
    except OSError:
        pass  # Windows filesystem ACLs govern access; this is not a permission guarantee.


def _credential_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Invalid credential file.')
        result[key] = value
    return result


class Auth:
    def __init__(self, path, *, clock=time.monotonic):
        path = Path(path)
        if path.stat().st_size > 4096:
            raise ValueError('Invalid credential file.')
        try:
            record = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_credential_pairs)
        except (ValueError, RecursionError) as error:
            raise ValueError('Invalid credential file.') from error
        if (type(record) is not dict or set(record) != {'version','username','salt','password_hash'}
                or type(record['version']) is not int or record['version'] != 1
                or not isinstance(record['username'], str)
                or re.fullmatch(r'[A-Za-z0-9_.-]{3,40}', record['username']) is None
                or not isinstance(record['salt'], str) or re.fullmatch(r'[0-9a-f]{32}',record['salt']) is None
                or not isinstance(record['password_hash'], str) or re.fullmatch(r'[0-9a-f]{128}',record['password_hash']) is None):
            raise ValueError('Invalid credential file.')
        self.username = record['username']
        self.salt = bytes.fromhex(record['salt'])
        self.password_hash = bytes.fromhex(record['password_hash'])
        self.clock = clock
        self.lock = Lock()
        self.verifier = Lock()
        self.failures = deque()
        self.attempts = deque()
        self.sessions = {}

    def _prune(self, now):
        for key, session in list(self.sessions.items()):
            if now-session['last'] >= IDLE_SECONDS or now-session['created'] >= ABSOLUTE_SECONDS:
                del self.sessions[key]

    def login(self, username, password, previous=None):
        now = self.clock()
        with self.lock:
            for queue in (self.failures, self.attempts):
                while queue and now-queue[0] >= 60:
                    queue.popleft()
            if len(self.failures) >= 5 or len(self.attempts) >= 10:
                return 429, None
            if not self.verifier.acquire(blocking=False):
                return 429, None
            self.attempts.append(now)
        try:
            try:
                candidate = derive(password, self.salt)
                matches = secrets.compare_digest(candidate, self.password_hash)
                matches = secrets.compare_digest(username.encode('utf-8'), self.username.encode('utf-8')) and matches
            except (ValueError, UnicodeError, AttributeError):
                matches = False
            with self.lock:
                if not matches:
                    self.failures.append(self.clock())
                    return 401, None
                self._prune(self.clock())
                if previous:
                    self.sessions.pop(previous, None)
                if len(self.sessions) >= 10:
                    return 429, None
                key = secrets.token_hex(32)
                self.sessions[key] = dict(username=self.username, csrf=secrets.token_hex(32),
                                          created=self.clock(), last=self.clock())
                return 200, key
        finally:
            self.verifier.release()

    def get(self, key):
        with self.lock:
            now = self.clock()
            self._prune(now)
            session = self.sessions.get(key)
            if session:
                session['last'] = now
                return dict(session)
            return None

    def logout(self, key):
        with self.lock:
            self.sessions.pop(key, None)
