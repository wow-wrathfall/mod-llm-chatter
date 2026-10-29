"""Quest questions use Guide facts and leave ordinary chat alone."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import chatter_quest_help as quest_help


class QuestHelpTests(TestCase):
    def test_matching_active_quest_and_pronoun(self):
        active = [{'ID': 1275, 'LogTitle': 'The Missing Diplomat'},
                  {'ID': 42, 'LogTitle': 'The Lost Letter'}]
        self.assertEqual(
            quest_help._matching_quest('Where do I turn in The Missing Diplomat?', active),
            (1275, ''),
        )
        self.assertIsNone(
            quest_help._matching_quest('Where do I turn this in?', active)[0]
        )
        self.assertEqual(
            quest_help._matching_quest('Where do I turn this in?', active[:1]),
            (1275, ''),
        )
        self.assertIsNone(quest_help._matching_quest(
            'Where do I turn in The Lost Letter?', active[:1]
        )[0])

    def test_quest_link_has_priority(self):
        self.assertEqual(
            quest_help._matching_quest('|Hquest:1275:10|h[The Missing Diplomat]|h', []),
            (1275, ''),
        )

    def test_guide_lookup_supplies_grounding(self):
        executor = SimpleNamespace(active_quest_ids=[], execute_tool=lambda *_: 'Turn in to: Jaina')
        active = [{'ID': 1275, 'LogTitle': 'The Missing Diplomat'}]
        with patch.object(quest_help, '_active_quests', return_value=active), patch.object(
            quest_help, '_guide_executor', return_value=executor
        ):
            result = quest_help.quest_help_context(
                object(), {}, 7, 'Where do I turn this in?'
            )
        self.assertIn('Turn in to: Jaina', result)
        self.assertEqual(executor.active_quest_ids, [1275])

    def test_no_lookup_for_ordinary_chat(self):
        with patch.object(quest_help, '_active_quests') as lookup:
            self.assertEqual(quest_help.quest_help_context(
                object(), {}, 7, 'How are you?'
            ), '')
            lookup.assert_not_called()

    def test_ambiguous_question_does_not_call_guide(self):
        active = [{'ID': 1, 'LogTitle': 'One'}, {'ID': 2, 'LogTitle': 'Two'}]
        with patch.object(quest_help, '_active_quests', return_value=active), patch.object(
            quest_help, '_guide_executor'
        ) as guide:
            result = quest_help.quest_help_context(
                object(), {}, 7, 'Where do I turn this in?'
            )
        self.assertIn('Ask the player', result)
        guide.assert_not_called()
