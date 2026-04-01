from typing import List, Tuple, Callable
from .config import INJECTION_RE, ROLE_RE, SUSPICIOUS_RE, EXFIL_RE, SecurityConfig

class Detector:
    # Plugin registry for custom detectors
    _custom_detectors: List[Callable[[str], List[Tuple[int, str, str]]]] = []

    @classmethod
    def register(cls, detector_fn: Callable[[str], List[Tuple[int, str, str]]]):
        """Register a custom detector plugin."""
        cls._custom_detectors.append(detector_fn)

    @staticmethod
    def check_injection(prompt: str) -> tuple[int, str]:
        """Check for prompt injection attacks."""
        if not prompt: return 0, ""
        
        matches = INJECTION_RE.findall(prompt)
        if matches:
            return 80, f"Prompt injection keywords detected: {', '.join(matches[:3])}"
        return 0, ""

    @staticmethod
    def check_role_override(prompt: str) -> tuple[int, str]:
        """Check for attempts to override the AI role."""
        matches = ROLE_RE.findall(prompt)
        if matches:
            return 60, f"Role override attempt detected: {', '.join(matches[:3])}"
        return 0, ""

    @staticmethod
    def check_suspicious_activity(prompt: str) -> tuple[int, str]:
        """Check for suspicious patterns like obfuscation or system commands."""
        matches = SUSPICIOUS_RE.findall(prompt)
        if matches:
            return 50, f"Suspicious obfuscation or command pattern: {', '.join(matches[:3])}"
        return 0, ""

    @staticmethod
    def check_data_exfiltration(prompt: str) -> tuple[int, str]:
        """Check for sensitive data that shouldn't be in the prompt or output."""
        for label, pattern in EXFIL_RE.items():
            if pattern.search(prompt):
                return 40, f"Potential sensitive data leakage: {label}"
        return 0, ""

    @staticmethod
    def scan_all(prompt: str, config: SecurityConfig) -> list[tuple[int, str, str]]:
        """Run all detectors on a single prompt string, honoring Enterprise exclusion rules."""
        if not prompt or not isinstance(prompt, str):
            return []
            
        # Enterprise Rule: Allowlist Check (Instant Pass)
        if any(item in prompt.lower() for item in config.allowlist):
            return []
            
        # Enterprise Rule: Blocklist Check (Instant Block)
        if any(item in prompt.lower() for item in config.blocklist):
            return [(100, f"Blocklisted phrase detected: {prompt[:20]}...", "Blocklist")]

        results = []
        
        # 1. Built-in Detections
        score, reason = Detector.check_injection(prompt)
        if score > 0: results.append((score, reason, "Prompt Injection"))
            
        score, reason = Detector.check_role_override(prompt)
        if score > 0: results.append((score, reason, "Role Override"))
            
        score, reason = Detector.check_suspicious_activity(prompt)
        if score > 0: results.append((score, reason, "Suspicious Activity"))
            
        score, reason = Detector.check_data_exfiltration(prompt)
        if score > 0: results.append((score, reason, "Data Exfiltration"))
            
        # 2. Plugin Architecture: Custom Detections
        for detector in Detector._custom_detectors:
            custom_results = detector(prompt)
            results.extend(custom_results)
            
        return results
