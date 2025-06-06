import pandas as pd
import glob

# Finding all stats CSV files for all the tests
csv_files = glob.glob("*_stats.csv")
summary_data = []

for file in csv_files:
    df = pd.read_csv(file)
    test_name = file.replace("_stats.csv", "")
    
    # Extracting the aggregated metrics
    agg_row = df[df["Name"] == "Aggregated"].iloc[0]
    total_requests = agg_row["Request Count"]
    total_failures = agg_row["Failure Count"]
    error_rate = (total_failures / total_requests) * 100 if total_requests > 0 else 0

    metrics = {
        "Test": test_name,
        "Total Requests": total_requests,
        "RPS": agg_row["Requests/s"],
        "Avg Latency (ms)": agg_row["Average Response Time"],
        "p50 Latency (ms)": agg_row["50%"],
        "p75 Latency (ms)": agg_row["75%"],
        "p95 Latency (ms)": agg_row["95%"],
        "Error Rate (%)": error_rate
    }

    # Extracting language-specific p95 latency
    languages = ["Hi", "Ta", "Bn"]  # Hindi, Tamil, Bengali
    for lang in languages:
        lang_row = df[df["Name"] == f"Transliterate {lang}"]
        if not lang_row.empty:
            metrics[f"{lang.capitalize()} p95 Latency (ms)"] = lang_row["95%"].iloc[0]
        else:
            metrics[f"{lang.capitalize()} p95 Latency (ms)"] = None

    summary_data.append(metrics)

# Saving to summary.csv
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv("summary.csv", index=False)
print("Summary saved to summary.csv")
