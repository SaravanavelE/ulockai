from .config import MEMORY_RE

class MemoryGuard:
    @staticmethod
    def inspect(memory: str) -> tuple[int, str]:
        """Inspect the conversation memory for poisoning or instruction manipulation."""
        if not memory or not isinstance(memory, str):
            return 0, ""
        
        matches = MEMORY_RE.findall(memory)
        if matches:
            return 75, f"Memory poisoning detected: {', '.join(matches[:3])}"
        
        # Check for multiple 'System:' prefixes which could be injection
        if memory.lower().count("system prompt:") > 1:
            return 90, "Multiple system prompts detected in memory context."
            
        return 0, ""
