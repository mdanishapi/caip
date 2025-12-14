
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration & Data Loading ---
st.set_page_config(layout="wide", page_title="Food Security Shock Simulation")

# Hardcoding the calculated parameters for deployment robustness
SHOCK_COEFFICIENT = -0.0987 
RMSE_VALUE = 0.69

# Load the final processed data
output_file_name = "processed_national_food_security_data_updated.csv"
try:
    # Ensure the dataframe is loaded with the correct index and types for plotting
    df_final = pd.read_csv(output_file_name, index_col='year', parse_dates=True)
except FileNotFoundError:
    st.error(f"Error: The processed data file ('{output_file_name}') was not found. Please ensure it is in the deployment folder.")
    st.stop()

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
        st.info("The Shock Index is defined as the Lagged Year-over-Year % Change in Total Supply (Production + Imports - Exports - Stock Variation).")

    with col_output:
        # Calculation is performed live within the Streamlit app execution context
        predicted_deviation = SHOCK_COEFFICIENT * simulated_shock

        st.subheader("Quantified Policy Impact")
        st.metric(
            label="Calculated Utilization Deviation",
            value=f"{predicted_deviation:+.2f}",
            delta_color="off",
            help="The predicted change in Kcal/capita/day from the expected baseline."
        )

        # Policy interpretation based on the model's actual correlation
        if SHOCK_COEFFICIENT < 0:
            if simulated_shock < 0: # Negative shock (e.g., -10% loss)
                interpretation = "The model suggests a resilient response: a negative supply shock is predicted to lead to a **higher** reported utilization relative to the baseline. This implies that strong government counter-measures (like stock release) or market adaptations successfully **overshot** the negative shock in the historical data."
                st.success(f"**Predicted Utilization Effect**: +{abs(predicted_deviation):.2f} kcal/capita/day (Higher than Baseline)")
            elif simulated_shock > 0: # Positive shock (e.g., +10% surplus)
                interpretation = "The model predicts a **lower** utilization relative to the baseline for a positive shock. This is often interpreted as market saturation or storage limits preventing the full utilization of the surplus in that year."
                st.error(f"**Predicted Utilization Effect**: -{abs(predicted_deviation):.2f} kcal/capita/day (Lower than Baseline)")
            else:
                interpretation = "No predicted deviation from the baseline."
                st.warning("No predicted deviation from the baseline.")
        else: # If the coefficient were positive (which implies no resilience/expected correlation)
            if simulated_shock > 0:
                interpretation = "The model predicts an increase in utilization, which is the expected result of a supply surplus."
                st.success(f"**Predicted Utilization Increase**: +{predicted_deviation:.2f} kcal/capita/day")
            elif simulated_shock < 0:
                interpretation = "The model predicts a decrease in utilization, which is the expected result of a supply loss."
                st.error(f"**Predicted Utilization Decrease**: {predicted_deviation:.2f} kcal/capita/day")
            else:
                interpretation = "No predicted deviation from the baseline."
                st.warning("No predicted deviation from the baseline.")

        st.caption(interpretation)


with tab3:
    st.header("Model Parameters")
    st.markdown("These are the key parameters used in the two-step modeling approach.")
    

[Image of Linear Regression Model Parameters]


    col_a, col_b = st.columns(2)

    col_a.subheader("Module 1: ARIMA Baseline")
    col_a.metric("Model Used", "ARIMA(1, 0, 0)")
    # Note: Kcal Baseline Avg needs the dataframe, which is loaded above.
    col_a.metric("Baseline Trend", f"{df_final['Kcal_Baseline_Forecast'].mean():.2f} kcal/cap/day (Avg.)")
    col_a.caption("Forecasts the expected Kcal supply based purely on historical time trend.")

    col_b.subheader("Module 2: Impact Regression")
    col_b.metric("Model Used", "Linear Regression")
    col_b.metric("Shock Coefficient (B)", f"{SHOCK_COEFFICIENT:+.4f} kcal per 1% shock")
    col_b.metric("Model RMSE (Deviation)", f"{RMSE_VALUE:.2f} kcal/cap/day")
    col_b.caption(f"**Interpretation**: A +1% increase in the lagged Systemic Supply Shock index is quantified as a {SHOCK_COEFFICIENT:+.4f} kcal/capita/day change in utilization.")
