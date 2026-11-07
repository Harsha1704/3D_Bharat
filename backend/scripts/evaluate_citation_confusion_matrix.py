"""
3D BHARAT — Phase 9.1.2 Citation Validation Confusion Matrix Evaluation
Evaluates `evaluate_claim_against_passage` on a manually labelled gold-standard dataset across 8 distinct error classes:
1. SUPPORTED: Genuine historical claim fully supported by passage.
2. UNSUPPORTED: Irrelevant passage with zero entity relation.
3. PARTIALLY_SUPPORTED: Blended claim with ungrounded extrapolations.
4. CONTRADICTED_DATE: Explicit date / year contradiction.
5. CONTRADICTED_DYNASTY: Mismatched dynastic attribution.
6. WRONG_MONUMENT: Feature attributed to incorrect monument.
7. INCORRECT_RELATIONSHIP: Correct entities but inverted or fabricated relationship.
8. INCORRECT_CONTEXT: Correct date but distorted historical event / context.
"""

import json
from typing import Dict, Any, List
from app.services.ai_citation_service import evaluate_claim_against_passage

LABELLED_CITATION_BENCHMARK: List[Dict[str, Any]] = [
    # 1. Correctly Supported Claims (Ground Truth = True)
    {
        "id": "c01", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The Konark Sun Temple was consecrated in 1250 CE by King Narasimhadeva I of the Eastern Ganga dynasty.",
        "claim": "King Narasimhadeva I of the Eastern Ganga dynasty consecrated the Konark Sun Temple in 1250 CE."
    },
    {
        "id": "c02", "category": "SUPPORTED", "ground_truth": True,
        "passage": "Brihadisvara Temple was consecrated on the 275th day of the 25th regnal year (1010 CE) of Rajaraja Chola I.",
        "claim": "The temple of Brihadisvara was consecrated in 1010 CE by Emperor Rajaraja Chola I."
    },
    {
        "id": "c03", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The monolithic Kailasa Temple at Ellora Cave 16 was excavated under the patronage of Rashtrakuta king Krishna I.",
        "claim": "Rashtrakuta king Krishna I commissioned the excavation of the monolithic Kailasa Temple at Ellora."
    },
    {
        "id": "c04", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The Vitthala Temple stone chariot at Hampi is dedicated to Garuda and built of dressed granite blocks.",
        "claim": "The granite stone chariot of the Vitthala Temple at Hampi is dedicated to Garuda."
    },
    {
        "id": "c05", "category": "SUPPORTED", "ground_truth": True,
        "passage": "Rani-ki-Vav was commissioned by Queen Udayamati in memory of her deceased husband King Bhima I of the Chaulukya dynasty.",
        "claim": "Queen Udayamati constructed Rani-ki-Vav as a memorial to Chaulukya ruler Bhima I."
    },
    {
        "id": "c06", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The Great Stupa at Sanchi was founded in the 3rd century BCE by Mauryan Emperor Ashoka.",
        "claim": "Mauryan Emperor Ashoka established the Great Stupa at Sanchi in the 3rd century BCE."
    },
    {
        "id": "c07", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The Vimana of Brihadisvara Temple rises 13 storeys to an extraordinary height of 66 meters crowned by a monolithic cupola.",
        "claim": "Brihadisvara Temple features a 66-meter Dravidian vimana capped by a single octagonal granite block."
    },
    {
        "id": "c08", "category": "SUPPORTED", "ground_truth": True,
        "passage": "Harappan Dholavira features sixteen monumental stone-cut stormwater reservoirs storing up to 250,000 cubic meters of water.",
        "claim": "Dholavira engineered sixteen rock-cut stormwater reservoirs to preserve desert precipitation."
    },
    {
        "id": "c09", "category": "SUPPORTED", "ground_truth": True,
        "passage": "Nalanda Mahavihara was patronized by the Gupta dynasty founder Kumaragupta I and later expanded by Pala rulers.",
        "claim": "Nalanda was established under Gupta Emperor Kumaragupta I and received continued Pala patronage."
    },
    {
        "id": "c10", "category": "SUPPORTED", "ground_truth": True,
        "passage": "The Taj Mahal was commissioned in 1631 CE by Mughal Emperor Shah Jahan for his empress Mumtaz Mahal.",
        "claim": "Shah Jahan commissioned the white marble Taj Mahal in 1631 CE as a mausoleum for Mumtaz Mahal."
    },

    # 2. Unsupported Claims (Ground Truth = False)
    {
        "id": "c11", "category": "UNSUPPORTED", "ground_truth": False,
        "passage": "The Great Stupa at Sanchi features a hemispherical masonry dome crowned by a harmika and three chhatras.",
        "claim": "The subterranean aqueduct transported forty thousand gallons of desert rainfall through terracotta pipes."
    },
    {
        "id": "c12", "category": "UNSUPPORTED", "ground_truth": False,
        "passage": "Ajanta Cave 26 contains a monumental monolithic relief of the Mahaparinirvana of Gautama Buddha measuring 7 meters.",
        "claim": "The iron pillar resisted rust due to a protective layer of crystalline iron hydrogen phosphate."
    },
    {
        "id": "c13", "category": "UNSUPPORTED", "ground_truth": False,
        "passage": "Chittorgarh Fort features seven defensive gates and the nine-storey Victory Tower (Vijay Stambha).",
        "claim": "The hydraulic lift raised ships across the tidal harbor using weighted granite counterbalances."
    },
    {
        "id": "c14", "category": "UNSUPPORTED", "ground_truth": False,
        "passage": "The Sun Temple at Modhera features the Surya Kund stepwell adorned with 108 miniature shrines.",
        "claim": "The Portuguese armada captured the sea citadel after a four-month siege in 1505 CE."
    },
    {
        "id": "c15", "category": "UNSUPPORTED", "ground_truth": False,
        "passage": "The Golconda fortress is protected by three concentric granite fortification walls with 87 semi-circular bastions.",
        "claim": "The Buddhist library stored ten million palm-leaf manuscripts translated into classical Chinese."
    },

    # 3. Partially Supported Claims (Ground Truth = False)
    {
        "id": "c16", "category": "PARTIALLY_SUPPORTED", "ground_truth": False,
        "passage": "King Narasimhadeva I built the Konark Sun Temple using khondalite stone with iron dowels.",
        "claim": "King Narasimhadeva I built Konark with khondalite and imported marble from Italian quarries."
    },
    {
        "id": "c17", "category": "PARTIALLY_SUPPORTED", "ground_truth": False,
        "passage": "Brihadisvara Temple was constructed under Rajaraja Chola I between 1003 and 1010 CE.",
        "claim": "Brihadisvara was constructed by Rajaraja Chola I alongside Venetian naval architects."
    },
    {
        "id": "c18", "category": "PARTIALLY_SUPPORTED", "ground_truth": False,
        "passage": "The Great Stupa of Sanchi was enlarged during the Sunga period with stone casing and torana gateways.",
        "claim": "Sanchi was enlarged by the Sungas who installed an electric lightning protection system."
    },
    {
        "id": "c19", "category": "PARTIALLY_SUPPORTED", "ground_truth": False,
        "passage": "Queen Udayamati commissioned Rani-ki-Vav with seven subterranean pillared terraces.",
        "claim": "Queen Udayamati built Rani-ki-Vav as a seven-tier stepwell equipped with steam turbine pumps."
    },
    {
        "id": "c20", "category": "PARTIALLY_SUPPORTED", "ground_truth": False,
        "passage": "Shah Jahan built the Taj Mahal using Makrana marble transported by bullock carts.",
        "claim": "Shah Jahan built the Taj Mahal using Makrana marble transported by diesel rail locomotives."
    },

    # 4. Contradicted Dates (Ground Truth = False)
    {
        "id": "c21", "category": "CONTRADICTED_DATE", "ground_truth": False,
        "passage": "Brihadisvara Temple was consecrated in 1010 CE during the 25th regnal year of Rajaraja Chola I.",
        "claim": "Brihadisvara Temple was consecrated in 1450 CE by Rajaraja Chola."
    },
    {
        "id": "c22", "category": "CONTRADICTED_DATE", "ground_truth": False,
        "passage": "The Konark Sun Temple was consecrated in 1250 CE by King Narasimhadeva I.",
        "claim": "King Narasimhadeva I completed the Konark Sun Temple in 1650 CE."
    },
    {
        "id": "c23", "category": "CONTRADICTED_DATE", "ground_truth": False,
        "passage": "Vijayanagara capital was founded in 1336 CE on the banks of the Tungabhadra River.",
        "claim": "The capital of Vijayanagara was founded in 1050 CE by Harihara and Bukka."
    },
    {
        "id": "c24", "category": "CONTRADICTED_DATE", "ground_truth": False,
        "passage": "The Taj Mahal construction commenced in 1631 CE following the death of Mumtaz Mahal.",
        "claim": "The Taj Mahal was commissioned in 1200 CE by Shah Jahan."
    },
    {
        "id": "c25", "category": "CONTRADICTED_DATE", "ground_truth": False,
        "passage": "Kakatiya Rudreshwara Ramappa Temple was consecrated in 1213 CE under King Ganapatideva.",
        "claim": "Ramappa Temple was consecrated in 1580 CE by General Recharla Rudra."
    },

    # 5. Contradicted Dynasties (Ground Truth = False)
    {
        "id": "c26", "category": "CONTRADICTED_DYNASTY", "ground_truth": False,
        "passage": "The monolithic Kailasa temple at Ellora was excavated under Rashtrakuta patronage.",
        "claim": "The monolithic Kailasa temple at Ellora was constructed by the Mughal dynasty."
    },
    {
        "id": "c27", "category": "CONTRADICTED_DYNASTY", "ground_truth": False,
        "passage": "The Brihadisvara Temple was built by Emperor Rajaraja Chola I of the Chola empire.",
        "claim": "Brihadisvara Temple was erected by the Pallava rulers in Thanjavur."
    },
    {
        "id": "c28", "category": "CONTRADICTED_DYNASTY", "ground_truth": False,
        "passage": "The Sun Temple at Konark was commissioned by King Narasimhadeva I of the Eastern Ganga dynasty.",
        "claim": "The Konark Sun Temple was commissioned by the Chandela dynasty in Odisha."
    },
    {
        "id": "c29", "category": "CONTRADICTED_DYNASTY", "ground_truth": False,
        "passage": "The Kandariya Mahadeva temple at Khajuraho was erected by Chandela king Vidyadhara.",
        "claim": "The Kandariya Mahadeva temple was built by the Maurya emperors at Khajuraho."
    },
    {
        "id": "c30", "category": "CONTRADICTED_DYNASTY", "ground_truth": False,
        "passage": "Golconda Fort was fortified by the Qutb Shahi dynasty with massive granite walls.",
        "claim": "Golconda Fort was fortified by the Chola dynasty in Hyderabad."
    },

    # 6. Wrong Monument Citations (Ground Truth = False)
    {
        "id": "c31", "category": "WRONG_MONUMENT", "ground_truth": False,
        "passage": "The Sun Temple at Konark is designed in the shape of a colossal chariot dedicated to Surya.",
        "claim": "The Taj Mahal features a colossal chariot design with 24 carved stone wheels."
    },
    {
        "id": "c32", "category": "WRONG_MONUMENT", "ground_truth": False,
        "passage": "Rani-ki-Vav at Patan is an inverted stepwell descending into seven subterranean terraces.",
        "claim": "The Kailasa temple descends into seven subterranean stepwell terraces dedicated to Vishnu."
    },
    {
        "id": "c33", "category": "WRONG_MONUMENT", "ground_truth": False,
        "passage": "The 66-meter Dravidian vimana of Brihadisvara Temple dominates the Thanjavur landscape.",
        "claim": "The Ajanta caves are crowned by a 66-meter granite Dravidian vimana."
    },
    {
        "id": "c34", "category": "WRONG_MONUMENT", "ground_truth": False,
        "passage": "Dholavira showcases Harappan water architecture with 16 interconnected masonry reservoirs.",
        "claim": "Meenakshi Temple preserves 16 Harappan rock-cut stormwater reservoirs."
    },
    {
        "id": "c35", "category": "WRONG_MONUMENT", "ground_truth": False,
        "passage": "The Sanchi Stupa 1 is surrounded by four ceremonial torana gateways with carved Jataka tales.",
        "claim": "Chittorgarh Fort is crowned by four torana gateways depicting Jataka tales."
    },

    # 7. Correct Entities but Incorrect Relationships (Ground Truth = False)
    {
        "id": "c36", "category": "INCORRECT_RELATIONSHIP", "ground_truth": False,
        "passage": "King Narasimhadeva I of the Eastern Ganga dynasty launched campaigns against the Delhi Sultanate.",
        "claim": "The Delhi Sultanate consecrated King Narasimhadeva I as the hereditary ruler of Konark."
    },
    {
        "id": "c37", "category": "INCORRECT_RELATIONSHIP", "ground_truth": False,
        "passage": "Queen Udayamati built Rani-ki-Vav in memory of her late husband King Bhima I.",
        "claim": "King Bhima I constructed Rani-ki-Vav to commemorate the demise of Queen Udayamati."
    },
    {
        "id": "c38", "category": "INCORRECT_RELATIONSHIP", "ground_truth": False,
        "passage": "Shah Jahan imprisoned in the Agra Fort gazed across the Yamuna at the Taj Mahal.",
        "claim": "The Taj Mahal held Emperor Shah Jahan prisoner to prevent his return to Agra Fort."
    },
    {
        "id": "c39", "category": "INCORRECT_RELATIONSHIP", "ground_truth": False,
        "passage": "Sir John Marshall excavated and restored the Buddhist stupas at Sanchi.",
        "claim": "The Buddhist stupas at Sanchi financed and commissioned Sir John Marshall."
    },
    {
        "id": "c40", "category": "INCORRECT_RELATIONSHIP", "ground_truth": False,
        "passage": "General Recharla Rudra served under Kakatiya monarch Ganapatideva during the construction of Ramappa Temple.",
        "claim": "Kakatiya monarch Ganapatideva served as chief architect under General Recharla Rudra."
    },

    # 8. Correct Dates but Incorrect Historical Context (Ground Truth = False)
    {
        "id": "c41", "category": "INCORRECT_CONTEXT", "ground_truth": False,
        "passage": "Brihadisvara was consecrated in 1010 CE by Rajaraja Chola I.",
        "claim": "In 1010 CE, the Vijayanagara empire was founded by Rajaraja Chola."
    },
    {
        "id": "c42", "category": "INCORRECT_CONTEXT", "ground_truth": False,
        "passage": "In 1250 CE, King Narasimhadeva I built the Sun Temple at Konark.",
        "claim": "In 1250 CE, King Narasimhadeva I constructed the Taj Mahal in Agra."
    },
    {
        "id": "c43", "category": "INCORRECT_CONTEXT", "ground_truth": False,
        "passage": "Vijayanagara was established in 1336 CE by Harihara I and Bukka Raya I.",
        "claim": "In 1336 CE, Harihara and Bukka completed the Buddhist caves of Ajanta."
    },
    {
        "id": "c44", "category": "INCORRECT_CONTEXT", "ground_truth": False,
        "passage": "In 1631 CE, Shah Jahan lost his queen Mumtaz Mahal and began planning the Taj Mahal.",
        "claim": "In 1631 CE, Shah Jahan conquered the Chola empire and consecrated Brihadisvara."
    },
    {
        "id": "c45", "category": "INCORRECT_CONTEXT", "ground_truth": False,
        "passage": "Ramappa Temple was consecrated in 1213 CE by Recharla Rudra.",
        "claim": "In 1213 CE, Recharla Rudra erected the Great Stupa of Sanchi."
    },
]


def run_confusion_matrix_evaluation() -> Dict[str, Any]:
    total_evals = len(LABELLED_CITATION_BENCHMARK)
    tp = 0  # Ground truth True, Classified True
    fp = 0  # Ground truth False, Classified True (False Acceptance)
    tn = 0  # Ground truth False, Classified False (True Rejection)
    fn = 0  # Ground truth True, Classified False (False Rejection)

    category_results = {}

    for item in LABELLED_CITATION_BENCHMARK:
        cid = item["id"]
        cat = item["category"]
        gt = item["ground_truth"]
        passage = item["passage"]
        claim = item["claim"]

        eval_res = evaluate_claim_against_passage(claim, passage)
        pred = eval_res.is_supported

        if cat not in category_results:
            category_results[cat] = {"total": 0, "correct": 0, "predictions": []}

        category_results[cat]["total"] += 1
        is_correct = (pred == gt)
        if is_correct:
            category_results[cat]["correct"] += 1

        category_results[cat]["predictions"].append({
            "id": cid,
            "claim": claim[:60],
            "ground_truth": gt,
            "predicted": pred,
            "status": eval_res.status,
            "reason": eval_res.reason
        })

        if gt and pred:
            tp += 1
        elif not gt and pred:
            fp += 1
        elif not gt and not pred:
            tn += 1
        elif gt and not pred:
            fn += 1

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    far = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0  # False Acceptance Rate
    accuracy = round((tp + tn) / total_evals, 4)

    report = {
        "total_test_cases": total_evals,
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
        },
        "metrics": {
            "precision": precision,
            "recall": recall,
            "false_acceptance_rate": far,
            "accuracy": accuracy,
        },
        "category_breakdown": {
            cat: {
                "total": data["total"],
                "accuracy": round(data["correct"] / data["total"], 4),
            }
            for cat, data in category_results.items()
        },
        "false_positive_cases": [
            p for cat, data in category_results.items()
            for p in data["predictions"]
            if not p["ground_truth"] and p["predicted"]
        ]
    }

    print("CITATION_VALIDATOR_CONFUSION_MATRIX_REPORT:")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    run_confusion_matrix_evaluation()
