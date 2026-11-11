# PH-Senti-Toolkit Tokenizer: Specification

Version 0.1.0 · source: [`src/ph_senti_toolkit/tokenizer.py`](../src/ph_senti_toolkit/tokenizer.py) · original file: tag [`paper-original`](https://github.com/dlsucelt/PH-Senti-Toolkit/tree/paper-original)

This document describes, rule by rule, what the tokenizer from Co et al. (2025) does. The tokenizer was written by the paper's student authors and is released **unchanged**, because it is the tokenizer that produced the corpus for the released Word2Vec models (`w2v_tweets_w{1,2,3}_d200_v2`, [Zenodo](https://doi.org/10.5281/zenodo.17369886)). Everything here describes the code's actual behaviour, including behaviour we consider flawed (marked **Known issue**). If you want your tokens to line up with the models, do not "fix" any of it.

## 1. Interface

```python
from ph_senti_toolkit import Tokenizer
Tokenizer().tokenize("Grabeeee!!! @kaibigan 3:00 PM 😂")
# ['grabeee', '!', '!', '!', '<USERHANDLE>', '<TIME>', '😂']
```

`tokenize(text: str) -> list[str]`. The input must be a `str` (passing `None`/`NaN` raises `TypeError`). The tokenizer has no state and no dependencies beyond Python's `re` module. An empty or whitespace-only string returns `[]`.

## 2. Processing order

The steps run in this fixed order, each on the output of the previous one. **The order matters**: a later step sees placeholders inserted by an earlier one.

| # | Step | Pattern |
|---|------|---------|
| 1 | User handles → `<USERHANDLE>` | `@\w+` |
| 2 | URLs → `<URL>` | `http\S+` \| `www\.\S+` \| `t.co//w+` |
| 3 | Times → `<TIME>` | `\b\d{1,2}:\d{2}\s?(?:am\|pm\|AM\|PM)?\b` |
| 4 | Phone numbers → `<PHONENUMBER>` | `\b(?:\+?\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b` |
| 5 | Remaining numbers → `<NUMBER>` | `\b\d+\b` |
| 6 | Letter repetition cut to 3 | `([a-zA-Z])\1{2,}` → `\1\1\1` |
| 7 | Split into tokens | `re.findall` with the token pattern (§5) |
| 8 | Casing | lowercase each token unless `token.isupper()` (§4) |

Python's `re` is used with default flags, so `\w`, `\d`, `\s` and `\b` are Unicode-aware (e.g. `\w` matches `ñ`, `é` and `_`).

## 3. Placeholders

| Placeholder | Produced by | Examples |
|-------------|-------------|----------|
| `<USERHANDLE>` | `@` followed by one or more word characters | `@juan_dc` → `<USERHANDLE>` |
| `<URL>` | anything starting with `http` or `www.` up to the next whitespace | `https://t.co/abc`, `www.example.com` |
| `<TIME>` | 1–2 digits, colon, exactly 2 digits, optional space + `am`/`pm`/`AM`/`PM` | `10:30pm`, `3:00 PM`, `10:30` |
| `<PHONENUMBER>` | any run of **3 or more digits**, optionally split by single spaces, dots, hyphens or brackets | `0917-123-4567`, `2024`, `123`, `1 2 3` |
| `<NUMBER>` | a standalone run of digits not already replaced, in practice **1 or 2 digits** | `7`, `42` |

Details:

- **Handles.** Rule 1 also fires inside e-mail addresses: `a@b.com` → `a`, `<USERHANDLE>`, `.`, `com`. A handle inside a URL is replaced first, but rule 2 then still swallows the whole URL.
- **URLs.** **Known issue:** the third alternative `t.co//w+` is a typo (for `t\.co/\w+`) and in practice never matches. `t.co` links are caught by `http\S+`. A bare domain without `http`/`www.` (e.g. `example.com`) is not a URL and splits into `example`, `.`, `com`. Trailing punctuation attached to a URL is absorbed into it.
- **Times.** **Known issue:** any `d:dd`/`dd:dd` counts, so scores or verse references such as `3:16` become `<TIME>`. `2:1` does not match (it needs two digits after the colon) and becomes `<NUMBER>`, `:`, `<NUMBER>`. `3pm` without a colon is not a time and is kept as `3pm`.
- **Phone numbers.** **Known issue:** the pattern is far broader than phone numbers. Every number with 3+ digits (years, prices, counts) becomes `<PHONENUMBER>`. The paper's example "1234 → `<NUMBER>`" therefore does **not** reflect the code: the code gives `<PHONENUMBER>`. The released models follow the code.
- **Numbers.** Digits attached to letters have no word boundary and are left alone: `1st`, `2nd`, `3pm`, `covid19` stay as they are.
- Placeholders are upper case, so the casing rule (§4) leaves them unchanged.

## 4. Casing rule

After splitting, each token is lowercased **unless** `str.isupper()` is `True` for it, meaning it has at least one cased letter and all cased letters are upper case.

- `Hello` → `hello`; `WORLD` → `WORLD`; `Lol` → `lol`; `LOL` → `LOL`.
- **Known issue:** `I`, all-caps words (`LOL`, `HAHAHA`, `OMG`), all-caps hashtags (`#OMG`) and emoticons such as `:D`/`:P` keep their case. The models hold separate vectors for e.g. `LOL` and `lol`.
- Tokens with no cased letters (digits, emoji, punctuation) pass through unchanged.

## 5. Splitting

Tokens are extracted with `re.findall` and this alternation. **The first alternative that matches at a position wins**:

1. the placeholders `<USERHANDLE>`, `<URL>`, `<TIME>`, `<PHONENUMBER>`, `<NUMBER>`
2. hashtags: `#\w+` (e.g. `#Bagong_Taon` → `#bagong_taon`; the `#` is kept)
3. emoticons (§5.1)
4. words with a straight apostrophe: `\w+'\w+` (`di'ba`, `can't`)
5. words with hyphens/underscores: `\w+[-\w]+` (`self-care`, `x_y`, at least 2 characters)
6. plain words: `\b\w+\b`
7. **any other single non-space character**: `[^\w\s]`

Whitespace is never part of a token, so `" ".join(tokens).split(" ")` round-trips. This matters because the training pipeline stored tokens that way (§8).

- **Punctuation** is one token per character: `!!!!!` → five `!` tokens, `...` → three `.` tokens. Repeated punctuation is **not** shortened (rule 6 covers ASCII letters only).
- **Known issue:** a curly apostrophe `’` is not `'`, so `it’s` → `it`, `’`, `s`.

### 5.1 Emoticons

The fixed, **case-sensitive** list. These are the strings the pattern can match, in pattern order:

```
:)  :(  :D  :P  ;P  :*  <3  </3  :'(  :'  :|  :o :-o  :-(  :-)  ;) ;-)  >< >-<  :O  :[
```

- **Known issue:** `<3` and `</3` can never be produced. Rule 5 runs first and turns the `3` into `<NUMBER>`, so `<3` → `<`, `<NUMBER>` and `</3` → `<`, `/`, `<NUMBER>`.
- **Known issue:** emoticons not in the list, or in another case (e.g. `:p`, `XD`, `:-D`), are split by the general rules: `:p` → `:`, `p`; `XD` stays `XD` as a word.

### 5.2 Emoji

There is **no emoji-specific rule**. Emoji fall through to alternative 7 and become **one token per Unicode code point**:

| Input | Tokens |
|-------|--------|
| 😂 | `😂` |
| 👍🏽 (thumbs up + skin tone) | `👍`, `🏽` |
| ❤️ (heart + variation selector U+FE0F) | `❤`, `️` |
| 👨‍👩‍👧 (ZWJ family sequence) | `👨`, `‍`, `👩`, `‍`, `👧` |

So **ZWJ sequences** are broken into their component emoji plus zero-width-joiner tokens (`‍`). **Skin-tone modifiers** (U+1F3FB–U+1F3FF) and the **variation selector** U+FE0F are separate tokens. All of these exist in the model vocabularies (e.g. `‍`, `🏻` and `️` are frequent tokens). Flag emoji (pairs of regional-indicator letters) likewise split into two tokens. **Known issue:** this loses the meaning of composed emoji. A future tokenizer should treat grapheme clusters as single tokens.

## 6. Repetition rule

Any ASCII letter (`a–z`, `A–Z`) repeated 3 or more times in a row is cut to exactly 3: `grabeeeee` → `grabeee`, `Hiiiii` → `hiii`, `HAHAAAAA` → `HAHAAA`. The rule runs **before** splitting and casing. **Known issue:** non-ASCII letters (`ñññññ`), digits, punctuation and emoji are not shortened.

## 7. What the tokenizer does *not* do

- No filtering. Tokenizing never drops a text. See §8 for the corpus-level filtering done in the original pipeline.
- No Unicode normalisation (NFC/NFKC), no stripping of accents.
- No stop-word removal, stemming or language identification.
- Emoji are **kept** (§5.2). The paper's "without emojis" experiments removed emojis in separate steps, not in this tokenizer.

## 8. How the training corpus was built (for reference)

This is **not** part of the tokenizer. It is recorded here so you know what the model vocabulary reflects. Sources: the project notebooks `1. Separate Data`, `2. Tag Sentiment`, `3. Preprocess Data`, `4a. Data Splitting`, `5a. Word2Vec Training`.

1. Rows with an empty `text` were dropped, and exact duplicate texts were removed within each raw file.
2. Tweets were split into those with and without a recognised Emoji Sentiment Ranking emoji. Tweets with emoji were labelled; tweets with a mean emoji score of exactly 0 were set aside.
3. Every tweet was tokenized with this tokenizer, and tokens were stored joined by single spaces.
4. Tweets left with no letter or digit after tokenization were removed. Every such tweet in the stored files had none. The code for this step was not found in the notebooks, but its effect is visible and consistent.
5. For the emoji-labelled set only, duplicate tokenized texts were removed before the train/validation/test split (`4a`). Duplicates were **not** removed from the no-emoji set.
6. Word2Vec was trained on the tokenized no-emoji tweets + zero-score tweets + the full (pre-undersampling) training split, reading each stored text with `pandas` and `text.split(" ")`. Gensim skip-gram, 200 dimensions, `min_count=5`, `negative=5`, `ns_exponent=0.75`, 5 epochs, `seed=42`, windows 1, 2, 3.

## 9. Validation of this release

Checked against the project's original data files (not distributed) before release:

| Check | Result |
|-------|--------|
| Re-tokenizing the stored raw no-emoji tweets reproduces the stored tokenized files | **7,292,731 / 7,292,731 identical**, plus 2 tweets whose whole text is `nan` or `null`, which `pandas` reads back as missing values (a CSV artifact, not a tokenizer difference) |
| Same for the zero-score tweets still present in raw form | **905 / 905 identical** |
| Corpus totals (paper: 8,922,888 tweets / 99,016,632 tokens / 1,583,053 types) | 8,922,888 / 99,016,629 / 1,583,055 |
| Vocabulary of `w2v_tweets_w1/w2/w3_d200_v2` vs. tokens with count ≥ 5 in the rebuilt corpus | **identical: 274,781 types, every frequency count equal**, for all three models |
| Files on Drive vs. files on Zenodo | identical CRC32 for all three `.wordvectors` files and the w2 `.vectors.npy` |

The tiny gaps against the paper's totals (3 tokens, 2 types) involve only words below the `min_count=5` cut-off, so they cannot affect the models. We believe they come from the two `nan`/`null` tweets above being counted differently in the original run. The paper's sub-counts (7,292,733 no-emoji and 21,090 zero-score tweets) sum to the same 8,922,888 total but split it 2 tweets differently from what we measure (7,292,731 and 21,092).

## 10. Known issues: summary

All of these are kept for compatibility with the released models and are marked `KNOWN ISSUE` in the source:

1. `t.co//w+` URL alternative is a typo and never matches (harmless).
2. Any `d:dd`/`dd:dd` becomes `<TIME>`.
3. Every number with 3+ digits becomes `<PHONENUMBER>`, not `<NUMBER>` (differs from the paper's example).
4. Handles are replaced inside e-mail addresses.
5. Repetition rule covers ASCII letters only.
6. Emoticon list is short and case-sensitive. `<3` / `</3` are never produced.
7. Emoji are split per code point (ZWJ, skin tones, U+FE0F become separate tokens).
8. Curly apostrophes split words.
9. All-caps tokens (including `I`) keep their case.

A corrected tokenizer would need new embeddings. It is left for a future release.
