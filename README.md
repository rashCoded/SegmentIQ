# SegmentIQ

<p align="center">
  A retail analytics platform that uncovers product co-purchase patterns and delivers market basket recommendations from real transactional data — built with an end-to-end pipeline from raw data to interactive dashboard.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit"/>
  <img src="https://img.shields.io/badge/scikit--learn-Apriori-F7931E?style=flat-square&logo=scikit-learn"/>
  <img src="https://img.shields.io/badge/pandas-2.x-150458?style=flat-square&logo=pandas"/>
  <img src="https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat-square&logo=plotly"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
</p>

---

## What It Does

SegmentIQ takes a real-world retail transaction dataset and turns it into actionable business intelligence. It answers two questions that matter in retail: **who is buying what**, and **what do they buy together**.

The platform has two operating modes — a research-grade notebook pipeline for deep exploratory analysis, and an interactive Streamlit dashboard where business users can explore patterns, tune parameters, and get product recommendations in real time.

---

## Features

### 📊 Exploratory Data Analysis
- Revenue and transaction volume breakdown by country, month, day of week, time of day, and hour
- Top customers by revenue and top products by quantity and revenue
- Country-level performance comparison (UK vs rest of world)
- Full static chart suite via matplotlib and seaborn for documentation-grade analysis

### 🛒 Market Basket Analysis
- Apriori algorithm on binary purchase indicator matrix built from transaction data
- Association rule mining with configurable minimum support and lift thresholds
- Rules filtered to remove trivial symmetric associations
- Ranked recommendations per product — top 3 by confidence then lift

### 🎯 Recommendation UI
- User selects a country and MBA parameters via sidebar controls
- Select any product from the antecedent vocabulary
- System returns top 3 recommended co-purchase products with supporting metrics
- Full rules table available with CSV export for analysts

### ⚡ Performance Optimisations for Interactive Use
- Top 150 products by frequency retained before basket construction — bounds matrix width and memory
- Itemsets capped at pairs (`max_len=2`) — prevents combinatorial explosion
- Row sampling to 50,000 when cleaned data exceeds threshold — keeps UI responsive
- `low_memory=True` in Apriori for memory safety

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web App | Streamlit |
| Data Processing | pandas, numpy |
| ML / Association Rules | mlxtend (Apriori + association rules) |
| Interactive Charts | Plotly |
| EDA Visualisation | matplotlib, seaborn |
| Notebook Orchestration | papermill, jupyter, nbconvert |

---

## Architecture

```
RetailData.csv (raw source)
        │
        ▼
01-FeatureEngineering.ipynb
   - Clean data
   - Add time features (Hour, DayOfWeek, Month, Week, TimeOfDay)
   - Compute Sales Revenue
   - Export CleanRetailData.csv
        │
        ▼
02-ExploratoryDataAnalysis.ipynb
   - Country, product, customer analysis
   - Revenue trends by time dimensions
   - Static chart suite
        │
        ▼
03-MarketBasketAnalysis.ipynb
   - Build basket matrix
   - Run Apriori
   - Generate association rules
   - Export item_sets.json
        │
        ▼
app.py (Streamlit Dashboard)
   - Loads and cleans data independently
   - Runs Apriori with performance constraints
   - Serves interactive recommendation UI
```

---

## Data Pipeline

### Raw Dataset
`RetailData.csv` — Online Retail transaction data with columns: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`. Auto-downloaded if not present.

### Cleaning Steps
- Remove rows with missing `Description` or `InvoiceNo`
- Remove cancelled invoices (InvoiceNo starting with `C`)
- Strip whitespace from descriptions
- Drop non-positive quantities
- Replace missing CustomerID with `Guest Customer`
- Drop short descriptions (length ≤ 8)
- Drop duplicate rows

### Feature Engineering
- `TotalPrice / Sales Revenue` = UnitPrice × Quantity
- `Hour`, `DayOfWeek`, `Month` extracted from InvoiceDate
- `Week of Year`, `Time of Day` added in notebook pipeline

### Market Basket Matrix
- One row per invoice, one column per product description
- Cell values are purchase quantities, binarised to 0/1
- Filtered to transactions with at least 2 distinct items
- Only top 150 products by frequency retained for interactive mode

---

## How Apriori Works (For the Viva)

**Support** — how often an itemset appears across all transactions. `support(A) = transactions containing A / total transactions`. Low support means rare co-occurrence.

**Confidence** — given A was bought, how often B was also bought. `confidence(A→B) = support(A∪B) / support(A)`. High confidence means strong directional association.

**Lift** — how much more often A and B appear together than expected by chance. `lift(A→B) = confidence(A→B) / support(B)`. Lift > 1 means the association is above random. We filter on lift to prioritise meaningful patterns over coincidental ones.

**Why pairwise rules only (`max_len=2`)?** Three-item or larger rules require exponentially more memory and computation. For an interactive app, pairwise rules give sufficient recommendation quality with predictable performance.

**Why top 150 products?** The full product catalogue has hundreds of items. A basket matrix with 500 columns and 50,000 rows would be too large for in-memory Apriori in a Streamlit session. Keeping the top 150 by frequency covers the products that matter most for recommendations.

---

## Running Locally

### Mode 1 — App Only (Recommended)
```bash
pip install -r requirements.txt
streamlit run app.py
```
The app downloads the dataset automatically if `RetailData.csv` is not present.

### Mode 2 — Full Notebook Pipeline
```bash
python run_project.py
```
This installs dependencies, downloads data if missing, and executes all three notebooks in sequence via papermill. Run this to refresh the EDA outputs and regenerate `item_sets.json`.

---

## Project Structure

```
SegmentIQ/
├── app.py                              # Streamlit dashboard
├── run_project.py                      # Notebook pipeline executor
├── requirements.txt                    # Dependencies
├── RetailData.csv                      # Raw transaction data (auto-downloaded)
├── CleanRetailData.csv                 # Cleaned + feature-engineered data
├── item_sets.json                      # Exported recommendation dictionary
├── 01-FeatureEngineering.ipynb         # Cleaning + feature creation
├── 02-ExploratoryDataAnalysis.ipynb    # EDA and business insights
└── 03-MarketBasketAnalysis.ipynb       # Apriori + association rules
```

---

## Engineering Decisions Worth Knowing

**UK as default country for analysis**
The UK accounts for the majority of transaction volume in the dataset. Using it as the default gives stable support estimates for association rules. Smaller countries have sparse transactions and produce unreliable or low-support rules.

**Lift as the primary rule quality metric**
Support and confidence alone can surface trivial rules — "customers who buy product A also buy product A." Lift measures whether the association is stronger than random chance. Filtering by lift > 1 ensures every rule in the output is genuinely informative.

**Notebook pipeline vs app pipeline drift**
The notebooks and `app.py` both clean the data but with slightly different rules — for example, the notebook drops the year 2010 rows (currently commented out) and handles `CustomerID` differently. This is a known tradeoff: the notebook preserves the full research methodology while the app optimises for runtime performance. They produce directionally consistent results but not identical outputs.

**papermill for notebook orchestration**
papermill executes Jupyter notebooks programmatically and captures outputs in separate output notebooks. This means the full research pipeline can be re-run with a single command and the outputs are preserved as reproducible artifacts.

---

## Author

**Rashmi Ranjan Badajena**
[GitHub](https://github.com/rashCoded) · [LinkedIn](https://www.linkedin.com/in/rashmiranjan-badajena/) · rashmiranjanbadajena.it@gmail.com

---

<p align="center">Built to turn raw transaction logs into decisions that make sense.</p>
