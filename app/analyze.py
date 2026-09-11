import pandas as pd


# -----------------------------
# LOAD DATA
# -----------------------------

meters = pd.read_csv("data/meters.csv")
energy = pd.read_csv("data/energy.csv")


# -----------------------------
# BASIC INFORMATION
# -----------------------------

print("\n==============================")
print("DATASET SUMMARY")
print("==============================")

print("Total meters:", len(meters))
print("Total energy records:", len(energy))

print("\nMeter columns:")
print(meters.columns.tolist())

print("\nEnergy columns:")
print(energy.columns.tolist())


# -----------------------------
# METER STATUS ANALYSIS
# -----------------------------

print("\n==============================")
print("METER STATUS")
print("==============================")

print(meters["installStatus"].value_counts())


# -----------------------------
# METER MAKE ANALYSIS
# -----------------------------

print("\n==============================")
print("METER MAKE")
print("==============================")

print(meters["make"].value_counts())


# -----------------------------
# PHASE TYPE ANALYSIS
# -----------------------------

print("\n==============================")
print("PHASE TYPE")
print("==============================")

print(meters["phaseType"].value_counts())


# -----------------------------
# ENERGY DATA CLEANING
# -----------------------------

energy["timestamp"] = pd.to_datetime(
    energy["timestamp"],
    dayfirst=True
)

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


# -----------------------------
# ENERGY SUMMARY PER METER
# -----------------------------

energy_summary = (
    energy
    .groupby("meterId")
    .agg(
        first_kwh=("kwh", "first"),
        last_kwh=("kwh", "last"),
        first_kvah=("kvah", "first"),
        last_kvah=("kvah", "last"),
        avg_voltage=("voltR", "mean"),
        energy_records=("meterId", "count"),
    )
    .reset_index()
)


# -----------------------------
# CALCULATE CONSUMPTION
# -----------------------------

energy_summary["kwh_consumption"] = (
    energy_summary["last_kwh"]
    - energy_summary["first_kwh"]
)

energy_summary["kvah_consumption"] = (
    energy_summary["last_kvah"]
    - energy_summary["first_kvah"]
)


# -----------------------------
# COMBINE METER + ENERGY DATA
# -----------------------------

analysis = meters.merge(
    energy_summary,
    on="meterId",
    how="left"
)


# -----------------------------
# TOP CONSUMING METERS
# -----------------------------

print("\n==============================")
print("TOP 10 CONSUMING METERS")
print("==============================")

top_consumers = (
    analysis
    .sort_values(
        "kwh_consumption",
        ascending=False
    )
    .head(10)
)

print(
    top_consumers[
        [
            "meterId",
            "make",
            "installStatus",
            "kwh_consumption",
            "avg_voltage",
        ]
    ].to_string(index=False)
)


# -----------------------------
# LOW CONSUMING METERS
# -----------------------------

print("\n==============================")
print("LOWEST 10 CONSUMING METERS")
print("==============================")

low_consumers = (
    analysis
    .sort_values(
        "kwh_consumption",
        ascending=True
    )
    .head(10)
)

print(
    low_consumers[
        [
            "meterId",
            "make",
            "installStatus",
            "kwh_consumption",
            "avg_voltage",
        ]
    ].to_string(index=False)
)


# -----------------------------
# AVERAGE VOLTAGE
# -----------------------------

print("\n==============================")
print("VOLTAGE ANALYSIS")
print("==============================")

print(
    "Overall average voltage:",
    round(energy["voltR"].mean(), 2)
)

print(
    "Minimum voltage:",
    energy["voltR"].min()
)

print(
    "Maximum voltage:",
    energy["voltR"].max()
)


# -----------------------------
# SAVE ANALYSIS DATA
# -----------------------------

analysis.to_csv(
    "data/meter_analysis.csv",
    index=False
)

print("\n==============================")
print("ANALYSIS COMPLETE")
print("==============================")

print("Created:")
print("data/meter_analysis.csv")