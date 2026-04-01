import asyncio
import functools
import time
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable, Generator, AsyncGenerator
from .detector import Detector
from .memory import MemoryGuard
from .api import APIGuard
from .config import RISK_THRESHOLD_BLOCK, RISK_THRESHOLD_FLAG, SecurityConfig
from .logger import logger
from .metrics import telemetry

@dataclass
class ScanResult:
    safe: bool
    risk_score: int
    risk_level: str
    attack_type: List[str]
    action: str
    reason: str
    latency_ms: float = 0.0
    
    def as_dict(self):
        return {
            "safe": self.safe,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "attack_type": self.attack_type,
            "action": self.action,
            "reason": self.reason,
            "latency_ms": self.latency_ms
        }

class Guard:
    """The Enterprise-grade orchestrator for the ulockai SDK."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        logger.setLevel(self.config.log_level)
        logger.info(f"UlockAI Guard initialized (strict_mode: {self.config.strict_mode})")

    def _get_risk_level(self, score: int) -> str:
        if score >= 90: return "Critical"
        if score >= 70: return "High"
        if score >= 40: return "Medium"
        if score > 0: return "Low"
        return "None"
        
    def _determine_action(self, score: int, threshold: int) -> str:
        if score >= threshold: return "block"
        if score >= RISK_THRESHOLD_FLAG: return "flag"
        return "allow"

    def scan(self, 
             user_prompt: str = "", 
             system_prompt: str = "", 
             memory: str = "", 
             tool_calls: List[dict] = None,
             strict: Optional[bool] = None) -> ScanResult:
        """
        Synchronously scans an AI interaction for security risks.
        """
        start_time = time.perf_counter()
        
        # Determine threshold
        is_strict = strict if strict is not None else self.config.strict_mode
        block_threshold = 50 if is_strict else self.config.block_threshold
        
        attack_types = []
        reasons = []
        max_score = 0
        
        # 1. Scan User Prompt (Now with allowlist/blocklist support)
        user_scans = Detector.scan_all(user_prompt, self.config)
        for score, reason, attack in user_scans:
            if score > max_score: max_score = score
            attack_types.append(attack)
            reasons.append(f"User: {reason}")
            
        # 2. Check Role Override explicitly
        score, reason = Detector.check_role_override(user_prompt)
        if score > max_score: max_score = score
            
        # 3. Scan Memory context
        if memory:
            score, reason = MemoryGuard.inspect(memory)
            if score > 0:
                if score > max_score: max_score = score
                attack_types.append("Memory Poisoning")
                reasons.append(f"Memory: {reason}")
                
        # 4. Scan Tool Calls
        if tool_calls:
            score, reason = APIGuard.validate_tool_calls(tool_calls)
            if score > 0:
                if score > max_score: max_score = score
                attack_types.append("API Misuse")
                reasons.append(f"Tool Call: {reason}")
                
        risk_level = self._get_risk_level(max_score)
        action = self._determine_action(max_score, block_threshold)
        safe = max_score < block_threshold
        
        attack_types = list(set(attack_types))
        combined_reason = "; ".join(reasons) if reasons else "Safe"
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        result = ScanResult(
            safe=safe, risk_score=max_score, risk_level=risk_level,
            attack_type=attack_types, action=action, reason=combined_reason,
            latency_ms=round(latency_ms, 4)
        )
        
        # Log to telemetry
        telemetry.log_scan(max_score, attack_types, latency_ms)
        
        if not safe:
            logger.warning(f"Detection: {attack_types} | Score: {max_score} | Latency: {latency_ms:.4f}ms")
        elif max_score > 0:
            logger.info(f"Flagged: {attack_types} | Score: {max_score}")
            
        return result

    async def ascan(self, *args, **kwargs) -> ScanResult:
        """Asynchronously scans an interaction."""
        return await asyncio.to_thread(self.scan, *args, **kwargs)

    # Enterprise Plugin Architecture
    def register_detector(self, detector_fn: Callable):
        """Register a custom detector plugin."""
        Detector.register(detector_fn)
        logger.info(f"New custom detector registered: {detector_fn.__name__}")

    def allowlist(self, phrases: List[str]):
        """Dynamically add phrases to the allowlist."""
        self.config.allowlist.update(phrases)

    def blocklist(self, phrases: List[str]):
        """Dynamically add phrases to the blocklist."""
        self.config.blocklist.update(phrases)

    # Enterprise Streaming Support
    def wrap_stream(self, generator: Generator) -> Generator:
        """
        Wraps a streaming LLM generator.
        Scans each chunk for dangerous content or exfiltration.
        """
        logger.info("Streaming guard active.")
        for chunk in generator:
            # Simple content scan for outgoing chunks
            content = str(chunk)
            # You'd typically scan for exfiltration patterns on output
            # We filter chunks to check if something sensitive like a Credit Card matches
            res = self.scan(user_prompt=content)
            if not res.safe:
                logger.error(f"Blocking streaming chunk due to: {res.reason}")
                yield "[BLOCKED BY ULOKAI SECURITY]"
                break
            yield chunk

    def wrap_llm(self, client_fn: Callable):
        """Middleware wrapper for LLM client functions."""
        @functools.wraps(client_fn)
        def wrapper(*args, **kwargs):
            prompt = kwargs.get("prompt", "") or (args[0] if args else "")
            security_check = self.scan(user_prompt=str(prompt))
            if not security_check.safe:
                logger.error(f"Blocking dangerous prompt in middleware: {security_check.reason}")
                raise SecurityBlockException(security_check)
            return client_fn(*args, **kwargs)
        return wrapper

    def wrap_agent(self, agent: Any):
        """Wraps an agent's run/call method with a security layer."""
        original_run = getattr(agent, "run", None) or getattr(agent, "__call__", None)
        if not original_run: raise ValueError("Agent must have a 'run' or '__call__' method.")
            
        @functools.wraps(original_run)
        def secure_run(*args, **kwargs):
            prompt = str(args[0]) if args else str(kwargs.get("message", ""))
            security_check = self.scan(user_prompt=prompt)
            if not security_check.safe:
                return f"Blocked: Security alert detected ({security_check.reason})"
            return original_run(*args, **kwargs)
            
        if hasattr(agent, "run"): agent.run = secure_run
        else: agent.__call__ = secure_run
        return agent

class SecurityBlockException(Exception):
    def __init__(self, result: ScanResult):
        self.result = result
        super().__init__(f"Prompt blocked by UlockAI: {result.reason}")

guard = Guard()
