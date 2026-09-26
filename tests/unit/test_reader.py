from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest

from sentinellab.ingestion.reader import (
    InputFileError, MAX_FILE_BYTES, MAX_LINE_BYTES, MAX_LINES,
    ValidationError, read_events, validate_event,
)


def sample(**changes):
    record = {
        "event_id": "example-1", "source": "test-lab",
        "timestamp": "2026-09-26T10:00:00Z", "source_ip": "192.0.2.10",
        "username": "Demo_User", "event_type": "login", "outcome": "failure",
    }
    record.update(changes)
    return record


class ReaderTests(unittest.TestCase):
    def read_bytes(self, content):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            path.write_bytes(content)
            return read_events(path)

    def read_lines(self, *lines):
        return self.read_bytes("\n".join(lines).encode("utf-8"))

    def test_valid_record_preserves_identity(self):
        event = validate_event(sample())
        self.assertEqual(event.username, "Demo_User")
        self.assertEqual(event.timestamp.utcoffset(), timedelta(0))

    def test_equivalent_timezones_normalize_to_same_instant(self):
        utc = validate_event(sample())
        offset = validate_event(sample(timestamp="2026-09-26T15:00:00+05:00"))
        self.assertEqual(utc, offset)

    def test_ipv6_normalizes_without_changing_address(self):
        event = validate_event(sample(source_ip="2001:0db8:0000:0000:0000:0000:0000:0001"))
        self.assertEqual(event.source_ip, "2001:db8::1")

    def test_microseconds_are_preserved(self):
        event = validate_event(sample(timestamp="2026-09-26T10:00:00.123456Z"))
        self.assertEqual(event.timestamp.microsecond, 123456)

    def test_invalid_timestamps_are_rejected(self):
        for stamp in ["2026-09-26T10:00:00", "2026-02-30T10:00:00Z",
                      "2026-09-26", "2026-09-26T10:00:00.1234567Z",
                      "2026-09-26T10:00:00+25:00", "2026-09-26T10:00:00+05:60",
                      "0001-01-01T00:00:00+01:00"]:
            with self.subTest(timestamp=stamp), self.assertRaises(ValidationError):
                validate_event(sample(timestamp=stamp))

    def test_missing_fields_have_safe_explanation(self):
        value = sample()
        del value["username"]
        with self.assertRaisesRegex(ValidationError, "missing required fields: username"):
            validate_event(value)

    def test_unknown_field_is_rejected_without_echoing_secret(self):
        with self.assertRaisesRegex(ValidationError, "unknown fields") as result:
            validate_event(sample(password="do-not-echo-me"))
        self.assertNotIn("do-not-echo-me", str(result.exception))

    def test_non_string_values_are_rejected(self):
        for name in sample():
            with self.subTest(field=name), self.assertRaises(ValidationError):
                validate_event(sample(**{name: 123}))

    def test_empty_and_oversized_identity_fields(self):
        for name, limit in [("event_id", 128), ("source", 64), ("username", 128)]:
            validate_event(sample(**{name: "x" * limit}))
            for value in ["", "   ", "x" * (limit + 1)]:
                with self.subTest(field=name, length=len(value)), self.assertRaises(ValidationError):
                    validate_event(sample(**{name: value}))

    def test_control_characters_and_unpaired_surrogates_rejected(self):
        for value in ["bad\nname", "bad\x00name", "bad\ud800name"]:
            with self.subTest(value=repr(value)), self.assertRaises(ValidationError):
                validate_event(sample(username=value))

    def test_invalid_outcomes_and_event_types(self):
        for change in [{"outcome": "banana"}, {"event_type": "logout"}]:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                validate_event(sample(**change))

    def test_invalid_ips(self):
        for address in ["999.1.1.1", "example.com", "fe80::1%3", ""]:
            with self.subTest(address=address), self.assertRaises(ValidationError):
                validate_event(sample(source_ip=address))

    def test_mixed_input_continues_after_errors_and_keeps_line_numbers(self):
        result = self.read_lines(json.dumps(sample()), "broken json", "",
                                 json.dumps(sample(outcome="banana")),
                                 json.dumps(sample(event_id="example-2", outcome="success")))
        self.assertEqual([item.line_number for item in result.accepted], [1, 5])
        self.assertEqual([item.line_number for item in result.rejected], [2, 4])
        self.assertEqual(result.blank_lines, 1)

    def test_original_text_is_preserved_but_hidden_in_repr(self):
        text = json.dumps(sample(timestamp="2026-09-26T15:00:00+05:00"), indent=None)
        result = self.read_lines(text)
        self.assertEqual(result.accepted[0].original_record, text)
        self.assertNotIn("original_record=", repr(result.accepted[0]))

    def test_duplicate_json_keys_rejected(self):
        text = json.dumps(sample())[:-1] + ', "outcome": "success"}'
        result = self.read_lines(text)
        self.assertEqual(len(result.accepted), 0)
        self.assertIn("duplicate JSON", result.rejected[0].reason)

    def test_non_objects_and_nonstandard_constants_rejected(self):
        for text in ["[]", "null", '"text"', "123", "NaN", "Infinity"]:
            with self.subTest(text=text):
                self.assertEqual(len(self.read_lines(text).rejected), 1)

    def test_invalid_utf8_does_not_hide_later_record(self):
        result = self.read_bytes(b"\xff\n" + json.dumps(sample()).encode())
        self.assertEqual(result.rejected[0].line_number, 1)
        self.assertEqual(result.accepted[0].line_number, 2)

    def test_empty_file_and_trailing_newlines(self):
        self.assertEqual(self.read_bytes(b"").summary(),
                         {"accepted": 0, "rejected": 0, "blank_lines": 0, "errors": []})
        result = self.read_bytes(json.dumps(sample()).encode() + b"\r\n\r\n")
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.blank_lines, 1)

    def test_oversized_line_rejected_without_crash(self):
        result = self.read_bytes(b"x" * (MAX_LINE_BYTES + 1) + b"\n" + json.dumps(sample()).encode())
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(len(result.accepted), 1)

    def test_oversized_file_is_fatal(self):
        with self.assertRaises(InputFileError):
            self.read_bytes(b"x" * (MAX_FILE_BYTES + 1))

    def test_line_count_limit(self):
        self.assertEqual(self.read_bytes(b"\n" * MAX_LINES).blank_lines, MAX_LINES)
        with self.assertRaises(InputFileError):
            self.read_bytes(b"\n" * (MAX_LINES + 1))

    def test_deep_json_is_rejected_without_traceback(self):
        result = self.read_lines("[" * 1500 + "0" + "]" * 1500)
        self.assertEqual(len(result.rejected), 1)

    def test_missing_file_and_directory_are_fatal(self):
        with tempfile.TemporaryDirectory() as folder:
            for path in [Path(folder), Path(folder) / "absent.jsonl"]:
                with self.subTest(path=path), self.assertRaises(InputFileError):
                    read_events(path)

    def test_deduplication_is_not_silently_claimed(self):
        text = json.dumps(sample())
        result = self.read_lines(text, text)
        self.assertEqual(len(result.accepted), 2)  # Storage stage will handle event identity.
