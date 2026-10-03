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
        return  -56.5

def isa_pressure(altitude):
    if altitude <= 11000:
        return  p0*((1-0.0065*(altitude/T0))*5.2561)
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
        if altitude <= (6000 * 0.3048):
            return aircraft.CT_desc_app*max_thrust
        else:
            return aircraft.CT_desc_low*max_thrust

# Now we calculate the ROD from altitude and aircraft data
def calculate_rod(aircraft,mass, altitude, velocity):
    rho = isa_air_density(altitude)
    W = mass*g
    Cl = (2*W) / (((rho*velocity)**2)*aircraft.S)
    if altitude <= (6000 * 0.3048):
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
    if altitude <= (6000 * 0.3048):
        v_min_rod = ((T + (T ** 2 + 12 * aircraft.CD0_clean * aircraft.CD2_clean * (W ** 2)) ** 0.5) / (3 * rho * aircraft.S * aircraft.CD0_clean)) ** 0.5
    else:
        v_min_rod = ((T + (T ** 2 + 12 * aircraft.CD0_app * aircraft.CD2_app * (W ** 2)) ** 0.5) / (3 * rho * aircraft.S * aircraft.CD0_app)) ** 0.5
    return v_min_rod



