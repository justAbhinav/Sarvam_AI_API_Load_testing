<!-- filepath: /home/asus/Desktop/Sarvam_TASK/README.md -->

<p align="center">
  <img src="https://img.shields.io/badge/Load%20Testing-Sarvam%20Transliteration%20API-blueviolet" alt="Sarvam Transliteration API Load Testing"/>
</p>

<h1 align="center">Sarvam Transliteration API Load Testing 🚀</h1>

<p align="center">
  <a href="https://docs.sarvam.ai/api-reference-docs/text/transliterate">API Docs</a> |
  <a href="#dashboard-features">Dashboard Features</a> |
  <a href="#google-sheets-report">Google Sheets Report</a>
</p>

---

> **A complete solution for load testing the [Sarvam Transliteration API](https://docs.sarvam.ai/api-reference-docs/text/transliterate):**
> - Automated load test scripts
> - Streamlit dashboard for configuration & live monitoring
> - Tools for aggregating and analyzing results
> - Designed for both quick and advanced load sweeps
> - Clear reporting and troubleshooting guidance

---

## 📑 Table of Contents

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

## 🗂️ Project Structure

| File/Folder                | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `API_Requests.py`         | Locust script for load test tasks (Hindi, Tamil, Bengali)                    |
| `dashboard.py`            | Streamlit dashboard for config, live metrics, and results                    |
| `run_tests.sh`            | Bash script for load sweep (varying users/spawn rates)                       |
| `process_results.py`      | Aggregates CSV outputs into `summary.csv`                                    |
| `<prefix>_stats.csv`      | Per-test CSV stats (e.g., `simple_test_stats.csv`)                           |
| `<prefix>_stats_history.csv` | Per-test CSV history                                                        |
| `summary.csv`             | Aggregated results from all tests                                            |
| `requirements.txt`        | Python dependencies                                                          |
| `.env`                    | (Optional) API keys and environment variables                                |
| `Report/`                 | Final PDF report                                                             |

---

## 🛠️ Requirements

All dependencies are listed in `requirements.txt`:

```bash
streamlit
requests
plotly
pandas
locust
python-dotenv
```

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

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

## 🔐 .env File Setup

Create a `.env` file in the project root:

```env
SARVAM_API_KEY=your_api_key_here
```

- Replace `your_api_key_here` with your actual Sarvam API key ([Get it here](https://dashboard.sarvam.ai/)).
- The project uses `python-dotenv` to load environment variables automatically.

Alternatively, export the variable in your shell:

```bash
export SARVAM_API_KEY="your_api_key_here"
```

---

## 🚦 Running Tests

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
   - Choose **Simple** (1 user, 1 spawn rate, 1m) or **Custom** test type.
   - Configure concurrency, spawn rate, run time (e.g., `30s`), and CSV prefix as needed.
   - Click **Run Test** to view live metrics and final results.

---

## 📊 Dashboard Features

- **Test Configuration**
  - *Simple Mode*: Fixed parameters (1 user, 1 spawn rate, 1m duration, `simple_test` prefix)
  - *Custom Mode*: User-defined concurrency, spawn rate, run time, and CSV prefix

- **Live Metrics**
  - Median, average, and p95 latency (ms)
  - Requests per second (RPS)
  - Error rate (%)

- **Final Results**
  - Total requests, RPS, average/p50/p75/p95 latency, error rate
  - Language-specific p95 latency (Hindi, Tamil, Bengali) with a bar chart

  > **Note:** There is a bug where you need to refresh the page for final results. All CSV files are saved correctly in the dashboard directory.

- **CSV Output**
  - Generates `<prefix>_stats.csv` and `<prefix>_stats_history.csv` per test

---

## 📈 Google Sheets Report

A detailed Google Sheets report is available for further analysis and visualization:

[**Sarvam Transliteration API Load Test Results**](https://docs.google.com/spreadsheets/d/1q0pvpEDn8v3_VsigQ7yOEAKGq1fv7nacC9gM7VlR4Y4/)

- **Tabs:**
  - *Summary Dashboard*: Visualizations of key metrics
  - *Raw Data*: Imported CSV data
  - *Sweep Configurations/Notes*: Test parameters and observations

---

## 🛠️ Troubleshooting

- **Port Conflicts**
  - Free ports `8089`/`8090` as shown in Setup.
  - Check for running Locust processes:
    ```bash
    ps aux | grep locust
    kill -9 <locust_pid>
    ```

---

## 📝 Notes

- The dashboard uses a single Locust instance on port `8089` for live metrics and a headless instance on port `8090` for CSV generation.
- If live metrics fail, verify API connectivity.
- Ensure your API key is valid and your network connection is stable.

---

<p align="center">
  <b>For questions or contributions, please open an issue or submit a pull request.</b>
</p>