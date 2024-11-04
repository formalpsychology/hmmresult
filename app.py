import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go

# Function to authenticate and connect to Google Sheets
def connect_to_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp"], scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open('HMMFinal').worksheet('Sheet1')
    except gspread.SpreadsheetNotFound as e:
        st.error(f"Error: {e}")
        return None
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Function to calculate summary statistics
def calculate_summary(df, latest_data):
    trials = [f'Trial {i} Time (Second)' for i in range(1, 11)]
    errors = [f'Trial {i} Error' for i in range(1, 11)]
    first_two_trials_mean_time = latest_data[trials[:2]].mean()
    last_two_trials_mean_time = latest_data[trials[-2:]].mean()
    first_two_trials_mean_error = latest_data[errors[:2]].mean()
    last_two_trials_mean_error = latest_data[errors[-2:]].mean()
    time_saving = first_two_trials_mean_time - last_two_trials_mean_time
    error_saving = first_two_trials_mean_error - last_two_trials_mean_error
    summary_df = pd.DataFrame({
        "Trial": ["First Two Trials", "Last Two Trials", "Savings"],
        "Mean Time": [first_two_trials_mean_time, last_two_trials_mean_time, None],
        "Mean Error": [first_two_trials_mean_error, last_two_trials_mean_error, None],
        "Time Saving": [None, None, time_saving],
        "Error Saving": [None, None, error_saving]
    })
    return summary_df

# Function to filter and display data
def filter_and_display_data(df):
    uid_filter = st.sidebar.text_input("Your UID")
    eid_filter = st.sidebar.text_input("Your EID")
    if st.sidebar.button("Get Result"):
        if uid_filter and eid_filter:
            filtered_df = df[
                (df['Subject UID'].astype(str).str.strip() == str(uid_filter).strip()) &
                (df['Examiner UID'].astype(str).str.strip() == str(eid_filter).strip())
                ]
            if not filtered_df.empty:
                st.success(f"Results found for UID: {uid_filter} and EID: {eid_filter}")
                latest_data = filtered_df.iloc[-1]
                summary_df = calculate_summary(filtered_df, latest_data)
                st.write("### Subject Credentials")
                st.write(f"**Your UID:** {uid_filter}")
                st.write(f"**Your EID:** {eid_filter}")
                st.write(f"**Test Date (mm/dd/yyyy):** {latest_data['Submission D/T']}")
                st.write(f"**Subject First Name:** {latest_data['Subject First Name']}")
                st.write(f"**Subject Last Name:** {latest_data['Subject Last Name']}")
                st.write(f"**Subject Email:** {latest_data['Subject Email']}")
                st.write(f"**Subject DOB:** {latest_data['Subject DOB']}")
                st.write(f"**Subject Gender:** {latest_data['Subject Gender']}")
                st.write(f"**Subject Institute:** {latest_data['Subject Institute']}")
                st.write(f"**Examiner First Name:** {latest_data['Examiner First Name']}")
                st.write(f"**Examiner Last Name:** {latest_data['Examiner Last Name']}")
                st.write(f"**Examiner Email ID:** {latest_data['Examiner Email ID']}")

                trials_data = latest_data[[f'Trial {i} Time (Second)' for i in range(1, 11)]].values.flatten()
                errors_data = latest_data[[f'Trial {i} Error' for i in range(1, 11)]].values.flatten()

                fig_errors = go.Figure()
                fig_errors.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=errors_data, mode='lines+markers', name='Errors',
                               line=dict(color='red')))
                fig_errors.update_layout(title='Errors per Trial', xaxis_title='Trial Number', yaxis_title='Errors')
                st.plotly_chart(fig_errors)

                fig_time = go.Figure()
                fig_time.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=trials_data, mode='lines+markers', name='Trial Times',
                               line=dict(color='blue')))
                fig_time.update_layout(title='Time per Trial', xaxis_title='Trial Number', yaxis_title='Time (s)')
                st.plotly_chart(fig_time)

                fig_combined = go.Figure()
                fig_combined.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=errors_data, mode='lines+markers', name='Errors',
                               line=dict(color='red')))
                fig_combined.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=trials_data, mode='lines+markers', name='Trial Times',
                               line=dict(color='blue')))
                fig_combined.update_layout(title='Errors and Trial Times per Trial', xaxis_title='Trial Number',
                                           yaxis_title='Values')
                st.plotly_chart(fig_combined)

                # Display summary results table
                st.write("### Summary Results Table")
                st.write(summary_df)

                # **Detailed Trial Data Table**
                trial_data_df = pd.DataFrame({
                    "Trial Number": list(range(1, 11)),
                    "Trial Time (Seconds)": trials_data,
                    "Errors": errors_data
                })
                st.write("### Detailed Trial Data Table")
                st.table(trial_data_df)  # Display the table of trial times and errors

                # Analysis Section
                analysis_statement = (
                    f"**Time Analysis**: The average time for the first two trials was {summary_df['Mean Time'][0]:.2f} seconds, "
                    f"while for the last two trials, it reduced to {summary_df['Mean Time'][1]:.2f} seconds. "
                    f"This indicates a time saving of {summary_df['Time Saving'][2]:.2f} seconds, suggesting improvement in speed.\n\n"
                    f"**Error Analysis**: The average error count for the first two trials was {summary_df['Mean Error'][0]:.2f}, "
                    f"and for the last two trials, it decreased to {summary_df['Mean Error'][1]:.2f}. "
                    f"This error reduction by {summary_df['Error Saving'][2]:.2f} shows enhanced accuracy in later trials.\n\n"
                    f"Overall, the user’s performance improved over time, as demonstrated by both quicker trial completion and fewer errors. "
                    f"This trend suggests effective learning and adaptation to the maze test."
                )
                st.write("### Analysis")
                st.write(analysis_statement)

            else:
                st.error(f"No data found for UID: {uid_filter} and EID: {eid_filter}")
        else:
            st.warning("Please enter both UID and EID to see the results.")

# Main function to run the app
def main():
    st.title("Hey there, Human Maze Master Test Result")
    st.write("Please use the sidebar to input your credentials. For any other information, please visit psiq.in.")
    df = connect_to_google_sheet()
    if df is not None:
        st.sidebar.success("Connected to PsiQ Database")
        filter_and_display_data(df)

if __name__ == "__main__":
    main()
