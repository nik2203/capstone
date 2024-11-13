import streamlit as st
import pandas as pd
import time
from pathlib import Path

# Path to the log file
LOG_FILE_PATH = "honeypot.log"

# Do not change this action mapping
# As logging is inconsistent, we had to do something :)
action_map = {
    "0": "Allow", 
    "1": "Block", 
    "2": "Delay", 
    "3": "Fake", 
    "4": "Insult", 
    'd': 'Not Found',
    'y': 'Delay',
    'k': 'Block', 
    'e': 'Fake',
    'w': 'Allow',
    't': 'Insult'
    }

# Initialize session state
if "log_data" not in st.session_state:
    st.session_state["log_data"] = pd.DataFrame()
if "last_updated" not in st.session_state:
    st.session_state["last_updated"] = 0

# Title
st.title("Honeypot Log Viewer")

# Sidebar for options
poll_interval = st.sidebar.slider("Polling Interval (seconds)", min_value=1, max_value=30, value=5, step=1)
force_sync = st.sidebar.button("Force Sync")

# Function to parse the log file
def parse_log_file(file_path):
    try:
        log_file = Path(file_path)
        if not log_file.exists():
            return pd.DataFrame(), "Log file not found."

        # Read and parse log file
        rows = []
        previous_entry = None  # Track the previous entry
        with log_file.open("r") as f:
            for line in f:
                parts = line.strip().split(" - ")
                print(parts)
                if len(parts) == 5:
                    # Parse a complete log entry
                    date_time, source_ip, command, action, response = parts
                    # Split date and timestamp
                    date, timestamp = date_time.split()
                    # Convert date format
                    date = "-".join(reversed(date.split("-")))
                    # Extract command (remove "Command" keyword)
                    command = command.replace("Command: ", "").strip()
                    # Map action
                    action = action_map[action.strip()[-1]]
                    # Add row to rows
                    response = response.replace("Response: ", "").strip()
                    previous_entry = [date, timestamp, source_ip, command, action, response.strip()]
                    rows.append(previous_entry)
                elif len(parts) == 1 and previous_entry:
                    # Append to the Response of the previous entry
                    previous_entry[5] += " " + parts[0].strip()

        # Create DataFrame
        df = pd.DataFrame(rows, columns=["Date", "Timestamp", "Source IP", "Command", "Action", "Response"])
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"Error reading log file: {e}"

# Polling or Force Sync
if force_sync or time.time() - st.session_state["last_updated"] > poll_interval:
    st.session_state["log_data"], error_message = parse_log_file(LOG_FILE_PATH)
    st.session_state["last_updated"] = time.time()
    if error_message:
        st.error(error_message)

# Display log data in a table
if not st.session_state["log_data"].empty:
    st.dataframe(st.session_state["log_data"], use_container_width=True)
else:
    st.write("No log data available.")

# Footer
st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state['last_updated']))}")
