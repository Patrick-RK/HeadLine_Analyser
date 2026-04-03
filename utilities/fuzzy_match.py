from thefuzz import fuzz


def find_cross_site_matches(runs_with_headlines, threshold=60):
    """Find headlines covering the same story across different sites.

    Args:
        runs_with_headlines: list of dicts, each with keys:
            - url: the site URL
            - headlines: list of headline dicts (text, compound, overall_sentiment, ...)
        threshold: minimum token_sort_ratio to consider a match (0-100)

    Returns:
        list of match groups, each a dict:
            {
                "anchor": headline text used as the group label,
                "matches": [
                    {"site": url, "text": str, "compound": float, "sentiment": str},
                    ...
                ]
            }
        Sorted by number of sites matched (most first), then by avg abs(compound).
    """
    if len(runs_with_headlines) < 2:
        return []

    # Build flat list with site labels
    all_headlines = []
    for run in runs_with_headlines:
        for h in run["headlines"]:
            all_headlines.append({
                "site": run["url"],
                "text": h["text"],
                "compound": h["compound"],
                "sentiment": h["overall_sentiment"],
            })

    used = set()
    groups = []

    for i, anchor in enumerate(all_headlines):
        if i in used:
            continue

        group = [anchor]
        used.add(i)
        seen_sites = {anchor["site"]}

        for j, candidate in enumerate(all_headlines):
            if j in used or candidate["site"] in seen_sites:
                continue
            score = fuzz.token_sort_ratio(anchor["text"], candidate["text"])
            if score >= threshold:
                group.append(candidate)
                used.add(j)
                seen_sites.add(candidate["site"])

        # Only keep groups that span 2+ sites
        if len(group) >= 2:
            compounds = [m["compound"] for m in group]
            max_deviation = max(abs(c) for c in compounds)
            spread = max(compounds) - min(compounds)
            groups.append({
                "anchor": anchor["text"],
                "score": max(
                    fuzz.token_sort_ratio(anchor["text"], m["text"])
                    for m in group[1:]
                ),
                "max_deviation": max_deviation,
                "spread": spread,
                "matches": group,
            })

    # Most extreme language first (biggest deviation from neutral),
    # then biggest spread between sites
    groups.sort(key=lambda g: (-g["max_deviation"], -g["spread"]))
    return groups
