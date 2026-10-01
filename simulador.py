# ============================================================
# CDO SIMULATOR - VERSION I
# ============================================================
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


#Air density (kg/m^3) related to altitude (in meters)
def isa_density(alt):
    if alt <= 11000:                       # troposphere
        temp = T0 - 0.0065 * alt
        return rho0 * (temp / T0) ** 4.2559
    else:                                # stratosphere
        rho11 = rho0 * (216.65 / T0) ** 4.2559
        return rho11 * math.exp(-g * (alt - 11000) / (R * 216.65))



# Step 2: idle thrust (Annex A equations)
def empuje_idle(avion, h):
    #"""Empuje en descenso (idle), configuración limpia, en N."""

    T_max = avion.CT1 * (1 - h / avion.CT2 + avion.CT3 * h ** 2)
    if h > avion.hp_desc:
        return avion.CT_desc_high * T_max
    else:
        return avion.CT_desc_low * T_max      # clean (por encima de 6000 ft)



# Step 3: ROD for  altitud h and velocity v known
# Stationary flight : W*sin(gamma) = D - T
def calcular_rod(avion, masa, h, V):
    rho = densidad_isa(h)
    W = masa * g
    CL = 2 * W / (rho * V ** 2 * avion.S)           # L = W (small gamma)
    CD = avion.CD0_clean + avion.CD2_clean * CL ** 2
    D = 0.5 * rho * V ** 2 * avion.S * CD
    T = empuje_idle(avion, h)
    sin_gamma = (D - T) / W
    ROD = V * sin_gamma                              # m/s (positive = decreasing)
    return ROD, sin_gamma


# Step 4: search velocity that minimizes ROD
# Try different velocities and choose the best

def velocidad_min_rod(avion, masa, h):
    mejor_V = None
    mejor_ROD = 1e9
    mejor_sin = 0
    V = 60.0                                          # m/s (TAS)
    while V <= 300.0:
        ROD, sin_gamma = calcular_rod(avion, masa, h, V)
        if ROD < mejor_ROD:
            mejor_ROD = ROD
            mejor_V = V
            mejor_sin = sin_gamma
        V += 0.5
    return mejor_V, mejor_ROD, mejor_sin


# Step 5: descent simulator in reverse in time
# Start at IAF (6000 ft, distance 0, time 0) and increasing in reverse. This allows us to know the exact altitude at which each aircraft at each distance/ time before IAF
def simular_cdo(avion, masa, h_max=12000.0, dt=1.0):
    h = 6000 * ft          # altitude at IAF (m)
    x = 0.0                # travelled distance before IAF (m)
    t = 0.0                # time before IAF (s)

    tabla = []             # each row: (t, x, h, V)
    while h < h_max:
        V, ROD, sin_gamma = velocidad_min_rod(avion, masa, h)
        tabla.append((t, x, h, V))
        gamma = math.asin(sin_gamma)
        x += V * math.cos(gamma) * dt     # avanzamos hacia atrás en distancia
        h += ROD * dt                     # subimos hacia atrás
        t += dt
    return tabla


# Step 6: read the table --> altitude and time for a given distance
def resultado_a_distancia(tabla, distancia_m):
    """Devuelve (altitud en m, tiempo hasta el IAF en s) a esa distancia del IAF."""
    for i in range(1, len(tabla)):
        if tabla[i][1] >= distancia_m:
            t1, x1, h1, V1 = tabla[i - 1]
            t2, x2, h2, V2 = tabla[i]
            f = (distancia_m - x1) / (x2 - x1)      # interpolación lineal
            return h1 + f * (h2 - h1), t1 + f * (t2 - t1)
    return None, None                                # larger distance


#
# PRUEBA: simulamos los 6 vuelos del enunciado

if __name__ == "__main__":
    vuelos = [
        # (avión, STAR, % MLW)
        (B767, "ALBER1Z", 0.80),
        (B777, "PUMAL1Z", 1.00),
        (B737, "MARTA3Z", 1.00),
        (A320, "MATEX3Z", 0.80),
        (A319, "LOBAR2W", 0.80),
        (B767, "CASPE2W", 1.00),
    ]

    # Distance for each STAR (first waypoint -> IAF), in NM.
    # Complete with the STAR card of ENAIRE AIP
    distancia_star_NM = {
        "ALBER1Z": 50, "PUMAL1Z": 50, "MARTA3Z": 50,
        "MATEX3Z": 50, "LOBAR2W": 50, "CASPE2W": 50,
    }

    for avion, star, pct in vuelos:
        masa = pct * avion.max_landing_weight
        tabla = simular_cdo(avion, masa)
        d = distancia_star_NM[star] * 1852
        h, t = resultado_a_distancia(tabla, d)
        print(avion.name, star, "peso", int(pct * 100), "% MLW")
        if h is None:
            print("   distancia fuera de la tabla")
        else:
            print("   altitud en el WP de entrada: %.0f ft" % (h / ft))
            print("   tiempo WP -> IAF: %.1f min" % (t / 60))
        print("   velocidad TAS a 6000 ft: %.0f kt, a ~20000 ft: %.0f kt" % (
            tabla[0][3] / 0.514444,
            min(tabla, key=lambda f: abs(f[2] - 20000 * ft))[3] / 0.514444))
