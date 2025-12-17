🧬 3D In-Vitro Lead Intelligence Agent

An AI-assisted decision intelligence pipeline that identifies, enriches, and prioritizes adoption-ready stakeholders for 3D in-vitro models used in toxicology and drug discovery.
The system combines scientific signals, business context, and ML-assisted ranking to help teams decide who to engage, why they matter, and why now.

📊 Live Demo

Interactive Streamlit dashboard demonstrating persona-driven lead identification and prioritization:

👉 http://localhost:8501/

🏛️ High-Level Architecture

The application follows an agent-style pipeline, orchestrated within the Streamlit app:

User Inputs (Persona + Scientific Context)
        ↓
Identification Layer
  • LinkedIn-like professional discovery (Mock API)
  • Scientific signal discovery (Real PubMed API)
        ↓
Enrichment Layer
  • Funding stage & budget readiness (Mock API)
  • Location & hub intelligence
        ↓
Decision Intelligence Engine
  • Feature engineering
  • ML-assisted propensity scoring (Random Forest)
  • Business rule interpretation
        ↓
Ranked Dashboard Output
  • Fit classification
  • Recommended outreach action


The pipeline executes each time the user runs the Data Pipeline from the UI.

🔄 Pipeline Stages
Stage 1: Identification

The agent identifies relevant professionals based on:

Role persona (e.g., Director of Toxicology, Head of Preclinical Safety)

Scientific context (e.g., DILI, hepatic models, organ-on-chip)

Sources:

Mocked professional network API (LinkedIn / Xing equivalent)

Real PubMed (NCBI E-utilities) API for recent publications

Stage 2: Enrichment

Each identified profile is enriched with:

Company funding stage (Series A/B, Seed, Public, etc.)

Budget readiness inference

Geographic context (HQ vs remote, major biotech hubs)

This layer converts raw profiles into commercially interpretable entities.

Stage 3: Decision Intelligence & Ranking

The enriched leads are passed through a decision intelligence engine that:

Performs feature engineering (seniority, funding, hub presence)

Uses a Random Forest classifier to estimate adoption propensity

Translates scores into human-readable insights

Outputs include:

Propensity to Collaborate (%)

Scientific + Business Fit (High / Medium / Low)

Recommended Action

High Priority Outreach

Warm Lead

Monitor

This ensures the output is actionable, not just ranked.

🧠 Key Design Decisions & Problems Addressed
1️⃣ Explainability over Black-Box ML

Problem: Pure ML scoring is difficult for BD teams to trust.
Solution: ML is used to assist ranking, while business rules clearly interpret outcomes into fit levels and actions.

2️⃣ Compliance-Aware Data Strategy

Problem: Scraping platforms like LinkedIn violates ToS and is unreliable.
Solution: Proprietary sources are abstracted via mocked APIs, while PubMed is accessed through its official public API, preserving a production-ready architecture without compliance risk.

3️⃣ Timing-Aware Lead Prioritization

Problem: Relevance alone does not indicate urgency or readiness.
Solution: The system explicitly surfaces:

Recent scientific activity

Funding recency

Decision-making seniority

This aligns ranking with budget timing and adoption readiness.

4️⃣ Persona-Driven Decision Context

Problem: Different stakeholders prioritize different signals.
Solution: The agent accepts persona and scientific context as first-class inputs, enabling scenario-specific prioritization.

📈 Output & Usability

The final dashboard provides:

Ranked, searchable lead list

Clear prioritization logic

Export-ready structure for downstream workflows

The system is designed to support real BD decision-making, not just data exploration.

🛠️ Tech Stack

Python

Streamlit – interactive UI & orchestration

scikit-learn – Random Forest classifier

Pandas / NumPy – data processing

Requests + XML parsing – PubMed API integration

📂 Repository Structure
.
├── app.py              # Streamlit app & pipeline orchestration
├── data_sources.py     # Mock APIs + PubMed integration
├── requirements.txt
└── README.md

🔧 Local Setup

Clone the repository and create a virtual environment:

git clone <repo-url>
cd 3d-invitro-lead-intelligence
python -m venv .venu
source .venu/bin/activate  # Windows: .venu\Scripts\activate
pip install -r requirements.txt
streamlit run app.py


No API keys are required.

📡 Compliance & Ethics

No LinkedIn scraping

No ToS-violating data collection

PubMed accessed via official public API

Proprietary data abstracted responsibly

🔮 Future Extensions

Persistent storage for historical runs

Explainable per-lead score breakdown

Integration with licensed data providers

Multi-persona weighting strategies

✅ Summary

This project demonstrates how AI-assisted decision intelligence can be applied to the 3D in-vitro and predictive toxicology domain, combining scientific relevance, business readiness, and explainable prioritization into a practical, production-minded tool.
