from thefuzz import fuzz

STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "it",
    "its", "this", "that", "these", "those", "he", "she", "they", "we",
    "his", "her", "their", "our", "my", "your", "who", "which", "what",
    "when", "where", "how", "not", "no", "nor", "so", "if", "then",
    "than", "too", "very", "just", "about", "up", "out", "into", "over",
    "after", "before", "between", "under", "again", "further", "also",
    "says", "said", "say", "new", "amid", "set",
})

MIN_SHARED_WORDS = 3


def _strip_stops(text):
    return " ".join(w for w in text.lower().split() if w not in STOP_WORDS)


def find_cross_site_matches(runs_with_headlines, threshold=45):
    """Find headlines covering the same story across different sites.

    Uses stop-word removal + minimum shared content words to reduce
    false positives while catching more legitimate overlaps.
    """
    if len(runs_with_headlines) < 2:
        return []

    all_headlines = []
    stripped = []
    word_sets = []
    for run in runs_with_headlines:
        for h in run["headlines"]:
            all_headlines.append({
                "site": run["url"],
                "text": h["text"],
                "compound": h["compound"],
                "sentiment": h["overall_sentiment"],
            })
            s = _strip_stops(h["text"])
            stripped.append(s)
            word_sets.append(set(s.split()))

    used = set()
    groups = []

    for i, anchor in enumerate(all_headlines):
        if i in used:
            continue

        group_indices = [i]
        used.add(i)
        seen_sites = {anchor["site"]}

        for j, candidate in enumerate(all_headlines):
            if j in used or candidate["site"] in seen_sites:
                continue
            # Quick check: must share at least N content words
            if len(word_sets[i] & word_sets[j]) < MIN_SHARED_WORDS:
                continue
            score = fuzz.token_sort_ratio(stripped[i], stripped[j])
            if score >= threshold:
                group_indices.append(j)
                used.add(j)
                seen_sites.add(candidate["site"])

        if len(group_indices) >= 2:
            group = [all_headlines[idx] for idx in group_indices]
            compounds = [m["compound"] for m in group]
            best_score = max(
                fuzz.token_sort_ratio(stripped[i], stripped[idx])
                for idx in group_indices[1:]
            )
            groups.append({
                "anchor": anchor["text"],
                "score": best_score,
                "max_deviation": max(abs(c) for c in compounds),
                "spread": max(compounds) - min(compounds),
                "matches": group,
            })

    groups.sort(key=lambda g: (-g["max_deviation"], -g["spread"]))
    return groups
