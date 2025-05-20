import streamlit as st
import pandas as pd
import requests
import tldextract
from time import sleep
import io

st.set_page_config(page_title="Annual Report Finder", layout="centered")
st.title("📊 Annual Report / Investor Relations Finder")

# Sidebar for API input
st.sidebar.header("🔐 API Configuration")
api_key = st.sidebar.text_input("Google API Key", type="password")
cx_id = st.sidebar.text_input("Search Engine ID (CX)")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV file with a 'Company Name' column", type=["csv"])

if uploaded_file and api_key and cx_id:
    df = pd.read_excel(uploaded_file)
    if 'Company Name' not in df.columns:
        st.error("The uploaded CSV must have a 'Company Name' column.")
    else:
        st.success("File loaded successfully. Ready to search!")

        if st.button("🔍 Start Searching"):
            results = []
            progress = st.progress(0)

            for i, company in enumerate(df['Company Name']):
                query = f"{company} investor relations OR annual report"
                url = f"https://www.googleapis.com/customsearch/v1?q={requests.utils.quote(query)}&key={api_key}&cx={cx_id}"

                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    items = data.get('items', [])

                    if items:
                        top_result = items[0]
                        link = top_result['link']
                        domain = tldextract.extract(link).registered_domain
                        results.append({
                            'Company Name': company,
                            'URL': link,
                            'Domain': domain,
                            'Status': 'Found'
                        })
                    else:
                        results.append({'Company Name': company, 'URL': '', 'Domain': '', 'Status': 'Not Found'})

                except Exception as e:
                    results.append({'Company Name': company, 'URL': '', 'Domain': '', 'Status': f'Error: {str(e)}'})

                progress.progress((i + 1) / len(df))
                sleep(1)  # Avoid API rate limits

            results_df = pd.DataFrame(results)
            st.success("✅ Search complete!")
            st.dataframe(results_df)

            # Download button
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_buffer.getvalue(),
                file_name="annual_report_results.csv",
                mime="text/csv"
            )
else:
    st.info("Please upload a CSV file and provide your API credentials to continue.")
