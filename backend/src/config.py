import os

# Base paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
MODEL_DIR = os.path.join(BACKEND_DIR, "models")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Data paths
RAW_DATA_PATH = os.path.join(DATA_DIR, "Space_Corrected.csv")
SITES_MAPPING_PATH = os.path.join(DATA_DIR, "sites_mapping.csv")
ENRICHED_DATA_PATH = os.path.join(DATA_DIR, "launches_with_weather.csv")

# Model paths
BEST_MODEL_PATH = os.path.join(MODEL_DIR, "best_model.joblib")
PREPROCESSORS_PATH = os.path.join(MODEL_DIR, "preprocessors.joblib")

# Coordinates dictionary for major space launch centers to skip Nominatim rate-limiting where possible.
# Dictionary keys are substrings that we look for in the location name.
SPACEPORT_COORDINATES = {
    "plesetsk": (62.925, 40.578),
    "baikonur": (45.920, 63.342),
    "cape canaveral": (28.396, -80.605),
    "kennedy space center": (28.572, -80.648),
    "lc-39a": (28.608, -80.604),
    "slc-40": (28.562, -80.577),
    "slc-41": (28.583, -80.583),
    "vandenberg": (34.742, -120.572),
    "slc-4e": (34.632, -120.610),
    "kourou": (5.239, -52.768),
    "tanegashima": (30.400, 130.970),
    "jiuquan": (40.965, 100.282),
    "satish dhawan": (13.720, 80.230),
    "sriharikota": (13.720, 80.230),
    "xichang": (28.246, 102.029),
    "taiyuan": (38.849, 111.608),
    "wallops": (37.939, -75.466),
    "uchinoura": (31.251, 131.079),
    "woomera": (-30.955, 136.532),
    "san marco": (-2.938, 40.214),
    "palmachim": (31.884, 34.680),
    "svobodny": (51.796, 128.115),
    "vostochny": (51.884, 128.334),
    "semnan": (35.234, 53.921),
    "sohae": (39.660, 124.705),
    "tonghae": (40.855, 129.666),
    "naro": (34.432, 127.535),
    "boca chica": (25.991, -97.157),
    "alcântara": (-2.373, -44.396),
    "alcantara": (-2.373, -44.396),
    "kodiak": (57.435, -152.339),
    "hammaguir": (30.863, -3.078),
    "barents sea": (74.348, 37.810),
    "submarine": (74.348, 37.810),
    "kwajalein": (9.119, 167.733),
    "wenchang": (19.614, 110.951),
    "shahrud": (36.425, 55.021),
    "jianhe": (27.550, 108.830),
    "imam khomeini": (35.234, 53.921),
    "yellow sea": (36.500, 121.200),
    "edwards afb": (34.905, -117.884),
    "mojave": (35.059, -118.152),
    "point mugu": (34.121, -119.121),
    "ramenskoye": (55.568, 38.140),
}
