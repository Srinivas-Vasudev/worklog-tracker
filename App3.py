#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 19:55:13 2025

@author: srinivas
"""

import streamlit as st
import pandas as pd
import datetime
import os

import plotly.express as px

# --- Settings ---
DATA_FILE = "worklog.csv"  # Define the file to save our data
hourly_rate = 12.48
non_working_days = ["Sunday", "Wednesday"]


# --- Functions to Load and Save Data ---
def load_data():
    """Loads worklog from CSV or creates a new one if it doesn't exist."""
    if os.path.exists(DATA_FILE):
        # If file exists, load it and ensure 'Date' is the right type
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    else:
        # If file doesn't exist, create the initial DataFrame
        start_date = datetime.date(2025, 9, 14)
        end_date = datetime.date(2025, 10, 11)
        dates = pd.date_range(start_date, end_date)

        return pd.DataFrame({
            "Date": dates.date,
            "Day": dates.day_name(),
            "Hours Worked": [0.0] * len(dates),
            "Hourly Rate": [hourly_rate] * len(dates),
            "Earned": [0.0] * len(dates),
            "To Earn": [0.0] * len(dates)
        })


def save_data(df):
    """Saves the worklog DataFrame to a CSV file."""
    df.to_csv(DATA_FILE, index=False)


# --- Initialize session state by loading data ---
if "worklog" not in st.session_state:
    st.session_state.worklog = load_data()

df = st.session_state.worklog

# --- Button to log today ---
today = datetime.date.today()
if st.button("Log Today"):
    if today in df["Date"].values:
        idx = df.index[df["Date"] == today][0]
        day_name = df.loc[idx, "Day"]

        if day_name in non_working_days:
            df.loc[idx, "Hours Worked"] = 0
            df.loc[idx, "Earned"] = 0
            st.warning(f"⛔ No work logged today ({day_name})")
        else:
            df.loc[idx, "Hours Worked"] = 4
            df.loc[idx, "Earned"] = df.loc[idx, "Hours Worked"] * df.loc[idx, "Hourly Rate"]
            st.success(f"✅ Logged 4 hours for {day_name} ({today})")

        save_data(df)  # <-- SAVE THE DATA
    else:
        st.error(f"⚠️ Today's date ({today}) is not in your worklog table!")

# --- Log missed day ---
missed_date = st.date_input("Pick a missed date to log", min_value=df["Date"].min(), max_value=df["Date"].max())
if st.button("Log Missed Day"):
    if missed_date in df["Date"].values:
        idx = df.index[df["Date"] == missed_date][0]
        day_name = df.loc[idx, "Day"]

        if day_name in non_working_days:
            st.warning(f"⛔ {missed_date} was a non-working day ({day_name})")
        elif df.loc[idx, "Hours Worked"] > 0:
            st.info(f"ℹ️ {missed_date} already logged ({df.loc[idx, 'Hours Worked']} hrs)")
        else:
            df.loc[idx, "Hours Worked"] = 4
            df.loc[idx, "Earned"] = df.loc[idx, "Hours Worked"] * df.loc[idx, "Hourly Rate"]
            st.success(f"✅ Logged 4 hours for {day_name} ({missed_date})")

        save_data(df)  # <-- SAVE THE DATA
    else:
        st.error(f"⚠️ {missed_date} is not in your worklog table!")

# --- NEW: Section to Remove a Log ---
st.subheader("Remove an Accidental Log")
date_to_remove = st.date_input(
    "Pick a date to remove the log from",
    min_value=df["Date"].min(),
    max_value=df["Date"].max(),
    key="remove_date"  # A unique key is good practice
)

if st.button("Remove Log"):
    # Find the row for the selected date
    idx = df.index[df["Date"] == date_to_remove][0]

    # Check if there were any hours logged on that day
    if df.loc[idx, "Hours Worked"] > 0:
        df.loc[idx, "Hours Worked"] = 0.0
        df.loc[idx, "Earned"] = 0.0
        save_data(df)  # <-- IMPORTANT: Save the change
        st.success(f"✅ Log for {date_to_remove} has been removed.")
        st.experimental_rerun()  # Optional: Reruns the script to show the update instantly
    else:
        st.info(f"ℹ️ No hours were logged for {date_to_remove}, so there is nothing to remove.")

# --- Recalculate "To Earn" ---
workdays_mask = ~df["Day"].isin(non_working_days)
# On working days, potential earning is 4 hours. "To Earn" is that potential minus what's already earned.
df.loc[workdays_mask, "To Earn"] = (4 * df.loc[workdays_mask, "Hourly Rate"]) - df.loc[workdays_mask, "Earned"]
# Ensure "To Earn" isn't negative if extra hours were logged somehow
df.loc[df["To Earn"] < 0, "To Earn"] = 0
# Non-working days have 0 "To Earn"
df.loc[~workdays_mask, "To Earn"] = 0

st.session_state.worklog = df

# --- Totals ---
total_earned = df["Earned"].sum()
total_toearn = df["To Earn"].sum()
total = total_earned + total_toearn

st.subheader("Work Log")
st.dataframe(df)

# --- Chart ---
fig = px.pie(
    names=["Earned", "To Earn"],
    values=[total_earned, total_toearn],
    hole=0.5,
    color=["Earned", "To Earn"],
    color_discrete_map={"Earned": "green", "To Earn": "gold"}
)
fig.update_traces(textinfo="label+percent", textfont_size=14)
st.plotly_chart(fig, use_container_width=True)

# --- Totals display ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Earned", f"£{total_earned:.2f}")
col2.metric("Total To Earn", f"£{total_toearn:.2f}")
col3.metric("Overall", f"£{total:.2f}")