"""Bounded JSON Lines reader. No database writes or attack detection happen here."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from ipaddress import ip_address
import json
from pathlib import Path
import re

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_LINE_BYTES = 16 * 1024
MAX_LINES = 10_000
FIELDS = frozenset({
    "event_id", "source", "timestamp", "source_ip", "username", "event_type", "outcome"
})
TEXT_LIMITS = {"event_id": 128, "source": 64, "username": 128}
TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)"
)


class ValidationError(ValueError):
    """A safe explanation of a rejected record, without echoing its contents."""


class InputFileError(ValueError):
    """A file cannot be processed within the documented limits."""


@dataclass(frozen=True)
class Event:
    event_id: str
    source: str
    timestamp: datetime
    source_ip: str
    username: str
    event_type: str
    outcome: str


@dataclass(frozen=True)
class AcceptedRecord:
    line_number: int
    event: Event
    original_record: str = field(repr=False)


@dataclass(frozen=True)
class RejectedRecord:
    line_number: int
    reason: str


@dataclass
class ImportResult:
    accepted: list[AcceptedRecord] = field(default_factory=list)
    rejected: list[RejectedRecord] = field(default_factory=list)
    blank_lines: int = 0

    def summary(self) -> dict:
        return {
            "accepted": len(self.accepted),
            "rejected": len(self.rejected),
            "blank_lines": self.blank_lines,
            "errors": [
                {"line": item.line_number, "reason": item.reason}
                for item in self.rejected
            ],
        }


def _unique_object(pairs: list[tuple]) -> dict:
    """Reject duplicate JSON keys instead of silently keeping the last value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON field names are not allowed")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError("non-standard JSON numbers are not allowed")


def validate_event(value: object) -> Event:
    """Validate one decoded record and normalize time/IP without changing identity."""
    if not isinstance(value, dict):
        raise ValidationError("each record must be a JSON object")
    missing = FIELDS - value.keys()
    if missing:
        raise ValidationError("missing required fields: " + ", ".join(sorted(missing)))
    if value.keys() - FIELDS:
        raise ValidationError("unknown fields are not allowed")
    for name in sorted(FIELDS):
        if not isinstance(value[name], str):
            raise ValidationError(f"{name} must be a string")
        # Control characters and unpaired Unicode surrogates are unsuitable for logs.
        if any(ord(char) < 32 or ord(char) == 127 or 0xD800 <= ord(char) <= 0xDFFF
               for char in value[name]):
            raise ValidationError(f"{name} contains unsupported characters")
    for name, limit in TEXT_LIMITS.items():
        if not value[name].strip() or len(value[name]) > limit:
            raise ValidationError(f"{name} must contain 1 to {limit} characters and not be blank")
    if value["event_type"] != "login":
        raise ValidationError("event_type must be login")
    if value["outcome"] not in {"success", "failure"}:
        raise ValidationError("outcome must be success or failure")

    stamp = value["timestamp"]
    if not TIMESTAMP_PATTERN.fullmatch(stamp):
        raise ValidationError("timestamp must include date, time, seconds, and Z or an explicit offset")
    try:
        timestamp = datetime.fromisoformat(stamp).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValidationError("timestamp contains an invalid or unsupported date/time") from None
    address = value["source_ip"]
    if len(address) > 45 or "%" in address:
        raise ValidationError("source_ip must be an IPv4 or IPv6 address without a zone ID")
    try:
        normalized_ip = str(ip_address(address))
    except ValueError:
        raise ValidationError("source_ip must be a valid IPv4 or IPv6 address") from None
    return Event(
        event_id=value["event_id"], source=value["source"], timestamp=timestamp,
        source_ip=normalized_ip, username=value["username"],
        event_type=value["event_type"], outcome=value["outcome"],
    )


def read_events(path: Path | str) -> ImportResult:
    """Read a bounded file and return accepted records plus line-specific errors.

    Acceptance means format validity only. Persistence and cross-import duplicate
    detection are deliberately left to the future storage layer.
    """
    path = Path(path)
    try:
        if not path.is_file():
            raise InputFileError("choose an existing regular file")
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
    except OSError:
        raise InputFileError("could not read the input file; check its location and permissions") from None
    if len(data) > MAX_FILE_BYTES:
        raise InputFileError("file exceeds the 2 MiB limit")
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()  # A final newline ends the last line; it is not an extra blank.
    if len(lines) > MAX_LINES:
        raise InputFileError("file exceeds the 10,000-line limit")

    result = ImportResult()
    for number, raw in enumerate(lines, start=1):
        try:
            if len(raw) > MAX_LINE_BYTES:
                raise ValidationError("record exceeds the 16 KiB line limit")
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                raise ValidationError("record is not valid UTF-8") from None
            if not text.strip():
                result.blank_lines += 1
                continue
            try:
                value = json.loads(
                    text, object_pairs_hook=_unique_object, parse_constant=_reject_constant
                )
            except (json.JSONDecodeError, RecursionError, ValueError) as error:
                if isinstance(error, ValidationError):
                    raise
                raise ValidationError("record is not valid JSON") from None
            event = validate_event(value)
            result.accepted.append(AcceptedRecord(number, event, text))
        except ValidationError as error:
            result.rejected.append(RejectedRecord(number, str(error)))
    return result
