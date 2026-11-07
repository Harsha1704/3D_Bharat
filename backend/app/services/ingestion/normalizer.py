import re
from typing import Optional, Tuple

# Official 28 States and 8 Union Territories mapping
STATE_NORMALIZATION_MAP = {
    "andaman and nicobar": "Andaman and Nicobar Islands",
    "andaman and nicobar islands": "Andaman and Nicobar Islands",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra and nagar haveli and daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "Delhi",
    "nct of delhi": "Delhi",
    "national capital territory of delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jammu and kashmir": "Jammu and Kashmir",
    "jammu & kashmir": "Jammu and Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "west bengal": "West Bengal",
}

CATEGORY_SYNONYMS = {
    "temple": "Temple",
    "mandir": "Temple",
    "kovil": "Temple",
    "fort": "Fort",
    "qila": "Fort",
    "fortress": "Fort",
    "cave": "Cave",
    "caves": "Cave",
    "stepwell": "Stepwell",
    "baoli": "Stepwell",
    "vav": "Stepwell",
    "palace": "Palace",
    "mahal": "Palace",
    "monument": "Monument",
    "tomb": "Tomb",
    "maqbara": "Tomb",
    "mosque": "Mosque",
    "masjid": "Mosque",
    "stupa": "Stupa",
    "chaitya": "Cave",
    "vihara": "Cave",
    "archaeological site": "Archaeological Site",
    "ancient site": "Archaeological Site",
    "excavation site": "Archaeological Site",
    "pillar": "Pillar / Inscription",
    "inscription": "Pillar / Inscription",
    "memorial": "Monument",
    "bridge": "Historic Structure",
}


def normalize_state(raw_state: Optional[str]) -> str:
    """
    Standardize Indian State/UT names, correcting historical and abbreviation variants.
    """
    if not raw_state or not raw_state.strip():
        return "Unknown"
    cleaned = raw_state.strip().lower()
    return STATE_NORMALIZATION_MAP.get(cleaned, raw_state.strip().title())


def normalize_name(raw_name: Optional[str]) -> str:
    """
    Cleans leading/trailing punctuation, collapses internal whitespace,
    and formats capitalizations.
    """
    if not raw_name:
        return ""
    name = raw_name.strip()
    name = re.sub(r"\s+", " ", name)
    # Strip leading/trailing dashes, quotes, and commas
    name = name.strip("- ,;\"'")
    # If entirely uppercase, title-case it cleanly
    if name.isupper() and len(name) > 3:
        name = name.title()
    return name


def validate_coordinates(
    raw_lat: Optional[float | str],
    raw_lon: Optional[float | str],
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Validates geographic coordinates for standard WGS84 adherence and checks
    against India's geographic bounding box (~6.0°N to 38.0°N, ~68.0°E to 98.0°E).
    Returns (lat, lon, error_or_warning_message).
    """
    if raw_lat is None or raw_lon is None:
        return None, None, None

    try:
        lat = float(raw_lat)
        lon = float(raw_lon)
    except (ValueError, TypeError):
        return None, None, f"Coordinates could not be parsed as float: lat='{raw_lat}', lon='{raw_lon}'"

    # Strict WGS84 range validation
    if not (-90.0 <= lat <= 90.0):
        return None, None, f"Latitude {lat} is out of WGS84 range [-90, 90]"
    if not (-180.0 <= lon <= 180.0):
        return None, None, f"Longitude {lon} is out of WGS84 range [-180, 180]"

    # Sub-check for India geographic bounding box
    warning = None
    if not (5.0 <= lat <= 39.0 and 67.0 <= lon <= 99.0):
        warning = f"Coordinates ({lat}, {lon}) fall outside India's geographic territory"

    return round(lat, 6), round(lon, 6), warning


def normalize_category(raw_category: Optional[str]) -> str:
    """
    Classify heritage structure into standardized categories.
    """
    if not raw_category or not raw_category.strip():
        return "Monument"

    cat_lower = raw_category.strip().lower()
    for key, standardized in CATEGORY_SYNONYMS.items():
        if key in cat_lower:
            return standardized

    return raw_category.strip().title()
