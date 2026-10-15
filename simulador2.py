from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from Airplanes import *                                      # airplanes
from functions_aircrafts import simulate_cdo, result_on_given_distance

NM = 1852        # 1 nautical mile in meters
ft = 0.3048      # 1 ft in meters

airplanes = {
    "B767": B767,
    "B777": B777,
    "B737": B737,
    "A320": A320,
    "A319": A319,
}

# Here we introduce the requested cases;
cases = [
    ("B767", 80, 69.7),
    ("B767", 80, 102.6),
    ("A320", 100, 88.6),
    ("B737", 100, 51),
    ("A319", 80, 81.7),
    ("B777", 100, 96.3),
]

# Fixed STAR entry time for Scenario 1
t_start_esc1 = datetime.strptime("11:45:00", "%H:%M:%S")

# Here we save the data of every flight
flight_list = []

for case in cases:

    # We read the three data of the case
    airplane_name = case[0]
    weight_pct = case[1]
    distance_nm = case[2]

    # We check that the data makes sense
    if airplane_name not in airplanes:
        print("Error: the airplane", airplane_name, "does not exist")
        continue
    if weight_pct < 50 or weight_pct > 100:
        print("Error: weight must be between 50 and 100 % MLW (case", case, ")")
        continue
    if distance_nm < 1 or distance_nm > 300:
        print("Error: distance must be between 1 and 300 NM (case", case, ")")
        continue

    # We simulate the descent with the real weight, with the normal ceiling (12000 m)
    airplane = airplanes[airplane_name]
    weight = (weight_pct / 100) * airplane.max_landing_weight
    ceiling = 12000
    table = simulate_cdo(airplane, weight, 1.0, ceiling)

    # We read the altitude and the time at the distance of the WP
    altitude, time = result_on_given_distance(table, distance_nm * NM)

    # If the WP is beyond the table, we raise the ceiling 500 m and we simulate again
    while altitude is None and ceiling < 16000:
        ceiling = ceiling + 500
        table = simulate_cdo(airplane, weight, 1.0, ceiling)
        altitude, time = result_on_given_distance(table, distance_nm * NM)

    # Position of the last row of the table
    last = len(table) - 1

    # If it is still out of the table (ceiling of 16000 m reached), we calculate it anyway
    out_of_table = False
    if altitude is None:
        out_of_table = True

        # We use the last two rows of the table and we continue the line
        row_1 = table[last - 1]
        row_2 = table[last]
        t1 = row_1[0]
        x1 = row_1[1]
        alt1 = row_1[2]
        t2 = row_2[0]
        x2 = row_2[1]
        alt2 = row_2[2]
        f = (distance_nm * NM - x1) / (x2 - x1)
        altitude = alt1 + f * (alt2 - alt1)
        time = t1 + f * (t2 - t1)

    # Scenario 1: arrival time at the IAF
    t_iaf_esc1 = t_start_esc1 + timedelta(seconds=time)

    # We save everything we need of this flight
    label_plot = airplane.name + " [" + str(weight_pct) + "% MLW] - " + str(distance_nm) + " NM"
    flight = {
        "label": label_plot,
        "flight_time_s": time,
        "t_iaf_esc1": t_iaf_esc1,
        "table": table,
        "distance_nm": distance_nm,
        "altitude": altitude,
        "out_of_table": out_of_table,
    }
    flight_list.append(flight)

# We sort the flights by arrival time at the IAF (from the earliest to the latest)
n_flights = len(flight_list)
for i in range(n_flights):
    for j in range(n_flights - 1 - i):
        if flight_list[j]["t_iaf_esc1"] > flight_list[j + 1]["t_iaf_esc1"]:
            temp = flight_list[j]
            flight_list[j] = flight_list[j + 1]
            flight_list[j + 1] = temp

# Scenario 2: 2 minutes of separation between consecutive flights at the IAF
for i in range(n_flights):
    flight = flight_list[i]

    if i == 0:
        # The first flight keeps its arrival time of the scenario 1
        flight["t_iaf_esc2"] = flight["t_iaf_esc1"]
    else:
        # Every other flight arrives 2 minutes after the previous one
        previous = flight_list[i - 1]
        flight["t_iaf_esc2"] = previous["t_iaf_esc2"] + timedelta(minutes=2)

    # Time when the aircraft must enter the STAR in Scenario 2
    flight["t_star_esc2"] = flight["t_iaf_esc2"] - timedelta(seconds=flight["flight_time_s"])

# Results of the scenario 2 in the console
for flight in flight_list:
    print("")
    print(flight["label"])
    print("   Flight time:", round(flight["flight_time_s"] / 60, 2), "min")
    print("   STAR Entry (Scenario 2):", flight["t_star_esc2"].strftime("%H:%M:%S"))
    print("   IAF Arrival (Scenario 2):", flight["t_iaf_esc2"].strftime("%H:%M:%S"))
    if flight["out_of_table"] == True:
        print("   (The distance is out of the table: the values are extrapolated")
        print("    above the ceiling and this case is not complete in the plot)")

plt.figure(figsize=(14, 7))

# Limits of the plot (they are updated with every flight)
max_h = 0           # highest altitude where the simulation ends (m)
min_h = 100000      # lowest altitude, the IAF (m)

n = 0               # number of the curve (to give it a color)

for flight in flight_list:

    # We read the data of this flight
    table = flight["table"]
    distance_nm = flight["distance_nm"]
    t_iaf = flight["t_iaf_esc2"]
    last = len(table) - 1

    # Complete curve: from the IAF up to the ceiling (the time goes backwards from the IAF)
    t_abs_all = []
    h_all = []
    for row in table:
        t_abs_all.append(t_iaf - timedelta(seconds=row[0]))
        h_all.append(row[2])      # altitude in meters

    # We update the limits of the plot with this flight
    if table[last][2] > max_h:    # last row: where the simulation ends
        max_h = table[last][2]
    if table[0][2] < min_h:       # first row: the IAF
        min_h = table[0][2]

    # Part of the curve between the STAR entry and the IAF
    t_abs_wp = []
    h_wp = []
    for row in table:
        if row[1] <= distance_nm * NM:
            t_abs_wp.append(t_iaf - timedelta(seconds=row[0]))
            h_wp.append(row[2])

    # We add the exact point of the STAR entry at the end of this part (only if it is in the table)
    if flight["out_of_table"] == False:
        t_abs_wp.append(t_iaf - timedelta(seconds=flight["flight_time_s"]))
        h_wp.append(flight["altitude"])

    # Color of this curve (C0, C1, C2... are the normal colors of matplotlib)
    color = "C" + str(n)
    n = n + 1

    # First the thin dashed line (complete curve up to the ceiling of this flight)
    plt.plot(t_abs_all, h_all, linestyle="--", linewidth=0.8, color=color)

    # Then the solid line (STAR entry -> IAF) on top, with the same color
    label_plot = flight["label"] + " (IAF: " + t_iaf.strftime("%H:%M:%S") + ")"
    plt.plot(t_abs_wp, h_wp, color=color, label=label_plot)

plt.axhline(6000 * ft, color="gray", linestyle="--", linewidth=0.8)    # IAF altitude

# Ceiling of the plot: 14000 m only if all the complete simulations fit
top_h = max_h
if max_h <= 14000:
    plt.axhline(14000, color="gray", linestyle=":", linewidth=0.8)     # ceiling
    top_h = 14000
else:
    print("")
    print("The complete simulations do not fit in 14000 m, the highest ends at", round(max_h), "m")

# Elastic limits: the height ends at the ceiling
plt.ylim(min_h * 0.95, top_h)

plt.xlabel("Time of the arrival (HH:MM:SS)")
plt.ylabel("Altitude [m]")
plt.title("Optimisation of arrival sequencing at the IAF (2-minute separation)")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()