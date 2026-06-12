from src.config import ABSOLUTE_MIN_YOE, ABSOLUTE_MAX_YOE, MIN_RESPONSE_RATE, DISALLOWED_TITLE_KEYWORDS

def is_honeypot(candidate):
    """
    Mathematical rules to detect fake/impossible profiles.
    Returns True if it's a honeypot, False otherwise.
    """
    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    
    # Honeypot Rule 1: A single skill's duration cannot exceed their total years of experience
    # (Allowing a tiny buffer for rounding errors)
    for skill in candidate.get("skills", []):
        duration_years = skill.get("duration_months", 0) / 12.0
        if duration_years > (yoe + 0.5):
            return True
            
    # Honeypot Rule 2: Multiple "expert" proficiencies but 0 duration
    expert_zero_duration_count = 0
    for skill in candidate.get("skills", []):
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 0) == 0:
            expert_zero_duration_count += 1
            
    if expert_zero_duration_count >= 3:
        return True
        
    return False

def is_keyword_stuffer(candidate):
    """
    Checks if the candidate holds a non-technical role but lists AI skills.
    We check BOTH current_title and their recent career_history titles.
    """
    current_title = candidate.get("profile", {}).get("current_title", "").lower()
    
    for disallowed_word in DISALLOWED_TITLE_KEYWORDS:
        if disallowed_word in current_title:
            return True
            
    return False

def passes_stage_1(candidate):
    """
    The Trap Door. Returns True if the candidate survives, False if they are dropped.
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    
    # 1. Experience check
    yoe = profile.get("years_of_experience", 0)
    if yoe < ABSOLUTE_MIN_YOE or yoe > ABSOLUTE_MAX_YOE:
        return False
        
    # 2. Ghost check
    if signals.get("recruiter_response_rate", 0) < MIN_RESPONSE_RATE:
        return False
        
    # 3. Honeypot check
    if is_honeypot(candidate):
        return False
        
    # 4. Keyword Stuffer check
    if is_keyword_stuffer(candidate):
        return False
        
    return True
