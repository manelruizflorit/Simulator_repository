import math
from aviones import B767, B777, B737, A320, A319

# ------------------------------------------------------------
# International standard atmosphere
# ------------------------------------------------------------
g = 9.80665          # gravity (m/s^2)
R = 287.05287        # air constant (J/(kg K))
T0 = 288.15          # sea level temp. (K)
rho0 = 1.225         # sea level density (kg/m^3)
ft = 0.3048          # 1 ft in meters


def isa_temperature(altitude):
    if altitude <= 11000:
        return 288.15-0.0065*altitude
    else:
        return  -56.5

def isa_pressure(altitude):
    if altitude <= 11000:
        return  101325*((1-0.0065*(altitude/288.15))*5.2561)
    else:
        return -56.5