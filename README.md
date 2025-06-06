# Sarvam Transliteration API Load Testing

This repository contains scripts and a dashboard for load testing the Sarvam Transliteration API. The project includes a Streamlit-based dashboard for configuring and running tests, generating live metrics, and producing CSV reports for analysis.

## Project Structure

- `API_Requests.py`: Locust script defining load test tasks for transliterating text in Hindi, Tamil, and Bengali.
- `dashboard.py`: Streamlit dashboard for configuring tests, displaying live metrics (latency, RPS, error rate), and showing final results with language-specific p95 latency.
- `run_tests.sh`: Bash script to perform a load sweep with varying user counts and spawn rates.
- `process_results.py`: Python script to aggregate CSV outputs into a `summary.csv` for analysis.
- `<prefix>_stats.csv`, `<prefix>_stats_history.csv`: CSV files generated per test (e.g., `simple_test_stats.csv`).
- `summary.csv`: Aggregated results from all tests.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install streamlit requests plotly pandas locust
   ```

2. **Set API Key**:
   Replace `your_api_key` with your Sarvam API key:
   ```bash
   export SARVAM_API_KEY="your_api_key"
   ```

3. **Free Ports**:
   Ensure ports `8089` and `8090` are free:
   ```bash
   lsof -i :8089
   lsof -i :8090
   kill -9 <pid>
   ```

## Running Tests

1. **Load Sweep Tests**:
   Execute the load sweep to test different user counts and spawn rates:
   ```bash
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

2. **Process Results**:
   Aggregate CSV outputs into `summary.csv`:
   ```bash
   python3 process_results.py
   ```

3. **Run Dashboard**:
   Launch the Streamlit dashboard:
   ```bash
   streamlit run dashboard.py
   ```
   - Open `http://localhost:8501` in your browser.
   - Select "Simple" (1 user, 1 spawn rate, 1m) or "Custom" test type.
   - Configure concurrency, spawn rate, run time (e.g., `30s`), and CSV prefix.
   - Click "Run Test" to view live metrics and final results.

## Dashboard Features

- **Test Configuration**:
  - Simple mode: Fixed parameters (1 user, 1 spawn rate, 1m duration, `simple_test` prefix).
  - Custom mode: User-defined concurrency, spawn rate, run time, and CSV prefix.
- **Live Metrics**:
  - Median, average, and p95 latency (ms).
  - Requests per second (RPS).
  - Error rate (%).
- **Final Results**:
  - Total requests, RPS, average/p50/p75/p95 latency, error rate.
  - Language-specific p95 latency (Hindi, Tamil, Bengali) with a bar chart.
- **CSV Output**:
  - Generates `<prefix>_stats.csv` and `<prefix>_stats_history.csv` per test.

## Google Sheets Report

View detailed results, including charts and raw data, in the Google Sheets report:
[Load Test Results](https://docs.google.com/spreadsheets/d/1q0pvpEDn8v3_VsigQ7yOEAKGq1fv7nacC9gM7VlR4Y4/)

- **Tabs**:
  - Summary Dashboard: Visualizations of key metrics.
  - Raw Data: Imported CSV data.
  - Sweep Configurations/Notes: Test parameters and observations.

## Troubleshooting

- **No Live Metrics**:
  - Check terminal for `API_Requests.py` logs (e.g., 401, 429 errors).
  - Verify API key:
    ```bash
    curl -H "x-api-key: $SARVAM_API_KEY" -X POST -H "Content-Type: application/json" \
    -d '{"text":"Hello","source_lang":"hindi","target_lang":"latin"}' \
    https://api.sarvam.ai/transliteration/v1/transliterate
    ```
  - Test `API_Requests.py`:
    ```bash
    locust -f API_Requests.py --host=https://api.sarvam.ai --users=1 --spawn-rate=1 --run-time=30s --headless
    ```

- **Empty CSV**:
  - Ensure directory permissions:
    ```bash
    chmod -R u+w .
    ```
  - Run headless Locust:
    ```bash
    locust -f API_Requests.py --host=https://api.sarvam.ai --web-port=8090 --users=1 --spawn-rate=1 --run-time=30s --csv=test_manual --csv-full-history --headless
    ```

- **Port Conflicts**:
  - Free ports `8089`/`8090` as shown in Setup.
  - Check running Locust processes:
    ```bash
    ps aux | grep locust
    kill -9 <locust_pid>
    ```

## Notes

- The dashboard uses a single Locust instance on port `8089` for live metrics and a headless instance on port `8090` for CSV generation.
- If live metrics fail, verify `API_Requests.py` and API connectivity.
- Update the Google Sheet with new CSVs using `process_results.py` before submission.