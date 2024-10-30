import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go

# Function to authenticate and connect to Google Sheets
def connect_to_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Use Streamlit secrets to load credentials from the secrets.toml file
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp"], scope)

    client = gspread.authorize(creds)

    # Try to open the specific sheet
    try:
        sheet = client.open('HMMFinal').worksheet('Sheet1')  # Updated to the correct sheet name
    except gspread.SpreadsheetNotFound as e:
        st.error(f"Error: {e}")
        return None

    # Get all data from the sheet
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    return df

# Function to calculate summary statistics
def calculate_summary(df, latest_data):
    trials = [f'Trial {i} Time (Second)' for i in range(1, 11)]  # Assuming Trial 1 to Trial 10 are trial times
    errors = [f'Trial {i} Error' for i in range(1, 11)]  # Assuming Trial 1 to Trial 10 are error values

    # Calculate means
    first_two_trials_mean_time = latest_data[trials[:2]].mean()
    last_two_trials_mean_time = latest_data[trials[-2:]].mean()
    first_two_trials_mean_error = latest_data[errors[:2]].mean()
    last_two_trials_mean_error = latest_data[errors[-2:]].mean()

    # Calculate time savings
    time_saving = first_two_trials_mean_time - last_two_trials_mean_time
    error_saving = first_two_trials_mean_error - last_two_trials_mean_error

    # Create summary DataFrame with 3 rows and 5 columns
    summary_df = pd.DataFrame({
        "Trial": ["First Two Trials", "Last Two Trials", "Savings"],
        "Mean Time": [first_two_trials_mean_time, last_two_trials_mean_time, None],
        "Mean Error": [first_two_trials_mean_error, last_two_trials_mean_error, None],
        "Time Saving": [None, None, time_saving],
        "Error Saving": [None, None, error_saving]
    })

    return summary_df, first_two_trials_mean_time, last_two_trials_mean_time, first_two_trials_mean_error, last_two_trials_mean_error, time_saving, error_saving

# Function to filter and display data
def filter_and_display_data(df):
    # Sidebar inputs for UID and EID
    uid_filter = st.sidebar.text_input("Your UID")
    eid_filter = st.sidebar.text_input("Your EID")

    # Button to apply filters
    if st.sidebar.button("Get Result"):
        if uid_filter and eid_filter:
            # Filter DataFrame while stripping any whitespace and converting to string
            filtered_df = df[
                (df['Subject UID'].astype(str).str.strip() == str(uid_filter).strip()) &
                (df['Examiner UID'].astype(str).str.strip() == str(eid_filter).strip())
            ]

            if not filtered_df.empty:
                st.success(f"Results found for UID: {uid_filter} and EID: {eid_filter}")

                # Prepare data for the table and graphs
                latest_data = filtered_df.iloc[-1]  # Get the latest entry
                summary_df, first_two_trials_mean_time, last_two_trials_mean_time, first_two_trials_mean_error, last_two_trials_mean_error, time_saving, error_saving = calculate_summary(filtered_df, latest_data)

                # Display UID, EID, and Date
                st.write("### Subject Credentials")
                st.write(f"**Your UID:** {uid_filter}")
                st.write(f"**Your EID:** {eid_filter}")
                st.write(f"**Test Date (mm/dd/yyyy):** {latest_data['Submission D/T']}")
                st.write(f"**Subject First Name:** {latest_data['Subject First Name']}")
                st.write(f"**Subject Last Name:** {latest_data['Subject Last Name']}")
                st.write(f"**Subject Email:** {latest_data['Subject Email']}")
                st.write(f"**Subject DOB:** {latest_data['Subject DOB']}")
                st.write(f"**Subject Gender:** {latest_data['Subject Gender']}")
                #st.write(f"**Subject Education Level:** {latest_data['Subject Edu Level']}")
                st.write(f"**Subject Institute:** {latest_data['Subject Institute']}")
                st.write(f"**Examiner First Name:** {latest_data['Examiner First Name']}")
                st.write(f"**Examiner Last Name:** {latest_data['Examiner Last Name']}")
                st.write(f"**Examiner Email ID:** {latest_data['Examiner Email ID']}")

                # Prepare data for the table and graphs
                latest_data = filtered_df.iloc[-1]  # Get the latest entry
                summary_df, first_two_trials_mean_time, last_two_trials_mean_time, first_two_trials_mean_error, last_two_trials_mean_error, time_saving, error_saving = calculate_summary(
                    filtered_df, latest_data)

                # Use the latest row for plotting
                trials_data = latest_data[[f'Trial {i} Time (Second)' for i in range(1, 11)]].values.flatten()
                errors_data = latest_data[[f'Trial {i} Error' for i in range(1, 11)]].values.flatten()

                # Create interactive graphs using Plotly
                # Graph for Errors
                fig_errors = go.Figure()
                fig_errors.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=errors_data, mode='lines+markers', name='Errors',
                               line=dict(color='red')))
                fig_errors.update_layout(title='Errors per Trial', xaxis_title='Trial Number', yaxis_title='Errors',
                                         xaxis=dict(tickvals=list(range(1, 11))))  # Ensure all trial numbers show
                st.plotly_chart(fig_errors)

                # Graph for Time
                fig_time = go.Figure()
                fig_time.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=trials_data, mode='lines+markers', name='Trial Times',
                               line=dict(color='blue')))
                fig_time.update_layout(title='Time per Trial', xaxis_title='Trial Number', yaxis_title='Time (s)',
                                       xaxis=dict(tickvals=list(range(1, 11))))  # Ensure all trial numbers show
                st.plotly_chart(fig_time)

                # Graph for both Errors and Time
                fig_combined = go.Figure()
                fig_combined.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=errors_data, mode='lines+markers', name='Errors',
                               line=dict(color='red')))
                fig_combined.add_trace(
                    go.Scatter(x=list(range(1, 11)), y=trials_data, mode='lines+markers', name='Trial Times',
                               line=dict(color='blue')))
                fig_combined.update_layout(title='Errors and Trial Times per Trial', xaxis_title='Trial Number',
                                           yaxis_title='Values',
                                           xaxis=dict(tickvals=list(range(1, 11))))  # Ensure all trial numbers show
                st.plotly_chart(fig_combined)

                # Display summary results table
                st.write("### Summary Results Table")
                st.markdown(f"<div style='text-align: center;'>{summary_df.to_html(escape=False, index=False)}</div>", unsafe_allow_html=True)

                # Add the analysis statement
                # Analysis of learning improvement over attempts
                analysis_statement = (f"The average time for the first two attempts was {first_two_trials_mean_time:.2f} seconds, while for the last two attempts, it reduced significantly to only {last_two_trials_mean_time:.2f} seconds. "
                                      f"This practice-induced improvement resulted in a time saving of {time_saving:.2f} seconds. This suggests that the quantity of the participant's learning increased due to practice. "
                                      f"Regarding inaccuracies, there were an average of {first_two_trials_mean_error:.2f} inaccuracies in the first two attempts, while there were none in the last two attempts. "
                                      f"Consequently, there was a {error_saving:.2f} reduction in inaccuracies due to practice, indicating an enhancement in the quality of learning. "
                                      f"There was progress in both the quantity and quality of learning.")
                
                # Section: Benefits of Maze Learning
                benefits_statement = (f"Maze learning is beneficial for enhancing cognitive skills such as spatial memory, problem-solving, and strategic thinking. Through repeated attempts, individuals develop improved navigation strategies and reduced error rates, as observed in this analysis. "
                                      f"Practicing maze-solving helps in adapting to complex environments, " 
                                      f"fosters better memory recall of spatial cues, and promotes efficient decision-making. " 
                                      f"This process is instrumental in cognitive neuroscience research and has practical applications in education, " 
                                      f"therapy, and AI, as it mirrors the brain's learning and memory mechanisms.")
    
                st.write("### Analysis")
                st.write(analysis_statement)
                st.write("### Befinifits of Maze Task")
                st.write(benefits_statement)
                st.write("This device is developed by Roshan Kumar using PsiQ Tech")

            else:
                st.error(f"No data found for UID: {uid_filter} and EID: {eid_filter}")
        else:
            st.warning("Please enter both UID and EID to see the results.")

# Main function to run the app
def main():
    st.title("Hey there, Human Maze Master Test Result")
    st.write("Please use the sidebar to input your credentials. For any other information, please visit psiq.in.")

    # Connect to Google Sheets and load data
    df = connect_to_google_sheet()

    # Only show the data frame on successful connection
    if df is not None:
        st.sidebar.success("Connected to PsiQ Database")

        # Call the filter and display data function to show sidebar inputs
        filter_and_display_data(df)

if __name__ == "__main__":
    main()
