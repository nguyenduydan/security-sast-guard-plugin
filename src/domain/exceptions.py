"""Domain exceptions for Security SAST Guard."""


class SecurityGuardError(Exception):
    """Base exception for all security guard errors."""


class SecurityIntegrityError(SecurityGuardError):
    """Raised when SHA-256 HMAC checksum or profile integrity verification fails."""


class RuleValidationError(SecurityGuardError):
    """Raised when a rule is malformed or invalid."""


class ConfigurationError(SecurityGuardError):
    """Raised when profile configuration is invalid or unreadable."""
