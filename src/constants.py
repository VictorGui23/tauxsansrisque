DB_COLUMNS = ["date", "country", "curve_name", "period", "rate", 
              "coupon_freq", "llp", "convergence", "va_int", "shock_int",
              "ufr", "alpha", "cra", "va", "date_upload"]


NAMES_TO_COLLECT = ["RFR_spot_no_VA", "RFR_spot_with_VA",
                    "Spot_NO_VA_shock_UP", "Spot_NO_VA_shock_DOWN",
                    "Spot_WITH_VA_shock_UP", "Spot_WITH_VA_shock_DOWN"]

NAMES_TO_COLLECT_VPS = ["RFR_SPOT_NO_VA", "RFR_SPOT_WITH_VA",
                    "SPOT_NO_VA_SHOCK_UP", "SPOT_NO_VA_SHOCK_DOWN",
                    "SPOT_WITH_VA_SHOCK_UP", "SPOT_WITH_VA_SHOCK_DOWN"]

EIOPA_URL = r"https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en"