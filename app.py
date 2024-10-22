import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# Function to authenticate and connect to Google Sheets
def connect_to_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Use Streamlit secrets to load credentials from the secrets.toml file
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp"], scope)

    client = gspread.authorize(creds)

    # Try to open the specific sheet
    try:
        sheet = client.open('dataCollector').sheet1
    except gspread.SpreadsheetNotFound as e:
        st.error(f"Error: {e}")
        return None

    # Get all data from the sheet
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    return df

# Function to filter and display data
def filter_and_display_data(df):
    st.sidebar.title("Input Credentials Here")

    # Sidebar inputs for UID and EID
    uid_filter = st.sidebar.text_input("Your UID")
    eid_filter = st.sidebar.text_input("Your EID")

    # Button to apply filters
    if st.sidebar.button("Apply Filters"):
        if uid_filter and eid_filter:
            # Filter DataFrame while stripping any whitespace and converting to string
            filtered_df = df[
                (df['uid'].astype(str).str.strip() == str(uid_filter).strip()) &
                (df['eid'].astype(str).str.strip() == str(eid_filter).strip())
            ]

            if not filtered_df.empty:
                st.success(f"Results found for UID: {uid_filter} and EID: {eid_filter}")

                # Prepare data for the table and graphs
                latest_data = filtered_df.iloc[-1]  # Get the latest entry
                trials = [f'd{i}' for i in range(1, 11)]  # Assuming d1 to d10 are trial times
                errors = [f'e{i}' for i in range(1, 11)]  # Assuming e1 to e10 are error values

                # Create a DataFrame for display with specified columns
                results_table = pd.DataFrame({
                    "Trial Number": range(1, 11),
                    "Errors": latest_data[errors].values.flatten(),
                    "Time": latest_data[trials].values.flatten()
                })

                # Display UID, EID, and date from the sheet
                st.write("### Your Credentials")
                st.write(f"**Your UID:** {uid_filter}")
                st.write(f"**Your EID:** {eid_filter}")
                st.write(f"**Test Date:** {latest_data['date']}")  # Assuming the date column is named 'date'

                # Center align the table
                st.write("### Results Table")
                st.markdown(f"<div style='text-align: center;'>{results_table.to_html(escape=False, index=False)}</div>", unsafe_allow_html=True)

                # Use the latest row for plotting
                trials_data = latest_data[trials].values.flatten()
                errors_data = latest_data[errors].values.flatten()

                # Create three separate graphs
                # Graph for Errors
                fig, ax = plt.subplots()
                ax.plot(range(1, 11), errors_data, label='Errors', marker='o', color='red')
                ax.set_title('Errors per Trial')
                ax.set_xlabel('Trial Number')
                ax.set_ylabel('Errors')
                ax.legend()
                st.pyplot(fig)

                # Graph for Time
                fig, ax = plt.subplots()
                ax.plot(range(1, 11), trials_data, label='Trial Times', marker='x', color='blue')
                ax.set_title('Time per Trial')
                ax.set_xlabel('Trial Number')
                ax.set_ylabel('Time (s)')
                ax.legend()
                st.pyplot(fig)

                # Graph for both Errors and Time
                fig, ax = plt.subplots()
                ax.plot(range(1, 11), errors_data, label='Errors', marker='o', color='red')
                ax.plot(range(1, 11), trials_data, label='Trial Times', marker='x', color='blue')
                ax.set_title('Errors and Trial Times per Trial')
                ax.set_xlabel('Trial Number')
                ax.set_ylabel('Values')
                ax.legend()
                st.pyplot(fig)

            else:
                st.error(f"No data found for UID: {uid_filter} and EID: {eid_filter}")
        else:
            st.warning("Please enter both UID and EID to see the results.")

# Main function to run the app
def main():
    st.title("Your Human Maze Master Result")

    # Connect to Google Sheets and load data
    df = connect_to_google_sheet()

    # Only show the data frame on successful connection
    if df is not None:
        st.sidebar.success("Connected to PsiQ Database")
        filter_and_display_data(df)

if __name__ == "__main__":
    main()
