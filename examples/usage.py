"""Minimal usage example for PH-Senti-Toolkit.

Install:
    pip install "ph-senti-toolkit[models] @ git+https://github.com/dlsucelt/PH-Senti-Toolkit"

Download a model from Zenodo (https://doi.org/10.5281/zenodo.17369886),
unzip it, and pass the path to the .wordvectors file below. Both files
(.wordvectors and .wordvectors.vectors.npy) must sit in the same folder.
"""

import sys

from ph_senti_toolkit import Tokenizer

tokenizer = Tokenizer()

text = "Grabeeee ang init ngayon!!! @kaibigan tara sa mall 3:00 PM \U0001F602"
tokens = tokenizer.tokenize(text)
print(tokens)
# ['grabeee', 'ang', 'init', 'ngayon', '!', '!', '!', '<USERHANDLE>',
#  'tara', 'sa', 'mall', '<TIME>', '\U0001F602']

if len(sys.argv) > 1:
    from gensim.models import KeyedVectors

    kv = KeyedVectors.load(sys.argv[1])  # e.g. w2v_tweets_w2_d200_v2.wordvectors

    in_vocab = [t for t in tokens if t in kv.key_to_index]
    missing = [t for t in tokens if t not in kv.key_to_index]
    print(f"{len(in_vocab)}/{len(tokens)} tokens in vocabulary; missing: {missing}")

    # Average the vectors of known tokens to get a simple document vector.
    if in_vocab:
        doc_vector = kv.get_mean_vector(in_vocab)
        print("document vector shape:", doc_vector.shape)

    print(kv.most_similar("init", topn=5))
