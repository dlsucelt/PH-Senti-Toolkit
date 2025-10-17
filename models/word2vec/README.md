# Philippine Twitter Word2Vec Models (v2, 200D)

These pretrained Word2Vec embeddings were developed for the paper:

> Co, S. T. S., Custodio, N. R. E., Dela Cruz, A. L. L., Sanchez, M. C. B., Jabanes, J. C., & Tighe, E. P. (2025). *Exploring Emoji-based Synthetic Annotations for Filipino-English Sentiment Analysis.* Proceedings of the Workshop on Computation: Theory and Practice (WCTP 2025).

## Available models

| Model | Window Size | Vector Dim | Description |
|--------|--------------|-------------|--------------|
| `w2v_tweets_w1_d200_v2` | 1 | 200 | narrow context (window = 1) |
| `w2v_tweets_w2_d200_v2` | 2 | 200 | balanced context (recommended) |
| `w2v_tweets_w3_d200_v2` | 3 | 200 | wider context |

Each model consists of two files:

* .w2v_tweets_wX_d200_v2.wordvectors
* .w2v_tweets_wX_d200_v2.wordvectors.vectors.npy

where X is the window size.

## Download

You can obtain the models from Zenodo:

🔗 [https://doi.org/10.5281/zenodo.17369886](https://doi.org/10.5281/zenodo.17369886)

Or via command line:
```
bash
wget https://zenodo.org/record/17369886/files/w2v_tweets_w2_d200_v2.zip
unzip w2v_tweets_w2_d200_v2.zip
```

## Loading example

```
from gensim.models import KeyedVectors

model = KeyedVectors.load("w2v_tweets_w2_d200_v2.wordvectors")
```
