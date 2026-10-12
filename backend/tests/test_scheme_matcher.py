"""
Tests for the deterministic scheme-eligibility engine. This is the module
most worth having tests for: it's the piece that guarantees the chatbot
never claims a farmer is eligible for something they aren't.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.scheme_matcher import match_schemes


def test_small_farmer_matches_income_and_insurance_schemes():
    profile = {"state": "Uttar Pradesh", "primary_crop": "wheat",
               "land_size_acres": 2, "category": "small"}
    matched_ids = {s["id"] for s in match_schemes(profile)}
    assert "pmkisan" in matched_ids
    assert "pmfby" in matched_ids
    assert "kcc" in matched_ids


def test_large_farmer_excluded_from_small_only_scheme():
    profile = {"state": "Punjab", "primary_crop": "wheat",
               "land_size_acres": 50, "category": "large"}
    matched_ids = {s["id"] for s in match_schemes(profile)}
    # PM-KISAN is restricted to small/marginal categories
    assert "pmkisan" not in matched_ids
    # KCC has no category restriction, should still be available
    assert "kcc" in matched_ids


def test_state_specific_scheme_only_matches_that_state():
    up_profile = {"state": "Uttar Pradesh", "primary_crop": "sugarcane",
                  "land_size_acres": 3, "category": "small"}
    other_state_profile = {"state": "Kerala", "primary_crop": "sugarcane",
                            "land_size_acres": 3, "category": "small"}

    up_matches = {s["id"] for s in match_schemes(up_profile)}
    other_matches = {s["id"] for s in match_schemes(other_state_profile)}

    assert "up_ganna_kisan" in up_matches
    assert "up_ganna_kisan" not in other_matches


def test_land_size_over_cap_excludes_irrigation_scheme():
    profile = {"state": "Bihar", "primary_crop": "rice",
               "land_size_acres": 15, "category": "small"}
    matched_ids = {s["id"] for s in match_schemes(profile)}
    # PM-KSY caps at 10 acres
    assert "pmksy" not in matched_ids


def test_empty_profile_returns_only_universally_open_schemes():
    profile = {"state": None, "primary_crop": None, "land_size_acres": None, "category": None}
    matches = match_schemes(profile)
    # Schemes with a category restriction require a category match — with
    # none given, they should be excluded rather than default-included.
    matched_ids = {s["id"] for s in matches}
    assert "pmkisan" not in matched_ids  # requires small/marginal category
