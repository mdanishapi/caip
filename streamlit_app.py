import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression # Need to import to get coef/intercept
import numpy as np

# --- Configuration & Data Loading ---
st.set_page_config(layout="wide", page_title="Food Security Shock Simulation")

# Load the final processed data
df_final = pd.read_csv("final_results_with_impact_model.csv", index_col='year', parse_dates=True)

# Retrain the model to extract the exact coefficient
# This ensures the deployed app uses the correct parameter
X_train = df_final[['Shock_Index_Pct']]
Y_train = df_final['Kcal_Deviation_Target']
reg_model = LinearRegression()
reg_model.fit(X_train, Y_train)
SHOCK_COEFFICIENT = reg_model.coef_[0]

# --- Dashboard Structure ---

st.title("🇵🇰 Food Security Impact & Scenario Simulator")
st.markdown("Quantifying the systemic availability shock impact on national Kcal utilization (CAIP Final Project).")

# --- Tabs for Structure ---
tab1, tab2, tab3 = st.tabs(["Forecasting Results", "Scenario Simulation", "Model Details"])

with tab1:
    st.header("Actual vs. Shock-Adjusted Forecast")
    st.markdown("The **Total Forecast** includes the calculated impact of the lagged supply shock on the expected baseline trend.")
    
    # Create the comparison plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_final.index, df_final['Kcal_Supply_Target'], marker='o', linestyle='-', color='black', label='Actual Kcal Supply')
    ax.plot(df_final.index, df_final['Kcal_Baseline_Forecast'], marker='^', linestyle='--', color='blue', label='Baseline Forecast (ARIMA)')
    ax.plot(df_final.index, df_final['Kcal_Total_Forecast'], marker='s', linestyle='-', color='red', label='Total Forecast (w/ Shock Impact)')
    
    ax.set_title('National Kcal Supply Forecast Comparison')
    ax.set_xlabel('Year')
    ax.set_ylabel('Food Supply (kcal/capita/day)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    st.pyplot(fig)

with tab2:
    st.header("Policy Scenario Simulation")
    st.markdown("Use the slider to simulate a **hypothetical systemic food supply shock** for the next year and instantly calculate the impact on Kcal supply.")
    
    col_input, col_output = st.columns([1, 1])

    with col_input:
        # User Input for Shock
        simulated_shock = st.slider(
            "Hypothetical Systemic Supply Shock (%)",
            min_value=-20.0,
            max_value=20.0,
            value=-10.0,
            step=0.5,
            format="%.1f%%"
        )
        st.info("The Shock Index is defined as the Lagged Year-over-Year % Change in Total Supply (Production - Stock Variation).")
        
    with col_output:
        # Calculation and Output
        # Impact = Coefficient * Shock
        predicted_deviation = SHOCK_COEFFICIENT * simulated_shock
        
        st.subheader("Quantified Policy Impact")
        st.metric(
            label="Calculated Utilization Deviation",
            value=f"{predicted_deviation:+.2f}",
            delta_color="off",
            help="The predicted change in Kcal/capita/day from the expected baseline."
        )
        
        # Policy interpretation based on the model's actual correlation
        if predicted_deviation > 0:
            interpretation = "The model predicts an **increase** in utilization relative to the baseline. This counter-intuitive result (a negative supply shock leading to higher reported utilization) suggests strong government counter-measures (like stock release) or other systemic factors are currently offsetting supply shocks in the historical data."
            st.success(f"**Predicted Utilization Increase**: +{predicted_deviation:.2f} kcal/capita/day")
        elif predicted_deviation < 0:
            interpretation = "The model predicts a **decrease** in utilization relative to the baseline. This is the expected result, indicating the supply shock has successfully impacted utilization."
            st.error(f"**Predicted Utilization Decrease**: {predicted_deviation:.2f} kcal/capita/day")
        else:
            interpretation = "No predicted deviation from the baseline."
            st.warning("No predicted deviation from the baseline.")
            
        st.caption(interpretation)


with tab3:
    st.header("Model Parameters")
    st.markdown("These are the key parameters used in the two-step modeling approach.")
    
    col_a, col_b = st.columns(2)
    
    col_a.subheader("Module 1: ARIMA Baseline")
    col_a.metric("Model Used", "ARIMA(1, 0, 0)")
    col_a.metric("Baseline Trend", f"{df_final['Kcal_Baseline_Forecast'].mean():.2f} kcal/cap/day (Avg.)")
    col_a.caption("Forecasts the expected Kcal supply based purely on historical time trend.")
    
    col_b.subheader("Module 2: Impact Regression")
    col_b.metric("Model Used", "Linear Regression")
    col_b.metric("Shock Coefficient (B)", f"{SHOCK_COEFFICIENT:+.2f} kcal per 1% shock")
    col_b.metric("Model RMSE (Deviation)", "65.03 kcal/cap/day")
    col_b.caption(f"**Interpretation**: A +1% increase in the lagged Systemic Supply Shock index is quantified as a {SHOCK_COEFFICIENT:+.2f} kcal/capita/day change in utilization.")
