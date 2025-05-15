import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from serpapi import GoogleSearch

st.title("Company Annual Report Finder (with SerpAPI)")

SERPAPI_API_KEY = st.text_input("Enter your SerpAPI API Key", type="password")

uploaded_file = st.file_uploader("Upload CSV with company names (one per line)", type=["csv", "txt"])

def get_official_website(company_name, api_key):
    params = {
        "engine": "google",
        "q": f"{company_name} official website",
        "api_key": api_key,
        "num": 1,
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        if organic_results:
            return organic_results[0].get("link")
    except Exception as e:
        return None
    return None

def find_annual_report_link(website_url):
    try:
        resp = requests.get(website_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            text = a.get_text(strip=True).lower()
            if any(keyword in href or keyword in text for keyword in ['annual-report', 'investor', 'financials', 'reports', 'fund']):
                full_url = href if href.startswith('http') else website_url.rstrip('/') + '/' + href.lstrip('/')
                return full_url
        return "Not found"
    except Exception:
        return "Error fetching site"

if uploaded_file and SERPAPI_API_KEY:
    companies = pd.read_csv(uploaded_file, header=None).iloc[:, 0].tolist()
    st.write(f"Loaded {len(companies)} companies")

    results = []
    progress = st.progress(0)

    for idx, company in enumerate(companies):
        st.write(f"🔎 Processing: {company}")
        official_website = get_official_website(company, SERPAPI_API_KEY)
        annual_report_url = find_annual_report_link(official_website) if official_website else "Not found"

        results.append({
            'Company': company,
            'Official Website': official_website or "Not found",
            'Annual Report URL': annual_report_url
        })

        progress.progress((idx + 1) / len(companies))
        time.sleep(1)

    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results as CSV", csv, "annual_reports.csv", "text/csv")

else:
    st.info("Please enter your SerpAPI key and upload a company list.")
