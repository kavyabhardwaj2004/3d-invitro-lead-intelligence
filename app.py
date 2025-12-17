import streamlit as st
import pandas as pd
import time
import random
#importing ml libraries
from sklearn.ensemble import RandomForestClassifier
import numpy as np
# connecting our data_source.py
from data_sources import linkedin_search_api, funding_intelligence_api

# basic page styling
st.set_page_config(page_title="Bio-Tech Lead Gen Agent", page_icon="🧬", layout="wide")

# custom styling for left frame buttons
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 2. MACHINE LEARNING ENGINE
# ==========================================

def run_ml_ranking(leads_df):
    """
    Train a Random Forest model on 'History' to predict score for new leads.
    """
    # 1. Mock Training Data (History of who bought)
    training_data = [
        {"role_seniority": "VP", "funding": "Series A", "hq_hub": 1, "target": 1},
        {"role_seniority": "Director", "funding": "Series B", "hq_hub": 1, "target": 1},
        {"role_seniority": "Director", "funding": "Public", "hq_hub": 0, "target": 1},
        {"role_seniority": "Senior", "funding": "Series A", "hq_hub": 1, "target": 1},
        {"role_seniority": "Scientist", "funding": "Seed", "hq_hub": 0, "target": 0},
        {"role_seniority": "Junior", "funding": "Grant Funded", "hq_hub": 1, "target": 0},
        {"role_seniority": "Scientist", "funding": "Public", "hq_hub": 0, "target": 0},
    ]

    # 2. Feature Engineering for Current List
    leads_df['hq_hub'] = leads_df['hq'].apply(
        lambda x: 1 if any(h in x for h in ['Cambridge', 'Boston', 'Basel', 'San Fran']) else 0)

    # 3. Numeric Encoding Helper Functions
    def get_role_score(title):
        title = title.lower()
        if "vp" in title or "head" in title: return 3
        if "director" in title or "principal" in title: return 2
        return 1

    def get_fund_score(stage):
        if stage in ["Series A", "Series B", "IPO", "Public"]: return 3
        if stage == "Seed": return 2
        return 1

    # 4. Prepare Feature Matrix
    X_pred = pd.DataFrame()
    X_pred['role_score'] = leads_df['title'].apply(get_role_score)
    X_pred['fund_score'] = leads_df['funding_stage'].apply(get_fund_score)
    X_pred['hub'] = leads_df['hq_hub']

    X_train = np.array([
        [3, 3, 1], [2, 3, 1], [2, 3, 0], [2, 3, 1],
        [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 1, 0]
    ])
    y_train = [1, 1, 1, 1, 0, 0, 0, 0]

    # 5. Train & Predict
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    probs = clf.predict_proba(X_pred)[:, 1]
    return probs * 100
def assign_fit_category(score):
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"

def recommend_action(score):
    if score >= 80:
        return "High Priority Outreach"
    elif score >= 60:
        return "Warm Lead"
    else:
        return "Monitor"
def recent_publication_flag(science_context):
    high_intent_topics = [
        "drug induced liver injury",
        "hepatic",
        "organ-on-chip",
        "predictive toxicology",
        "NASH"
    ]

    return "Yes (≤12 months)" if any(k.lower() in science_context.lower() for k in high_intent_topics) else "No"


# UI Layer(side bar)
# --- MAIN TITLE ---
st.title("🧬 AI Lead Agent: 3D In-Vitro Market")
st.markdown(
    "**Decision intelligence engine** combining scientific signals, business context, "
    "and ML-assisted ranking to prioritize 3D in-vitro adoption."
)

# side bar inputs with possible related keywords
with st.sidebar:
    st.header("Agent Inputs")

    # UPGRADED: Dropdown for Roles
    role_input = st.selectbox(
        "Role Persona",
        [
            "Director of Toxicology",
            "Head of Preclinical Safety",
            "VP of In Vitro Biology",
            "Principal Investigator",
            "Chief Scientific Officer"
        ]
    )

    # Dropdown for scientific content
    science_input = st.selectbox(
        "Scientific Context",
        [
            "drug induced liver injury",
            "organ-on-chip",
            "hepatic spheroids",
            "predictive toxicology",
            "NASH / liver fibrosis",
            "cardiotoxicity"
        ]
    )

    st.divider()

    launch_btn = st.button("🚀 Run Data Pipeline")

    st.caption("Config: RandomForest / Hybrid-Search")

# --- MAIN LOGIC ---
if launch_btn:
    # proper loading logic for each stage starting from loading linkedin.....to.....re-ranking using ML model
    status_box = st.info(f"🕷️ API Handshake - Querying LinkedIn for '{role_input}'...")
    progress_bar = st.progress(0)

    # 1. generate/crawl (40+ profiles)
    leads = linkedin_search_api([], [], count=45)
    progress_bar.progress(35)
    time.sleep(0.5)

    # 2. ENRICH (Funding Data)
    status_box.info("🌍 Enrichment - Querying Capital IQ / Crunchbase Mock API...")
    df = pd.DataFrame(leads)
    df['funding_stage'] = df['company'].apply(lambda x: funding_intelligence_api(x)['stage'])
    progress_bar.progress(70)
    time.sleep(0.5)

    # 3. ML SCORING (Random Forest)
    status_box.info("🧮 Scoring Leads based on 'Propensity to Buy' Machine Learning Model...")
    df['ml_score'] = run_ml_ranking(df)

    df['Scientific + Business Fit'] = df['ml_score'].apply(assign_fit_category)
    df['Recommended Action'] = df['ml_score'].apply(recommend_action)

    df = df.sort_values(by='ml_score', ascending=False)
    df['Recent Publication'] = recent_publication_flag(science_input)

    progress_bar.progress(100)
    status_box.success("✅ Pipeline Complete. ML Model has re-ranked the prospect list.")

    # --- METRICS DISPLAY ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Prospects", len(df))
    c2.metric("Hot Leads (>80%)", len(df[df['ml_score'] > 80]))
    c3.metric("Funding Qualified", len(df[df['funding_stage'].isin(['Series A', 'Series B', 'IPO'])]))

    # --- DATAFRAME ---
    st.subheader(f"Ranked Leads for: {role_input}")
    st.dataframe(
        df[['ml_score', 'Scientific + Business Fit', 'Recommended Action',
            'name', 'title', 'company', 'location', 'funding_stage', 'hq']],
        column_config={
            "ml_score": st.column_config.ProgressColumn(
                "Propensity to Collaborate (%)",
                help="Combined scientific relevance and commercial readiness score",
                min_value=0,
                max_value=100
            ),
            "Scientific + Business Fit": "Fit Level",
            "Recommended Action": "BD Recommendation",
            "location": "Person Location",
            "hq": "Company HQ"
        },
        use_container_width=True,
        height=700
    )


else:
    # Landing State (Instructions)
    st.markdown("### Waiting for Input...")
    st.write("Choose a target persona and scientific focus to activate the lead intelligence engine 🚀🧠")