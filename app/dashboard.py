import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Urja Meter Analytics",
    page_icon="⚡",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

meters = pd.read_csv("data/meters.csv")
energy = pd.read_csv("data/energy.csv")
analysis = pd.read_csv("data/meter_analysis.csv")


# ============================================================
# DATA PREPARATION
# ============================================================

# Convert timestamp
energy["timestamp"] = pd.to_datetime(
    energy["timestamp"],
    dayfirst=True,
    errors="coerce"
)

# Convert numeric columns
energy["kwh"] = pd.to_numeric(
    energy["kwh"],
    errors="coerce"
)

energy["kvah"] = pd.to_numeric(
    energy["kvah"],
    errors="coerce"
)

energy["voltR"] = pd.to_numeric(
    energy["voltR"],
    errors="coerce"
)

analysis["kwh_consumption"] = pd.to_numeric(
    analysis["kwh_consumption"],
    errors="coerce"
)

analysis["avg_voltage"] = pd.to_numeric(
    analysis["avg_voltage"],
    errors="coerce"
)


# ============================================================
# CALCULATE ACTUAL ENERGY CONSUMPTION
# ============================================================

# Sort readings by meter and timestamp
energy = energy.sort_values(
    ["meterId", "timestamp"]
)

# Calculate consumption between consecutive readings
energy["consumption"] = (
    energy.groupby("meterId")["kwh"].diff()
)


# ============================================================
# TITLE
# ============================================================

st.title("⚡ Urja Meter Analytics Dashboard")

st.markdown(
    "Interactive analysis of meter installation, "
    "energy consumption and voltage data."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")


# ------------------------------------------------------------
# Installation Status
# ------------------------------------------------------------

status_options = sorted(
    meters["installStatus"].dropna().unique()
)

selected_status = st.sidebar.multiselect(
    "Installation Status",
    status_options,
    default=status_options
)


# ------------------------------------------------------------
# Manufacturer
# ------------------------------------------------------------

make_options = sorted(
    meters["make"].dropna().unique()
)

selected_make = st.sidebar.multiselect(
    "Meter Manufacturer",
    make_options,
    default=make_options
)


# ------------------------------------------------------------
# Phase Type
# ------------------------------------------------------------

phase_options = sorted(
    meters["phaseType"].dropna().unique()
)

selected_phase = st.sidebar.multiselect(
    "Phase Type",
    phase_options,
    default=phase_options
)


# ============================================================
# FILTER METER DATA
# ============================================================

filtered_meters = meters[
    meters["installStatus"].isin(selected_status)
    & meters["make"].isin(selected_make)
    & meters["phaseType"].isin(selected_phase)
].copy()


# ============================================================
# FILTER ANALYSIS DATA
# ============================================================

filtered_analysis = analysis[
    analysis["meterId"].isin(
        filtered_meters["meterId"]
    )
].copy()


# ============================================================
# FILTER ENERGY DATA
# ============================================================

filtered_energy = energy[
    energy["meterId"].isin(
        filtered_meters["meterId"]
    )
].copy()


# ============================================================
# EMPTY FILTER CHECK
# ============================================================

if filtered_meters.empty:

    st.warning(
        "No meters match the selected filters. "
        "Please select at least one value from each filter."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_meters = len(filtered_meters)

total_energy_records = len(filtered_energy)

total_consumption = filtered_analysis[
    "kwh_consumption"
].sum()

avg_consumption = filtered_analysis[
    "kwh_consumption"
].mean()


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Meters",
    f"{total_meters:,}"
)

col2.metric(
    "Energy Records",
    f"{total_energy_records:,}"
)

col3.metric(
    "Total Consumption",
    f"{total_consumption:,.2f} kWh"
)

col4.metric(
    "Avg Consumption / Meter",
    f"{avg_consumption:,.2f} kWh"
)


# ============================================================
# INSTALLATION STATUS
# ============================================================

st.subheader("📊 Meter Installation Status")

status_data = (
    filtered_meters["installStatus"]
    .value_counts()
    .reset_index()
)

status_data.columns = [
    "installStatus",
    "count"
]

fig_status = px.bar(
    status_data,
    x="installStatus",
    y="count",
    text="count",
    title="Meters by Installation Status"
)

fig_status.update_layout(
    xaxis_title="Installation Status",
    yaxis_title="Number of Meters"
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)


# ============================================================
# TWO COLUMN ANALYSIS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# MANUFACTURER
# ------------------------------------------------------------

with col1:

    st.subheader("🏭 Meters by Manufacturer")

    make_data = (
        filtered_meters["make"]
        .value_counts()
        .reset_index()
    )

    make_data.columns = [
        "make",
        "count"
    ]

    fig_make = px.bar(
        make_data,
        x="make",
        y="count",
        text="count",
        title="Meter Distribution by Manufacturer"
    )

    fig_make.update_layout(
        xaxis_title="Manufacturer",
        yaxis_title="Number of Meters"
    )

    st.plotly_chart(
        fig_make,
        use_container_width=True
    )


# ------------------------------------------------------------
# PHASE TYPE
# ------------------------------------------------------------

with col2:

    st.subheader("⚡ Meters by Phase Type")

    phase_data = (
        filtered_meters["phaseType"]
        .value_counts()
        .reset_index()
    )

    phase_data.columns = [
        "phaseType",
        "count"
    ]

    fig_phase = px.pie(
        phase_data,
        names="phaseType",
        values="count",
        title="Single vs Three Phase Meters"
    )

    st.plotly_chart(
        fig_phase,
        use_container_width=True
    )


# ============================================================
# CONSUMPTION ANALYSIS
# ============================================================

st.subheader("⚡ Consumption Analysis")


# ------------------------------------------------------------
# CONSUMPTION BY INSTALLATION STATUS
# ------------------------------------------------------------

consumption_status = (
    filtered_analysis
    .groupby("installStatus")["kwh_consumption"]
    .agg(
        count="count",
        mean="mean",
        total="sum"
    )
    .reset_index()
)

fig_consumption_status = px.bar(
    consumption_status,
    x="installStatus",
    y="total",
    text_auto=".2f",
    title="Total Consumption by Installation Status"
)

fig_consumption_status.update_layout(
    xaxis_title="Installation Status",
    yaxis_title="Total kWh"
)

st.plotly_chart(
    fig_consumption_status,
    use_container_width=True
)


# ------------------------------------------------------------
# CONSUMPTION BY MANUFACTURER
# ------------------------------------------------------------

make_consumption = (
    filtered_analysis
    .groupby("make")["kwh_consumption"]
    .agg(
        count="count",
        mean="mean",
        total="sum"
    )
    .reset_index()
)

fig_consumption_make = px.bar(
    make_consumption,
    x="make",
    y="total",
    text_auto=".2f",
    title="Total Consumption by Manufacturer"
)

fig_consumption_make.update_layout(
    xaxis_title="Manufacturer",
    yaxis_title="Total kWh"
)

st.plotly_chart(
    fig_consumption_make,
    use_container_width=True
)


# ============================================================
# CONSUMPTION BY PHASE
# ============================================================

phase_consumption = (
    filtered_analysis
    .groupby("phaseType")["kwh_consumption"]
    .agg(
        count="count",
        mean="mean",
        total="sum"
    )
    .reset_index()
)

fig_phase_consumption = px.bar(
    phase_consumption,
    x="phaseType",
    y="mean",
    text_auto=".2f",
    title="Average Consumption by Phase Type"
)

fig_phase_consumption.update_layout(
    xaxis_title="Phase Type",
    yaxis_title="Average kWh per Meter"
)

st.plotly_chart(
    fig_phase_consumption,
    use_container_width=True
)


# ============================================================
# DAILY ENERGY TREND
# ============================================================

st.subheader("📈 Daily Energy Consumption Trend")

trend_data = filtered_energy.dropna(
    subset=["timestamp", "consumption"]
).copy()


if not trend_data.empty:

    # Extract date
    trend_data["date"] = (
        trend_data["timestamp"].dt.date
    )

    # Sum actual interval consumption
    daily_consumption = (
        trend_data
        .groupby("date")["consumption"]
        .sum()
        .reset_index()
    )

    daily_consumption.columns = [
        "date",
        "total_kwh"
    ]

    fig_trend = px.line(
        daily_consumption,
        x="date",
        y="total_kwh",
        markers=True,
        title="Daily Energy Consumption"
    )

    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily Consumption (kWh)"
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )

else:

    st.info(
        "No valid energy consumption data available "
        "for the selected filters."
    )


# ============================================================
# VOLTAGE ANALYSIS
# ============================================================

st.subheader("🔌 Voltage Analysis")

voltage_avg = filtered_analysis[
    "avg_voltage"
].mean()

voltage_min = filtered_analysis[
    "avg_voltage"
].min()

voltage_max = filtered_analysis[
    "avg_voltage"
].max()


col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Voltage",
    f"{voltage_avg:.2f} V"
)

col2.metric(
    "Minimum Voltage",
    f"{voltage_min:.2f} V"
)

col3.metric(
    "Maximum Voltage",
    f"{voltage_max:.2f} V"
)


# ------------------------------------------------------------
# Voltage Distribution
# ------------------------------------------------------------

fig_voltage = px.histogram(
    filtered_analysis,
    x="avg_voltage",
    nbins=20,
    title="Voltage Distribution"
)

fig_voltage.update_layout(
    xaxis_title="Average Voltage (V)",
    yaxis_title="Number of Meters"
)

st.plotly_chart(
    fig_voltage,
    use_container_width=True
)


# ============================================================
# FAULTY METERS
# ============================================================

st.subheader("🚨 Faulty Meter Analysis")

faulty = filtered_analysis[
    filtered_analysis["installStatus"] == "Faulty"
]

faulty_count = len(faulty)

faulty_avg_consumption = faulty[
    "kwh_consumption"
].mean()


col1, col2 = st.columns(2)

col1.metric(
    "Faulty Meters",
    f"{faulty_count:,}"
)


if faulty_count > 0:

    col2.metric(
        "Avg Faulty Meter Consumption",
        f"{faulty_avg_consumption:.2f} kWh"
    )

else:

    col2.metric(
        "Avg Faulty Meter Consumption",
        "N/A"
    )


# ============================================================
# TOP 10 CONSUMERS
# ============================================================

st.subheader("🏆 Top 10 Consuming Meters")

top10 = (
    filtered_analysis
    .sort_values(
        "kwh_consumption",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    top10[
        [
            "meterId",
            "make",
            "phaseType",
            "installStatus",
            "kwh_consumption",
            "avg_voltage"
        ]
    ],
    use_container_width=True
)


# ============================================================
# LOWEST 10 CONSUMERS
# ============================================================

st.subheader("📉 Lowest 10 Consuming Meters")

bottom10 = (
    filtered_analysis
    .sort_values(
        "kwh_consumption",
        ascending=True
    )
    .head(10)
)

st.dataframe(
    bottom10[
        [
            "meterId",
            "make",
            "phaseType",
            "installStatus",
            "kwh_consumption",
            "avg_voltage"
        ]
    ],
    use_container_width=True
)


# ============================================================
# FILTERED ENERGY DATA
# ============================================================

with st.expander("⚡ View Filtered Energy Data"):

    st.write(
        f"Showing {len(filtered_energy):,} energy records"
    )

    st.dataframe(
        filtered_energy,
        use_container_width=True
    )


# ============================================================
# FILTERED METER DATA
# ============================================================

with st.expander("📋 View Filtered Meter Data"):

    st.write(
        f"Showing {len(filtered_analysis):,} meters"
    )

    st.dataframe(
        filtered_analysis,
        use_container_width=True
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.subheader("📥 Download Filtered Data")

col1, col2 = st.columns(2)


with col1:

    meter_csv = filtered_analysis.to_csv(
        index=False
    )

    st.download_button(
        label="Download Meter Analysis CSV",
        data=meter_csv,
        file_name="filtered_meter_analysis.csv",
        mime="text/csv"
    )


with col2:

    energy_csv = filtered_energy.to_csv(
        index=False
    )

    st.download_button(
        label="Download Energy Data CSV",
        data=energy_csv,
        file_name="filtered_energy.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Urja Meter Analytics | Data Analysis & Visualization Project"
)