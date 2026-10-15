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

# cases = [
#     ("B767", 100, 50),
#     ("A320", 100, 50),
#     ("B737", 100, 50),
#     ("A319", 100, 50),
#     ("B777", 100, 50),
#     ("B767", 80, 50),
#     ("A320", 80, 50),
#     ("B737", 80, 50),
#     ("A319", 80, 50),
#     ("B777", 80, 50),
# ]

plt.figure(figsize=(14, 7))

# Limits of the plot (they are updated with every case)
max_x = 0           # farthest distance before the IAF (m)
max_h = 0           # highest altitude where the simulation ends (m)
min_h = 100000      # lowest altitude, the IAF (m)

n = 0               # number of the curve (to give it a color)

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

    # Complete curve: from the IAF up to the ceiling
    x_all = []
    h_all = []
    for row in table:
        x_all.append(-row[1])     # negative: before the IAF
        h_all.append(row[2])      # altitude in meters

    # We update the limits of the plot with this case
    if table[last][1] > max_x:    # last row: where the simulation ends
        max_x = table[last][1]
    if table[last][2] > max_h:
        max_h = table[last][2]
    if table[0][2] < min_h:       # first row: the IAF
        min_h = table[0][2]

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

    # Color of this curve (C0, C1, C2... are the normal colors of matplotlib)
    color = "C" + str(n)
    n = n + 1

    # First the thin dashed line (complete curve up to the ceiling of this case)
    plt.plot(x_all, h_all, linestyle="--", linewidth=0.8, color=color)

    # Then the solid line (IAF -> WP) on top, with the same color
    label_plot = airplane.name + " [" + str(weight_pct) + "% MLW] - " + str(distance_nm) + " NM"
    plt.plot(x_wp, h_wp, color=color, label=label_plot)

    print("")
    print(label_plot)
    print("   Ceiling used in the simulation:", ceiling, "m")
    print("   The simulation ends at", round(table[last][1] / NM, 1), "NM before the IAF")
    print("   Altitude at WP:", round(altitude / ft), "ft (", round(altitude), "m )")
    print("   Time WP -> IAF:", round(time / 60, 1), "min")
    if out_of_table == True:
        print("   (The distance is out of the table: the values are extrapolated")
        print("    above the ceiling and this case is not complete in the plot)")

plt.axhline(6000 * ft, color="gray", linestyle="--", linewidth=0.8)    # IAF altitude

# Ceiling of the plot: 14000 m only if all the complete simulations fit
top_h = max_h
if max_h <= 14000:
    plt.axhline(14000, color="gray", linestyle=":", linewidth=0.8)     # ceiling
    top_h = 14000
else:
    print("")
    print("The complete simulations do not fit in 14000 m, the highest ends at", round(max_h), "m")

# Elastic limits: the height ends at the ceiling, the width a bit further
plt.xlim(-max_x * 1.05, max_x * 0.02)
plt.ylim(min_h * 0.95, top_h)

plt.xlabel("x [m]")
plt.ylabel("h [m]")
plt.title("Continuous descent (CDO) until the IAF (x = 0)")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()