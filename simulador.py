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

#Here we introduce the requested cases;

cases = [
    ("B767", 80, 69.7),
    ("B767", 80, 102.6),
    ("A320", 100, 88.6),
    ("B737", 100, 51),
    ("A319", 80, 81.7),
    ("B777", 100, 96.3),
]
"""
cases = [
    ("B767", 100, 50),
    ("A320", 100, 50),
    ("B737", 100, 50),
    ("A319", 100, 50),
    ("B777", 100, 50),
    ("B767", 80, 50),
    ("A320", 80, 50),
    ("B737", 80, 50),
    ("A319", 80, 50),
    ("B777", 80, 50),
]
"""

plt.figure(figsize=(14, 7))

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

    # We simulate the descent with the real weight
    airplane = airplanes[airplane_name]
    weight = (weight_pct / 100) * airplane.max_landing_weight
    table = simulate_cdo(airplane, weight)

    # We read the altitude and the time at the distance of the WP
    altitude, time = result_on_given_distance(table, distance_nm * NM)

    # If the distance is out of the table, we calculate it anyway (only for the console)
    out_of_table = False
    if altitude is None:
        out_of_table = True

        # We use the slope of the last two rows of the table and we continue the line
        t1, x1, alt1, velocity1 = table[-2]
        t2, x2, alt2, velocity2 = table[-1]
        f = (distance_nm * NM - x1) / (x2 - x1)
        altitude = alt1 + f * (alt2 - alt1)
        time = t1 + f * (t2 - t1)

    # Complete curve: from the IAF up to the ceiling (12000 m)
    x_all = []
    h_all = []
    for row in table:
        x_all.append(-row[1])     # negative: before the IAF
        h_all.append(row[2])      # altitude in meters

    # Part of the curve between the IAF and the WP
    x_wp = []
    h_wp = []
    for row in table:
        if row[1] <= distance_nm * NM:
            x_wp.append(-row[1])
            h_wp.append(row[2])

    # We add the exact point of the WP at the end of this part (only if it is in the table)
    if out_of_table == False:
        x_wp.append(-distance_nm * NM)
        h_wp.append(altitude)

    # First the thin dashed line (complete curve up to 12000 m)
    line = plt.plot(x_all, h_all, linestyle="--", linewidth=0.8)
    color = line[0].get_color()

    # Then the solid line (IAF -> WP) on top, with the same color
    label_plot = f"{airplane.name} [{weight_pct}% MLW] - {distance_nm} NM"
    plt.plot(x_wp, h_wp, color=color, label=label_plot)

    print("\n", label_plot)
    print(f"   Altitude at WP: {altitude / ft:.0f} ft ({altitude:.0f} m)")
    print(f"   Time WP -> IAF: {time / 60:.1f} min")
    if out_of_table:
        print("   (The distance is out of the table: the values are extrapolated")
        print("    above 12000 m and this case is not complete in the plot)")

plt.axhline(6000 * ft, color="gray", linestyle="--", linewidth=0.8)    # IAF altitude
plt.axhline(12000, color="gray", linestyle=":", linewidth=0.8)         # ceiling
plt.xlabel("x [m]")
plt.ylabel("h [m]")
plt.title("Continuous descent (CDO) until the IAF (x = 0)")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()