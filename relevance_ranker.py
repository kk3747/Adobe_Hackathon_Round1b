from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import wordninja

def add_spaces(text):
    # First, apply the regex splitting as before
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    s = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', s)
    s = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', s)

    # If still few or no spaces, use wordninja to split it!
    # Only apply if there are long runs without space (e.g., > 20 chars).
    tokens = []
    for part in s.split():
        if len(part) > 15 and part.count(' ') == 0:
            tokens.extend(wordninja.split(part))
        else:
            tokens.append(part)
    s = ' '.join(tokens)
    # Remove double spaces that may result
    return re.sub(r'\s+', ' ', s).strip()

def split_into_sentences(text):
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]

def clean_text(text):
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = add_spaces(cleaned)
    return cleaned.strip()

def compute_section_relevance(sections, persona, job, model_path=None):
    context = f"{persona}. {job}"
    model = SentenceTransformer(model_path or 'all-MiniLM-L6-v2')
    context_emb = model.encode([context], convert_to_numpy=True)

    section_texts = [s['section_title'] + '. ' + s['section_text'] for s in sections]
    section_embs = model.encode(section_texts, convert_to_numpy=True)
    sims = cosine_similarity(context_emb, section_embs)[0]

    ranked_indices = np.argsort(sims)[::-1]
    ranked_sections = []
    for rank, idx in enumerate(ranked_indices, 1):
        sec = sections[idx].copy()
        sec["importance_rank"] = rank
        sec["score"] = float(sims[idx])  # Keep internally for filtering, but will exclude from output
        ranked_sections.append(sec)
    return ranked_sections, model

def extract_subsections(section, context, model, max_snippets=5):
    sentences = split_into_sentences(section['section_text'])
    if not sentences:
        return []

    context_emb = model.encode([context], convert_to_numpy=True)
    sentence_embs = model.encode(sentences, convert_to_numpy=True)
    sims = cosine_similarity(context_emb, sentence_embs)[0]

    scored_sentences = list(zip(sentences, sims))
    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    seen = set()
    filtered_snippets = []
    for sent, score in scored_sentences:
        cleaned_sent = clean_text(sent)
        normalized = cleaned_sent.lower()
        if normalized not in seen and len(cleaned_sent) > 15:
            filtered_snippets.append({
                "document": section["document"],
                "page_number": section["page"],
                "section_title": section["section_title"],
                "refined_text": cleaned_sent,
                "score": float(score)  # Keep internally for filtering, but will exclude from output
            })
            seen.add(normalized)
            if len(filtered_snippets) >= max_snippets:
                break
    return filtered_snippets
