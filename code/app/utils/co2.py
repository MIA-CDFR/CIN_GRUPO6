
CO2_STCP_GPKM = 109.9 
CO2_METRO_GPKM = 40.0


def get_co2(modo: str):
    if modo == "METRO":
        return CO2_METRO_GPKM
    elif modo == "STCP":
        return CO2_STCP_GPKM

    return 0