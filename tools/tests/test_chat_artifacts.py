"""Malformed model envelopes must never become bot speech."""

import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chatter_db import insert_chat_message
from chatter_shared import parse_conversation_response
from chatter_text import parse_single_response


class ChatArtifactTests(TestCase):
    def test_valid_json_extracts_only_speech(self):
        self.assertEqual(parse_single_response(
            '{"message":"Meet me at the inn.","emote":null}'
        )['message'], 'Meet me at the inn.')

    def test_null_and_unknown_json_are_not_speech(self):
        for raw in ('null', 'None', '{"message":null}',
                    '{"message":"null"}', '{"reply":"hello"}',
                    '{"message":', '[{"message":"hello"}]'):
            with self.subTest(raw=raw):
                self.assertEqual(parse_single_response(raw)['message'], '')

    def test_plain_text_still_works(self):
        self.assertEqual(parse_single_response('Meet me at the inn.')['message'],
                         'Meet me at the inn.')

    def test_conversation_drops_null_line(self):
        result = parse_conversation_response(
            '[{"speaker":"A","message":"null"},'
            '{"speaker":"B","message":"At the inn."}]', ['A', 'B'])
        self.assertEqual([entry['message'] for entry in result], ['At the inn.'])

    def test_delivery_gate_drops_raw_artifacts(self):
        db = Mock()
        for message in ('null', '{"message":"hello"}'):
            with self.subTest(message=message):
                self.assertIsNone(insert_chat_message(
                    db, 1, 'Bot', message, channel='general'))
        db.cursor.assert_not_called()
