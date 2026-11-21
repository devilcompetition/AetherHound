import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mock_malware"))

from morse import pattern_duration, text_to_morse, text_to_pattern


def test_sos_morse():
    assert text_to_morse("SOS") == "... --- ..."


def test_word_separator():
    assert text_to_morse("E T") == ". / -"


def test_pattern_sos():
    p = text_to_pattern("S")
    assert p == [(True, 1), (False, 1), (True, 1), (False, 1), (True, 1)]


def test_duration():
    # E = one dot = 1 unit
    assert pattern_duration(text_to_pattern("E"), 2.0) == 2.0
