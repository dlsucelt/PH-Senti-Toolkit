import re

# NOTE (added for the public release):
# This is the tokenizer used to build the corpus for the Word2Vec models
# released with Co et al. (2025) (w2v_tweets_w{1,2,3}_d200_v2). Its logic is
# intentionally left exactly as it was when the models were trained. Changing
# any pattern below would produce tokens the models have never seen.
#
# Comments marked "KNOWN ISSUE" flag behaviour that should be improved in a
# future tokenizer (which would also need retrained embeddings). They are
# documentation only; no code was changed. See docs/TOKENIZER_SPEC.md.

class Tokenizer:
    def __init__(self):
        # Define patterns
        self.userhandle_pattern = r'@\w+'
        # KNOWN ISSUE: the third alternative `t.co//w+` is a typo for `t\.co/\w+`
        # (forward slashes instead of a backslash, unescaped dot). It almost
        # never matches anything; t.co links are caught by `http\S+` instead.
        self.url_pattern = r'http\S+|www\.\S+|t.co//w+'
        # KNOWN ISSUE: any `d:dd` or `dd:dd` becomes <TIME>, including scores
        # ("2:1" does not match, but "3:16" or "10:30" do) and verse numbers.
        # "3pm" (no colon) is NOT treated as a time and stays "3pm".
        self.time_pattern = r'\b\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)?\b'
        # KNOWN ISSUE: this pattern is very broad. Any run of 3 or more digits,
        # optionally separated by single spaces, dots or hyphens, becomes
        # <PHONENUMBER>, e.g. "2024" and "1 2 3". In practice only 1- and
        # 2-digit numbers reach <NUMBER>.
        self.phone_pattern = r'\b(?:\+?\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
        # Numbers attached to letters ("1st", "3pm") have no word boundary
        # between digit and letter, so they are left unchanged.
        self.number_pattern = r'\b\d+\b'
        # KNOWN ISSUE: only ASCII letters are shortened. Repeated punctuation
        # ("!!!!!"), digits, emoji and non-ASCII letters (e.g. "ñ") are kept
        # at their original length.
        self.repeating_chars_pattern = r'([a-zA-Z])\1{2,}'
        # KNOWN ISSUE: the list is small and case-sensitive (":P" is kept but
        # ":p" is split into ":" and "p"). "<3" and "</3" can never match
        # because the number substitution runs first and turns "3" into
        # <NUMBER>, giving the tokens "<", "<NUMBER>" (and "<", "/", "<NUMBER>").
        self.emoticon_pattern = r':\)|:\(|:D|:P|;P|:\*|<3|</3|:\'\(|:\'|:\||:-?o|:-?\(|:-?\)|;-?\)|>-?<|:O|:\['
        # KNOWN ISSUE: the final catch-all `[^\w\s]` emits every other symbol
        # as its own one-character token. Emoji are therefore split per Unicode
        # code point: ZWJ sequences become their parts plus "‍" tokens,
        # skin-tone modifiers (e.g. "\U0001F3FD") and the variation selector
        # "️" become separate tokens. Only the straight apostrophe is kept
        # inside words; a curly apostrophe ("it’s") splits the word.
        self.token_pattern = fr'<USERHANDLE>|<URL>|<TIME>|<PHONENUMBER>|<NUMBER>|#\w+|{self.emoticon_pattern}|\w+\'\w+|\w+[-\w]+|\b\w+\b|[^\w\s]'

    def tokenize(self, text):
        # Replace user handles with <USERHANDLE>
        # (also fires inside e-mail addresses: "a@b.com" -> "a", "<USERHANDLE>", ".", "com")
        text = re.sub(self.userhandle_pattern, '<USERHANDLE>', text)

        # Replace URLs with <URL>
        text = re.sub(self.url_pattern, '<URL>', text)

        # Replace time expressions with <TIME>
        text = re.sub(self.time_pattern, '<TIME>', text)

        # Replace phone numbers with <PHONENUMBER>
        text = re.sub(self.phone_pattern, '<PHONENUMBER>', text)

        # Replace generic numbers with <NUMBER>
        text = re.sub(self.number_pattern, '<NUMBER>', text)

        # Reduce repeating characters greater than or equal to three to three
        text = re.sub(self.repeating_chars_pattern, r'\1\1\1', text)

        # Split text into tokens
        tokens = re.findall(self.token_pattern, text)

        # Lowercase tokens except those in uppercase
        # KNOWN ISSUE: str.isupper() is True for any token whose cased letters
        # are all uppercase, so "I", "LOL", "#OMG" and ":D" keep their case
        # while "Lol" becomes "lol". The models therefore hold separate vectors
        # for "LOL" and "lol". Placeholders such as <URL> rely on this rule.
        processed_tokens = []
        for token in tokens:
            if not token.isupper():
                processed_tokens.append(token.lower())
            else:
                processed_tokens.append(token)

        return processed_tokens
