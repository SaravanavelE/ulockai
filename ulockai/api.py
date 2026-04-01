class APIGuard:
    @staticmethod
    def validate_tool_calls(tool_calls: list) -> tuple[int, str]:
        """Validate tool calls for potentially dangerous operations or misuse."""
        if not tool_calls:
            return 0, ""
        
        # Keywords that indicate dangerous system-level access
        danger_tools = ["exec", "shell", "delete", "rm", "format", "eval"]
        danger_args = ["rm ", "chmod ", ".sh", "sudo ", "destroy", "wipe", "/etc/passwd"]
        
        for call in tool_calls:
            # Check tool name
            name = call.get("name", "").lower()
            if any(dt in name for dt in danger_tools):
                return 85, f"Dangerous tool call detected: {name}"
            
            # Check arguments (if provided)
            args = str(call.get("args", "") or "").lower()
            if any(da in args for da in danger_args):
                return 90, f"Dangerous tool arguments detected in: {name}"
                
        return 0, ""

    @staticmethod
    def check_rate_excess(api_metadata: dict) -> tuple[int, str]:
        """Check for unusual API usage patterns (dummy implementation)."""
        # This could be integrated with a stateful storage to track token usage, 
        # prompt density, or call frequency.
        return 0, ""
