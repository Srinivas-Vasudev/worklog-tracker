#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 26 20:10:34 2025

@author: srinivas
"""

import streamlit as st

# Set page title and icon
st.set_page_config(page_title="Trade Discipline Tool", page_icon="📈")

st.title("🛡️ Trade Execution Checklist")
st.markdown("---")

# Section 1: Pre-Flight Context
st.header("Step 1: Market Context")
trend = st.radio("Is the higher timeframe (HTF) trend aligned?", ["Yes", "No", "Ranging"])
news = st.checkbox("Have I checked the economic calendar for red folder news?")

# Section 2: Strategy Criteria (Example: Supply/Demand)
st.header("Step 2: Strategy Validation")
col1, col2 = st.columns(2)

with col1:
    crit_1 = st.checkbox("Price reached HTF Point of Interest (POI)")
    crit_2 = st.checkbox("Lower timeframe (LTF) Change of Character (ChoCh)")

with col2:
    crit_3 = st.checkbox("Fair Value Gap (FVG) or Order Block present")
    crit_4 = st.checkbox("RSI/Indicator divergence confirmed")

# Section 3: Risk Management
st.header("Step 3: Risk Management")
risk_pct = st.number_input("Risk % for this trade", min_value=0.0, max_value=2.0, value=0.5, step=0.1)
rr_ratio = st.number_input("Target Risk:Reward Ratio (e.g., 3 for 1:3)", value=2.0)

# The Logic Gate
all_criteria_met = crit_1 and crit_2 and crit_3 and crit_4 and news and (trend == "Yes")

st.markdown("---")

if all_criteria_met:
    st.success("✅ ALL CRITERIA MET. You have permission to trade.")
    st.balloons()
    
    # Display Summary
    st.info(f"Summary: Risking {risk_pct}% to gain {risk_pct * rr_ratio}%")
else:
    st.warning("⚠️ CRITERIA NOT MET. Step away from the terminal. Do not click 'Buy' or 'Sell'.")
    st.write("Missing requirements:")
    if not crit_1: st.write("- Wait for price to hit your POI.")
    if not crit_2: st.write("- Wait for market structure shift (ChoCh).")
    if trend != "Yes": st.write("- Higher Timeframe trend is not in your favor.")