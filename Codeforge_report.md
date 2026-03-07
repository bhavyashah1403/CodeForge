# CodeForge: AI-Powered Options Market Analytics Platform

**Authors:** Team CodeForge  
**Affiliation:** Department of Computer Science and Engineering  
**Date:** March 2026

## Abstract
Options market data is high-volume, multi-dimensional, and time-sensitive, which makes manual interpretation difficult for analysts and traders. This work presents **CodeForge**, an end-to-end analytics platform that converts raw options chain data into interpretable insights through data preprocessing, domain-aware feature engineering, anomaly detection, and interactive visualization. The proposed system combines financial features such as implied volatility and Greeks with machine learning-based anomaly identification using Isolation Forest. A modular backend architecture supports both dashboard-based exploration and API-based consumption for frontend applications. Experimental analysis on multi-day options datasets demonstrates that the platform can identify unusual market behavior, summarize sentiment shifts, and provide strike-level risk intelligence. The solution is designed for extensibility toward real-time analytics and alerting.

## Keywords
Options Analytics, Isolation Forest, Implied Volatility, Greeks, FastAPI, Streamlit, Financial Data Engineering

## I. Introduction
Financial derivatives markets generate large streams of option chain observations across strikes, expiries, and timestamps. Although these data contain valuable information about sentiment, liquidity, and risk positioning, extracting actionable knowledge is challenging without structured analytics.

The objective of this project is to design and implement a practical system that can:
- ingest and standardize options data from multiple files,
- compute advanced options features,
- detect anomalous patterns using AI/ML methods,
- visualize market structure and behavior interactively, and
- expose processed outputs via REST APIs for integration with external clients.

The motivation behind CodeForge is to bridge the gap between raw options data and decision-ready market intelligence using a reproducible and deployment-oriented pipeline.

## II. Dataset Understanding
The project uses options market CSV snapshots captured across multiple dates. The dataset includes fields for strike price, expiry, option premiums, open interest, volume, spot price, and timestamp metadata.

### A. Data Sources
- `data/2026-02-17_exp.csv`
- `data/2026-02-24_exp.csv`
- `data/2026-03-02_exp.csv`

### B. Preprocessing Performed
The preprocessing stage standardizes and cleans the raw data before analysis:
- parsing and validating datetime fields,
- handling missing and inconsistent values,
- numeric type enforcement for analytics stability,
- duplicate reduction based on key identifiers,
- generation of derived columns such as total open interest and total volume.

### C. Feature Engineering
Financially meaningful features were added to improve model quality and interpretability:
- put-call ratio (PCR)-based indicators,
- moneyness and time-to-expiry transformations,
- implied volatility (Black-Scholes based estimation),
- option Greeks (Delta, Gamma, Theta, Vega),
- open-interest and volume change metrics.

## III. Proposed Approach and Methodology
CodeForge follows a modular architecture in which each stage performs a clear function.

### A. System Architecture
1. Ingestion Layer: Loads and consolidates options data files.
2. Preprocessing Layer: Cleans, aligns, and enriches the dataset.
3. Feature Layer: Computes options-specific quantitative features.
4. Analytics Layer: Runs anomaly and spike detection algorithms.
5. Visualization Layer: Produces interactive analytical charts.
6. Serving Layer: Delivers outputs through dashboard and REST APIs.

### B. Data Processing Pipeline
The processing flow is implemented as reusable Python modules:
- `src/data_loader.py`
- `src/preprocessing.py`
- `src/feature_engineering.py`
- `src/analytics.py`
- `src/visualizations.py`

### C. AI/ML Method
An unsupervised **Isolation Forest** model is used to identify unusual observations from multi-feature options data. Inputs include premium, volume, OI, and derived aggregate features. The model produces:
- anomaly labels,
- anomaly scores,
- ranked lists of suspicious market states.

Complementary statistical detectors (z-score based) are used for volume spikes and unusual OI behavior.

## IV. Uniqueness and Innovation
The proposed solution offers the following unique contributions:
- integration of domain-specific options features with unsupervised ML,
- hybrid analytics strategy (model-based + rule-based detectors),
- dual-serving design that supports both interactive dashboards and API clients,
- modular engineering that enables easy replacement or extension of components.

Unlike generic anomaly pipelines, CodeForge is tailored to options microstructure and therefore better aligned with practical market analysis workflows.

## V. Implementation Details
### A. Technology Stack
- Python
- Pandas, NumPy
- Scikit-learn
- DuckDB
- Plotly
- Streamlit
- FastAPI, Uvicorn

### B. Core Components
- `api.py`: REST endpoints for frontend integration.
- `app.py`: Streamlit dashboard for interactive analytics.
- `config.py`: configuration constants and thresholds.
- `src/*`: modular implementation of pipeline stages.

### C. Algorithms Implemented
- Isolation Forest for anomaly detection.
- Z-score detector for abnormal volume events.
- Z-score detector for unusual OI changes.
- Black-Scholes iterative implied volatility estimation.

### D. Platform Demonstration
The working platform includes:
- strike-level OI/volume visualization,
- volatility smile and sentiment trends,
- anomaly tables with ranked scores,
- API outputs consumable by React frontend.

## VI. Results and Observations
The system was evaluated on the combined multi-day options dataset and produced the following outcomes:
- successful end-to-end data processing and feature computation,
- robust anomaly detection with meaningful separation behavior,
- interpretable market snapshots from PCR, OI, and volume analytics,
- practical integration readiness through documented REST endpoints.

The analytics outputs consistently highlighted periods of unusual activity, offering useful signals for deeper review.

## VII. Discussion
### A. Interpretation
The model and analytics stack can effectively expose atypical market behavior and structural shifts in strike participation. The combined use of financial features and unsupervised ML improves detection quality over naive threshold-only approaches.

### B. Limitations
- no labeled anomaly ground truth for supervised evaluation,
- parameter sensitivity in contamination and threshold settings,
- batch processing orientation rather than true stream processing,
- model persistence not yet fully automated in the baseline workflow.

### C. Improvement Opportunities
- add model versioning and persistence workflows,
- introduce adaptive thresholds by volatility regime,
- integrate near real-time ingestion and alerting,
- add explainability for anomaly contributors.

## VIII. Conclusion and Future Work
This report presented CodeForge, a complete options analytics platform that transforms raw market data into actionable insights through preprocessing, financial feature engineering, machine learning, and visual analytics. The implementation demonstrates strong practical utility and clean system modularity for further expansion.

Future work will focus on real-time analytics, automated retraining, explainable anomaly diagnostics, and broader multi-asset support.

## IX. References
[1] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," *Proceedings of the 2008 IEEE International Conference on Data Mining*, 2008.  
[2] Scikit-learn Documentation, "IsolationForest," Available: https://scikit-learn.org/  
[3] FastAPI Documentation, Available: https://fastapi.tiangolo.com/  
[4] Plotly Python Documentation, Available: https://plotly.com/python/  
[5] Streamlit Documentation, Available: https://docs.streamlit.io/  
[6] DuckDB Documentation, Available: https://duckdb.org/docs/  
[7] J. C. Hull, *Options, Futures, and Other Derivatives*, 10th ed., Pearson, 2017.
