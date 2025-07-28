import json
from datetime import datetime
import re

def add_spaces(text):
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    s = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', s)
    s = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', s)
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)
    s = re.sub(r'([a-zA-Z])([A-Z])', r'\1 \2', s)
    return s.strip()

def write_output(output_path, input_documents, persona, job, ranked_sections, subsections_ranked, score_threshold=0.15):
    # Filter sections by score threshold (internally kept)
    filtered_sections = [s for s in ranked_sections if s.get("score", 0) >= score_threshold]

    # Map (title, page) -> section
    section_map = {}
    for sec in filtered_sections:
        key = (sec["section_title"], sec["page"])
        sec["refined_texts"] = []
        # Normalize section_title spacing for output
        sec["section_title"] = add_spaces(sec["section_title"])
        section_map[key] = sec

    # Group subsections under respective sections with cleaned text
    for sub in subsections_ranked:
        key = (sub["section_title"], sub["page_number"])
        if key in section_map:
            cleaned_text = add_spaces(sub["refined_text"])
            section_map[key]["refined_texts"].append({
                "text": cleaned_text,
                "page_number": sub["page_number"]
                # Score excluded from output
            })

    # Sort sections by importance rank
    output_sections = sorted(section_map.values(), key=lambda x: x["importance_rank"])

    # Build output JSON without 'score' fields as requested
    output = {
        "metadata": {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": sec["document"],
                "page_number": sec["page"],
                "section_title": sec["section_title"],
                "importance_rank": sec["importance_rank"],
                "refined_texts": sec["refined_texts"]
            }
            for sec in output_sections
        ]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
