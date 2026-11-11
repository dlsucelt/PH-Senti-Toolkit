# Philippine Twitter Word2Vec Models (v2, 200D)

These pretrained Word2Vec embeddings were developed for the paper:

> Co, S. T. S., Custodio, N. R. E., Dela Cruz, A. L. L., Sanchez, M. C. B., Jabanes, J. C., & Tighe, E. P. (2025). *Exploring Emoji-based Synthetic Annotations for Filipino-English Sentiment Analysis.* Proceedings of the Workshop on Computation: Theory and Practice (WCTP 2025). [in-press]

If you plan to use any of our models, please cite our paper. Please also remember that our models are not ready for deployment or for end-user purposes. We released these models for the academic community to further research in Philippine language processing.

## Available models

| Model | Window Size | Vector Dim | Description |
|--------|--------------|-------------|--------------|
| `w2v_tweets_w1_d200_v2` | 1 | 200 | narrow context (window = 1) |
| `w2v_tweets_w2_d200_v2` | 2 | 200 | balanced context (recommended) |
| `w2v_tweets_w3_d200_v2` | 3 | 200 | wider context |

Each model consists of two files:

* `w2v_tweets_wX_d200_v2.wordvectors`
* `w2v_tweets_wX_d200_v2.wordvectors.vectors.npy`

where X is the window size. Keep both files in the same folder.

All three models share one vocabulary of 274,781 tokens (minimum count 5) and were trained with Gensim skip-gram on the same 8,922,888 tokenized tweets (negative sampling 5, NS exponent 0.75, 5 epochs). Window size 2 performed best in the paper's ablation study.

## Tokenize your text the same way

The vocabulary was built with the tokenizer in this repository. To look up words in these models, tokenize with it unchanged:

```python
from ph_senti_toolkit import Tokenizer
tokens = Tokenizer().tokenize("Grabeeee ang init!!! 😂")
# ['grabeee', 'ang', 'init', '!', '!', '!', '😂']
```

Placeholder tokens in the vocabulary: `<USERHANDLE>`, `<URL>`, `<TIME>`, `<PHONENUMBER>`, `<NUMBER>`. Emoji appear one Unicode code point per token (including skin-tone modifiers, `\u200d` and `\ufe0f`). See [`docs/TOKENIZER_SPEC.md`](../../docs/TOKENIZER_SPEC.md).

## Download

You can obtain the models from Zenodo:

🔗 [https://doi.org/10.5281/zenodo.17369886](https://doi.org/10.5281/zenodo.17369886)

Or via command line:
```bash
wget -O w2v_tweets_w2_d200_v2.zip "https://zenodo.org/records/17369886/files/w2v_tweets_w2_d200_v2.zip?download=1"
unzip w2v_tweets_w2_d200_v2.zip -x "__MACOSX/*"
```

Each zip unpacks into a folder named after the model.

## Loading example (Python)

After unzipping, load a model with Gensim (`pip install "gensim>=4.1"`):

```python
from gensim.models import KeyedVectors

model = KeyedVectors.load("w2v_tweets_w2_d200_v2/w2v_tweets_w2_d200_v2.wordvectors")
model.most_similar("init", topn=5)
```

For more on what you can do with the models via Gensim, please see the official API: [https://radimrehurek.com/gensim/models/keyedvectors.html](https://radimrehurek.com/gensim/models/keyedvectors.html)