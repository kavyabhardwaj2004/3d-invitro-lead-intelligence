import streamlit as st
import pandas as pd
import time
import random
# importing ml libraries
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from data_sources import linkedin_search_api, funding_intelligence_api, pubmed_author_api

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
    # Handle NaN values in HQ to prevent errors
    leads_df['hq'] = leads_df['hq'].fillna("Unknown")

    leads_df['hq_hub'] = leads_df['hq'].apply(
        lambda x: 1 if any(h in str(x) for h in ['Cambridge', 'Boston', 'Basel', 'San Fran']) else 0)

    # 3. Numeric Encoding Helper Functions
    def get_role_score(title):
        title = str(title).lower()
        if "vp" in title or "head" in title or "chief" in title: return 3
        # Added 'principal' (PI) and 'investigator' to high value roles
        if "director" in title or "principal" in title or "investigator" in title: return 2
        return 1

    def get_fund_score(stage):
        if stage in ["Series A", "Series B", "IPO", "Public"]: return 3
        if stage == "Seed": return 2
        return 1

    # 4. Prepare Feature Matrix
    X_pred = pd.DataFrame()
    X_pred['role_score'] = leads_df['title'].apply(get_role_score)
    X_pred['funding_stage'] = leads_df['funding_stage'].fillna("Unknown")  # handle missing funding
    X_pred['fund_score'] = X_pred['funding_stage'].apply(get_fund_score)
    X_pred['hub'] = leads_df['hq_hub']

    # Training Data (Mock)
    X_train = np.array([
        [3, 3, 1], [2, 3, 1], [2, 3, 0], [2, 3, 1],
        [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 1, 0]
    ])
    y_train = [1, 1, 1, 1, 0, 0, 0, 0]

    # 5. Train & Predict
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Extract features for prediction
    features = X_pred[['role_score', 'fund_score', 'hub']].values

    probs = clf.predict_proba(features)[:, 1]
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


def recent_publication_flag(row, keyword):
    """
    Checks if the source is PubMed OR if the keyword matches context.
    """
    # If it came from the PubMed API, it's definitely a recent publication
    if row.get('source') == "PubMed":
        return "YES (Verified Source)"

    # Fallback for LinkedIn leads (mock logic)
    high_intent_topics = ["drug induced liver injury", "hepatic", "organ-on-chip", "NASH"]
    return "Yes (≤12 months)" if any(k.lower() in keyword.lower() for k in high_intent_topics) else "No"


# UI Layer (side bar)
st.title("🧬 AI Lead Agent: 3D In-Vitro Market")
st.markdown(
    "**Decision intelligence engine** combining scientific signals (PubMed), business context (LinkedIn/Crunchbase), "
    "and ML-assisted ranking."
)

with st.sidebar:
    st.header("Agent Inputs")

    role_input = st.selectbox(
        "Role Persona",
        ["Director of Toxicology", "Head of Preclinical Safety", "VP of In Vitro Biology", "Principal Investigator",
         "Chief Scientific Officer"]
    )

    science_input = st.selectbox(
        "Scientific Context",
        ["drug induced liver injury", "organ-on-chip", "hepatic spheroids", "predictive toxicology",
         "NASH / liver fibrosis", "cardiotoxicity"]
    )

    st.divider()
    launch_btn = st.button("🚀 Run Data Pipeline")
    st.caption("Sources: LinkedIn API, PubMed (E-Utils), CapitalIQ")

# --- MAIN LOGIC ---
if launch_btn:
    status_box = st.info(f"🕷️ API Handshake - Querying LinkedIn for '{role_input}'...")
    progress_bar = st.progress(0)

    # 1. LINKEDIN CRAWL
    leads_linkedin = linkedin_search_api([], [], count=25)
    progress_bar.progress(20)
    time.sleep(0.5)

    # PUBMED API INTEGRATION
    status_box.info(f"📚 Science Signal - Querying PubMed for authors publishing on '{science_input}'...")
    pubmed_raw = pubmed_author_api(science_input, max_months=12)

    # Normalize PubMed data to match LinkedIn schema for the DataFrame
    leads_pubmed = []
    for p in pubmed_raw:
        # Extract the first part of affiliation as Company/University
        aff = p.get('affiliation', 'Unknown Institute')
        company_name = aff.split(',')[0] if aff else "Unknown Institute"

        leads_pubmed.append({
            "name": p['name'],
            "title": "Principal Investigator (Author)",  # Map author to a job title
            "company": company_name,
            "location": "Global / Academic",
            "hq": "Unknown",  # Academic HQs are harder to parse
            "source": "PubMed",
            "funding_stage": "Grant Funded"  # Academic/Research leads are usually grant funded
        })

    progress_bar.progress(50)
    time.sleep(0.5)

    # 3. MERGE DATA
    status_box.info("🔄 Merging Business & Scientific Datasets...")
    all_leads = leads_linkedin + leads_pubmed
    df = pd.DataFrame(all_leads)

    # 4. ENRICH (Funding Data)
    # Only run enrichment on rows that don't have funding_stage yet (LinkedIn ones)
    status_box.info("🌍 Enrichment - Querying Capital IQ / Crunchbase Mock API...")


    def enrich_wrapper(row):
        if 'funding_stage' in row and row['funding_stage']:
            return row['funding_stage']
        return funding_intelligence_api(row['company'])['stage']


    df['funding_stage'] = df.apply(enrich_wrapper, axis=1)
    progress_bar.progress(75)

    # 5. ML SCORING
    status_box.info("🧮 Scoring Leads based on 'Propensity to Buy' ML Model...")
    df['ml_score'] = run_ml_ranking(df)

    df['Scientific + Business Fit'] = df['ml_score'].apply(assign_fit_category)
    df['Recommended Action'] = df['ml_score'].apply(recommend_action)

    # Update Publication flag logic to handle the new PubMed data
    df['Recent Publication'] = df.apply(lambda row: recent_publication_flag(row, science_input), axis=1)

    # Sort: Highest score first
    df = df.sort_values(by='ml_score', ascending=False)

    progress_bar.progress(100)
    status_box.success(f"✅ Pipeline Complete. Found {len(df)} leads ({len(leads_pubmed)} from PubMed).")

    # --- METRICS DISPLAY ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Prospects", len(df))
    c2.metric("Hot Leads (>80%)", len(df[df['ml_score'] > 80]))
    c3.metric("PubMed Verified", len(df[df['source'] == 'PubMed']))
    c4.metric("Funding Qualified", len(df[df['funding_stage'].isin(['Series A', 'Series B', 'IPO'])]))

    # --- DATAFRAME ---
    st.subheader(f"Ranked Leads for: {role_input} + {science_input}")

    st.dataframe(
        df[['ml_score', 'source', 'name', 'title', 'company', 'Recent Publication', 'Recommended Action',
            'funding_stage']],
        column_config={
            "ml_score": st.column_config.ProgressColumn(
                "Score",
                help="Propensity to Collaborate",
                min_value=0,
                max_value=100,
                format="%.1f"
            ),
            "source": st.column_config.TextColumn("Lead Source"),
            "Recent Publication": "Active Researcher?",
        },
        use_container_width=True,
        height=700
    )

else:
    st.markdown("### Waiting for Input...")
    st.write("👈🏻 Choose a target persona and scientific focus to activate the lead intelligence engine 🚀🧠")
