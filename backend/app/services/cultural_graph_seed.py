import logging
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cultural_graph import (
    CulturalEvidenceStatus,
    CulturalGraphEntity,
    CulturalGraphRelationship,
    CulturalEntityType,
    CulturalRelationshipType,
)
from app.models.heritage_connection import HeritageConnection
from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource

logger = logging.getLogger("3d_bharat.cultural_graph_seed")


def seed_cultural_knowledge_graph(db: Session) -> Dict[str, int]:
    """
    Idempotent seeding and synchronization of the Cultural Knowledge Graph:
    1. Synchronize all HeritageSites as HERITAGE_SITE entities with canonical foreign key.
    2. Seed authentic historical Dynasties, Persons, Events, Architectural Styles, and Traditions.
    3. Migrate all 8 existing HeritageConnections into CulturalGraphRelationships with DOCUMENTED status.
    4. Link monuments to their authentic historical builders, dynasties, and styles.
    """
    # ---------------------------------------------------------
    # 1. HERITAGE SITE ENTITY SYNCHRONIZATION
    # ---------------------------------------------------------
    sites = db.execute(select(HeritageSite)).scalars().all()
    entity_by_site_id: Dict[int, CulturalGraphEntity] = {}

    for site in sites:
        slug = f"site-{site.id}-{site.name.lower().replace(' ', '-').replace('/', '-')[:50]}"
        entity = db.execute(
            select(CulturalGraphEntity).where(
                (CulturalGraphEntity.heritage_site_id == site.id)
                | (CulturalGraphEntity.slug == slug)
            )
        ).scalar_one_or_none()

        if not entity:
            entity = CulturalGraphEntity(
                entity_type=CulturalEntityType.HERITAGE_SITE.value,
                canonical_name=site.name,
                slug=slug,
                heritage_site_id=site.id,
                alternative_names=site.alternative_names,
                description=site.description,
                geographical_context=f"{site.city or site.district or 'India'}, {site.state or ''}".strip(", "),
                period=site.period,
                metadata_json={
                    "category": site.category,
                    "latitude": site.latitude,
                    "longitude": site.longitude,
                    "external_id": site.external_id,
                },
                verification_status=CulturalEvidenceStatus.VERIFIED.value,
            )
            db.add(entity)
            db.flush()

        entity_by_site_id[site.id] = entity

    # ---------------------------------------------------------
    # 2. SEED CANONICAL HISTORICAL ENTITIES (EVIDENCE-BACKED)
    # ---------------------------------------------------------
    historical_entities_spec = [
        # Dynasties
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Chola Dynasty",
            "slug": "dynasty-chola",
            "period": "c. 300 BCE – 1279 CE (Imperial era 9th–13th c.)",
            "desc": "One of the longest-ruling maritime dynasties in world history, renowned for bronze sculpture, overseas trade, and grand Dravidian stone temples.",
            "geo": "Tamilakam / Thanjavur / Kaveri Delta",
            "meta": {"prominent_rulers": ["Rajaraja Chola I", "Rajendra Chola I"], "capital": "Thanjavur"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Vijayanagara Empire",
            "slug": "dynasty-vijayanagara",
            "period": "1336 – 1646 CE",
            "desc": "Prominent Deccan empire established to protect Southern Indian culture, celebrated for pillared mandapas, multi-tiered gopurams, and vibrant international commerce at Hampi.",
            "geo": "Deccan Plateau / Tungabhadra River Basin",
            "meta": {"prominent_rulers": ["Harihara I", "Krishnadevaraya"], "capital": "Hampi (Vijayanagara)"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Rashtrakuta Dynasty",
            "slug": "dynasty-rashtrakuta",
            "period": "753 – 982 CE",
            "desc": "Major empire that ruled vast areas of the Indian subcontinent from Manyakheta, celebrated for patronizing the monolithic rock-cut Kailasa Temple at Ellora.",
            "geo": "Deccan / Maharashtra / Karnataka",
            "meta": {"prominent_rulers": ["Dantidurga", "Krishna I"], "capital": "Manyakheta"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Maurya Empire",
            "slug": "dynasty-maurya",
            "period": "322 – 185 BCE",
            "desc": "Iron Age historical power in ancient India founded by Chandragupta Maurya, which under Ashoka the Great fostered Buddhist philosophy and monumental pillar/stupa architecture.",
            "geo": "Magadha / Pan-Indian",
            "meta": {"prominent_rulers": ["Chandragupta Maurya", "Ashoka"], "capital": "Pataliputra"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Mughal Dynasty",
            "slug": "dynasty-mughal",
            "period": "1526 – 1857 CE",
            "desc": "Early modern empire spanning the Indian subcontinent, distinguished by monumental symmetric marble and sandstone architecture, gardens, and court arts.",
            "geo": "Northern & Central India",
            "meta": {"prominent_rulers": ["Akbar", "Shah Jahan"], "capital": "Agra / Delhi"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Eastern Ganga Dynasty",
            "slug": "dynasty-eastern-ganga",
            "period": "5th – 15th Century CE",
            "desc": "Medieval Indian dynasty ruling Kalinga (modern Odisha), builders of the monumental Sun Temple at Konark and Jagannath Temple at Puri.",
            "geo": "Kalinga / Odisha / Eastern Coast",
            "meta": {"prominent_rulers": ["Anantavarman Chodaganga", "Narasimhadeva I"], "capital": "Kalinganagara"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Chandela Dynasty",
            "slug": "dynasty-chandela",
            "period": "9th – 13th Century CE",
            "desc": "Central Indian Rajput dynasty that ruled the Jejakabhukti region (Bundelkhand), celebrated for the Nagara-style temple complexes at Khajuraho.",
            "geo": "Bundelkhand / Madhya Pradesh",
            "meta": {"capital": "Mahoba / Khajuraho"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Kakatiya Dynasty",
            "slug": "dynasty-kakatiya",
            "period": "12th – 14th Century CE",
            "desc": "Deccan dynasty based in Orugallu (Warangal), known for hydraulic engineering, stone forts, and the foundation of Golconda.",
            "geo": "Telangana / Andhra Pradesh",
            "meta": {"prominent_rulers": ["Rudrama Devi", "Prataparudra"], "capital": "Warangal"},
        },
        {
            "type": CulturalEntityType.DYNASTY.value,
            "name": "Pandya Dynasty",
            "slug": "dynasty-pandya",
            "period": "6th Century BCE – 17th Century CE",
            "desc": "Ancient Tamil dynasty of Southern India that made Madurai their capital and patronized the sacred Meenakshi Sundareswarar complex.",
            "geo": "Madurai / Tamil Nadu",
            "meta": {"capital": "Madurai"},
        },

        # Historical People
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "Rajaraja Chola I",
            "slug": "person-rajaraja-chola",
            "period": "c. 947 – 1014 CE (r. 985–1014 CE)",
            "desc": "Chola emperor who unified South India, organized maritime commerce, and commissioned the Great Brihadisvara Temple at Thanjavur.",
            "geo": "Thanjavur, Tamil Nadu",
            "meta": {"title": "Rajaraja Peruvudaiyar", "dynasty": "Chola Dynasty"},
        },
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "Emperor Ashoka",
            "slug": "person-ashoka",
            "period": "304 – 232 BCE (r. 268–232 BCE)",
            "desc": "Third Mauryan emperor who embraced Buddhism after the Kalinga war, patronizing stupas across India including the Great Stupa at Sanchi.",
            "geo": "Pataliputra / Pan-India",
            "meta": {"dynasty": "Maurya Empire"},
        },
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "Krishnadevaraya",
            "slug": "person-krishnadevaraya",
            "period": "1471 – 1529 CE (r. 1509–1529 CE)",
            "desc": "Celebrated ruler of the Vijayanagara Empire whose reign marked the golden age of arts, literature, and monumental temple construction across Hampi.",
            "geo": "Hampi, Karnataka",
            "meta": {"dynasty": "Vijayanagara Empire"},
        },
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "Krishna I",
            "slug": "person-krishna-1",
            "period": "r. 756 – 774 CE",
            "desc": "Rashtrakuta king who commissioned the magnificent monolithic rock-cut Kailasa Temple (Cave 16) at Ellora.",
            "geo": "Ellora / Manyakheta",
            "meta": {"dynasty": "Rashtrakuta Dynasty"},
        },
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "King Narasimhadeva I",
            "slug": "person-narasimhadeva-1",
            "period": "r. 1238 – 1264 CE",
            "desc": "Eastern Ganga monarch who commissioned the colossal Sun Temple at Konark designed as a stone chariot of Surya with 24 carved wheels.",
            "geo": "Konark, Odisha",
            "meta": {"dynasty": "Eastern Ganga Dynasty"},
        },
        {
            "type": CulturalEntityType.HISTORICAL_PERSON.value,
            "name": "Shah Jahan",
            "slug": "person-shah-jahan",
            "period": "1592 – 1666 CE (r. 1628–1658 CE)",
            "desc": "Fifth Mughal emperor who presided over the golden era of Mughal architecture, commissioning the Taj Mahal in Agra.",
            "geo": "Agra / Delhi",
            "meta": {"dynasty": "Mughal Dynasty"},
        },

        # Architectural Styles
        {
            "type": CulturalEntityType.ARCHITECTURAL_STYLE.value,
            "name": "Dravidian Architecture",
            "slug": "style-dravidian",
            "period": "7th Century CE – Present",
            "desc": "Classical South Indian temple architectural tradition characterized by pyramidal tiered vimanas, pillared mandapas, and monumental towering gopurams.",
            "geo": "South India",
            "meta": {"key_features": ["Pyramidal Vimana", "Gopuram", "Kalyana Mandapa", "Water Tank / Teppakulam"]},
        },
        {
            "type": CulturalEntityType.ARCHITECTURAL_STYLE.value,
            "name": "Nagara Architecture",
            "slug": "style-nagara",
            "period": "5th Century CE – Present",
            "desc": "Classical North and Central Indian temple style distinguished by beehive-shaped, curvilinear towers (shikharas) over the inner sanctum with intricate narrative stone carvings.",
            "geo": "Northern & Central India",
            "meta": {"key_features": ["Curvilinear Shikhara", "Amalaka", "Kalasha", "Cruciform Ground Plan"]},
        },
        {
            "type": CulturalEntityType.ARCHITECTURAL_STYLE.value,
            "name": "Rock-cut Monolithic Architecture",
            "slug": "style-rock-cut-monolithic",
            "period": "3rd Century BCE – 10th Century CE",
            "desc": "Subtractive sculpting tradition where entire temples, chaityas, and monasteries are hewn directly top-down from living cliff faces and volcanic basalt hills.",
            "geo": "Western Ghats / Deccan Plateau",
            "meta": {"key_features": ["Top-down excavation", "Chaitya arches", "Monolithic pillars", "Rock bas-reliefs"]},
        },
        {
            "type": CulturalEntityType.ARCHITECTURAL_STYLE.value,
            "name": "Kalinga Architecture",
            "slug": "style-kalinga",
            "period": "6th – 15th Century CE",
            "desc": "Distinct sub-tradition of Nagara architecture developed in Odisha, comprising Rekha Deula (sanctum tower), Pidha Deula (assembly hall), and exquisite chlorite stone carving.",
            "geo": "Odisha / Eastern India",
            "meta": {"key_features": ["Rekha Deula", "Jagamohana", "Chariot Wheels", "Chlorite Reliefs"]},
        },
        {
            "type": CulturalEntityType.ARCHITECTURAL_STYLE.value,
            "name": "Indo-Islamic Architecture",
            "slug": "style-indo-islamic",
            "period": "12th – 18th Century CE",
            "desc": "Synthesis of Central Asian, Persian, and indigenous Indian masonry traditions featuring bulbous domes, pointed arches, jaali screens, and pietre dure inlay.",
            "geo": "North & Deccan India",
            "meta": {"key_features": ["Bulbous Dome", "Pietra Dura Inlay", "Charbagh Garden", "Minarets", "Jaali Screens"]},
        },

        # Cultural Traditions
        {
            "type": CulturalEntityType.CULTURAL_TRADITION.value,
            "name": "Living Saiva Temple Tradition",
            "slug": "tradition-living-saiva",
            "period": "Ancient – Present",
            "desc": "Continuous centuries-old Agamic worship, temple chariot processions, ritual bronze arts, and classical music honoring Lord Shiva in Tamil and Deccan shrines.",
            "geo": "Tamil Nadu & Deccan",
            "meta": {"texts": ["Saiva Agamas", "Tevaram"]},
        },
        {
            "type": CulturalEntityType.CULTURAL_TRADITION.value,
            "name": "Theravada & Mahayana Buddhist Tradition",
            "slug": "tradition-buddhist-heritage",
            "period": "6th Century BCE – Present",
            "desc": "Spiritual, philosophical, and artistic heritage encompassing stupa circumambulation, Jataka mural paintings, and monastic meditation.",
            "geo": "Central & Western India",
            "meta": {"practices": ["Stupa Pradakshina", "Vihara Monastic Living", "Jataka Visual Narratives"]},
        },
    ]

    named_entities: Dict[str, CulturalGraphEntity] = {}
    for spec in historical_entities_spec:
        ent = db.execute(
            select(CulturalGraphEntity).where(CulturalGraphEntity.slug == spec["slug"])
        ).scalar_one_or_none()

        if not ent:
            ent = CulturalGraphEntity(
                entity_type=spec["type"],
                canonical_name=spec["name"],
                slug=spec["slug"],
                description=spec["desc"],
                geographical_context=spec["geo"],
                period=spec["period"],
                metadata_json=spec.get("meta"),
                verification_status=CulturalEvidenceStatus.VERIFIED.value,
            )
            db.add(ent)
            db.flush()

        named_entities[spec["name"]] = ent

    # ---------------------------------------------------------
    # 3. MIGRATE EXISTING 8 HERITAGE CONNECTIONS 1-TO-1
    # ---------------------------------------------------------
    legacy_connections = db.execute(select(HeritageConnection)).scalars().all()
    primary_source = db.execute(select(HeritageSource).limit(1)).scalar_one_or_none()
    primary_source_id = primary_source.id if primary_source else None

    migrated_connections_count = 0
    for conn in legacy_connections:
        source_ent = entity_by_site_id.get(conn.source_site_id)
        target_ent = entity_by_site_id.get(conn.target_site_id)

        if not source_ent or not target_ent:
            continue

        existing_rel = db.execute(
            select(CulturalGraphRelationship).where(
                CulturalGraphRelationship.source_entity_id == source_ent.id,
                CulturalGraphRelationship.target_entity_id == target_ent.id,
                CulturalGraphRelationship.relationship_type == CulturalRelationshipType.HISTORICALLY_CONNECTED_TO.value,
            )
        ).scalar_one_or_none()

        if not existing_rel:
            rel = CulturalGraphRelationship(
                source_entity_id=source_ent.id,
                target_entity_id=target_ent.id,
                relationship_type=CulturalRelationshipType.HISTORICALLY_CONNECTED_TO.value,
                description=conn.description or f"Documented connection: {conn.relationship_type}",
                directionality="UNDIRECTED",
                evidence_status=CulturalEvidenceStatus.DOCUMENTED.value,
                confidence_score=conn.confidence_score or 0.9,
                primary_source_id=primary_source_id,
                source_citation="Archaeological Survey of India & National Heritage Network Baseline",
                historical_period=source_ent.period or target_ent.period,
                legacy_connection_id=conn.id,
                metadata_json={"legacy_type": conn.relationship_type},
            )
            db.add(rel)
            migrated_connections_count += 1

    # ---------------------------------------------------------
    # 4. EVIDENCE-BACKED HISTORICAL RELATIONSHIPS (ASI/UNESCO)
    # ---------------------------------------------------------
    def link_entities(
        site_keyword: str,
        target_entity_name: str,
        rel_type: CulturalRelationshipType,
        desc: str,
        period: Optional[str] = None,
    ):
        site_ent = next(
            (e for e in entity_by_site_id.values() if site_keyword.lower() in e.canonical_name.lower()),
            None,
        )
        target_ent = named_entities.get(target_entity_name)

        if not site_ent or not target_ent or site_ent.id == target_ent.id:
            return

        exists = db.execute(
            select(CulturalGraphRelationship).where(
                CulturalGraphRelationship.source_entity_id == site_ent.id,
                CulturalGraphRelationship.target_entity_id == target_ent.id,
                CulturalGraphRelationship.relationship_type == rel_type.value,
            )
        ).scalar_one_or_none()

        if not exists:
            new_rel = CulturalGraphRelationship(
                source_entity_id=site_ent.id,
                target_entity_id=target_ent.id,
                relationship_type=rel_type.value,
                description=desc,
                directionality="DIRECTED",
                evidence_status=CulturalEvidenceStatus.VERIFIED.value,
                confidence_score=1.0,
                primary_source_id=primary_source_id,
                source_citation="Archaeological Survey of India & UNESCO World Heritage Inscription Records",
                historical_period=period or site_ent.period,
            )
            db.add(new_rel)

    # Brihadisvara Temple linkages
    link_entities("Brihadisvara", "Chola Dynasty", CulturalRelationshipType.ASSOCIATED_WITH_DYNASTY, "Imperial Chola patron dynasty during reign of Rajaraja I", "11th Century CE")
    link_entities("Brihadisvara", "Rajaraja Chola I", CulturalRelationshipType.BUILT_BY, "Commissioned by Emperor Rajaraja Chola I and consecrated in 1010 CE", "1010 CE")
    link_entities("Brihadisvara", "Dravidian Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Quintessential masterpiece of Southern Indian Dravidian stone temple engineering")
    link_entities("Brihadisvara", "Living Saiva Temple Tradition", CulturalRelationshipType.ASSOCIATED_WITH_TRADITION, "Active living center of Saivite ritual, agamic tradition, and Chola bronze arts")

    # Hampi linkages
    link_entities("Hampi", "Vijayanagara Empire", CulturalRelationshipType.ASSOCIATED_WITH_DYNASTY, "Imperial capital city of the Vijayanagara Empire from 1336 to 1565 CE", "14th–16th Century CE")
    link_entities("Hampi", "Krishnadevaraya", CulturalRelationshipType.ASSOCIATED_WITH_PERSON, "Greatest Vijayanagara emperor who expanded the Hazara Rama and Krishna temple complexes", "1509–1529 CE")
    link_entities("Hampi", "Dravidian Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Late medieval Dravidian architecture with multi-pillared musical halls and dynamic monoliths")

    # Ellora & Kailasa linkages
    link_entities("Ellora", "Rashtrakuta Dynasty", CulturalRelationshipType.PATRONIZED_BY, "Monolithic Kailasa temple excavated under Rashtrakuta royal patronage", "8th Century CE")
    link_entities("Ellora", "Krishna I", CulturalRelationshipType.PATRONIZED_BY, "King Krishna I commissioned the single-rock top-down excavation of Kailasa", "c. 756–774 CE")
    link_entities("Ellora", "Rock-cut Monolithic Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "World's largest monolithic rock excavation hewn vertically from Charanandri hills")

    # Ajanta linkages
    link_entities("Ajanta", "Rock-cut Monolithic Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "30 rock-cut Buddhist cave monuments excavated along a horseshoe-shaped river ravine")
    link_entities("Ajanta", "Theravada & Mahayana Buddhist Tradition", CulturalRelationshipType.ASSOCIATED_WITH_TRADITION, "Monastic viharas and chaitya worship sanctuaries preserving classical Buddhist frescoes")

    # Sanchi linkages
    link_entities("Sanchi", "Maurya Empire", CulturalRelationshipType.PATRONIZED_BY, "Original hemispherical brick stupa founded under Mauryan royal sponsorship", "3rd Century BCE")
    link_entities("Sanchi", "Emperor Ashoka", CulturalRelationshipType.ASSOCIATED_WITH_PERSON, "Emperor Ashoka oversaw initial stupa construction and erected the polished sandstone pillar", "3rd Century BCE")
    link_entities("Sanchi", "Theravada & Mahayana Buddhist Tradition", CulturalRelationshipType.ASSOCIATED_WITH_TRADITION, "Venerated pilgrimage stupa complex with exquisitely carved Torana gateways depicting Jataka tales")

    # Konark Sun Temple linkages
    link_entities("Konark", "Eastern Ganga Dynasty", CulturalRelationshipType.ASSOCIATED_WITH_DYNASTY, "Built under the Eastern Ganga monarchs of coastal Kalinga", "13th Century CE")
    link_entities("Konark", "King Narasimhadeva I", CulturalRelationshipType.BUILT_BY, "Commissioned by King Narasimhadeva I to celebrate military victories and honor the Sun god Surya", "1250 CE")
    link_entities("Konark", "Kalinga Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Pinnacle of Kalinga architecture representing the cosmic chariot of Surya with 24 carved stone wheels")

    # Khajuraho linkages
    link_entities("Khajuraho", "Chandela Dynasty", CulturalRelationshipType.PATRONIZED_BY, "Built by the Chandela rulers of Bundelkhand between 950 and 1050 CE", "10th–11th Century CE")
    link_entities("Khajuraho", "Nagara Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Masterpiece of Central Indian Nagara temple architecture with curvilinear shikharas and narrative facades")

    # Taj Mahal linkages
    link_entities("Taj", "Mughal Dynasty", CulturalRelationshipType.ASSOCIATED_WITH_DYNASTY, "Peak architectural achievement of the Mughal Empire in northern India", "17th Century CE")
    link_entities("Taj", "Shah Jahan", CulturalRelationshipType.BUILT_BY, "Commissioned by Mughal Emperor Shah Jahan as a mausoleum for Mumtaz Mahal", "1631–1648 CE")
    link_entities("Taj", "Indo-Islamic Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Monumental Indo-Islamic marble architecture with symmetrical charbagh gardens and pietra dura inlay")

    # Golconda Fort linkages
    link_entities("Golconda", "Kakatiya Dynasty", CulturalRelationshipType.ASSOCIATED_WITH_DYNASTY, "Originally built as a mud fort by the Kakatiyas in the 12th century before Qutb Shahi expansion")

    # Meenakshi Amman Temple linkages
    link_entities("Meenakshi", "Pandya Dynasty", CulturalRelationshipType.PATRONIZED_BY, "Ancient royal seat and sacred religious center patronized by the Pandya kings of Madurai")
    link_entities("Meenakshi", "Dravidian Architecture", CulturalRelationshipType.HAS_ARCHITECTURAL_STYLE, "Iconic Dravidian sacred complex dominated by 14 monumental gopurams encrusted with thousands of stucco figures")
    link_entities("Meenakshi", "Living Saiva Temple Tradition", CulturalRelationshipType.ASSOCIATED_WITH_TRADITION, "Continuously active Saivite and Shakta living traditions with daily rituals and the annual Chithirai festival")

    db.commit()

    total_entities = db.execute(select(CulturalGraphEntity)).scalars().all()
    total_relationships = db.execute(select(CulturalGraphRelationship)).scalars().all()

    return {
        "total_entities": len(total_entities),
        "total_relationships": len(total_relationships),
        "migrated_legacy_connections": migrated_connections_count,
    }
