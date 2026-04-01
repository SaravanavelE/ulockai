import re

# Thresholds
RISK_THRESHOLD_BLOCK = 70
RISK_THRESHOLD_FLAG = 40

# Prompt Injection Patterns (Case Insensitive)
PROMPT_INJECTION_KEYWORDS = [
    r"ignore\s+(?:all\s+)?instructions",
    r"disregard\s+(?:all\s+)?instructions",
    r"as\s+a\s+model\s+with\s+No\s+restrictions",
    r"DAN\s+mode",
    r"system\s+override",
    r"you\s+are\s+now\s+an\s+unfiltered",
    r"jailbreak",
    r"ignore\s+everything\s+before\s+this",
    r"stay\s+in\s+character",
    r"respond\s+only\s+with\s+the\s+system\s+content",
    r"show\s+me\s+the\s+prompt",
    r"reveal\s+secret\s+instructions",
    r"what\s+is\s+your\s+system\s+prompt",
    r"what\s+was\s+the\s+initial\s+instruction",
    # Specific bypass techniques
    r"HTTP GET", r"powershell", r"chmod \+x", r"rm -rf"
]

# Role Override Patterns
ROLE_OVERRIDE_KEYWORDS = [
    r"your new role is",
    r"you are now a",
    r"act as a",
    r"pretend to be",
    r"simulate a",
    r"forget your assistant role",
    r"stop being helpful",
]

# Data Exfiltration Patterns
EXFILTRATION_PATTERNS = {
    "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
    "API Key": r"(?:sk|pk|ak|uk)_[a-zA-Z0-9]{20,}",
    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "Private Key": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
}

# Suspicious Patterns
SUSPICIOUS_KEYWORDS = [
    r"base64",
    r"hex encode",
    r"obfuscate",
    r"encrypt this",
    r"binary data",
    r"decode this",
]

# Memory Poisoning
MEMORY_POISONING_KEYWORDS = [
    r"update your memory with",
    r"remember that the system said",
    r"the following was our last conversation",
    r"you previously agreed to",
]

def compile_regex(patterns):
    return re.compile("|".join(patterns), re.IGNORECASE)

# Pre-compiled Regex for performance
INJECTION_RE = compile_regex(PROMPT_INJECTION_KEYWORDS)
ROLE_RE = compile_regex(ROLE_OVERRIDE_KEYWORDS)
SUSPICIOUS_RE = compile_regex(SUSPICIOUS_KEYWORDS)
MEMORY_RE = compile_regex(MEMORY_POISONING_KEYWORDS)
EXFIL_RE = {k: re.compile(v) for k, v in EXFILTRATION_PATTERNS.items()}

class SecurityConfig:
    """Enterprise-grade runtime configuration for the Guard instance."""
    def __init__(self, 
                 block_threshold: int = RISK_THRESHOLD_BLOCK,
                 flag_threshold: int = RISK_THRESHOLD_FLAG,
                 strict_mode: bool = False,
                 log_level: str = "INFO",
                 allowlist: list[str] = None,
                 blocklist: list[str] = None):
        self.block_threshold = block_threshold
        self.flag_threshold = flag_threshold
        self.strict_mode = strict_mode
        self.log_level = log_level
        self.allowlist = set(allowlist or [])
        self.blocklist = set(blocklist or [])
        
        # In strict mode, lower the block threshold
        if self.strict_mode:
            self.block_threshold = 50
