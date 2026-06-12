from src.config import (
    MULTIPLIER_NOTICE_PERIOD_UNDER_30,
    MULTIPLIER_HIGH_GITHUB_ACTIVITY,
    MULTIPLIER_HIGH_RESPONSE_RATE,
    MULTIPLIER_LOCATION_MATCH,
    MULTIPLIER_WILLING_TO_RELOCATE
)

def apply_behavioral_multipliers(base_score, candidate):
    """
    Takes the base semantic (TF-IDF) score and multiplies it by behavioral signals.
    This fulfills the JD requirement that a perfect-on-paper candidate who 
    is unresponsive should be down-weighted.
    """
    score = base_score
    signals = candidate.get("redrob_signals", {})
    profile = candidate.get("profile", {})
    
    # Notice Period (Bonus if they can join quickly)
    notice_days = signals.get("notice_period_days", 90)
    if notice_days <= 30:
        score *= MULTIPLIER_NOTICE_PERIOD_UNDER_30
        
    # GitHub Activity (Bonus for strong open-source/coding activity)
    github_score = signals.get("github_activity_score", -1)
    if github_score >= 50:
        score *= MULTIPLIER_HIGH_GITHUB_ACTIVITY
        
    # Recruiter Response Rate (Bonus if they actually reply)
    response_rate = signals.get("recruiter_response_rate", 0)
    if response_rate >= 0.8:
        score *= MULTIPLIER_HIGH_RESPONSE_RATE
        
    # Location Match (Bonus if they are already in target cities or willing to move)
    location = profile.get("location", "").lower()
    if "pune" in location or "noida" in location:
        score *= MULTIPLIER_LOCATION_MATCH
    elif signals.get("willing_to_relocate", False):
        score *= MULTIPLIER_WILLING_TO_RELOCATE
        
    return score
