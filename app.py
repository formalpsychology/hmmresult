import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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
    uid_filter = st.sidebar.text_input("Filter by UID")
    eid_filter = st.sidebar.text_input("Filter by EID")

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

                # Display the filtered data including date and time
                columns_to_display = ['date', 'time', 'uid', 'eid', 'e1', 'd1', 'e2', 'd2',
                                      'e3', 'd3', 'e4', 'd4', 'e5', 'd5', 'e6', 'd6',
                                      'e7', 'd7', 'e8', 'd8', 'e9', 'd9', 'e10', 'd10']
                event_data = filtered_df[columns_to_display]

                st.write("Event Data")
                st.table(event_data)
            else:
                st.error(f"No data found for UID: {uid_filter} and EID: {eid_filter}")
        else:
            st.warning("Please enter both UID and EID to see the results.")


# Main function to run the app
def main():
    st.title("Your Result will be shown here")

    # Connect to Google Sheets and load data
    df = connect_to_google_sheet()

    # Only show the data frame on successful connection
    if df is not None:
        st.sidebar.success("Connected to PsiQ Database")

        # Here we don't display the entire DataFrame immediately
        filter_and_display_data(df)


if __name__ == "__main__":
    main()
