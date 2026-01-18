import asyncio
import subprocess
from typing import Optional

# Cache for the primary account name (detected once, reused)
_cached_account_name: Optional[str] = None


def get_primary_account_name() -> str:
    """Get the name of the primary Notes account.

    This handles localized account names (e.g., "iCloud" in English,
    "Osobní" in Czech, etc.) by detecting the first available account.

    Returns:
        The name of the primary Notes account.
    """
    global _cached_account_name

    if _cached_account_name is not None:
        return _cached_account_name

    script = 'tell application "Notes" to get name of first account'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        _cached_account_name = result.stdout.strip()
    else:
        # Fallback to "iCloud" if detection fails
        _cached_account_name = "iCloud"

    return _cached_account_name


# Constant for use in AppleScript strings - will be replaced at runtime
ICLOUD_ACCOUNT = get_primary_account_name()


class BaseAppleScriptOperations:
    """Base class with common AppleScript execution functionality."""

    @staticmethod
    async def execute_applescript(script: str) -> str:
        """Execute AppleScript and return result."""
        process = await asyncio.create_subprocess_exec(
            "osascript",
            "-e",
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"AppleScript error: {stderr.decode()}")

        return stdout.decode().strip()
