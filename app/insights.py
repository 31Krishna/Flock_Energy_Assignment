import pandas as pd


# Load analyzed data
df = pd.read_csv("data/meter_analysis.csv")


print("\n==============================")
print("BUSINESS INSIGHTS")
print("==============================")


# 1. Overall consumption
total_consumption = df["kwh_consumption"].sum()

print("\n1. TOTAL KWH CONSUMPTION")
print("------------------------------")
print(round(total_consumption, 2), "kWh")


# 2. Average consumption
average_consumption = df["kwh_consumption"].mean()

print("\n2. AVERAGE CONSUMPTION PER METER")
print("------------------------------")
print(round(average_consumption, 2), "kWh")


# 3. Consumption by meter status
status_consumption = (
    df.groupby("installStatus")["kwh_consumption"]
    .agg(["count", "mean", "sum"])
    .reset_index()
)

print("\n3. CONSUMPTION BY INSTALLATION STATUS")
print("------------------------------")
print(status_consumption.to_string(index=False))


# 4. Consumption by manufacturer
make_consumption = (
    df.groupby("make")["kwh_consumption"]
    .agg(["count", "mean", "sum"])
    .reset_index()
    .sort_values("sum", ascending=False)
)

print("\n4. CONSUMPTION BY METER MAKE")
print("------------------------------")
print(make_consumption.to_string(index=False))


# 5. Phase comparison
phase_consumption = (
    df.groupby("phaseType")["kwh_consumption"]
    .agg(["count", "mean", "sum"])
    .reset_index()
)

print("\n5. CONSUMPTION BY PHASE TYPE")
print("------------------------------")
print(phase_consumption.to_string(index=False))


# 6. High consumption meters
high_consumption = df[
    df["kwh_consumption"] >=
    df["kwh_consumption"].quantile(0.90)
]

print("\n6. HIGH CONSUMPTION METERS")
print("------------------------------")
print(
    "Meters above 90th percentile:",
    len(high_consumption)
)


# 7. Low consumption meters
low_consumption = df[
    df["kwh_consumption"] <=
    df["kwh_consumption"].quantile(0.10)
]

print("\n7. LOW CONSUMPTION METERS")
print("------------------------------")
print(
    "Meters below 10th percentile:",
    len(low_consumption)
)


# 8. Voltage analysis
print("\n8. VOLTAGE INSIGHTS")
print("------------------------------")

print(
    "Average:",
    round(df["avg_voltage"].mean(), 2),
    "V"
)

print(
    "Minimum:",
    df["avg_voltage"].min(),
    "V"
)

print(
    "Maximum:",
    df["avg_voltage"].max(),
    "V"
)


# 9. Faulty meters with consumption
faulty = df[
    df["installStatus"] == "Faulty"
]

print("\n9. FAULTY METERS")
print("------------------------------")

print(
    "Faulty meters:",
    len(faulty)
)

print(
    "Average faulty-meter consumption:",
    round(faulty["kwh_consumption"].mean(), 2),
    "kWh"
)


# 10. Top 10 meters
print("\n10. TOP 10 CONSUMING METERS")
print("------------------------------")

top10 = (
    df.sort_values(
        "kwh_consumption",
        ascending=False
    )
    .head(10)
)

print(
    top10[
        [
            "meterId",
            "make",
            "phaseType",
            "installStatus",
            "kwh_consumption",
            "avg_voltage",
        ]
    ].to_string(index=False)
)


print("\n==============================")
print("INSIGHTS ANALYSIS COMPLETE")
print("==============================")