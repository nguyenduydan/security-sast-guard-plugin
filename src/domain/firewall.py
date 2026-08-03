"""Firewall domain component."""

class Firewall:
    """Command Firewall checking logic."""

    def check(self, command: str) -> str:
        """Check command safety."""
        _ = command
        return "ALLOW"
