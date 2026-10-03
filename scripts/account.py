"""Provision one local account without putting passwords in command arguments."""
import argparse
import getpass
from pathlib import Path
import sys
import warnings
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from sentinellab.web.auth import create_account


def main():
    parser = argparse.ArgumentParser(description='Create a local SentinelLab account with hidden password entry.')
    parser.add_argument('--file', type=Path, default=Path('secrets/analyst.json'))
    parser.add_argument('--username', required=True)
    args = parser.parse_args()
    try:
        # Do not fall back to echoing a password in redirected/noninteractive input.
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            password = getpass.getpass('New password (15 to 128 characters): ')
            if password != getpass.getpass('Repeat password: '):
                raise ValueError('Passwords did not match.')
        create_account(args.file, args.username, password)
    except FileExistsError:
        print('Account file already exists; it was not changed.', file=sys.stderr)
        return 2
    except (OSError, ValueError, getpass.GetPassWarning, EOFError):
        print('Account not created. Use an interactive terminal, a valid username, matching 15-128 character passwords, and a writable new file.', file=sys.stderr)
        return 2
    print('Local account created. Keep the credential file private and outside Git.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
