"""Seed database with major heritage sites across India and cultural connections."""
from app.core.database import SessionLocal
from app.models.heritage_site import HeritageSite
from app.models.heritage_connection import HeritageConnection

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(HeritageSite).first()
        if existing:
            print("Database already has heritage sites. Skipping seed.")
            return

        sites_data = [
            {
                "external_id": "ASI_HAMPI_001",
                "name": "Group of Monuments at Hampi",
                "state": "Karnataka",
                "district": "Vijayanagara",
                "city": "Hosapete",
                "category": "Temple Complex & Ruins",
                "period": "14th - 16th Century CE (Vijayanagara Empire)",
                "description": "The austere, grandiose site of Hampi was the capital of the Vijayanagara Empire. It comprises monumental temple complexes, palaces, and aquatic structures along the Tungabhadra River.",
                "significance": "UNESCO World Heritage Site, epicenter of South Indian medieval renaissance and Dravidian architecture.",
                "architecture": "Vijayanagara Dravidian architecture with monolithic granite sculptures, musical pillars, and stone chariots.",
                "latitude": 15.3350,
                "longitude": 76.4600,
                "tags": ["UNESCO", "Dravidian", "Vijayanagara", "Granite Architecture", "Tungabhadra"],
                "historical_events": ["Coronation of Krishnadevaraya 1509", "Battle of Talikota 1565"],
                "associated_people": ["Krishnadevaraya", "Harihara I", "Bukka Raya I"],
                "traditions": ["Hampi Utsav", "Virupaksha Car Festival"]
            },
            {
                "external_id": "ASI_BRIHAD_002",
                "name": "Brihadisvara Temple",
                "state": "Tamil Nadu",
                "district": "Thanjavur",
                "city": "Thanjavur",
                "category": "Temple",
                "period": "11th Century CE (Chola Dynasty)",
                "description": "Built by Raja Raja Chola I, this monumental Shiva temple is one of the Great Living Chola Temples, crowned with a massive monolithic granite kumbam weighing over 80 tons.",
                "significance": "Pinnacle of pure Dravidian temple architecture and monumental stone carving.",
                "architecture": "Dravidian Vimana architecture with massive sanctum tower, fresco murals, and bronze iconographies.",
                "latitude": 10.7828,
                "longitude": 79.1318,
                "tags": ["UNESCO", "Chola", "Dravidian", "Granite", "Great Living Chola Temples"],
                "historical_events": ["Consecration by Raja Raja Chola I in 1010 CE"],
                "associated_people": ["Raja Raja Chola I", "Karuvur Devar"],
                "traditions": ["Natyanjali Dance Festival", "Maha Shivaratri celebrations"]
            },
            {
                "external_id": "ASI_KONARK_003",
                "name": "Sun Temple Konark",
                "state": "Odisha",
                "district": "Puri",
                "city": "Konark",
                "category": "Temple",
                "period": "13th Century CE (Eastern Ganga Dynasty)",
                "description": "A monumental 24-wheel chariot of the Sun God Surya pulled by seven horses, carved exquisitely from Khondalite stone on the Bay of Bengal coastline.",
                "significance": "Masterpiece of Kalinga architectural geometry and symbolic solar horology.",
                "architecture": "Kalinga architecture with rekha deula sanctum, intricately carved celestial dancers, sundials, and erotic stone reliefs.",
                "latitude": 19.8876,
                "longitude": 86.0945,
                "tags": ["UNESCO", "Kalinga", "Eastern Ganga", "Solar Horology", "Coastal Heritage"],
                "historical_events": ["Commissioned by King Narasimhadeva I (1250 CE)"],
                "associated_people": ["King Narasimhadeva I", "Bisu Maharana"],
                "traditions": ["Konark Dance Festival", "Chandrabhaga Mela"]
            },
            {
                "external_id": "ASI_AJANTA_004",
                "name": "Ajanta Caves",
                "state": "Maharashtra",
                "district": "Chhatrapati Sambhaji Nagar",
                "city": "Ajanta",
                "category": "Rock-cut Cave Complex",
                "period": "2nd Century BCE - 5th Century CE",
                "description": "Thirty rock-cut Buddhist cave monuments carved into a horseshoe cliff along the Waghora River, housing world-renowned Buddhist frescoes and sculptures.",
                "significance": "Regarded as the pinnacle of ancient Indian mural painting and classical Buddhist narrative art.",
                "architecture": "Rock-cut Viharas and Chaitya Grihas with tempera mural masterpieces and monolithic stupas.",
                "latitude": 20.5519,
                "longitude": 75.7033,
                "tags": ["UNESCO", "Buddhist", "Murals", "Vakataka", "Rock-cut Architecture"],
                "historical_events": ["Rediscovery by John Smith in 1819"],
                "associated_people": ["Harisena", "Varahadeva"],
                "traditions": ["Ajanta Ellora International Festival", "Buddha Jayanti"]
            },
            {
                "external_id": "ASI_ELLORA_005",
                "name": "Ellora Caves & Kailasa Temple",
                "state": "Maharashtra",
                "district": "Chhatrapati Sambhaji Nagar",
                "city": "Ellora",
                "category": "Rock-cut Monument",
                "period": "6th - 10th Century CE",
                "description": "A complex of 34 major caves representing Hindu, Buddhist, and Jain faiths, featuring Cave 16 (Kailasa Temple), the largest monolithic rock excavation in the world.",
                "significance": "Supreme engineering feat of single-rock top-down mountain carving symbolizing Mount Kailash.",
                "architecture": "Monolithic multi-storey rock excavation, Dravidian shikhara, Rashtrakuta stone sculpture.",
                "latitude": 20.0268,
                "longitude": 75.1780,
                "tags": ["UNESCO", "Rashtrakuta", "Monolithic", "Kailasa", "Multi-faith Heritage"],
                "historical_events": ["Commissioned by Rashtrakuta King Krishna I (756-773 CE)"],
                "associated_people": ["Krishna I", "Rashtrakuta dynasty builders"],
                "traditions": ["Ellora Mahotsav", "Maha Shivaratri"]
            },
            {
                "external_id": "ASI_KHAJURAHO_006",
                "name": "Khajuraho Group of Monuments",
                "state": "Madhya Pradesh",
                "district": "Chhatarpur",
                "city": "Khajuraho",
                "category": "Temple Complex",
                "period": "950 - 1050 CE (Chandela Dynasty)",
                "description": "Celebrated group of Hindu and Jain nagara temples famous for expressive stone sculptures, architectural harmony, and celebration of human life and spirituality.",
                "significance": "Peak expression of North Indian Nagara temple architecture and artistic freedom.",
                "architecture": "Nagara style with soaring curvilinear shikhara, jagati platforms, and sandstone friezes.",
                "latitude": 24.8318,
                "longitude": 79.9199,
                "tags": ["UNESCO", "Nagara", "Chandela", "Sandstone Sculptures", "Jain Heritage"],
                "historical_events": ["Built under Chandela kings Yashovarman and Dhanga"],
                "associated_people": ["King Dhanga", "Yashovarman"],
                "traditions": ["Khajuraho Dance Festival"]
            },
            {
                "external_id": "ASI_SANCHI_007",
                "name": "Buddhist Monuments at Sanchi",
                "state": "Madhya Pradesh",
                "district": "Raisen",
                "city": "Sanchi",
                "category": "Stupa Complex",
                "period": "3rd Century BCE - 12th Century CE",
                "description": "The Great Stupa at Sanchi is the oldest surviving stone structure in India, commissioned by Emperor Ashoka with monumental toranas (ceremonial gateways).",
                "significance": "Foundational Buddhist architectural model and early narrative stone relief carving in Asia.",
                "architecture": "Hemispherical stone stupa with circumambulatory path (pradakshina patha) and four carved toranas.",
                "latitude": 23.4795,
                "longitude": 77.7397,
                "tags": ["UNESCO", "Mauryan", "Ashoka", "Buddhist", "Stupa"],
                "historical_events": ["Foundation laid by Emperor Ashoka the Great 3rd c. BCE"],
                "associated_people": ["Emperor Ashoka", "Queen Devi"],
                "traditions": ["Chethiyagiri Vihara Festival", "Buddha Jayanti"]
            },
            {
                "external_id": "ASI_MEENAKSHI_008",
                "name": "Meenakshi Amman Temple",
                "state": "Tamil Nadu",
                "district": "Madurai",
                "city": "Madurai",
                "category": "Living Temple",
                "period": "6th Century BCE foundation / 16th - 17th Century CE Nayak reconstruction",
                "description": "Historic Hindu temple on the Vaigai River, famous for 14 towering gopurams encrusted with thousands of stucco mythological figures and the Hall of 1000 Pillars.",
                "significance": "Centerpiece of Tamil literary, musical, and living spiritual heritage for over two millennia.",
                "architecture": "Late Dravidian Nayak architecture with soaring polychrome gopurams and musical stone pillars.",
                "latitude": 9.9195,
                "longitude": 78.1193,
                "tags": ["Living Heritage", "Dravidian", "Pandya", "Nayak", "Vaigai"],
                "historical_events": ["Rebuilt by Vishwanatha Nayak and Tirumala Nayak (1623-1655 CE)"],
                "associated_people": ["Tirumala Nayak", "Queen Mangammal"],
                "traditions": ["Chithirai Festival", "Meenakshi Thirukalyanam"]
            },
            {
                "external_id": "ASI_TAJ_009",
                "name": "Taj Mahal",
                "state": "Uttar Pradesh",
                "district": "Agra",
                "city": "Agra",
                "category": "Mausoleum",
                "period": "1631 - 1648 CE (Mughal Empire)",
                "description": "An immense ivory-white marble mausoleum on the right bank of the Yamuna River, harmonizing Persian, Islamic, and Indian architectural aesthetics.",
                "significance": "Universal icon of architectural proportion, pietra dura inlay craftsmanship, and Mughal aesthetic zenith.",
                "architecture": "Indo-Islamic Mughal symmetry, double-dome geometry, minarets, charbagh gardens, and marble lapidary inlay.",
                "latitude": 27.1751,
                "longitude": 78.0421,
                "tags": ["UNESCO", "Mughal", "Marble", "Indo-Islamic", "Yamuna"],
                "historical_events": ["Commissioned by Emperor Shah Jahan in memory of Mumtaz Mahal"],
                "associated_people": ["Shah Jahan", "Mumtaz Mahal", "Ustad Ahmad Lahori"],
                "traditions": ["Taj Mahotsav"]
            },
            {
                "external_id": "ASI_GOLCONDA_010",
                "name": "Golconda Fort",
                "state": "Telangana",
                "district": "Hyderabad",
                "city": "Hyderabad",
                "category": "Fortress",
                "period": "12th Century CE (Kakatiya) - 16th Century CE (Qutb Shahi)",
                "description": "Fortified citadel famous for its acoustic engineering, water supply systems, diamond vaults, and the legendary Koh-i-Noor diamond trade.",
                "significance": "Strategic medieval citadel connecting Deccan geopolitical routes and global gem trade.",
                "architecture": "Indo-Islamic and Kakatiya military fortifications, acoustic grand arches, and royal palaces.",
                "latitude": 17.3833,
                "longitude": 78.4011,
                "tags": ["Deccan", "Kakatiya", "Qutb Shahi", "Acoustics", "Fortress"],
                "historical_events": ["Siege of Golconda by Aurangzeb in 1687"],
                "associated_people": ["Ibrahim Quli Qutb Shah", "Muhammad Quli Qutb Shah"],
                "traditions": ["Golconda Masters", "Bonalu Celebrations"]
            }
        ]

        created_sites = []
        for s in sites_data:
            site = HeritageSite(
                external_id=s["external_id"],
                name=s["name"],
                state=s["state"],
                district=s["district"],
                city=s["city"],
                category=s["category"],
                period=s["period"],
                description=s["description"],
                significance=s["significance"],
                architecture=s["architecture"],
                latitude=s["latitude"],
                longitude=s["longitude"],
                location=f"POINT({s['longitude']} {s['latitude']})",
                tags=s["tags"],
                historical_events=s["historical_events"],
                associated_people=s["associated_people"],
                traditions=s["traditions"]
            )
            db.add(site)
            created_sites.append(site)

        db.commit()

        # Refresh to get generated IDs
        for site in created_sites:
            db.refresh(site)

        site_by_ext = {s.external_id: s.id for s in created_sites}

        # Seed cultural connections
        connections_data = [
            # Hampi <-> Brihadisvara (Dravidian architecture & imperial rivalry/patronage)
            ("ASI_HAMPI_001", "ASI_BRIHAD_002", "ARCHITECTURAL_EVOLUTION", "Evolution of Dravidian temple stone carving from Chola monumentalism to Vijayanagara dynamic pillared halls", 0.92),
            # Brihadisvara <-> Meenakshi (Tamil classical temple continuum)
            ("ASI_BRIHAD_002", "ASI_MEENAKSHI_008", "CULTURAL_CONTINUUM", "Continuum of Tamil temple traditions, bronze arts, and living Saiva rituals", 0.95),
            # Ajanta <-> Ellora (Rock-cut cliff neighbors & artistic evolution)
            ("ASI_AJANTA_004", "ASI_ELLORA_005", "GEOGRAPHICAL_AND_ARTISTIC_SUCCESSION", "Sequential evolution of Western Ghats rock-cut architecture from Buddhist monasteries to multi-faith monolithic temples", 0.98),
            # Ellora (Kailasa) <-> Brihadisvara (Monolithic stone ambition)
            ("ASI_ELLORA_005", "ASI_BRIHAD_002", "MONUMENTAL_STONE_TRADITION", "Shared monumental stone engineering ambition across Rashtrakuta and Chola empires", 0.85),
            # Sanchi <-> Ajanta (Buddhist transmission)
            ("ASI_SANCHI_007", "ASI_AJANTA_004", "BUDDHIST_PHILOSOPHICAL_TRANSMISSION", "Transmission of Buddhist visual narratives and stupa iconography from central India to Deccan rock caves", 0.90),
            # Khajuraho <-> Konark (Nagara & Kalinga shikhara geometric affinity)
            ("ASI_KHAJURAHO_006", "ASI_KONARK_003", "TEMPLE_GEOMETRIC_AFFINITY", "Parallel 10th-13th century Nagara-Kalinga architectural mastery in curvilinear shikharas and narrative temple facades", 0.88),
            # Golconda <-> Hampi (Deccan Sultanate and Vijayanagara geopolitical interaction)
            ("ASI_GOLCONDA_010", "ASI_HAMPI_001", "DECCAN_GEOPOLITICAL_INTERACTION", "Intersecting trade routes, diamond economy, and military fortification developments across medieval Deccan", 0.86),
            # Taj Mahal <-> Golconda (Indo-Islamic architectural & material interchange)
            ("ASI_TAJ_009", "ASI_GOLCONDA_010", "MATERIAL_AND_CRAFT_EXCHANGE", "Mughal and Deccan courtly aesthetic interchange and lapidary gem trade", 0.80),
        ]

        for src_ext, tgt_ext, rel, desc, score in connections_data:
            if src_ext in site_by_ext and tgt_ext in site_by_ext:
                conn = HeritageConnection(
                    source_site_id=site_by_ext[src_ext],
                    target_site_id=site_by_ext[tgt_ext],
                    relationship_type=rel,
                    description=desc,
                    confidence_score=score
                )
                db.add(conn)

        db.commit()
        print(f"Successfully seeded {len(created_sites)} heritage sites and {len(connections_data)} cultural connections!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
