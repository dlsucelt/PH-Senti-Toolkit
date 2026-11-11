# PH Senti Toolkit
**A research-oriented toolkit for sentiment analysis in Philippine languages**  
Developed by researchers at the [Center for Language Technologies (CeLT)](https://github.com/CeLT-DLSU), De La Salle University, Manila, Philippines.

---

### ⚠️ Research release
This toolkit is published for **transparency and reproducibility** of Co et al. (2025). The tokenizer and Word2Vec models are **not production-ready** and likely carry **biases and limitations**. We release them for researchers working to advance Philippine-language sentiment analysis, and we welcome work that improves them toward real-world use.

---

### 🧠 Overview
The **PH Senti Toolkit** serves as a **research resource** accompanying our work  
> *Exploring Emoji-based Synthetic Annotations for Filipino-English Sentiment Analysis*,  
> accepted to the **Workshop on Computation: Theory and Practice (WCTP) 2025**.

The toolkit’s purpose is **transparency and reproducibility**. We are making our resources publicly visible so that others can examine, replicate, and extend our work on sentiment and affect analysis in Philippine languages. Over time, this repository will be populated with additional materials, code, and documentation from our ongoing and future studies.

---

### 📦 Included Resources
We are distributing select artifacts from our research for **academic transparency**:

- 🪶 **Word2Vec models** trained on Philippine Twitter text data. See [`models/word2vec`](./models/word2vec/README.md).
- ✂️ **Tokenizer** used in our preprocessing pipeline, released exactly as used to train the Word2Vec models. See [`docs/TOKENIZER_SPEC.md`](./docs/TOKENIZER_SPEC.md).
- 🤖 (Upcoming) **Best-performing sentiment classifier** trained using emoji-based synthetic labels  
- 💬 (Upcoming) **Tweet ID datasets** (in compliance with Twitter’s data redistribution policy)  

These resources are made available **to support further research** and not as finalized products.

---

### 🚀 Installation

Requires Python 3.8+. The tokenizer has no dependencies.

```bash
pip install git+https://github.com/dlsucelt/PH-Senti-Toolkit
```

To also load the Word2Vec models (adds [Gensim](https://radimrehurek.com/gensim/)):

```bash
pip install "ph-senti-toolkit[models] @ git+https://github.com/dlsucelt/PH-Senti-Toolkit"
```

### ✂️ Quick start

```python
from ph_senti_toolkit import Tokenizer

tokenizer = Tokenizer()
tokenizer.tokenize("Grabeeee ang init ngayon!!! @kaibigan tara sa mall 3:00 PM 😂")
# ['grabeee', 'ang', 'init', 'ngayon', '!', '!', '!', '<USERHANDLE>',
#  'tara', 'sa', 'mall', '<TIME>', '😂']
```

With a Word2Vec model downloaded from [Zenodo](https://doi.org/10.5281/zenodo.17369886):

```python
from gensim.models import KeyedVectors

kv = KeyedVectors.load("w2v_tweets_w2_d200_v2.wordvectors")
tokens = tokenizer.tokenize("ang init ngayon")
vectors = [kv[t] for t in tokens if t in kv.key_to_index]
```

A runnable version is in [`examples/usage.py`](./examples/usage.py).

**Important:** the tokenizer is released *unchanged*, with its known quirks (for example, every number with 3+ digits becomes `<PHONENUMBER>`, and emoji are split per Unicode code point). This is deliberate: it is the only way your tokens will match the models' vocabulary. We verified that rebuilding the training corpus with this tokenizer reproduces the vocabulary of all three released models exactly. The quirks are listed in the [specification](./docs/TOKENIZER_SPEC.md) and marked `KNOWN ISSUE` in the source. The untouched original file is preserved at the [`paper-original`](https://github.com/dlsucelt/PH-Senti-Toolkit/tree/paper-original) tag.

The tokenizer does **not** filter anything. The original corpus-level filtering (dropping empty or duplicate tweets and tweets with no letters or digits) is described in the specification for reference only.

### 🧪 Tests

```bash
pip install -e ".[test]"
pytest
```

All test strings are invented. No tweets are distributed in this repository.

---

### 🔍 Intended Use
The **PH Senti Toolkit** is designed for:
- Researchers studying sentiment or affect analysis in low-resource and multilingual contexts  
- Developers experimenting with Philippine-language NLP models  
- Educators and students analyzing sentiment modeling approaches in code-mixed or regional language data

---

### 🧩 Roadmap
This repository is **a work in progress**. We will **gradually populate** it with:
- tweet ID datasets
- the best-performing sentiment classifiers
- updated pretrained embeddings and an improved tokenizer
- model architectures and configuration details  
- references to future CeLT studies related to sentiment and affect analysis  

---

### 🏛️ Citation
If you find this work useful in your research or plan to use any of the resources provided here, please cite:

> Co, S. T. S., Custodio, N. R. E., Dela Cruz, A. L. L., Sanchez, M. C. B., Jabanes, J. C., & Tighe, E. P. (2025). *Exploring Emoji-based Synthetic Annotations for Filipino-English Sentiment Analysis.* Proceedings of the Workshop on Computation: Theory and Practice (WCTP 2025).

A final bibliographic citation will be provided once the official publication is released. Machine-readable metadata is in [`CITATION.cff`](./CITATION.cff) (GitHub's "Cite this repository" button).

---

### 🙏 Credits
The tokenizer and preprocessing code were written by the paper's student authors, **Sean Timothy S. Co, Nicholas Rupert E. Custodio, Alexis Louis L. Dela Cruz, Martin Christopher B. Sanchez and Jason Jan C. Jabanes**, advised by **Edward P. Tighe**.

---

### 📄 License
The **PH Senti Toolkit** is currently released under the [MIT License](./License)  
to promote openness, transparency, and reproducibility in research.

This license allows others to freely use, modify, and redistribute the code and resources,
provided that the original copyright and license notice are retained.
The authors and the Center for Language Technologies (CeLT), De La Salle University,
retain full ownership of all intellectual property associated with this work.

*Content of the README was primarily generated with the help of ChatGPT, and later revised with the help of Claude.*
