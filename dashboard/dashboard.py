import streamlit as st
import subprocess
import requests
import time
import pandas as pd
import plotly.graph_objects as go
from threading import Timer
import socket
import os

# Function to check if port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Function to wait for port to be available
def wait_for_port(host, port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(0.5)
    return False

# Function to parse run_time (e.g., "1m" to 60 seconds)
def parse_run_time(run_time_str):
    if run_time_str.endswith('m'):
        minutes = int(run_time_str[:-1])
        return minutes * 60
    elif run_time_str.endswith('s'):
        seconds = int(run_time_str[:-1])
        return seconds
    else:
        raise ValueError("Invalid run_time format. Use 'Xm' for minutes or 'Xs' for seconds.")

# Initialize Locust process for live metrics
if 'locust_process' not in st.session_state:
    if is_port_in_use(8089):
        st.error("Port 8089 is already in use. Please stop any running Locust processes and try again.")
        st.write("Run `lsof -i :8089` to find the process and `kill -9 <pid>` to terminate it.")
        st.stop()
    try:
        process = subprocess.Popen([
            "locust",
            "-f", "API_Requests.py",
            "--host=https://api.sarvam.ai",
            "--web-host=127.0.0.1",
            "--web-port=8089"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if wait_for_port("127.0.0.1", 8089):
            st.session_state.locust_process = process
            st.success("Locust server started on port 8089.")
        else:
            stdout, stderr = process.communicate()
            st.error(f"Locust server failed to start on port 8089: {stderr.decode('utf-8')}")
            st.stop()
    except Exception as e:
        st.error(f"Error starting Locust: {str(e)}")
        st.stop()

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
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

        # Reset stats
        try:
            response = requests.get("http://127.0.0.1:8089/stats/reset")
            st.write(f"Stats reset: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"Failed to reset stats: {str(e)}")
            st.stop()

        # Start the test
        response = requests.post(
            "http://127.0.0.1:8089/swarm",
            json={"user_count": concurrency, "spawn_rate": float(spawn_rate)}
        )
        if response.status_code == 200:
            st.session_state.test_running = True
            st.session_state.start_time = time.time()
            # Initialize data storage
            st.session_state.latency_data = {'time': [], 'median': [], 'avg': [], 'p95': []}
            st.session_state.rps_data = {'time': [], 'rps': []}
            st.session_state.error_data = {'time': [], 'error_rate': []}
            # Timer to stop test and generate CSV
            def stop_test():
                try:
                    response = requests.get("http://127.0.0.1:8089/stop")
                    st.write(f"Test stopped on port 8089: {response.status_code}")
                    # Terminate Locust process to free port 8089
                    if 'locust_process' in st.session_state:
                        st.session_state.locust_process.terminate()
                        st.session_state.locust_process.wait()
                        st.write("Locust server stopped on port 8089")
                        del st.session_state['locust_process']
                    # Check if port 8090 is free
                    if is_port_in_use(8090):
                        st.warning("Port 8090 is in use. Please free it with `lsof -i :8090` and `kill -9 <pid>`.")
                        st.session_state.test_running = False
                        return
                    # Run headless Locust for CSV
                    process_csv = subprocess.run([
                        "locust",
                        "-f", "API_Requests.py",
                        "--host=https://api.sarvam.ai",
                        "--web-host=127.0.0.1",
                        "--web-port=8090",
                        "--users", str(concurrency),
                        "--spawn-rate", str(spawn_rate),
                        "--run-time", run_time,
                        "--csv", csv_prefix,
                        "--csv-full-history",
                        "--headless"
                    ])
                    if process_csv.returncode == 0:
                        st.write(f"CSV generated: {csv_prefix}_stats.csv")
                    else:
                        st.warning(f"Headless Locust failed: {process_csv.stderr.decode('utf-8')}")
                except Exception as e:
                    st.warning(f"Error during test stop or CSV generation: {str(e)}")
                st.session_state.test_running = False
            timer = Timer(run_time_seconds, stop_test)
            timer.start()
            st.success(f"Test started: {concurrency} users, {spawn_rate} spawn rate, {run_time} duration.")
        else:
            st.error(f"Failed to start test: {response.status_code} {response.text}")
            st.stop()

# Display live metrics
if 'test_running' in st.session_state and st.session_state.test_running:
    st.write("### Test Running - Live Metrics")
    placeholder = st.empty()
    if st.session_state.get("test_running", False):
        response = requests.get("http://127.0.0.1:8089/stats/requests")
        if response.status_code == 200:
            stats = response.json()
            if stats["state"] in ["stopped", "ready"]:
                st.session_state.test_running = False
            else:
                with placeholder.container():
                    try:
                        response = requests.get("http://127.0.0.1:8089/stats/requests")
                        if response.status_code == 200:
                            stats = response.json()
                            st.write(f"API response: {stats}")  # Debug
                            if stats["state"] in ["stopped", "ready"]:
                                st.write(f"Test stopped early due to state: {stats['state']}")
                                st.session_state.test_running = False
                            # Find aggregated stats
                            agg_stats = next((s for s in stats["stats"] if s["name"] == "Aggregated"), None)
                            if agg_stats and agg_stats["num_requests"] > 0:
                                current_time = time.time() - st.session_state.start_time
                                # Latency metrics
                                median = agg_stats.get("median_response_time", 0)
                                avg = agg_stats.get("avg_response_time", 0)
                                p95 = stats.get("current_response_time_percentile_0.95", 0) or 0
                                st.session_state.latency_data['time'].append(current_time)
                                st.session_state.latency_data['median'].append(median)
                                st.session_state.latency_data['avg'].append(avg)
                                st.session_state.latency_data['p95'].append(p95)
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
                                fig_latency.add_trace(go.Scatter(
                                    x=st.session_state.latency_data['time'],
                                    y=st.session_state.latency_data['p95'],
                                    mode='lines',
                                    name='p95 Latency'
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
                            else:
                                st.write("No requests processed yet.")
                        else:
                            st.warning(f"Stats API failed: {response.status_code} {response.text}")
                    except requests.RequestException as e:
                        st.warning(f"Failed to fetch stats: {str(e)}")
                    time.sleep(5)  # Update every 5 seconds
                    st.experimental_rerun()
    st.success("Test completed.")

# Display final results from CSV
if not st.session_state.get('test_running', False):
    try:
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
        for lang in ["Hindi", "Tamil", "Bengali"]:
            lang_row = df[df["Name"] == f"Transliterate {lang}"]
            if not lang_row.empty:
                st.write(f"**{lang} p95 Latency**: {lang_row['95%'].iloc[0]} ms")
            else:
                st.write(f"**{lang} p95 Latency**: Not available")
        # Plot language-specific p95 latency
        lang_data = []
        for lang in ["Hindi", "Tamil", "Bengali"]:
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