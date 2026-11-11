"""Tests for the PH-Senti-Toolkit tokenizer.

All example strings are invented; no real tweets are used.

The expected outputs document the tokenizer *as it was used to train the
released Word2Vec models*, including its known issues. If one of these
tests fails, the tokenizer no longer matches the models.
"""

import hashlib
import io
import pathlib
import tokenize as pytokenize

import pytest

from ph_senti_toolkit import Tokenizer, __version__

TOK = Tokenizer()

# Fingerprint of the code in the `paper-original` tag, ignoring comments and
# whitespace. Any change to the tokenizer's logic changes this value.
ORIGINAL_CODE_FINGERPRINT = "fed75d8ca1650598671e28256aab8c72354faf5622094892fb4f071cf0865dbc"


def _code_fingerprint(source: str) -> str:
    skip = {
        pytokenize.COMMENT, pytokenize.NL, pytokenize.NEWLINE, pytokenize.INDENT,
        pytokenize.DEDENT, pytokenize.ENDMARKER, pytokenize.ENCODING,
    }
    parts = [
        t.string
        for t in pytokenize.generate_tokens(io.StringIO(source).readline)
        if t.type not in skip
    ]
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()


def test_logic_matches_paper_original():
    import ph_senti_toolkit.tokenizer as mod

    source = pathlib.Path(mod.__file__).read_text(encoding="utf-8")
    assert _code_fingerprint(source) == ORIGINAL_CODE_FINGERPRINT


def test_version():
    assert __version__ == "0.1.0"


CASES = [
    # placeholders
    ("@juan_dc hello", ["<USERHANDLE>", "hello"]),
    ("see https://t.co/abc and www.example.com", ["see", "<URL>", "and", "<URL>"]),
    ("at 10:30pm ok", ["at", "<TIME>", "ok"]),
    ("3:00 PM", ["<TIME>"]),
    ("call 0917-123-4567", ["call", "<PHONENUMBER>"]),
    ("7 days", ["<NUMBER>", "days"]),
    ("42 pesos", ["<NUMBER>", "pesos"]),
    # known issue: 3+ digit numbers become <PHONENUMBER>
    ("year 2024 na", ["year", "<PHONENUMBER>", "na"]),
    ("1 2 3", ["<PHONENUMBER>"]),
    # numbers attached to letters are untouched
    ("3pm 1st 2nd", ["3pm", "1st", "2nd"]),
    # known issue: e-mail addresses
    ("email a@b.com", ["email", "a", "<USERHANDLE>", ".", "com"]),
    # repetition: ASCII letters only, cut to three
    ("grabeeeee!!!!!", ["grabeee", "!", "!", "!", "!", "!"]),
    ("Hiiiii", ["hiii"]),
    ("ñññññ", ["ñññññ"]),
    # casing
    ("Hello WORLD", ["hello", "WORLD"]),
    ("I am LOL Lol", ["I", "am", "LOL", "lol"]),
    # hashtags
    ("#Bagong_Taon #OMG", ["#bagong_taon", "#OMG"]),
    # emoticons (case-sensitive; <3 is broken by the number rule)
    (":) :( :D :P :-) ;)", [":)", ":(", ":D", ":P", ":-)", ";)"]),
    (":p", [":", "p"]),
    ("<3", ["<", "<NUMBER>"]),
    ("</3", ["<", "/", "<NUMBER>"]),
    # apostrophes and hyphens
    ("di'ba self-care", ["di'ba", "self-care"]),
    ("it’s", ["it", "’", "s"]),
    # punctuation
    ("...", [".", ".", "."]),
    # emoji: split per code point
    ("\U0001F468‍\U0001F469‍\U0001F467",
     ["\U0001F468", "‍", "\U0001F469", "‍", "\U0001F467"]),
    ("\U0001F44D\U0001F3FD", ["\U0001F44D", "\U0001F3FD"]),
    ("❤️", ["❤", "️"]),
    # edge cases
    ("", []),
    ("   ", []),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_cases(text, expected):
    assert TOK.tokenize(text) == expected


def test_tokens_contain_no_spaces():
    # Training joined tokens with " " and split on " ", which is only
    # lossless if no token contains a space.
    text = "Grabe!! @user 10:30 pm sa www.x.com \U0001F602 #Laban 0917 123 4567"
    assert all(" " not in t for t in TOK.tokenize(text))
