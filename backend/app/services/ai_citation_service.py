import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional

from app.schemas.ai import AICitation
from app.services.ai_retrieval_service import EvidenceItem

KNOWN_DYNASTIES = [
    "Chola", "Pallava", "Chalukya", "Rashtrakuta", "Maurya", "Gupta",
    "Mughal", "Kakatiya", "Eastern Ganga", "Chandela", "Pandya",
    "Solanki", "Chaulukya", "Guhila", "Sisodia", "Yadava", "Seuna",
    "Qutb Shahi", "Vakataka", "Satavahana", "Sunga", "Pala", "Karkota", "Nayaka"
]

KNOWN_MONUMENTS = [
    "Konark", "Brihadisvara", "Hampi", "Ajanta", "Ellora", "Kailasa", "Khajuraho",
    "Sanchi", "Meenakshi", "Taj Mahal", "Golconda", "Rani-ki-Vav", "Pattadakal",
    "Mahabodhi", "Nalanda", "Ramappa", "Dholavira", "Chittorgarh", "Kumbhalgarh",
    "Martand", "Bekal", "Daulatabad", "Adalaj", "Vijayanagara", "Modhera",
    "Fatehpur Sikri", "Red Fort", "Qutb Minar", "Elephanta", "Mahabalipuram"
]


@dataclass
class ClaimEvaluation:
    claim_sentence: str
    citation_tag: str
    is_supported: bool
    status: str  # SUPPORTED, CONTRADICTED_DATE, CONTRADICTED_DYNASTY, CONTRADICTED_MONUMENT, UNSUPPORTED
    reason: str


def extract_dates(text: str) -> List[str]:
    """Extract 3-4 digit years, centuries, and eras."""
    pattern = r"\b(?:1\d{3}|20\d{2}|[3-9]\d{2})\s*(?:CE|BCE|AD|BC)?\b|\b\d{1,2}(?:st|nd|rd|th)\s+century(?:\s*(?:BCE|CE|AD|BC))?\b"
    return [m.strip().lower() for m in re.findall(pattern, text, re.IGNORECASE)]


def extract_dynasties(text: str) -> List[str]:
    """Find known dynastic mentions."""
    found = []
    text_lower = text.lower()
    for d in KNOWN_DYNASTIES:
        if d.lower() in text_lower:
            found.append(d)
    return found


def extract_monuments(text: str) -> List[str]:
    """Find known monument mentions."""
    found = []
    text_lower = text.lower()
    for m in KNOWN_MONUMENTS:
        if m.lower() in text_lower:
            found.append(m)
    return found


def evaluate_claim_against_passage(claim_sentence: str, evidence_snippet: str) -> ClaimEvaluation:
    """
    Evaluates whether a factual claim is genuinely supported by an evidence passage.
    Checks dates, dynasties, monument attribution, and core entity coverage.
    """
    if not claim_sentence or not evidence_snippet:
        return ClaimEvaluation(
            claim_sentence=claim_sentence,
            citation_tag="",
            is_supported=False,
            status="UNSUPPORTED",
            reason="Empty claim or evidence passage.",
        )

    claim_lower = claim_sentence.lower()
    evidence_lower = evidence_snippet.lower()

    # 1. Date / Year Verification
    claim_dates = extract_dates(claim_sentence)
    evidence_dates = extract_dates(evidence_snippet)

    if claim_dates and evidence_dates:
        # Check if the specific year asserted in claim appears in the evidence
        claim_years = [re.sub(r"[^\d]", "", d) for d in claim_dates if re.search(r"\d{3,4}", d)]
        evidence_years = [re.sub(r"[^\d]", "", d) for d in evidence_dates if re.search(r"\d{3,4}", d)]
        if claim_years and evidence_years:
            if not any(cy in evidence_years for cy in claim_years):
                return ClaimEvaluation(
                    claim_sentence=claim_sentence,
                    citation_tag="",
                    is_supported=False,
                    status="CONTRADICTED_DATE",
                    reason=f"Date mismatch: Claim asserts {claim_dates}, but evidence passage records {evidence_dates}.",
                )

    # 2. Dynasty Attribution Verification
    claim_dynasties = extract_dynasties(claim_sentence)
    evidence_dynasties = extract_dynasties(evidence_snippet)

    if claim_dynasties:
        # If claim asserts a dynasty, that dynasty must be present in evidence
        matching_dynasty = any(cd.lower() in evidence_lower for cd in claim_dynasties)
        if not matching_dynasty:
            return ClaimEvaluation(
                claim_sentence=claim_sentence,
                citation_tag="",
                is_supported=False,
                status="CONTRADICTED_DYNASTY",
                reason=f"Dynasty contradiction: Claim asserts {claim_dynasties}, but passage records {evidence_dynasties or 'none'}.",
            )

    # 3. Monument Attribution Verification
    claim_monuments = extract_monuments(claim_sentence)
    evidence_monuments = extract_monuments(evidence_snippet)

    if claim_monuments and evidence_monuments:
        if not any(cm.lower() in evidence_lower for cm in claim_monuments):
            return ClaimEvaluation(
                claim_sentence=claim_sentence,
                citation_tag="",
                is_supported=False,
                status="CONTRADICTED_MONUMENT",
                reason=f"Monument mismatch: Claim asserts {claim_monuments}, but passage belongs to {evidence_monuments}.",
            )

    # 4. Lexical and Named Entity Overlap Check
    claim_tokens = {
        w.lower()
        for w in re.findall(r"\b[a-zA-Z]{4,}\b", claim_sentence)
        if w.lower() not in {
            "this", "that", "these", "those", "from", "with", "have", "were", "been",
            "also", "their", "into", "over", "what", "which", "where", "when", "does",
            "about", "under", "after", "before", "between", "according", "records",
            "features", "feature", "constructed", "built", "commissioned", "consecrated",
            "established", "dedicated", "memorial", "preserves", "crowned", "rises",
            "single", "monument", "temple", "temples", "complex"
        }
    }

    if not claim_tokens:
        return ClaimEvaluation(
            claim_sentence=claim_sentence,
            citation_tag="",
            is_supported=True,
            status="SUPPORTED",
            reason="Broad general claim without verifiable named entities.",
        )

    overlap = sum(1 for token in claim_tokens if token in evidence_lower)
    overlap_ratio = overlap / len(claim_tokens)
    missing_tokens = [t for t in claim_tokens if t not in evidence_lower]
    missing_ratio = len(missing_tokens) / len(claim_tokens)

    # Require at least 2 distinct substantive tokens or >= 25% overlap
    if overlap < 2 and overlap_ratio < 0.25:
        return ClaimEvaluation(
            claim_sentence=claim_sentence,
            citation_tag="",
            is_supported=False,
            status="UNSUPPORTED",
            reason=f"Insufficient entity overlap ({overlap}/{len(claim_tokens)} tokens supported).",
        )

    # Detect claims with substantial uncorroborated assertions (>= 50% tokens missing)
    if len(claim_tokens) >= 4 and missing_ratio >= 0.50:
        return ClaimEvaluation(
            claim_sentence=claim_sentence,
            citation_tag="",
            is_supported=False,
            status="PARTIALLY_UNSUPPORTED",
            reason=f"Claim contains uncorroborated assertions ({len(missing_tokens)}/{len(claim_tokens)} tokens missing: {', '.join(missing_tokens[:3])}).",
        )

    return ClaimEvaluation(
        claim_sentence=claim_sentence,
        citation_tag="",
        is_supported=True,
        status="SUPPORTED",
        reason=f"Corroborated by passage with {overlap} matching entity tokens.",
    )


def validate_claim_evidence_support(claim_sentence: str, evidence_snippet: str) -> bool:
    """
    Backwards-compatible wrapper returning boolean support judgment.
    """
    eval_result = evaluate_claim_against_passage(claim_sentence, evidence_snippet)
    return eval_result.is_supported


def process_and_validate_citations(
    raw_answer: str,
    retrieved_evidence: List[EvidenceItem],
) -> Tuple[str, List[AICitation]]:
    """
    Structured citation validation process:
    1. Extracts factual claims and their cited tags.
    2. Retrieves the exact supporting document passage.
    3. Evaluates dates, dynasties, monuments, and entity coverage.
    4. Strips or qualifies unsupported/contradicted claims and invalid citations.
    5. Preserves valid, evidence-grounded citations.
    """
    evidence_by_tag = {item.citation_id: item for item in retrieved_evidence}

    # Split answer into sentence blocks
    sentences = re.split(r"(?<=[.!?•\n])\s+", raw_answer)
    valid_citations_map: Dict[int, AICitation] = {}
    cleaned_sentences: List[str] = []

    for sentence in sentences:
        sent = sentence.strip()
        if not sent:
            continue

        # Find any citation tags in this sentence
        tags = re.findall(r"\[CITATION_(\d+)\]", sent)
        if not tags:
            cleaned_sentences.append(sent)
            continue

        # Evaluate each tag against this sentence
        sent_has_valid_tag = False
        sent_cleaned = sent

        for tag_str in tags:
            idx = int(tag_str)
            full_tag = f"[CITATION_{idx}]"

            if full_tag not in evidence_by_tag:
                # Hallucinated tag not in evidence
                sent_cleaned = sent_cleaned.replace(full_tag, "").strip()
                continue

            ev = evidence_by_tag[full_tag]
            # Strict claim-to-evidence support check
            eval_res = evaluate_claim_against_passage(sent_cleaned, ev.content)

            if eval_res.is_supported:
                sent_cleaned = sent_cleaned.replace(full_tag, f"[{idx}]")
                sent_has_valid_tag = True

                if idx not in valid_citations_map:
                    valid_citations_map[idx] = AICitation(
                        citation_id=f"[{idx}]",
                        source_id=ev.source_id,
                        source_title=ev.title,
                        institution=ev.institution,
                        source_url=ev.source_url,
                        publication_date=ev.publication_date,
                        relevant_excerpt=ev.content[:300],
                        associated_site_id=ev.associated_site_id,
                        associated_site_name=ev.associated_site_name,
                        associated_graph_entity_id=ev.associated_graph_entity_id,
                        associated_graph_entity_name=ev.associated_graph_entity_name,
                        evidence_classification=ev.evidence_classification,
                    )
            else:
                # Discard citation tag for contradicted or unsupported claim
                sent_cleaned = sent_cleaned.replace(full_tag, "").strip()

        cleaned_sentences.append(sent_cleaned)

    cleaned_answer = " ".join(cleaned_sentences).strip()

    # Sort valid citations by their index
    sorted_citations = [valid_citations_map[idx] for idx in sorted(valid_citations_map.keys())]

    # Fallback: if answer is factual and retrieved evidence exists but tags were omitted, attach top evidence
    if not sorted_citations and retrieved_evidence and "insufficient" not in cleaned_answer.lower():
        for i, ev in enumerate(retrieved_evidence[:3], start=1):
            sorted_citations.append(
                AICitation(
                    citation_id=f"[{i}]",
                    source_id=ev.source_id,
                    source_title=ev.title,
                    institution=ev.institution,
                    source_url=ev.source_url,
                    publication_date=ev.publication_date,
                    relevant_excerpt=ev.content[:300],
                    associated_site_id=ev.associated_site_id,
                    associated_site_name=ev.associated_site_name,
                    associated_graph_entity_id=ev.associated_graph_entity_id,
                    associated_graph_entity_name=ev.associated_graph_entity_name,
                    evidence_classification=ev.evidence_classification,
                )
            )

    return cleaned_answer, sorted_citations
