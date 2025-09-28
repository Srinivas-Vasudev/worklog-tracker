import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(layout="centered")

# --- SETTINGS ---
DATA_FILE = "worklog.csv"
hourly_rate = 12.48
non_working_days = ["Sunday", "Wednesday"]

# --- FUNCTIONS TO LOAD AND SAVE DATA ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    else:
        start_date = datetime.date(2025, 9, 14)
        end_date = datetime.date(2025, 10, 11)
        dates = pd.date_range(start_date, end_date)
        return pd.DataFrame({
            "Date": dates.date, "Day": dates.day_name(),
            "Hours Worked": [0.0] * len(dates), "Hourly Rate": [hourly_rate] * len(dates),
            "Earned": [0.0] * len(dates), "To Earn": [0.0] * len(dates)
        })

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- INITIALIZE SESSION STATE ---
if "worklog" not in st.session_state:
    st.session_state.worklog = load_data()

df = st.session_state.worklog

# --- HEADER & PRIMARY ACTION ---
st.title("Work Log Tracker")

st.subheader("Log Today's Hours")
today = datetime.date.today()
# We check if today's date (September 28, 2025) is within the DataFrame's range
if today >= df["Date"].min() and today <= df["Date"].max():
    if st.button("Log Today", use_container_width=True, type="primary"):
        idx = df.index[df["Date"] == today][0]
        day_name = df.loc[idx, "Day"]
        if day_name in non_working_days:
            # It's Sunday, which is a non-working day
            st.warning(f"Today ({day_name}) is a non-working day.")
        else:
            df.loc[idx, "Hours Worked"] = 4
            df.loc[idx, "Earned"] = df.loc[idx, "Hours Worked"] * df.loc[idx, "Hourly Rate"]
            save_data(df)
            st.success(f"Logged 4 hours for {today}")
            st.rerun()
else:
    st.info(f"Today's date ({today}) is outside the current logging period.")


# --- DEFERRED ACTIONS (Placed below the main button) ---
# These actions are not executed immediately but defined for later use.
# We will call them in the "Detailed Work Log" section.

def log_missed_day_action():
    missed_date = st.session_state.missed_date_widget
    idx = df.index[df["Date"] == missed_date][0]
    day_name = df.loc[idx, "Day"]
    if day_name in non_working_days:
        st.warning(f"{missed_date} was a non-working day.")
    elif df.loc[idx, "Hours Worked"] > 0:
        st.info(f"{missed_date} already has hours logged.")
    else:
        df.loc[idx, "Hours Worked"] = 4
        df.loc[idx, "Earned"] = df.loc[idx, "Hours Worked"] * df.loc[idx, "Hourly Rate"]
        save_data(df)
        st.success(f"Logged 4 hours for {missed_date}")
        st.rerun()

def remove_log_action():
    date_to_remove = st.session_state.remove_date_widget
    idx = df.index[df["Date"] == date_to_remove][0]
    if df.loc[idx, "Hours Worked"] > 0:
        df.loc[idx, "Hours Worked"] = 0.0
        df.loc[idx, "Earned"] = 0.0
        save_data(df)
        st.success(f"Log for {date_to_remove} has been removed.")
        st.rerun()
    else:
        st.info(f"No hours were logged for {date_to_remove}.")

st.divider()

# --- RECALCULATE DATA ---
workdays_mask = ~df["Day"].isin(non_working_days)
df.loc[workdays_mask, "To Earn"] = (4 * df.loc[workdays_mask, "Hourly Rate"]) - df.loc[workdays_mask, "Earned"]
df.loc[df["To Earn"] < 0, "To Earn"] = 0
df.loc[~workdays_mask, "To Earn"] = 0
st.session_state.worklog = df

# --- METRICS & CHART ---
total_earned = df["Earned"].sum()
total_toearn = df["To Earn"].sum()
total = total_earned + total_toearn

st.header("Financial Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Earned", f"£{total_earned:.2f}")
col2.metric("Total To Earn", f"£{total_toearn:.2f}")
col3.metric("Overall", f"£{total:.2f}")

fig = px.pie(
    names=["Earned", "To Earn"], values=[total_earned, total_toearn],
    hole=0.5, color=["Earned", "To Earn"],
    color_discrete_map={"Earned": "green", "To Earn": "gold"}
)
fig.update_traces(textinfo="label+percent", textfont_size=14)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- DETAILED LOG & EDITING CONTROLS ---
st.header("Detailed Work Log")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Log a Missed Day")
    st.date_input("Select a date", min_value=df["Date"].min(), max_value=df["Date"].max(), key="missed_date_widget")
    st.button("Log Missed Day", on_click=log_missed_day_action, use_container_width=True)

with col2:
    st.subheader("Remove a Log")
    st.date_input("Select a date", min_value=df["Date"].min(), max_value=df["Date"].max(), key="remove_date_widget")
    st.button("Remove Log", on_click=remove_log_action, use_container_width=True)

st.dataframe(df)