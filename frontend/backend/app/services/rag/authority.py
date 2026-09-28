from typing import Dict

# Authority multipliers specified in Section 19:
# Tier A: MoSPI, NSO, NSSTA, iGOT Karmayogi, UNSD, UNECE
# Tier B: OECD, World Bank, IMF, ILO, FAO
# Tier C: Universities, ISI Kolkata, Academic Peer-Reviewed
# Tier D: General web
AUTHORITY_TIER_WEIGHTS: Dict[str, float] = {
    "TIER_A": 1.25,
    "TIER_B": 1.10,
    "TIER_C": 0.95,
    "TIER_D": 0.70,
}


def get_authority_multiplier(tier: str) -> float:
    return AUTHORITY_TIER_WEIGHTS.get(tier.upper(), 0.85)
