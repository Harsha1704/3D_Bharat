import math
from enum import Enum
from typing import Optional, Tuple
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.services.ingestion.normalizer import normalize_name


class MatchStatus(str, Enum):
    NO_MATCH = "NO_MATCH"
    EXACT_MATCH = "EXACT_MATCH"
    AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"


def _haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class DuplicateDetector:
    """
    Multi-tier duplicate detector for Indian heritage records:
    1. Exact external_id lookup.
    2. Exact normalized name and state lookup.
    3. Spatial proximity check (< 300m) with high name similarity.
    4. Ambiguous name match flag for human review.
    """

    def __init__(self, db: Session):
        self.db = db

    def check_duplicate(
        self,
        external_id: str,
        name: str,
        state: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Tuple[MatchStatus, Optional[HeritageSite], str]:
        """
        Returns (MatchStatus, matched_site, explanation).
        """
        # Tier 1: Exact external_id match
        if external_id:
            site_by_ext = self.db.execute(
                select(HeritageSite).where(HeritageSite.external_id == external_id)
            ).scalar_one_or_none()
            if site_by_ext:
                return (
                    MatchStatus.EXACT_MATCH,
                    site_by_ext,
                    f"Exact external_id match '{external_id}' (Site ID #{site_by_ext.id})",
                )

        norm_input_name = normalize_name(name).lower()

        # Tier 2: Exact normalized name and state match
        if norm_input_name and state:
            exact_name_state = self.db.execute(
                select(HeritageSite).where(
                    func.lower(HeritageSite.name) == norm_input_name,
                    func.lower(HeritageSite.state) == state.lower(),
                )
            ).scalars().first()

            if exact_name_state:
                return (
                    MatchStatus.EXACT_MATCH,
                    exact_name_state,
                    f"Exact name '{exact_name_state.name}' and state '{state}' match (Site ID #{exact_name_state.id})",
                )

        # Tier 3: Spatial proximity check (< 300 meters)
        if latitude is not None and longitude is not None:
            # Bounding box candidate filter (~0.005 degrees ~= 550m)
            delta = 0.005
            candidates = self.db.execute(
                select(HeritageSite).where(
                    HeritageSite.latitude.is_not(None),
                    HeritageSite.longitude.is_not(None),
                    HeritageSite.latitude.between(latitude - delta, latitude + delta),
                    HeritageSite.longitude.between(longitude - delta, longitude + delta),
                )
            ).scalars().all()

            for cand in candidates:
                dist = _haversine_distance_meters(latitude, longitude, cand.latitude, cand.longitude)
                if dist <= 200.0:
                    cand_norm_name = normalize_name(cand.name).lower()
                    if norm_input_name in cand_norm_name or cand_norm_name in norm_input_name:
                        return (
                            MatchStatus.EXACT_MATCH,
                            cand,
                            f"Spatial proximity ({round(dist, 1)}m) and name similarity with '{cand.name}' (Site ID #{cand.id})",
                        )
                    else:
                        return (
                            MatchStatus.AMBIGUOUS_MATCH,
                            cand,
                            f"Ambiguous spatial proximity ({round(dist, 1)}m) with differently named site '{cand.name}' (Site ID #{cand.id})",
                        )

        # Tier 4: Cross-state same name check (flag as ambiguous review if monument has same distinctive name in other states)
        if norm_input_name and len(norm_input_name) > 8:
            other_state_site = self.db.execute(
                select(HeritageSite).where(func.lower(HeritageSite.name) == norm_input_name)
            ).scalars().first()
            if other_state_site and other_state_site.state.lower() != state.lower():
                return (
                    MatchStatus.AMBIGUOUS_MATCH,
                    other_state_site,
                    f"Identical monument name '{other_state_site.name}' found in different state '{other_state_site.state}' vs '{state}'",
                )

        return MatchStatus.NO_MATCH, None, "No duplicate detected"
