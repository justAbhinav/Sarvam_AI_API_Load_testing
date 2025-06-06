import streamlit as st
import subprocess
import requests
import time
import pandas as pd
import plotly.graph_objects as go
from threading import Timer
import socket
import os
import shutil

# Function to parse run_time (e.g: "1m" to 60 seconds)
def parse_run_time(run_time_str):
    if run_time_str.endswith('m'):
        minutes = int(run_time_str[:-1])
        return minutes * 60
    elif run_time_str.endswith('s'):
        seconds = int(run_time_str[:-1])
        return seconds
    else:
        raise ValueError("Invalid run_time format. Use 'Xm' for minutes or 'Xs' for seconds.")



def wait_for_port(host, port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(0.5)
    return False


# Initialize Locust process if not already running
if 'locust_process' not in st.session_state:
    # Check if port 8089 is already in use (Locust web server running)
    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0
    if not is_port_in_use(8089):
        process = subprocess.Popen([
            "locust",
            "-f", "API_Requests.py",
            "--host=https://api.sarvam.ai",
            "--web-host=127.0.0.1",
            "--web-port=8089"
        ])
        if wait_for_port("127.0.0.1", 8089):
            st.success("Locust server started.")
        else:
            st.error("Locust server failed to start on port 8089.")
            st.stop()
    st.session_state.locust_process = True
        

# Dashboard title
st.title("Sarvam Transliteration API Load Testing Dashboard")
st.write("Configure and run load tests for the Sarvam Transliteration API.")

# Input fields
test_type = st.selectbox("Test Type", ["Simple", "Custom"])
if test_type == "Simple":
    concurrency = 1
    spawn_rate = 1
    run_time = "1m"
    csv_prefix = "simple_test"
else:
    concurrency = st.number_input("Concurrency (number of users)", min_value=1, value=1, step=1)
    spawn_rate = st.number_input("Spawn Rate (users per second)", min_value=1, value=1, step=1)
    run_time = st.text_input("Run Time (e.g., '1m' or '30s')", value="1m")
    csv_prefix = st.text_input("CSV Output Prefix", value="test")

# Run Test button
if st.button("Run Test"):
    if 'test_running' in st.session_state and st.session_state.test_running:
        st.warning("A test is already running. Please wait for it to complete.")
    else:
        try:
            run_time_seconds = parse_run_time(run_time)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        # Start the test via Locust API
        response = requests.post(
            "http://127.0.0.1:8089/swarm",
            data={"user_count": concurrency, "spawn_rate": spawn_rate}
        )
        if response.status_code == 200:
            st.session_state.test_running = True
            st.session_state.start_time = time.time()
            # Initialize data storage
            st.session_state.latency_data = {'time': [], 'median': [], 'avg': []}
            st.session_state.rps_data = {'time': [], 'rps': []}
            st.session_state.error_data = {'time': [], 'error_rate': []}
            # Timer to stop the test and save CSV
            def stop_test():
                requests.get("http://127.0.0.1:8089/stop")
                # Run headless Locust to generate CSV (no web server)
                proc = subprocess.run([
                    "locust",
                    "-f", "API_Requests.py",
                    "--host=https://api.sarvam.ai",
                    "--users", str(concurrency),
                    "--spawn-rate", str(spawn_rate),
                    "--run-time", run_time,
                    "--csv", csv_prefix,
                    "--headless"
                ])
                # Wait for the main CSV file to exist (max 30s)
                csv_path = f"{csv_prefix}_stats.csv"
                for _ in range(30):
                    if os.path.exists(csv_path):
                        break
                    time.sleep(1)
                st.session_state.test_running = False
                st.experimental_rerun()  # Force rerun to show results immediately
            timer = Timer(run_time_seconds, stop_test)
            timer.start()
            st.success(f"Test started: {concurrency} users, {spawn_rate} spawn rate, {run_time} duration.")
        else:
            st.error("Failed to start test. Check Locust configuration or API key.")

# Display live metrics if test is running
if 'test_running' in st.session_state and st.session_state.test_running:
    st.write("### Test Running - Live Metrics")
    placeholder = st.empty()
    while st.session_state.test_running:
        with placeholder.container():
            try:
                response = requests.get("http://127.0.0.1:8089/stats/requests")
                if response.status_code == 200:
                    stats = response.json()
                    if stats["state"] == "stopped":
                        st.session_state.test_running = False
                        break
                    # Find aggregated stats
                    agg_stats = next((s for s in stats["stats"] if s["name"] == "Aggregated"), None)
                    if agg_stats:
                        current_time = time.time() - st.session_state.start_time
                        # Latency metrics
                        median = agg_stats.get("median_response_time", 0)
                        avg = agg_stats.get("avg_response_time", 0)
                        st.session_state.latency_data['time'].append(current_time)
                        st.session_state.latency_data['median'].append(median)
                        st.session_state.latency_data['avg'].append(avg)
                        # RPS
                        rps = agg_stats.get("current_rps", 0)
                        st.session_state.rps_data['time'].append(current_time)
                        st.session_state.rps_data['rps'].append(rps)
                        # Error rate
                        num_requests = agg_stats.get("num_requests", 0)
                        num_failures = agg_stats.get("num_failures", 0)
                        error_rate = (num_failures / num_requests * 100) if num_requests > 0 else 0
                        st.session_state.error_data['time'].append(current_time)
                        st.session_state.error_data['error_rate'].append(error_rate)

                        # Latency chart
                        fig_latency = go.Figure()
                        fig_latency.add_trace(go.Scatter(
                            x=st.session_state.latency_data['time'],
                            y=st.session_state.latency_data['median'],
                            mode='lines',
                            name='Median Latency'
                        ))
                        fig_latency.add_trace(go.Scatter(
                            x=st.session_state.latency_data['time'],
                            y=st.session_state.latency_data['avg'],
                            mode='lines',
                            name='Average Latency'
                        ))
                        fig_latency.update_layout(title="Latency Metrics (ms)", xaxis_title="Time (s)", yaxis_title="Latency (ms)")
                        st.plotly_chart(fig_latency, use_container_width=True)

                        # RPS chart
                        fig_rps = go.Figure()
                        fig_rps.add_trace(go.Scatter(
                            x=st.session_state.rps_data['time'],
                            y=st.session_state.rps_data['rps'],
                            mode='lines',
                            name='RPS'
                        ))
                        fig_rps.update_layout(title="Requests Per Second", xaxis_title="Time (s)", yaxis_title="RPS")
                        st.plotly_chart(fig_rps, use_container_width=True)

                        # Error rate chart
                        fig_error = go.Figure()
                        fig_error.add_trace(go.Scatter(
                            x=st.session_state.error_data['time'],
                            y=st.session_state.error_data['error_rate'],
                            mode='lines',
                            name='Error Rate'
                        ))
                        fig_error.update_layout(title="Error Rate (%)", xaxis_title="Time (s)", yaxis_title="Error Rate (%)")
                        st.plotly_chart(fig_error, use_container_width=True)
            except requests.RequestException:
                st.warning("Failed to fetch stats. Test may have stopped unexpectedly.")
                break
            time.sleep(5)  # Update every 5 seconds
    st.success("Test completed.")

# Display final results from CSV
if not st.session_state.get('test_running', False):
    try:
        # Wait for CSV to exist (max 10s)
        for _ in range(10):
            if os.path.exists(f"{csv_prefix}_stats.csv"):
                break
            time.sleep(1)
        df = pd.read_csv(f"{csv_prefix}_stats.csv")
        st.write("### Final Test Results")
        agg_row = df[df["Name"] == "Aggregated"].iloc[0]
        st.write(f"**Total Requests**: {agg_row['Request Count']}")
        st.write(f"**RPS**: {agg_row['Requests/s']:.2f}")
        st.write(f"**Average Latency**: {agg_row['Average Response Time']:.2f} ms")
        st.write(f"**p50 Latency**: {agg_row['50%']} ms")
        st.write(f"**p75 Latency**: {agg_row['75%']} ms")
        st.write(f"**p95 Latency**: {agg_row['95%']} ms")
        st.write(f"**Error Rate**: {(agg_row['Failure Count'] / agg_row['Request Count'] * 100) if agg_row['Request Count'] > 0 else 0:.2f}%")
        # Language-specific p95
        st.write("**Language-Specific p95 Latency**")
        for lang in ["Hi", "Ta", "Bn"]:
            lang_row = df[df["Name"] == f"Transliterate {lang}"]
            if not lang_row.empty:
                st.write(f"**{lang} p95 Latency**: {lang_row['95%'].iloc[0]} ms")
            else:
                st.write(f"**{lang} p95 Latency**: Not available")
        # Plot language-specific p95 latency
        lang_data = []
        for lang in ["Hi", "Ta", "Bn"]:
            lang_row = df[df["Name"] == f"Transliterate {lang}"]
            if not lang_row.empty:
                lang_data.append({"Language": lang, "p95 Latency (ms)": lang_row["95%"].iloc[0]})
        if lang_data:
            fig_lang = go.Figure()
            fig_lang.add_trace(go.Bar(
                x=[d["Language"] for d in lang_data],
                y=[d["p95 Latency (ms)"] for d in lang_data],
                name="p95 Latency"
            ))
            fig_lang.update_layout(
                title="Language-Specific p95 Latency",
                xaxis_title="Language",
                yaxis_title="p95 Latency (ms)"
            )
            st.plotly_chart(fig_lang, use_container_width=True)
    except FileNotFoundError:
        st.info("No test results available. Run a test to generate results.")

# Google Sheets report link
st.markdown("For detailed results, view the [Google Sheets Report](https://docs.google.com/spreadsheets/d/1q0pvpEDn8v3_VsigQ7yOEAKGq1fv7nacC9gM7VlR4Y4/).")