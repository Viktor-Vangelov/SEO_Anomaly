
import streamlit as st
import pandas as pd

st.set_page_config(page_title="SEO Anomaly Detector", layout="wide")

st.title("🔍 Weekly SEO Anomaly Detector")
st.markdown("Upload your Screaming Frog/Lumar crawl, GA4, and GSC exports to detect weekly anomalies.")

# Upload files
crawl_file = st.file_uploader("📂 Upload Crawl Data (.xlsx)", type="xlsx")
ga_file = st.file_uploader("📈 Upload GA4 Data (.xlsx)", type="xlsx")
gsc_file = st.file_uploader("🔍 Upload GSC Data (.xlsx)", type="xlsx")

if crawl_file and ga_file and gsc_file:
    # Load data
    crawl_df = pd.read_excel(crawl_file)
    ga_df = pd.read_excel(ga_file)
    gsc_df = pd.read_excel(gsc_file)

    crawl_df = crawl_df.rename(columns={'Address': 'URL'})
    ga_df = ga_df.rename(columns={ga_df.columns[0]: 'URL'})
    gsc_df = gsc_df.rename(columns={gsc_df.columns[0]: 'URL'})

    # Merge
    df = crawl_df.merge(ga_df, on='URL', how='left').merge(gsc_df, on='URL', how='left')

    st.subheader("🧠 Anomaly Report")
    anomalies = []

    for _, row in df.iterrows():
        url = row['URL']
        issues = []

        if row.get('Status Code') not in [200, 301, 302]:
            issues.append("Non-200/3xx status")

        if row.get('Indexability') not in ["Indexable", "Canonical"]:
            issues.append("Not indexable")

        if pd.notna(row.get('Crawl Depth')) and row['Crawl Depth'] > 4:
            issues.append("High crawl depth")

        if pd.notna(row.get('Word Count')) and row['Word Count'] < 300:
            issues.append("Thin content")

        if pd.notna(row.get('Performance Score')) and row['Performance Score'] < 50:
            issues.append("Low performance score")

        if pd.notna(row.get('CTR')) and row['CTR'] < 0.5:
            issues.append("Low CTR")

        if pd.notna(row.get('Position')) and row['Position'] > 20:
            issues.append("Poor average position")

        if pd.notna(row.get('GA4 Engagement rate')) and row['GA4 Engagement rate'] < 0.3:
            issues.append("Low engagement rate")

        if 'OpenAI: 1' in df.columns:
            val = row.get('OpenAI: 1')
                if pd.notna(val) and isinstance(val, (int, float)) and val < 0.5:
                    issues.append("Low OpenAI EEAT score")

        if issues:
            anomalies.append({
                "URL": url,
                "Issues": ", ".join(issues),
                "Severity": len(issues)
            })

    anomaly_df = pd.DataFrame(anomalies)
    st.write(anomaly_df)

    csv = anomaly_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Anomaly Report", csv, "weekly_anomalies_report.csv", "text/csv")
