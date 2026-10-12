"""
Rule-based government scheme eligibility matcher.

Deliberately NOT delegated to the LLM: eligibility is a deterministic
function of structured fields (state, crop, land size, farmer category),
so filtering happens in plain Python where it's auditable and can't
hallucinate a scheme into or out of eligibility. The LLM's job (see
utils/gemini_client.py) is only to *explain* these matches conversationally
— never to decide them.
"""
import json
import os

with open(os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")) as f:
    SCHEMES = json.load(f)


def _matches_field(scheme_value, user_value):
    if scheme_value == "all" or scheme_value is None:
        return True
    if user_value is None:
        return False
    if isinstance(scheme_value, list):
        return user_value.lower() in [v.lower() for v in scheme_value]
    return str(scheme_value).lower() == str(user_value).lower()


def match_schemes(profile: dict) -> list:
    """
    profile: {state, primary_crop, land_size_acres, category}
    Returns the subset of SCHEMES the farmer is eligible for, each annotated
    with a short `matched_reason` for transparency.
    """
    state = profile.get("state")
    crop = profile.get("primary_crop")
    land_size = profile.get("land_size_acres")
    category = profile.get("category")

    matched = []
    for scheme in SCHEMES:
        if not _matches_field(scheme["eligible_states"], state):
            continue
        if not _matches_field(scheme["eligible_crops"], crop):
            continue
        # A restriction we can't evaluate (missing profile data) must exclude
        # the scheme rather than silently pass it — "unconfirmed" is not the
        # same as "eligible" for something as consequential as a government
        # scheme match. This mirrors the treatment of state/crop above, where
        # a missing user value already fails _matches_field.
        if scheme["max_land_acres"] is not None:
            if land_size is None or float(land_size) > float(scheme["max_land_acres"]):
                continue
        if scheme["eligible_categories"]:
            if not category or category.lower() not in [c.lower() for c in scheme["eligible_categories"]]:
                continue

        matched.append({**scheme, "matched_reason": _reason(scheme, profile)})

    return matched


def _reason(scheme, profile):
    bits = []
    if scheme["eligible_states"] != "all":
        bits.append(f"available in {profile.get('state', 'your state')}")
    if scheme["eligible_crops"] != "all":
        bits.append(f"applies to {profile.get('primary_crop', 'your crop')}")
    if scheme["max_land_acres"] is not None:
        bits.append(f"land holding under {scheme['max_land_acres']} acres")
    if not bits:
        return "Open to all eligible farmers nationwide."
    return "Matched because: " + ", ".join(bits) + "."


def get_all_schemes():
    return SCHEMES
