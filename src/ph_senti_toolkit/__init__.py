"""PH-Senti-Toolkit: research resources from Co et al. (2025).

The tokenizer is the one used to build the corpus for the released
Word2Vec models (w2v_tweets_w{1,2,3}_d200_v2). Use it unchanged if you
want your tokens to line up with those models' vocabulary.
"""

from .tokenizer import Tokenizer

__version__ = "0.1.0"

__all__ = ["Tokenizer", "__version__"]
