
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
