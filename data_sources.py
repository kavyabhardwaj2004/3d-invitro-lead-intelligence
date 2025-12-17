import requests
import xml.etree.ElementTree as ET
import random
import time


# linkedin mock api for generating 40+ leads
def linkedin_search_api(job_titles, locations, count=40):
    """
    Simulates LinkedIn API by returning a mix of fixed 'Golden' profiles
    and synthetically generated realistic profiles to fill the table.
    """

    # A. The "Golden" Profiles (From your PDF personas)
    fixed_profiles = [
        {"name": "Dr. Emily Ross", "title": "Director of Toxicology", "company": "NeoLiver Bio",
         "location": "Boston, MA", "hq": "Cambridge, MA", "source": "LinkedIn", "seniority": "Director"},
        {"name": "Dr. Alex Morgan", "title": "Senior Scientist – Safety", "company": "HepatoTech",
         "location": "Remote – Texas", "hq": "San Diego, CA", "source": "LinkedIn", "seniority": "Senior"},
        {"name": "Sarah Jenkins", "title": "VP of Preclinical Safety", "company": "BioTox Solutions",
         "location": "Basel, Switzerland", "hq": "Basel, Switzerland", "source": "Xing", "seniority": "VP"},
    ]

    # B. The Generators (To create volume)
    first_names = ["James", "Robert", "Michael", "David", "Jennifer", "Linda", "Elizabeth", "Barbara", "William",
                   "Susan", "Thomas", "Jessica", "Lisa", "Karen", "Andrew", "Matthew"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
                  "Anderson", "Thomas", "Jackson", "White"]

    pharma_cos = ["Amgen", "Gilead", "Vertex", "Regeneron", "Moderna", "Biogen", "Sanofi", "Pfizer", "Merck", "Takeda",
                  "AstraZeneca", "Novartis", "Roche", "Bayer", "GSK", "AbbVie"]
    biotech_startups = ["CellModel", "LiverChip", "OrganoVir", "ToxScreen", "HepaGlobal", "3DTissue", "VivoLogic",
                        "SafetyFirst Bio"]

    roles = ["Director of Toxicology", "Head of Safety Assessment", "Principal Investigator", "Senior Scientist",
             "VP of R&D", "Research Scientist", "Scientific Director"]
    hubs = ["Boston, MA", "Cambridge, MA", "San Francisco, CA", "San Diego, CA", "London, UK", "Basel, CH",
            "Research Triangle, NC"]

    # Generate needed profiles
    generated = []
    needed = count - len(fixed_profiles)

    for i in range(needed):
        company_type = "Pharma" if random.random() > 0.4 else "StartUp"
        comp = random.choice(pharma_cos) if company_type == "Pharma" else random.choice(biotech_startups)

        loc = random.choice(hubs)
        is_remote = random.choice([True, False])

        person_loc = f"Remote ({random.choice(['TX', 'FL', 'CO', 'AZ'])})" if is_remote else loc

        profile = {
            "name": f"Dr. {random.choice(first_names)} {random.choice(last_names)}",
            "title": random.choice(roles),
            "company": comp,
            "location": person_loc,
            "hq": loc,
            "source": "LinkedIn",
            "seniority": "Director" if "Director" in roles else "Scientist"
        }
        generated.append(profile)

    return fixed_profiles + generated


# ========================================================
# 2. FUNDING MOCK API
# ========================================================
def funding_intelligence_api(company_name):
    """
    Randomly assigns realistic funding statuses to unknown companies.
    """
    known_db = {
        "NeoLiver Bio": {"stage": "Series B", "status": "Funded"},
        "HepatoTech": {"stage": "Seed", "status": "Bootstrapped"},
    }

    if company_name in known_db:
        return known_db[company_name]

    # For generated companies, assign random plausible status
    stages = ["Series A", "Series B", "IPO", "Public", "Seed", "Grant Funded"]
    chosen_stage = random.choice(stages)

    return {
        "stage": chosen_stage,
        "status": "Cash Ready" if chosen_stage in ["Series A", "Series B", "IPO", "Public"] else "Limited Budget"
    }
# ========================================================
# 3. REAL PUBMED API (NCBI E-UTILITIES)
# ========================================================
def pubmed_author_api(keywords, max_months=12):
    """
    REAL API: finding keywords within 12 months
    Returns the Corresponding Authors (Sales Leads).

    API Used: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
    Dependencies: requests
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    tool_name = "lead_gen_bot"
    email = "demo@example.com"  # required NCBI email for good etiqueets

    # (esearch) to get List of IDs
    term = f"({keywords}) AND (\"last {max_months} months\"[dp])"
    search_params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": 5,  # Limit to 5 for speed in this demo
        "tool": tool_name,
        "email": email
    }

    try:
        search_resp = requests.get(f"{base_url}esearch.fcgi", params=search_params)
        search_data = search_resp.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return []

        # 2. Fetch Details (efetch) for those IDs
        # ---------------------------------------
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "tool": tool_name,
            "email": email
        }

        fetch_resp = requests.get(f"{base_url}efetch.fcgi", params=fetch_params)

        # 3. Parse XML to Extract Authors (Leads)
        # ---------------------------------------
        root = ET.fromstring(fetch_resp.content)
        leads = []

        for article in root.findall(".//PubmedArticle"):
            try:
                title = article.find(".//ArticleTitle").text
                journal = article.find(".//Journal/Title").text

                # In Sci-sales, the LAST author is usually the Senior PI (Budget Holder)
                # The FIRST author is usually the user (Influencer)
                author_list = article.findall(".//AuthorList/Author")

                if author_list:
                    # let's grab the Last Author (likely PI)
                    last_author = author_list[-1]
                    last_name = last_author.find("LastName").text if last_author.find("LastName") is not None else ""
                    fore_name = last_author.find("ForeName").text if last_author.find("ForeName") is not None else ""

                    # Try to find affiliation (Organization/Location)
                    affiliation = "Unknown"
                    aff_node = last_author.find(".//Affiliation")
                    if aff_node is not None:
                        affiliation = aff_node.text

                    leads.append({
                        "source": "PubMed",
                        "name": f"{fore_name} {last_name}",
                        "paper_title": title[:50] + "...",
                        "journal": journal,
                        "affiliation": affiliation,
                        "role_inference": "Likely PI / Budget Holder",
                        "relevance": "High (Published recently)"
                    })
            except Exception as e:
                continue

        return leads

    except Exception as e:
        print(f"API Connection Error: {e}")
        return []
# TESTER (Uncomment to verify in console)

if __name__ == "__main__":
    print("--- Testing LinkedIn API ---")
    print(linkedin_search_api(None, None)[0])

    print("\n--- Testing Funding API ---")
    print(funding_intelligence_api("NeoLiver Bio"))

    print("\n---Testing REAL PubMed API---")
    real_leads = pubmed_author_api("drug induced liver injury", max_months=6)
    for lead in real_leads:
        print(f"Found Author: {lead['name']} | Affiliation: {lead['affiliation'][:30]}...")