# Financial Risk Analytics & Decision Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-Analytics-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-Scientific-013243?style=for-the-badge&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=for-the-badge"/>
  <img src="[https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)"/>
</p>

<p align="center">
  An end-to-end financial decision support system that transforms raw KAP (Public Disclosure Platform) balance sheets into dynamic risk intelligence — computing health scores, risk tiers, trend directions, sector benchmarks, and macroeconomic stress resilience.
</p>

---

## Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Features](#features)
- [Architecture](#architecture)
- [Scoring Methodology](#scoring-methodology)
- [Stress Testing](#stress-testing)
- [Installation](#installation)
- [Usage](#usage)
- [Input Format](#input-format)
- [Project Structure](#project-structure)
- [Disclaimer](#disclaimer)

---

## Overview

Traditional financial analysis is largely **static and descriptive** — a snapshot of ratios with no forward-looking interpretation.

This platform moves beyond that. It builds a **quantitative risk engine** on top of raw accounting data, producing:

- A single interpretable **health score (0–100)**
- A **trend-aware scoring model** that distinguishes improving companies from deteriorating ones with identical current ratios
- **Sector benchmarking** that contextualizes performance relative to industry standards
- A **stress test simulator** that models revenue shocks and debt shocks without mutating original data

The goal is to give decision-makers — analysts, investors, credit officers — an explainable, reproducible risk signal rather than a table of ratios they must interpret themselves.

---

## Demo

> *Dashboard screenshots coming soon*

To run the interactive dashboard locally:

```bash
streamlit run app.py
```

---

## Features

| Feature | Description |
|---|---|
| KAP-compatible Excel parsing | Reads balance sheets in standard KAP disclosure format |
| Automated ETL pipeline | Cleans, validates, and indexes financial statement rows |
| Financial ratio engine | Computes Current Ratio, D/E, Net Margin, EBITDA Margin |
| Linear normalization | Maps each ratio to a 0–100 score using configurable thresholds |
| Trend-aware scoring | Weights recent performance, trend direction, and historical average |
| Sector benchmarking | Compares company ratios against predefined industry standards |
| Stress test simulation | Applies revenue/debt shocks and recalculates risk in real time |
| Interactive dashboard | Streamlit web app with sliders, metrics, and live recalculation |
| Excel reporting | Exports multi-sheet report: executive summary, scores, benchmark |

---

## Architecture

```
Raw Excel File (KAP Format)
           │
           ▼
  Data Validation & Cleaning
  (pd.read_excel → set_index → to_numeric)
           │
           ▼
  Financial Ratio Engine
  (Current Ratio, D/E, Net Margin, EBITDA Margin)
           │
           ▼
  Scoring Engine
  (Linear normalization per ratio → weighted final score)
           │
           ▼
  Benchmark Engine
  (Company vs. sector standard → gap & status)
           │
           ▼
  Stress Test Engine
  (Parametric shock → re-score → restore original)
           │
           ▼
  Streamlit Dashboard + Excel Report
```

---

## Scoring Methodology

### Ratios & Weights

| Ratio | Formula | Weight |
|---|---|---:|
| Current Ratio | Current Assets / Current Liabilities | 25% |
| Debt/Equity | Total Liabilities / Total Equity | 25% |
| Net Profit Margin | Net Income / Revenue | 15% |
| EBITDA Margin | Operating Profit / Revenue | 35% |

### Normalization

Each ratio is linearly normalized to **[0, 100]** using configurable lower and upper thresholds. Inverse ratios (e.g. Debt/Equity, where lower is better) are handled explicitly:

```python
# Standard ratio (higher = better)
score = (value - lower) / (upper - lower) * 100

# Inverse ratio (lower = better)
score = (upper - value) / (upper - lower) * 100
```

### Final Score Composition

| Component | Weight |
|---|---:|
| Last year performance | 40% |
| Trend direction | 40% |
| Historical average | 20% |

Trend direction is scored as **100** for improving trends, **50** for flat, and **0** for deteriorating (reversed for inverse ratios). This ensures a company with a mediocre current ratio but a consistently improving trajectory scores higher than one with a strong ratio that has been declining.

### Risk Classification

| Score | Category |
|---|---|
| ≥ 80 | 🟢 Low Risk |
| 60 – 79 | 🟡 Medium Risk |
| < 60 | 🔴 High Risk |

---

## Sector Benchmarking

The engine compares each company ratio against predefined sector standards and assigns a directional status:

| Ratio | Company | Industry | Status |
|---|---:|---:|---|
| Current Ratio | 1.82 | 1.60 | ✅ Good |
| Debt/Equity | 1.10 | 1.20 | ✅ Good |
| Net Margin | 0.09 | 0.12 | ⚠️ Watch |
| EBITDA Margin | 0.20 | 0.18 | ✅ Good |

Benchmarks and thresholds are configurable via the class constructor.

---

## Stress Testing

The stress test engine applies parametric shocks to the most recent period's data and recomputes ratios and risk scores **without mutating the original dataset**. After simulation, all values are restored.

Supported shock parameters:

| Parameter | Range |
|---|---|
| Revenue shock | −50% → +50% |
| Short-term debt shock | −50% → +50% |

The Streamlit dashboard exposes these as interactive sliders with live score recalculation.

---

## Installation

```bash
# Clone repository
git clone https://github.com/malpyilmaz/financial-risk-engine.git
cd financial-risk-engine

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**

```
pandas
numpy
matplotlib
streamlit
openpyxl
xlsxwriter
```

---

## Usage

### Streamlit Dashboard (recommended)

```bash
streamlit run engine.py
```

Upload a KAP-format Excel file via the sidebar. The dashboard renders the health score, risk category, stress test simulator, ratio tables, benchmark comparison, and trend charts.

### CLI / Terminal

```bash
python engine.py
```

Reads `aselsan.xlsx` from the working directory and prints ratio scores, benchmark comparison, and the overall risk score to stdout. Also renders matplotlib charts.

### Python API

```python
from engine import FinancialRiskAnalyzer

analyzer = FinancialRiskAnalyzer("aselsan.xlsx")

# Compute ratios
ratios = analyzer.rasyolari_hesapla()

# Get overall score and risk tier
score, risk, breakdown = analyzer.firma_skoru_uret()
print(f"Score: {score:.2f} | Risk: {risk}")

# Sector benchmark
benchmark = analyzer.benchmark_karsilastirma()

# Stress test: -20% revenue, +10% short-term debt
sim_score, sim_risk = analyzer.senaryo_simule_et(
    hasilat_degisim_yuzdesi=-20,
    borc_degisim_yuzdesi=10
)


```

---

## Input Format

Input Excel files must follow the KAP financial statement format with data beginning at **row 9 (0-indexed: header=8)** and a column named `FİNANSAL DURUM TABLOSU` used as the row index.

Required rows:

```
Dönen Varlıklar
Kısa Vadeli Yükümlülükler
Toplam Yükümlülükler
Toplam Özkaynaklar
Net Dönem Kârı (Zararı)
Hasılat
Esas Faaliyet Kârı (Zararı)
```

Each column beyond the index represents a reporting period (quarter or year). The engine uses the full time series for trend analysis and the final column as the most recent period.

---

## Project Structure

```
financial-risk-engine/
│
├── engine.py                  # Core engine + Streamlit dashboard
├── aselsan.xlsx            # Sample input (KAP disclosure)
├── screenshots/            # Dashboard screenshots
├── requirements.txt
└── README.md
```

---

## Disclaimer

This project is developed solely for **educational and portfolio purposes**.

**This is not investment advice.** Sample data is sourced from public financial disclosures available on the KAP platform. No proprietary or non-public information is used.

---

## Author

**Mehmet Alp Yılmaz**  
Statistics & Data Science | Risk Analytics · Machine Learning · Financial Modeling

<p>
  <a href="https://www.linkedin.com/in/malpyilmaz"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin"/></a>
  <a href="mailto:malpylmz26@gmail.com"><img src="https://img.shields.io/badge/Email-Contact-EA4335?style=flat-square&logo=gmail&logoColor=white"/></a>
</p>
