from app.client import UrjaClient
import csv
import os


client = UrjaClient()

# -----------------------------
# 1. LOGIN
# -----------------------------

login_result = client.login()

print("Server response:", login_result)
print("Session established:", client.session_established())


# -----------------------------
# 2. GET ALL METERS
# -----------------------------

all_meters = []
page = 1

while True:

    print(f"\nPAGE {page}")
    print("=" * 40)

    result = client.search_meters(page=page)

    meters = result.get("data", [])

    if not meters:
        break

    print("Number of meters:", len(meters))
    print("First meter:", meters[0]["meterId"])
    print("Last meter:", meters[-1]["meterId"])

    all_meters.extend(meters)

    page += 1


print("\nTOTAL METERS:", len(all_meters))


# -----------------------------
# 3. GET DETAILS
# -----------------------------

meter_rows = []
energy_rows = []

for index, meter in enumerate(all_meters, start=1):

    meter_id = meter["meterId"]

    print("\n" + "-" * 40)
    print(f"[{index}/{len(all_meters)}] Processing {meter_id}")

    try:

        details = client.get_meter_details(meter)

        geo = details.get("geo") or {}
        energy = details.get("energy") or []

        print("Geo:", geo)
        print("Energy records:", len(energy))

        # -----------------------------
        # Meter information
        # -----------------------------

        meter_rows.append({
            "meterId": meter.get("meterId"),
            "serialNo": meter.get("serialNo"),
            "make": meter.get("make"),
            "phaseType": meter.get("phaseType"),
            "installStatus": meter.get("installStatus"),
            "dtCode": meter.get("dtCode"),
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
        })

        # -----------------------------
        # Energy information
        # -----------------------------

        for record in energy:

            energy_rows.append({
                "meterId": meter_id,
                "timestamp": record.get("timestamp"),
                "kwh": record.get("kwh"),
                "kvah": record.get("kvah"),
                "voltR": record.get("voltR"),
            })

    except Exception as e:

        print(f"ERROR for {meter_id}: {e}")


# -----------------------------
# 4. CREATE DATA FOLDER
# -----------------------------

os.makedirs("data", exist_ok=True)


# -----------------------------
# 5. SAVE METERS CSV
# -----------------------------

with open(
    "data/meters.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "meterId",
        "serialNo",
        "make",
        "phaseType",
        "installStatus",
        "dtCode",
        "latitude",
        "longitude",
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(meter_rows)


# -----------------------------
# 6. SAVE ENERGY CSV
# -----------------------------

with open(
    "data/energy.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "meterId",
        "timestamp",
        "kwh",
        "kvah",
        "voltR",
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(energy_rows)


# -----------------------------
# 7. FINAL SUMMARY
# -----------------------------

print("\n")
print("=" * 50)
print("EXTRACTION COMPLETE")
print("=" * 50)

print("Meters extracted:", len(meter_rows))
print("Energy records extracted:", len(energy_rows))

print("\nFiles created:")
print("data/meters.csv")
print("data/energy.csv")