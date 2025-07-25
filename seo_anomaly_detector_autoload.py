
import pandas as pd

def load_datasets(ga_path, gsc_path, crawl_path):
    ga = pd.read_excel(ga_path)
    gsc = pd.read_excel(gsc_path)
    crawl = pd.read_excel(crawl_path)
    return ga, gsc, crawl

def detect_anomalies(ga_df, gsc_df, crawl_df):
    anomalies = []

    # Normalize column names for joining
    crawl_df = crawl_df.rename(columns={'Address': 'URL'})
    ga_df = ga_df.rename(columns={ga_df.columns[0]: 'URL'})
    gsc_df = gsc_df.rename(columns={gsc_df.columns[0]: 'URL'})

    # Merge everything on URL
    df = crawl_df.merge(ga_df, on='URL', how='left').merge(gsc_df, on='URL', how='left')

    for _, row in df.iterrows():
        issues = []
        url = row['URL']

        # Status code changes
        if row.get('Status Code') not in [200, 301, 302]:
            issues.append("Non-200/3xx status")

        # Indexability issues
        if row.get('Indexability') not in ["Indexable", "Canonical"]:
            issues.append("Not indexable")

        # Crawl depth
        if pd.notna(row.get('Crawl Depth')) and row['Crawl Depth'] > 4:
            issues.append("High crawl depth")

        # Low word count
        if pd.notna(row.get('Word Count')) and row['Word Count'] < 300:
            issues.append("Thin content")

        # Performance issues
        if pd.notna(row.get('Performance Score')) and row['Performance Score'] < 50:
            issues.append("Low performance score")

        # GSC anomalies
        if pd.notna(row.get('CTR')) and row['CTR'] < 0.5:
            issues.append("Low CTR")
        if pd.notna(row.get('Position')) and row['Position'] > 20:
            issues.append("Poor average position")

        # GA anomalies
        if pd.notna(row.get('GA4 Engagement rate')) and row['GA4 Engagement rate'] < 0.3:
            issues.append("Low engagement rate")

        # OpenAI scoring
        if pd.notna(row.get('OpenAI: 1')) and row['OpenAI: 1'] < 0.5:
            issues.append("Low OpenAI EEAT score")

        if issues:
            anomalies.append({
                "URL": url,
                "Issues": ", ".join(issues),
                "Severity": len(issues)
            })

    return pd.DataFrame(anomalies)

def main():
    ga_path = "analytics_all.xlsx"
    gsc_path = "search_console_all.xlsx"
    crawl_path = "internal_all.xlsx"

    ga, gsc, crawl = load_datasets(ga_path, gsc_path, crawl_path)
    anomalies = detect_anomalies(ga, gsc, crawl)
    anomalies.to_csv("weekly_anomalies_report.csv", index=False)
    print("Anomaly report saved as weekly_anomalies_report.csv")

if __name__ == "__main__":
    main()
