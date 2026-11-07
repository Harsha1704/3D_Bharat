from abc import ABC, abstractmethod
import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from app.services.ingestion.normalizer import (
    normalize_category,
    normalize_name,
    normalize_state,
    validate_coordinates,
)


class BaseSourceAdapter(ABC):
    """
    Abstract interface for parsing and streaming raw monument records
    from diverse formats and national archives.
    """

    def __init__(
        self,
        source_name: str,
        source_organization: str,
        source_url: Optional[str] = None,
        license: Optional[str] = None,
    ):
        self.source_name = source_name
        self.source_organization = source_organization
        self.source_url = source_url
        self.license = license

    @abstractmethod
    def load_records(self) -> Iterable[Dict[str, Any]]:
        """
        Yields raw records as dictionaries.
        """
        pass

    def transform_record(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardizes raw dictionary into canonical HeritageSite fields.
        """
        name = normalize_name(raw.get("name") or raw.get("monument_name") or raw.get("title"))
        state = normalize_state(raw.get("state") or raw.get("state_name") or raw.get("region"))
        category = normalize_category(raw.get("category") or raw.get("monument_type"))

        lat_raw = raw.get("latitude") or raw.get("lat")
        lon_raw = raw.get("longitude") or raw.get("lon") or raw.get("long")
        lat, lon, coord_warning = validate_coordinates(lat_raw, lon_raw)

        # Parse tags
        tags = raw.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        alt_names = raw.get("alternative_names") or raw.get("local_name") or []
        if isinstance(alt_names, str):
            alt_names = [a.strip() for a in alt_names.split(";") if a.strip()]

        ext_id = str(raw.get("external_id") or raw.get("id") or raw.get("whc_id") or raw.get("asi_id") or "")
        if not ext_id:
            # Generate deterministic fallback
            clean_sub = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
            clean_state = re.sub(r"[^a-zA-Z0-9]+", "-", state.lower()).strip("-")
            ext_id = f"NAT-{clean_state}-{clean_sub}"

        return {
            "external_id": ext_id,
            "name": name,
            "alternative_names": alt_names if alt_names else None,
            "state": state,
            "district": raw.get("district"),
            "city": raw.get("city") or raw.get("location"),
            "category": category,
            "period": raw.get("period") or raw.get("era"),
            "dynasty": raw.get("dynasty"),
            "construction_year": raw.get("construction_year") or raw.get("date"),
            "architecture": raw.get("architecture") or raw.get("architectural_style"),
            "description": raw.get("description") or f"{name} is an important heritage structure located in {state}, India.",
            "significance": raw.get("significance"),
            "latitude": lat,
            "longitude": lon,
            "tags": tags if tags else None,
            "associated_people": raw.get("associated_people"),
            "historical_events": raw.get("historical_events"),
            "traditions": raw.get("traditions"),
            "verification_status": raw.get("verification_status", "OFFICIAL_SOURCE"),
            "source_reference": raw.get("source_reference") or self.source_name,
            "_coord_warning": coord_warning,
        }


import re


class CsvSourceAdapter(BaseSourceAdapter):
    """
    Adapter for CSV tabular monument inventories.
    """

    def __init__(
        self,
        file_path_or_content: Union[str, Path, io.StringIO],
        source_name: str,
        source_organization: str,
        source_url: Optional[str] = None,
        license: Optional[str] = None,
    ):
        super().__init__(source_name, source_organization, source_url, license)
        self.source = file_path_or_content

    def load_records(self) -> Iterable[Dict[str, Any]]:
        if isinstance(self.source, io.StringIO):
            reader = csv.DictReader(self.source)
            for row in reader:
                yield self.transform_record(row)
        elif isinstance(self.source, (str, Path)):
            with open(self.source, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield self.transform_record(row)


class JsonSourceAdapter(BaseSourceAdapter):
    """
    Adapter for JSON array or wrapped object monument inventories.
    """

    def __init__(
        self,
        file_path_or_content: Union[str, Path, List[Dict[str, Any]]],
        source_name: str,
        source_organization: str,
        source_url: Optional[str] = None,
        license: Optional[str] = None,
    ):
        super().__init__(source_name, source_organization, source_url, license)
        self.source = file_path_or_content

    def load_records(self) -> Iterable[Dict[str, Any]]:
        records = []
        if isinstance(self.source, list):
            records = self.source
        elif isinstance(self.source, (str, Path)):
            with open(self.source, mode="r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    records = data.get("records") or data.get("monuments") or data.get("items") or []

        for row in records:
            yield self.transform_record(row)


class UnescoIndiaAdapter(JsonSourceAdapter):
    """
    Specialized adapter for UNESCO World Heritage Centre public records for India.
    """

    def __init__(self, file_path_or_content: Union[str, Path, List[Dict[str, Any]]]):
        super().__init__(
            file_path_or_content=file_path_or_content,
            source_name="UNESCO World Heritage List — India",
            source_organization="UNESCO World Heritage Centre",
            source_url="https://whc.unesco.org/en/list/",
            license="UNESCO Public Information Terms / CC-BY-SA",
        )

    def transform_record(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        record = super().transform_record(raw)
        whc_id = raw.get("whc_id")
        if whc_id:
            record["external_id"] = f"UNESCO-WHC-{whc_id}"
            record["source_reference"] = f"UNESCO World Heritage Property #{whc_id}"
        record["verification_status"] = "OFFICIAL_SOURCE"
        return record


class AsiMonumentsAdapter(CsvSourceAdapter):
    """
    Specialized adapter for Archaeological Survey of India (ASI) Centrally Protected Monuments.
    """

    def __init__(self, file_path_or_content: Union[str, Path, io.StringIO]):
        super().__init__(
            file_path_or_content=file_path_or_content,
            source_name="ASI Centrally Protected Monuments Gazetteer",
            source_organization="Archaeological Survey of India (ASI)",
            source_url="https://asi.nic.in/monuments/",
            license="Open Government Data (OGD) Platform India",
        )

    def transform_record(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        record = super().transform_record(raw)
        circle = raw.get("circle") or raw.get("asi_circle")
        asi_id = raw.get("asi_id") or raw.get("notification_number")
        if asi_id:
            clean_asi_id = re.sub(r"[^a-zA-Z0-9]+", "-", str(asi_id).strip())
            record["external_id"] = f"ASI-{clean_asi_id}"
        if circle:
            tags = record.get("tags") or []
            circle_tag = f"ASI Circle: {circle}"
            if circle_tag not in tags:
                tags.append(circle_tag)
            record["tags"] = tags
        record["verification_status"] = "OFFICIAL_SOURCE"
        return record
