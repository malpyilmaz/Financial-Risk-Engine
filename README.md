# Financial Risk Analytics & Decision Engine
("Bu analizler yatırım tavsiyesi değildir")
*[Türkçe versiyon için aşağı kaydırın / Scroll down for Turkish version](#türkçe-versiyon)*

This project is a Python and Streamlit-based **Decision Support & Risk Scoring Engine** that analyzes corporate financial statements, applying statistical trend analysis, linear scoring, and macroeconomic stress testing.

## Project Objective
Traditional financial analysis relies on static calculations. This engine processes raw Excel data (ETL) to provide not just descriptive analytics, but proactive, data-driven insights by simulating **"historical trends"** and **"what-if scenarios"** for decision-makers.

## Core Features
* **Automated Data Pipeline (ETL):** Reads, formats, and transforms raw financial statements (KAP format) into analyzable datasets.
* **Weighted Scoring Engine:** Evaluates metrics using a linear interpolation technique (0-100 scale) based on **Last Year (40%)**, **Trend Direction (40%)**, and **Historical Average (20%)**.
* **Industry Benchmark Analysis:** Compares the company's metrics against defined industry standards to highlight strengths and vulnerabilities.
* **Scenario Simulation (Stress Testing):** Interactive *What-If* analysis that simulates the real-time impact of revenue shocks and debt fluctuations on the company's "Overall Health Score".
* **BI Dashboard:** Provides an interactive user interface (UI) and data visualizations via Streamlit.

## Tech Stack
* **Python 3.x**
* **Pandas & NumPy:** Data manipulation, financial modeling, and scalar normalization.
* **Matplotlib:** Time-series trend analysis and visualizations.
* **Streamlit:** Interactive web interface and simulation tools.

## How to Run

**Option 1: Run as an Interactive Web Dashboard**
```bash

streamlit run app.py

