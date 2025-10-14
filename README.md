# MOOSE-Chem: Large Language Models for Rediscovering Unseen Chemistry Scientific Hypotheses



<!-- <a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FZonglinY%2FMOOSE-Chem&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/></a> -->
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/cloudposse.svg?style=social&label=Follow%20%40Us)](https://x.com/Yang_zy223)
[![GitHub Repo stars](https://img.shields.io/github/stars/ZonglinY/MOOSE-Chem%20)](https://github.com/ZonglinY/MOOSE-Chem)
[![arXiv](https://img.shields.io/badge/arXiv-b31b1b.svg)](https://arxiv.org/abs/2410.07076)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

We introduce **MOOSE-Chem**, which is an LLM-based multi-agent framework for automated chemistry scientific hypothesis discovery. 

With only LLMs with training data up to October 2023, it has rediscovered many chemistry hypotheses published on Nature, Science, or similar levels in 2024 (also only available online in 2024) with very high similarity, covering the main innovations.



<p align="center" width="100%">
  <img src="./Resources/main_figure_io_insp_corpus.png" alt="MOOSE-Chem" style="width: 75%; display: block; margin: auto;"></a>
</p>

The input to MOOSE-Chem can be as simple as only:

&emsp;(1) *research question*: can be on any chemistry & material science domain;

&emsp;(2) *background survey*: (optionally) a several-paragraph-long survey describing the existing methods for the *research question*;

&emsp;(3) *inspiration corpus*: (this repo contains the default 3000 papers) title and abstract of many (random) chemistry papers that might serve as inspirations for the *research question*, preferably published on top venues. You can also build a custom corpus from Excel files or automatically from paper references using the Semantic Scholar API.

**MOOSE-Chem** can then output a list of ranked chemistry hypotheses (might take a few hours to "think") that could be both novel and valid.


---------- 

This repo contains all the code of **MOOSE-Chem**, to help every chemistry lab to catalyze their chemistry scientific discovery process.

In general, **MOOSE-Chem** contains three stages:  
&emsp;(1) inspiration retrieval;  
&emsp;(2) hypothesis composition;   
&emsp;(3) hypothesis ranking.

The commands for the three stages are introduced after the "quick start".

---

## 🏗️ Improved Architecture

**MOOSE-Chem** now features an improved, modular architecture following software engineering best practices:

- **Configuration Management**: Type-safe configuration using Pydantic Settings
- **LLM Abstraction Layer**: Unified interface for OpenAI, Azure, and Google LLM providers
- **Data Models**: Strongly-typed data structures with automatic validation
- **Comprehensive Testing**: Unit tests for all new components

📖 **See [ARCHITECTURE.md](ARCHITECTURE.md)** for detailed documentation and usage examples.

🔧 **See [REWRITE.md](REWRITE.md)** for the architectural suggestions that guided this refactoring.

💡 **Quick example:**
```python
from Method.llm_client import create_llm_client
from Method.models import Hypothesis

# Easy provider switching
client = create_llm_client(provider="openai", api_key="...", model="gpt-4")
response = client.generate(prompt="Your prompt here")

# Automatic validation
hypothesis = Hypothesis(text="...", scores=[8.5, 9.0])
print(hypothesis.average_score)  # 8.75
```

--- 

## ⚡ Step 0: Quick Start

```bash
git clone https://github.com/ZonglinY/MOOSE-Chem.git
cd MOOSE-Chem
conda create -n msc python=3.10
conda activate msc
pip install -r requirements.txt
```

Then, open `main.sh` and configure the following parameters:

* `api_type`
* `api_key`
* `base_url`
* `model_name_insp_retrieval`
* `model_name_gene`
* `model_name_eval`

> 🔧 **Note:**
> Set `api_type` to `0` if you're using an OpenAI API key, and to `1` if you're using an Azure OpenAI API key.
>
> 💡 **Tip:**
> You can assign the same model name to all three tasks (`model_name_insp_retrieval`, `model_name_gene`, and `model_name_eval`).

## 🚀 New Command-Line Interface

The `main.sh` script now supports command-line options to run specific steps instead of commenting/uncommenting code:

```bash
# Run a specific step:
bash main.sh retrieval      # Step 3: Inspiration Retrieval
bash main.sh generation     # Step 4: Hypothesis Composition  
bash main.sh ranking        # Step 5: Hypothesis Ranking
bash main.sh display        # Step 6: Hypothesis Display

# Run all main steps sequentially:
bash main.sh all

# Optional steps:
bash main.sh background     # Step 1: Custom Research Background
bash main.sh corpus         # Step 2: Custom Inspiration Corpus (uses Semantic Scholar by default)
bash main.sh analysis       # Step 7: Analysis

# Show help:
bash main.sh --help
```

> 💡 **Quick Start Tip:**
> For most users, simply run `bash main.sh all` to execute the complete pipeline (steps 3-6).

### 📝 Migration from Old Approach

**Before (manual editing required):**
- Edit `main.sh` to comment/uncomment specific Python commands
- Risk of syntax errors from manual editing
- Difficult to run partial workflows

**Now (command-line driven):**
- Clean command-line interface
- No manual code editing required  
- Easy to run individual steps or full pipeline
- Built-in help and error handling

---

## 📋 Step 1: (Optional) Provide Custom Research Background — or Use the Default Benchmark

You can supply your own `research_question` and `background_survey` as input. Otherwise, the system will use a built-in benchmark.

#### To provide custom input:

1. Open `./Preprocessing/custom_research_background_dumping_and_output_displaying.py`
2. In the `research_background_to_json()` function, manually fill in:
   - `research_question`
   - `background_survey`
3. Set `custom_research_background_path` in `main.sh` to store the customized research question and background survey
4. Run the step:

```bash
bash main.sh background
```

> ✅ Once done, this will generate a custom research background file that can be used in later steps.

---



## 📋 Step 2: (Optional) Use a Custom Inspiration Corpus — or Stick with the Default

You can provide your own inspiration corpus (titles and abstracts) to set up the hypothesis search space. If not provided, the system will use the default ones in the benchmark dataset.

### ✅ Three Ways to Provide a Custom Corpus:

#### **Option 1**: Manually Compose Your Own

Prepare a list of papers and save them in the following format:

```python
[[title1, abstract1], [title2, abstract2], ...]
```

Save this to the path specified by `custom_inspiration_corpus_path` in `main.sh`.

---

#### **Option 2**: Use Semantic Scholar API to Retrieve References

🆕 **New Feature!** Automatically build an inspiration corpus from the references of a specific paper using the Semantic Scholar API.

**Method A: Using main.sh (Recommended)**

1. **Configure main.sh**
   - Set `custom_inspiration_corpus_path` in `main.sh` to the desired output path for the inspiration corpus
   - Set `semantic_scholar_paper_id` in `main.sh` to your desired paper ID (currently set to "CorpusId:276775381")
   - Run the step:

```bash
bash main.sh corpus
```

**Method B: Direct Python Command**

Use the Semantic Scholar method directly with a paper ID:

```bash
# Using ArXiv ID
python Preprocessing/construct_custom_inspiration_corpus.py \
  --method semanticscholar \
  --paper_id "arXiv:1706.03762" \
  --max_references 100 \
  --custom_inspiration_corpus_path "./my_semantic_scholar_corpus.json"

# Using DOI
python Preprocessing/construct_custom_inspiration_corpus.py \
  --method semanticscholar \
  --paper_id "10.1038/nature14539" \
  --max_references 50 \
  --custom_inspiration_corpus_path "./my_semantic_scholar_corpus.json"
```

**Supported Paper ID formats:**
- **DOI**: `10.1038/nature14539`
- **ArXiv**: `arXiv:1706.03762` or `1706.03762`
- **Semantic Scholar ID**: `649def34f8be52c8b66281af98ae884c09aef38b`
- **Corpus ID**: `CorpusId:276775381`
- **Pubmed ID**: `PMID:19872477`

**Parameters:**
- `--paper_id`: The ID of the paper whose references you want to retrieve
- `--max_references`: (Optional) Maximum number of references to retrieve. If not specified, all available references will be used
- `--custom_inspiration_corpus_path`: Output path for the generated corpus file

> ✅ This method automatically extracts title-abstract pairs from the reference list of the specified paper, providing a focused and relevant inspiration corpus.

> 💡 **Note**: This is now the default method used by `bash main.sh corpus`. You can change the paper ID by modifying the `semantic_scholar_paper_id` variable in `main.sh`.

---

#### **Option 3**: Use Web of Science to Download in Bulk

1. **Prepare the Raw Data**
   * Use [Web of Science](https://www.webofscience.com/wos/woscc/summary/0d1f66e0-aebb-4b29-a6c8-d685e04c2ea9-015bae6080/relevance/1) to search for papers by journal name and optionally filter with keywords.
   * Select the desired papers by checking their boxes.
   * Click **"Export"** in the top menu.
   * Choose **"Excel"** as the format.
   * Set **"Record Content"** to **"Author, Title, Source, Abstract"**
   * Click **"Export"** to download the file (The file should have a `.xlsx` or `.xls` extension).

   Save all `.xlsx` or `.xls` files into a single folder for further processing.

2. **Configure and Run**  
   - Add a `custom_raw_inspiration_data_dir` variable in `main.sh` pointing to your Excel files folder
   - Set `custom_inspiration_corpus_path` in `main.sh` to the desired output path for the processed inspiration corpus
   - Modify the `run_corpus()` function in `main.sh` to use the Excel method:
   
   ```bash
   # Add this variable at the top of main.sh (around line 70):
   custom_raw_inspiration_data_dir="/path/to/your/excel/files"
   
   # Change the run_corpus() function to:
   run_corpus() {
       echo "=== Step 2: Custom Inspiration Corpus Construction ==="
       python -u ./Preprocessing/construct_custom_inspiration_corpus.py \
               --custom_inspiration_corpus_path ${custom_inspiration_corpus_path} \
               --method excel --raw_data_dir ${custom_raw_inspiration_data_dir}
   }
   ```
   
   - Run the step:

```bash
bash main.sh corpus
```

**Alternative: Direct Python Command**

You can also run the Excel processing directly without modifying main.sh:

```bash
python Preprocessing/construct_custom_inspiration_corpus.py \
  --method excel \
  --raw_data_dir "/path/to/your/excel/files" \
  --custom_inspiration_corpus_path "./my_excel_corpus.json"
```

> ✅ Once done, this will generate a custom inspiration corpus file that can be used in later steps.

> 💡 **Note**: By default, `bash main.sh corpus` uses the Semantic Scholar method. To use Excel files from Web of Science, you need to modify `main.sh` as shown above.


---

## 🔍 Step 3: Inspiration Retrieval

This step retrieves relevant literature snippets to serve as inspiration for hypothesis generation.

#### Configuration:

- If using custom research background and inspiration corpus: Ensure `custom_research_background_path` and `custom_inspiration_corpus_path` are set in `main.sh`
- If using the default benchmark: Set both variables to empty strings (`""`) in `main.sh`

#### Run the step:

```bash
bash main.sh retrieval
```

<!-- Customized *research question* and *background survey* can be used by modifying ```custom_rq, custom_bs = None, None``` to any string in inspiration_screening.py. -->

<!-- Customized *inspiration corpus* can be adopted by setting ```--title_abstract_all_insp_literature_path``` to your customized file with format ```[[title, abstract], ...]```. -->

---

## 🧠 Step 4: Hypothesis Composition

#### Run the step:

```bash
bash main.sh generation
```

> 📝 **Note:** Keep the `custom_research_background_path` and `custom_inspiration_corpus_path` settings from your previous steps.

---

## 📈 Step 5: Hypothesis Ranking

#### Run the step:

```bash
bash main.sh ranking
```

> 📝 **Note:** Keep the `custom_inspiration_corpus_path` setting from your previous steps.

---

## 🖥️ Step 6: (Optional) Display Ranked Generated Hypothesis

#### Run the step:

```bash
bash main.sh display
```

The ranked generated hypotheses will be saved to the file specified by `display_txt_file_path` in `main.sh`.

---


<!-- These basic commands for the three stages can also be found in ```main.sh```.  -->

```Assumption1-RetrieveUnseen.sh``` and ```Assumption2-Reason2Unknown.sh``` contain combinations of these three basic commands (with different arg parameters) to investigate LLMs' ability on these three aspects.

---

## Analysis

```./Analysis/analysis.py``` can be used to analyze the results of the three stages. 
This [link](https://drive.google.com/file/d/1WdnB5Ztb4n3DNfwJeE9GJW-BJvdoWmNN/view?usp=sharing) stores the result files from all the experiments mentioned in the paper. They can be used with ```analysis.py``` to display the experiment results reported in the paper.

---

## An Example

Here we present a rediscovered hypothesis from MOOSE-Chem, with input:

(1) a research question && a survey on existing methods for the question; and

(2) 300 random chemistry papers published on Nature or Science, containing two groundtruth inspirations papers.

### Ground Truth Hypothesis

*The main hypothesis is that a **nitrogen-doped ruthenium (Ru)** electrode can effectively catalyze the reductive deuteration of (hetero)arenes in the presence of **D_2O**, leading to high deuterium incorporation into the resulting saturated cyclic compounds. The findings validate this hypothesis by demonstrating that this electrocatalytic method is highly efficient, scalable, and versatile, suitable for a wide range of substrates.*

### Rediscovered Hypothesis

*A pioneering integrated electrocatalytic system leveraging **ruthenium** nanoparticles embedded in **nitrogen-doped** graphene, combined with a dual palladium-coated ion-exchange membrane reactor, will catalyze efficient, scalable, and site-selective reductive deuteration of aromatic hydrocarbons and heteroarenes. Utilizing deuterium sources from both $D_2$ gas and **D_2O**, this system will optimize parameters through real-time machine learning-driven dynamic adjustments. Specific configurations include ruthenium nanoparticle sizes (2-4 nm), nitrogen doping levels (12-14\%), precisely engineered palladium membranes (5 micrometers, ensuring 98\% deuterium-selective permeability), and advanced cyclic voltammetry protocols (1-5 Hz, -0.5V to -1.5V).*

### Expert's analysis 

The proposed hypothesis effectively covers two key points from the ground truth hypothesis: **the incorporation of ruthenium (Ru) and the use of D_2O as a deuterium source** within the electrocatalytic system. However, the current content does not detail the mechanism by which Ru-D is produced, which is essential for explaining the process of reductive deuteration. Nevertheless, the results are still insightful. The specific level of nitrogen doping, for example, is highly suggestive and warrants further investigation. Overall, the match remains strong in its alignment with the original hypothesis while also presenting opportunities for deeper exploration.

---

## Bib Info
If you found this repository useful, please consider 📑citing:

	@inproceedings{yang2024moose,
	  title={MOOSE-Chem: Large Language Models for Rediscovering Unseen Chemistry Scientific Hypotheses},
	  author={Yang, Zonglin and Liu, Wanhao and Gao, Ben and Xie, Tong and Li, Yuqiang and Ouyang, Wanli and Poria, Soujanya and Cambria, Erik and Zhou, Dongzhan},
	  booktitle={Proceedings of the International Conference on Learning Representations (ICLR)},
	  year={2025}
	}


---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
