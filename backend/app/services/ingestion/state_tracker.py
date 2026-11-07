from typing import Dict, List, Optional
from pydantic import BaseModel


class StateCoverageEntry(BaseModel):
    state_name: str
    region: str
    asi_circles: List[str]
    estimated_monuments: int
    status: str  # NOT_STARTED, BASELINE_INGESTED, IN_PROGRESS, COMPLETED
    records_ingested: int = 0
    records_with_coordinates: int = 0
    quality_notes: Optional[str] = None


# Official 36 Indian States and Union Territories
NATIONAL_STATE_REGISTRY: List[Dict[str, object]] = [
    # Northern Region
    {"state_name": "Delhi", "region": "Northern", "asi_circles": ["Delhi"], "estimated_monuments": 174, "status": "BASELINE_INGESTED"},
    {"state_name": "Haryana", "region": "Northern", "asi_circles": ["Chandigarh"], "estimated_monuments": 91, "status": "NOT_STARTED"},
    {"state_name": "Himachal Pradesh", "region": "Northern", "asi_circles": ["Shimla"], "estimated_monuments": 40, "status": "NOT_STARTED"},
    {"state_name": "Jammu and Kashmir", "region": "Northern", "asi_circles": ["Srinagar", "Jammu"], "estimated_monuments": 70, "status": "BASELINE_INGESTED"},
    {"state_name": "Ladakh", "region": "Northern", "asi_circles": ["Srinagar", "Leh"], "estimated_monuments": 35, "status": "NOT_STARTED"},
    {"state_name": "Punjab", "region": "Northern", "asi_circles": ["Chandigarh"], "estimated_monuments": 33, "status": "NOT_STARTED"},
    {"state_name": "Rajasthan", "region": "Northern", "asi_circles": ["Jaipur", "Jodhpur"], "estimated_monuments": 162, "status": "BASELINE_INGESTED"},
    {"state_name": "Uttar Pradesh", "region": "Northern", "asi_circles": ["Agra", "Lucknow", "Sarnath", "Meerut"], "estimated_monuments": 745, "status": "BASELINE_INGESTED"},
    {"state_name": "Uttarakhand", "region": "Northern", "asi_circles": ["Dehradun"], "estimated_monuments": 44, "status": "NOT_STARTED"},
    {"state_name": "Chandigarh", "region": "Northern", "asi_circles": ["Chandigarh"], "estimated_monuments": 5, "status": "NOT_STARTED"},

    # Southern Region
    {"state_name": "Andhra Pradesh", "region": "Southern", "asi_circles": ["Amaravati"], "estimated_monuments": 129, "status": "BASELINE_INGESTED"},
    {"state_name": "Karnataka", "region": "Southern", "asi_circles": ["Bengaluru", "Dharwad", "Hampi"], "estimated_monuments": 506, "status": "BASELINE_INGESTED"},
    {"state_name": "Kerala", "region": "Southern", "asi_circles": ["Thrissur"], "estimated_monuments": 29, "status": "BASELINE_INGESTED"},
    {"state_name": "Tamil Nadu", "region": "Southern", "asi_circles": ["Chennai", "Tiruchirappalli"], "estimated_monuments": 413, "status": "BASELINE_INGESTED"},
    {"state_name": "Telangana", "region": "Southern", "asi_circles": ["Hyderabad"], "estimated_monuments": 68, "status": "BASELINE_INGESTED"},
    {"state_name": "Puducherry", "region": "Southern", "asi_circles": ["Chennai"], "estimated_monuments": 7, "status": "NOT_STARTED"},
    {"state_name": "Lakshadweep", "region": "Southern", "asi_circles": ["Thrissur"], "estimated_monuments": 1, "status": "NOT_STARTED"},

    # Western Region
    {"state_name": "Goa", "region": "Western", "asi_circles": ["Goa"], "estimated_monuments": 21, "status": "BASELINE_INGESTED"},
    {"state_name": "Gujarat", "region": "Western", "asi_circles": ["Vadodara", "Rajkot"], "estimated_monuments": 204, "status": "BASELINE_INGESTED"},
    {"state_name": "Maharashtra", "region": "Western", "asi_circles": ["Mumbai", "Aurangabad", "Nagpur"], "estimated_monuments": 286, "status": "BASELINE_INGESTED"},
    {"state_name": "Dadra and Nagar Haveli and Daman and Diu", "region": "Western", "asi_circles": ["Vadodara"], "estimated_monuments": 12, "status": "NOT_STARTED"},

    # Central Region
    {"state_name": "Chhattisgarh", "region": "Central", "asi_circles": ["Raipur"], "estimated_monuments": 47, "status": "NOT_STARTED"},
    {"state_name": "Madhya Pradesh", "region": "Central", "asi_circles": ["Bhopal", "Jabalpur"], "estimated_monuments": 291, "status": "BASELINE_INGESTED"},

    # Eastern Region
    {"state_name": "Bihar", "region": "Eastern", "asi_circles": ["Patna"], "estimated_monuments": 70, "status": "BASELINE_INGESTED"},
    {"state_name": "Jharkhand", "region": "Eastern", "asi_circles": ["Ranchi"], "estimated_monuments": 13, "status": "NOT_STARTED"},
    {"state_name": "Odisha", "region": "Eastern", "asi_circles": ["Bhubaneswar"], "estimated_monuments": 80, "status": "BASELINE_INGESTED"},
    {"state_name": "West Bengal", "region": "Eastern", "asi_circles": ["Kolkata"], "estimated_monuments": 136, "status": "BASELINE_INGESTED"},
    {"state_name": "Andaman and Nicobar Islands", "region": "Eastern", "asi_circles": ["Kolkata"], "estimated_monuments": 1, "status": "NOT_STARTED"},

    # North-Eastern Region
    {"state_name": "Arunachal Pradesh", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 5, "status": "NOT_STARTED"},
    {"state_name": "Assam", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 55, "status": "BASELINE_INGESTED"},
    {"state_name": "Manipur", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 1, "status": "NOT_STARTED"},
    {"state_name": "Meghalaya", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 8, "status": "NOT_STARTED"},
    {"state_name": "Mizoram", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 1, "status": "NOT_STARTED"},
    {"state_name": "Nagaland", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 4, "status": "NOT_STARTED"},
    {"state_name": "Sikkim", "region": "North-Eastern", "asi_circles": ["Kolkata"], "estimated_monuments": 3, "status": "NOT_STARTED"},
    {"state_name": "Tripura", "region": "North-Eastern", "asi_circles": ["Guwahati"], "estimated_monuments": 8, "status": "NOT_STARTED"},
]


class StateCoverageTracker:
    """
    State-by-State expansion tracker for all 36 Indian States and Union Territories.
    Enables tracking of data acquisition, normalization, coordinate coverage, and quality.
    """

    def __init__(self):
        self._entries: Dict[str, StateCoverageEntry] = {}
        for item in NATIONAL_STATE_REGISTRY:
            entry = StateCoverageEntry(**item)
            self._entries[entry.state_name] = entry

    def get_state(self, state_name: str) -> Optional[StateCoverageEntry]:
        return self._entries.get(state_name)

    def list_all_states(self) -> List[StateCoverageEntry]:
        return list(self._entries.values())

    def update_metrics(
        self,
        state_name: str,
        records_ingested: int,
        records_with_coordinates: int,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[StateCoverageEntry]:
        entry = self._entries.get(state_name)
        if not entry:
            return None
        entry.records_ingested = records_ingested
        entry.records_with_coordinates = records_with_coordinates
        if status:
            entry.status = status
        if notes:
            entry.quality_notes = notes
        return entry

    def get_national_summary(self) -> Dict[str, object]:
        total_states = len(self._entries)
        active_or_ingested = sum(
            1 for s in self._entries.values() if s.status in ("BASELINE_INGESTED", "COMPLETED")
        )
        total_estimated = sum(s.estimated_monuments for s in self._entries.values())
        total_ingested = sum(s.records_ingested for s in self._entries.values())
        total_with_coords = sum(s.records_with_coordinates for s in self._entries.values())

        return {
            "total_states_and_uts": total_states,
            "states_with_baseline_or_completed": active_or_ingested,
            "total_estimated_national_monuments": total_estimated,
            "total_records_ingested": total_ingested,
            "total_records_with_coordinates": total_with_coords,
            "national_state_coverage_pct": round((active_or_ingested / total_states) * 100, 1),
        }
