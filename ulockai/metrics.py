import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class MetricsStore:
    """In-memory store for SDK telemetry and performance metrics."""
    total_scans: int = 0
    blocked_scans: int = 0
    flagged_scans: int = 0
    attack_types: Counter = field(default_factory=Counter)
    latency_ms: List[float] = field(default_factory=list)
    
    def log_scan(self, score: int, attacks: List[str], latency: float):
        self.total_scans += 1
        self.latency_ms.append(latency)
        
        for attack in attacks:
            self.attack_types[attack] += 1
            
        if score >= 70:
            self.blocked_scans += 1
        elif score >= 40:
            self.flagged_scans += 1
            
        # Keep only the last 1000 latencies to prevent memory bloat
        if len(self.latency_ms) > 1000:
            self.latency_ms.pop(0)

    def get_report(self) -> Dict:
        avg_latency = sum(self.latency_ms) / len(self.latency_ms) if self.latency_ms else 0
        return {
            "total_scans": self.total_scans,
            "blocked_scans": self.blocked_scans,
            "flagged_scans": self.flagged_scans,
            "attack_distribution": dict(self.attack_types),
            "avg_latency_ms": round(avg_latency, 4),
            "throughput_estimate": "N/A" # Calculated at runtime usually
        }

# Shared metrics instance
telemetry = MetricsStore()
