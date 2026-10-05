import math
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

