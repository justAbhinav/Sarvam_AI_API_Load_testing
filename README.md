# Sarvam Transliteration API Load Testing

This repository provides a complete solution for load testing the [Sarvam Transliteration API](https://docs.sarvam.ai/api-reference-docs/text/transliterate). It includes scripts for automated load tests, a Streamlit-based dashboard for configuration and live monitoring, and tools for aggregating and analyzing results. The project is designed for both quick, simple tests and advanced, customizable load sweeps, with clear reporting and troubleshooting guidance.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [.env File Setup](#env-file-setup)
- [Running Tests](#running-tests)
- [Dashboard Features](#dashboard-features)
- [Google Sheets Report](#google-sheets-report)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

---

## Project Structure

- `API_Requests.py`: Locust script defining load test tasks for transliterating text in Hindi, Tamil, and Bengali.
- `dashboard.py`: Streamlit dashboard for configuring and running tests, displaying live metrics (latency, RPS, error rate), and showing final results with language-specific p95 latency.
- `run_tests.sh`: Bash script to perform a load sweep with varying user counts and spawn rates.
- `process_results.py`: Aggregates CSV outputs into a `summary.csv` for analysis.
- `<prefix>_stats.csv`, `<prefix>_stats_history.csv`: CSV files generated per test (e.g., `simple_test_stats.csv`).
- `summary.csv`: Aggregated results from all tests.
- `requirements.txt`: Lists all Python dependencies for the project.
- `.env`: (Optional) File for storing environment variables such as API keys.
- `Report/`: Contains the final PDF report.

---

## Requirements

All dependencies are listed in `requirements.txt`. Example contents:

```
streamlit
requests
plotly
pandas
locust
python-dotenv
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/justAbhinav/Sarvam_AI_API_Load_testing
   cd Sarvam_AI_API_Load_testing
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**

   You can set your Sarvam API key in your shell or in a `.env` file (recommended for convenience and security).

---

## .env File Setup

Create a `.env` file in the project root with the following content:

```
SARVAM_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Sarvam API key (Get it From [here](https://dashboard.sarvam.ai/)). The project uses `python-dotenv` to automatically load environment variables from this file.

Alternatively, you can export the variable in your shell:

```bash
export SARVAM_API_KEY="your_api_key_here"
```

---

## Running Tests

1. **Free Required Ports**

   The dashboard and Locust use ports `8089` and `8090`. Ensure these ports are free:

   ```bash
   lsof -i :8089
   lsof -i :8090
   kill -9 <pid>
   ```

2. **Load Sweep Tests**

   Run the load sweep to test different user counts and spawn rates:

   ```bash
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

3. **Process Results**

   Aggregate all CSV outputs into a single `summary.csv`:

   ```bash
   python3 process_results.py
   ```

4. **Run the Dashboard**

   Launch the Streamlit dashboard for interactive test configuration and live monitoring:

   ```bash
   streamlit run dashboard.py
   ```

   - Open [http://localhost:8501](http://localhost:8501) in your browser.
   - Choose "Simple" (1 user, 1 spawn rate, 1m) or "Custom" test type.
   - Configure concurrency, spawn rate, run time (e.g., `30s`), and CSV prefix as needed.
   - Click "Run Test" to view live metrics and final results.

---

## Dashboard Features

- **Test Configuration**
  - *Simple Mode*: Fixed parameters (1 user, 1 spawn rate, 1m duration, `simple_test` prefix).
  - *Custom Mode*: User-defined concurrency, spawn rate, run time, and CSV prefix.

- **Live Metrics**
  - Median, average, and p95 latency (ms)
  - Requests per second (RPS)
  - Error rate (%)

- **Final Results**
  - Total requests, RPS, average/p50/p75/p95 latency, error rate
  - Language-specific p95 latency (Hindi, Tamil, Bengali) with a bar chart

  There is a bug currently where you need to refresh the page for the final results, however all the csv files are saved in the dashboard directory correclty.

- **CSV Output**
  - Generates `<prefix>_stats.csv` and `<prefix>_stats_history.csv` per test

---

## Google Sheets Report

A detailed Google Sheets report is available for further analysis and visualization:

[Load Test Results](https://docs.google.com/spreadsheets/d/1q0pvpEDn8v3_VsigQ7yOEAKGq1fv7nacC9gM7VlR4Y4/)

- **Tabs:**
  - *Summary Dashboard*: Visualizations of key metrics
  - *Raw Data*: Imported CSV data
  - *Sweep Configurations/Notes*: Test parameters and observations

---

## Troubleshooting

- **Port Conflicts**
  - Free ports `8089`/`8090` as shown in Setup.
  - Check for running Locust processes:
    ```bash
    ps aux | grep locust
    kill -9 <locust_pid>
    ```

---

## Notes

- The dashboard uses a single Locust instance on port `8089` for live metrics and a headless instance on port `8090` for CSV generation.
- If live metrics fail, verify API connectivity.
- Ensure your API key is valid and your network connection is stable.

---

**For questions or contributions, please open an issue or submit a pull request.**