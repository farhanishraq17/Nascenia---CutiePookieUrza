---
task_categories:
- text-generation
language:
- bn
multilinguality:
- monolingual
source_datasets:
- original
tags:
- bangla bangla-paraphrase bangla-health-paraphrase
pretty_name: BanglaHealthParaphrase
license: cc-by-4.0
size_categories:
- 100K<n<1M
---
# Dataset Card for "BanglaHealthParaphrase"

<!-- Provide a quick summary of the dataset. -->

BanglaHealthParaphrase is a Bengali paraphrasing dataset specifically curated for the health domain. It contains over 200,000 sentence pairs, where each pair consists of an original Bengali sentence and its paraphrased version. The dataset was created through a multi-step pipeline involving extraction of health-related content from Bengali news sources, English pivot-based paraphrasing, and back-translation to ensure linguistic diversity while preserving semantic integrity. A custom python script was developed to achieve this task. This dataset aims to support research in Bengali paraphrase generation, text simplification, chatbot development, and domain-specific NLP applications.


### Dataset Description

| Field       | Description                                 |
|-------------|---------------------------------------------|
| Language    | Bengali (Bangla)                            |
| Domain      | Health                                      |
| Size        | 200,000 sentence pairs                      |
| Format      | CSV with fields: `sl`, `id`, `source_sentence`, `paraphrase_sentence` |
| License     | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Each entry contains:
- `SL`: SL represents serial number of the sentence pair.
- `ID`: ID represents unique identifier for each sentence pair.
- `source_sentence`: A Bengali sentence from a health-related article.
- `paraphrased_sentence`: A meaning-preserving paraphrase of the source sentence.

## 🛠️ Construction Methodology

The dataset was developed through the following steps:

1. **Data Collection**: Health-related sentences were scraped from leading Bengali online newspapers and portals.
2. **Preprocessing**: Cleaned and normalized sentences using custom text-cleaning scripts.
3. **Pivot Translation Method**:
   - Translated original Bengali sentences into English.
   - Generated English paraphrases using a T5-based paraphraser.
   - Back-translated English paraphrases to Bengali using NMT models.
4. **Filtering**: Applied semantic similarity filtering and sentence length constraints.
5. **Manual Validation**: A sample subset was manually reviewed by 100 peers to ensure quality and diversity.

## ✨ Key Features

- Focused entirely on the **Healthcare Domain**.
- High-quality paraphrases generated using a robust multilingual pivoting approach.
- Suitable for use in **Bengali NLP tasks** such as paraphrase generation, low-resource model training, and chatbot development.

## 📰 Related Publication

This dataset is published in **Data in Brief (Elsevier)**:
> **BanglaHealth: A Bengali paraphrase Dataset on Health Domain**  
> [Faisal Ibn Aziz, Dr. Mohammad Nazrul Islam, 2025](https://doi.org/10.1016/j.dib.2025.111699)

### Dataset Sources

[Detailed in the paper](https://doi.org/10.1016/j.dib.2025.111699) 

### Licensing Information
Contents of this repository are restricted to only non-commercial research purposes under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). Copyright of the dataset contents belongs to the original copyright holders.

### Data Instances

Sample data format. 
```
{
  "sl": 28,
  "id": 28,
  "source_sentence": "ডেঙ্গু হেমোরেজিক ফিভারে মূলত রোগীর রক্তনালীগুলোর দেয়ালে যে ছোট ছোট ছিদ্র থাকে, সেগুলো বড় হয়ে যায়।",
  "paraphrased_sentence": "ডেঙ্গু হেমোরেজিক ফিভারে রোগীর রক্তনালীর দেয়ালে ছোট ছোট ছিদ্র বড় হয়ে যায়।"
}
  ```

## Loading the dataset
```python
from datasets import load_dataset
dataset = load_dataset("faisal4590aziz/bangla-health-related-paraphrased-dataset")

```

## Citation
If you are using this dataset, please cite this in your research.

```
@article{AZIZ2025111699,
  title = {BanglaHealth: A Bengali paraphrase Dataset on Health Domain},
  journal = {Data in Brief},
  pages = {111699},
  year = {2025},
  issn = {2352-3409},
  doi = {https://doi.org/10.1016/j.dib.2025.111699},
  url = {https://www.sciencedirect.com/science/article/pii/S2352340925004299},
  author = {Faisal Ibn Aziz and Muhammad Nazrul Islam},
  keywords = {Natural Language Processing (NLP), Paraphrasing, Bengali Paraphrasing, Bengali Language, Health Domain},
}
```