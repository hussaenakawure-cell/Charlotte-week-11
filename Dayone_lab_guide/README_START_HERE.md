# Week 11 Class 1 · Student release

**Topic:** Missing Data & Imputation. 180-minute notebook-led class; one 60–90-minute independent Python lab, including PR.

## Before class
1. Use Python 3.10+ with VS Code Python + Jupyter extensions.
2. In your `.venv`, run `python -m pip install -r lab/requirements.txt`; ensure `ipykernel` is installed for notebooks (`python -m pip install ipykernel`).
3. Open `teaching/Week11_Class1_Detailed_Interactive_Notebook.ipynb` with your `.venv` kernel. Launch VS Code with this folder open so the demo CSV resolves.

## During class
Follow notebook Sections A–E. Try short questions and discuss three AWS-style scenarios. No need to finish a second homework project.

## After class — assessed lab
Read `lab/Week11_Class1_Student_Lab_Guide.docx`. Implement `lab/missing_data_lab.py`, run the file from the `lab` directory, and submit a PR to *your own repository* on `feature/week11-class01-missing-data`.

## Data provenance
- `teaching/retail_missing_demo_SYNTHETIC.csv`: fully synthetic classroom demo.
- An unmodified public-data subset is held by the **instructor only** for provenance checking. The original observations come from Gapminder via `plotly.express.data.gapminder()` (8 countries, 12 dates per country).
- `lab/gapminder_instructional_missing.csv` / `.xlsx`: same subset with **17 cell values deliberately removed** for teaching purposes. This missingness is synthetic; the underlying nonblank observations are public-derived. The spreadsheet is an alternate representation of the same rows, not an extra assignment.

**Sources:** https://www.gapminder.org/data/ ; https://plotly.com/python/plotly-express/ ; https://pandas.pydata.org/docs/user_guide/missing_data.html ; https://docs.aws.amazon.com/aws-certification/latest/data-engineer-associate-01/data-engineer-associate-01-domain1.html


## Lab: Week 11 Class 1 - Missing Data Lab (My Work)

**What I did:**
- Profiled missingness in `gapminder_instructional_missing.csv` (96 rows, 17 blanks deliberately removed for class)
- Added `lifeExp_was_missing` and `gdpPercap_was_missing` flags BEFORE any filling
- Filled missing `continent` from other rows of the same country
- Imputed `lifeExp` and `gdpPercap` with continent-level median, with global median fallback
- Verified: 96 rows kept, no nulls, originally observed values unchanged

**Decisions:**
I chose continent median over mean because median is not pulled by rich/poor outliers.

**Limitation / Risk:**
Median imputation is estimation, not recovery. It reduces real spread and makes data look more confident than it is. The 17 blanks are instructional missingness, not real missingness, so results should not be claimed as true Gapminder values.

**Outputs:**
- `outputs/missingness_report.csv`
- `outputs/imputed_gapminder.csv`
