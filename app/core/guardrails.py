import re
from typing import Optional, Tuple

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"system\s+prompt",
    r"developer\s+mode",
    r"jailbreak",
    r"override\s+(the\s+)?safeguards",
    r"reveal\s+(the\s+)?(system|developer)\s+prompt",
    r"bypass\s+(the\s+)?guardrails",
    r"act\s+as\s+if\s+you\s+are\s+not\s+bound",
]

HARMFUL_REQUEST_PATTERNS = [
    "bypass mfa",
    "disable mfa",
    "steal credentials",
    "dump passwords",
    "social engineer",
    "exploit vulnerability",
    "bypass authentication",
    "unlock account without approval",
    "gain access to other users",
    "ddos",
    "malware",
    "ransomware",
    "credential stuffing",
]

OUTPUT_REJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"system\s+prompt",
    r"developer\s+mode",
    r"as\s+an\s+ai\s+assistant",
]


def _normalize(value: str) -> str:
    return " ".join((value or "").strip().split())


def validate_input(question: str) -> Tuple[bool, Optional[str]]:
    cleaned = _normalize(question)

    if not cleaned:
        return False, "Please enter a question before sending it."

    if len(cleaned) < 2:
        return False, "Your question is too short to be useful."

    if len(cleaned) > 2000:
        return False, "Your question is too long. Please keep it under 2000 characters."

    lower = cleaned.lower()

    if any(re.search(pattern, lower, flags=re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS):
        return False, "I can help with IT support questions, but I cannot bypass safeguards or reveal instructions. Please ask about a company IT policy, access issue, or troubleshooting topic."

    if any(term in lower for term in HARMFUL_REQUEST_PATTERNS):
        return False, "I can help with IT support and safe troubleshooting steps safely, but I cannot assist with harmful or unauthorized access activity."

    return True, None


def validate_output(answer: str) -> Tuple[bool, Optional[str]]:
    cleaned = _normalize(answer)

    if not cleaned:
        return False, "The generated answer was empty. Please retry with a specific IT support question."

    if len(cleaned) < 25:
        return False, "The answer was too short to be specific or useful."

    lower = cleaned.lower()

    if any(re.search(pattern, lower, flags=re.IGNORECASE) for pattern in OUTPUT_REJECTION_PATTERNS):
        return False, "The generated output was not safe or specific enough to return."

    if re.fullmatch(r"i\s+can\s+help\s+with\s+that\.?", lower):
        return False, "The answer was too generic. Please provide a concrete, specific response based on the company KB or verified web evidence."

    if re.search(r"\b(i\s+am\s+not\s+sure|maybe\s+try\s+again|try\s+again|not\s+sure|uncertain|generic\s+placeholder|placeholder\s+answer)\b", lower):
        return False, "The answer was too generic or uncertain to be safe and specific enough."

    if "lorem ipsum" in lower or "placeholder" in lower:
        return False, "The answer was not a valid support response."

    return True, None


def safe_refusal(question: str) -> str:
    return (
        "I can help with company IT support questions, but I can't provide unsafe or unsupported instructions. "
        "Please rephrase the request as a specific access, troubleshooting, or policy question and I will try again."
    )
