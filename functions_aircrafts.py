import math
import matplotlib.pyplot as plt
from Airplanes import *

# ------------------------------------------------------------
# International standard atmosphere
# ------------------------------------------------------------
g = 9.80665          # gravity (m/s^2)
R = 287.05287        # air constant (J/(kg K))
T0 = 288.15          # sea level temp. (K)
rho0 = 1.225         # sea level density (kg/m^3)
ft = 0.3048          # 1 ft in meters
p0 = 101325          # isa sea level pressure (Pa)

#ISA IMPORTANT ALTITUDE DEPENDENT DATA

def isa_temperature(altitude):
    if altitude <= 11000:
        return T0-0.0065*altitude
    else:
        return  216.65

def isa_pressure(altitude):
    if altitude <= 11000:
        return  p0*((1-0.0065*(altitude/T0))**5.2561)
    else:
        return 22632*math.e**((-g/(R*216.65))*(altitude-11000))

def isa_air_density(altitude):
    return isa_pressure(altitude)/(R*isa_temperature(altitude))

#Aircraft's idle thrust
def idle_thrust(aircraft, altitude):
    max_thrust = aircraft.CT1*(1-(altitude/aircraft.CT2)+aircraft.CT3*(altitude**2))
    if altitude > aircraft.hp_desc:
        return aircraft.CT_desc_high*max_thrust
    else:
        if altitude <= (6000 * ft):
            return aircraft.CT_desc_app*max_thrust
        else:
            return aircraft.CT_desc_low*max_thrust

# Now we calculate the ROD from altitude and aircraft data
def calculate_rod(aircraft,mass, altitude, velocity):
    rho = isa_air_density(altitude)
    W = mass*g
    Cl = (2*W) / ((rho*velocity**2)*aircraft.S)
    if altitude <= (6000 * ft):
        Cd = aircraft.CD0_clean + aircraft.CD2_clean * (Cl ** 2)
    else:
        Cd = aircraft.CD0_app + aircraft.CD2_app * (Cl ** 2)
    D = 0.5 * rho * (velocity ** 2) * aircraft.S * Cd
    T = idle_thrust(aircraft, altitude)
    sin_gamma = (D - T) / W
    ROD = velocity * sin_gamma                              # m/s (positive = decreasing)
    return ROD, sin_gamma

# We obtain the velocity that minimizes ROD
def min_rod_velocity(aircraft, mass, altitude):
    rho = isa_air_density(altitude)
    W = mass * g
    T = idle_thrust(aircraft, altitude)
    if altitude <= (6000 * ft):
        v_min_rod = ((T + (T ** 2 + 12 * aircraft.CD0_clean * aircraft.CD2_clean * (W ** 2)) ** 0.5) / (3 * rho * aircraft.S * aircraft.CD0_clean)) ** 0.5
    else:
        v_min_rod = ((T + (T ** 2 + 12 * aircraft.CD0_app * aircraft.CD2_app * (W ** 2)) ** 0.5) / (3 * rho * aircraft.S * aircraft.CD0_app)) ** 0.5
    return v_min_rod

# Descent simulator in reverse in time
# Start at IAF (6000 ft, distance 0, time 0) and increasing in reverse.
# This allows us to know the exact altitude at which each aircraft at each distance/ time before IAF
def simulate_cdo(aircraft, mass, dt=1.0):
    max_alt = 12000
    alt = 6000 * ft          # altitude at IAF (m)
    x = 0.0                # travelled distance before IAF (m)
    t = 0.0                # time before IAF (s)

    table = []             # each row: (t, x, alt, velocity)
    while alt < max_alt:
        velocity = min_rod_velocity(aircraft, mass, alt)
        rod, sin_gamma = calculate_rod(aircraft,mass, alt, velocity)
        table.append((t, x, alt, velocity))
        gamma = math.asin(sin_gamma)
        x += velocity * math.cos(gamma) * dt     # we go back in distance
        alt += rod * dt                     # we go back in height
        t += dt
    return table

#read the table --> altitude and time for a given distance
def result_on_given_distance(table, distance):
    """Returns (altitude in m, time to reach IAF) at the given distance to the IAF."""
    for i in range(1, len(table)):
        if table[i][1] >= distance:
            t1, x1, alt1, velocity1 = table[i - 1]
            t2, x2, alt2, velocity2 = table[i]
            f = (distance - x1) / (x2 - x1)      # linear interpolation
            return alt1 + f * (alt2 - alt1), t1 + f * (t2 - t1)
    return None, None                                # larger distance

def ask_option(text, options):
    """Asks until the user writes one of the options."""
    options = list(options)
    while True:
        a = input(f"{text} {options}: ").strip().upper()
        if a in options:
            return a
        print("Not valid, try again")


def ask_for_number(text, minimum, maximum):
    """Asks until the user writes a number between [minimum, maximum]."""
    while True:
        try:
            v = float(input(f"{text} ({minimum}-{maximum}): ").replace(",", "."))
            if minimum <= v <= maximum:
                return v
        except ValueError:
            pass
        print("Not valid, try again")


def add_flight(ax_h, ax_v, airplane, pct):
    """Simulates one aircraft/weight and draws its curves. Returns the table and the line."""
    table = simulate_cdo(airplane, pct * airplane.max_landing_weight)
    label = f"{airplane.name} [{round(pct * 100)}% MLW]"
    x = [-row[1] for row in table]                       # negative: before the IAF (m)
    line, = ax_h.plot(x, [row[2] for row in table], label=label)             # h (m)
    ax_v.plot(x, [row[3] / KT for row in table], color=line.get_color(), label=label)  # TAS (kt)
    return table, line


def run_simulator():
    """Asks for the data in the console, simulates and shows the plots."""
    fig_h, ax_h = plt.subplots(figsize=(14, 7))   # altitude plot (like the reference figure)
    fig_v, ax_v = plt.subplots(figsize=(14, 5))   # TAS plot

    mode = ask_option("Mode", ["FLIGHTS", "ALL"])

    if mode == "ALL":
        # Reproduces the reference figure: 5 aircraft x (100% and 80% MLW)
        for airplane in airplanes.values():
            for pct in (1.0, 0.8):
                add_flight(ax_h, ax_v, airplane, pct)
    else:
        while True:
            print("\n--- New flight ---")
            name = ask_option("Airplane", airplanes)
            airplane = airplanes[name]
            pct = ask_for_number("Weight (% of MLW)", 50, 100) / 100

            star = ask_option("STAR", list(distance_from_star) + ["OTHER"])
            if star == "OTHER":
                dist_nm = ask_for_number("Distance of WP from IAF (NM)", 1, 300)
                star = f"{dist_nm:.0f} NM"
            else:
                dist_nm = distance_from_star[star]

            table, line = add_flight(ax_h, ax_v, airplane, pct)
            altitude, t = result_on_given_distance(table, dist_nm * NM)

            print(f"\n{airplane.name} - {star} - {round(pct * 100)}% MLW")
            if altitude is None:
                print("The distance is out of the table")
            else:
                print(f" Altitude at the entry WP: {altitude / ft:.0f} ft ({altitude:.0f} m)")
                print(f" Time WP -> IAF: {t / 60:.1f} min")
                # Mark the entry WP on the curve
                ax_h.plot(-dist_nm * NM, altitude, "o", color=line.get_color())
                ax_h.annotate(f"{star}: {altitude:.0f} m", (-dist_nm * NM, altitude),
                              textcoords="offset points", xytext=(8, 8))

            if input("\nAdd another flight? (y/n): ").strip().lower() not in ("y", "s"):
                break

    # Format of the altitude plot
    ax_h.axhline(6000 * ft, color="gray", linestyle="--", linewidth=0.8)
    ax_h.text(0, 6000 * ft, "IAF (6000 ft) ", ha="right", va="bottom", color="gray")
    ax_h.set_xlabel("x [m]")
    ax_h.set_ylabel("h [m]")
    ax_h.set_title("Continuous descent (CDO) until the IAF (x = 0)")
    ax_h.grid(True)
    ax_h.legend(loc="upper right")

    # Format of the TAS plot
    ax_v.set_xlabel("x [m]")
    ax_v.set_ylabel("TAS [kt]")
    ax_v.set_title("True airspeed during the descent")
    ax_v.grid(True)
    ax_v.legend(loc="upper right")

    fig_h.tight_layout()
    fig_v.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_simulator()