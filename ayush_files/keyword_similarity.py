import pickle
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any
import os
import json
import torch
import numpy as np

# ---------------- Model ----------------
model = SentenceTransformer("sentence-transformers/paraphrase-albert-small-v2")
# model.quantize(bits=8)  # optional for smaller memory footprint

# ---------------- Precompute Prof Embeddings ----------------
def pre_compute_prof_data(prof_data: List[Dict[str, Any]], save_path: str = "prof_data.pt") -> None:
    """
    Compute embeddings for professor keywords and save the list of dictionaries as a pickle file.
    Each prof dict will have an added key 'prof_embedding'.
    """
    embeddings = []
    for prof in prof_data:
        keywords = prof.get("prof_keywords")
        emb = model.encode(keywords, convert_to_tensor=True, normalize_embeddings=True)
        print(emb.shape, emb.dtype)
        embeddings.append(emb)
        print(prof['prof_name'])
    embeddings = torch.stack(embeddings) # convert to numpy for pickling
    print(embeddings.shape)

    torch.save(embeddings, save_path)
    print(f"Saved precomputed professor embeddings to {save_path}")


# ---------------- Compute Top Similar Professors ----------------
def get_top_similar_profs(student_keywords: List[str], threshold: float = 0.3, prof_data_path: str = "prof_data.pt") -> List[Dict[str, Any]]:
    """
    Compare a student's research interests to precomputed professor embeddings.
    Returns augmented prof dicts with similarity scores and matched interests (without embeddings).
    """
    if not student_keywords:
        return []

    # Load precomputed prof data
    if not os.path.exists(prof_data_path):
        raise FileNotFoundError(f"Precomputed prof data file not found: {prof_data_path}")
    
    prof_meta = json.load(open('../filtered_authors_and_topics.json', 'r'))
    prof_data = torch.load(prof_data_path)

    # Encode student keywords once
    student_emb = model.encode(student_keywords, convert_to_tensor=True, normalize_embeddings=True)

    results = []

    for meta, prof_emb in zip(prof_meta, prof_data):
        prof_keywords = meta.get("prof_keywords", [])

        if prof_emb is None or not prof_keywords:
            score, matched_interests = 0.0, []
        else:
            sims = util.cos_sim(student_emb, prof_emb)
            print(sims.shape)

            # Find matched interests
            matched_keywords = set()
            for i, student_kw in enumerate(student_keywords):
                for j, prof_kw in enumerate(prof_keywords):
                    sim_val = sims[i][j].item()
                    if sim_val >= threshold:
                        more_specific = student_kw if len(student_kw.split()) >= len(prof_kw.split()) else prof_kw
                        matched_keywords.add(more_specific)

            # Smooth score: average of max similarity per student keyword
            #@TODO: ignore if max sim is below a lower threshold?
            max_sims = [max(sims[i]).item() for i in range(len(student_keywords))]
            print(max_sims)
            total_sum = 0.0
            for i in range(len(student_keywords)):
                if max_sims[i] > threshold:
                    total_sum += max_sims[i]
            score = total_sum / len(student_keywords)

            matched_interests = list(matched_keywords)
            score = round(score, 5)

        # Copy professor dict, remove embedding, add similarity info
        augmented_prof = meta.copy()
        augmented_prof["similarity_score"] = score
        augmented_prof["matched_interests"] = matched_interests

        results.append(augmented_prof)

    # Sort descending by similarity
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results

# ---------------- Example Usage ----------------
if __name__ == "__main__":
    # Example professors

    with open('../filtered_authors_and_topics.json', 'rb') as f:
        profs = json.load(f)

    # Step 1: Precompute embeddings and save
    pre_compute_prof_data(profs, save_path="prof_data.pt")

    # Step 2: Compare a student
    student_keywords = ["machine learning", "robotics", "reinforcement learning"]
    top_profs = get_top_similar_profs(student_keywords, threshold=0.3, prof_data_path="prof_data.pt")

    for prof in top_profs:
        print(prof)
