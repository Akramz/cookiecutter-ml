#!/usr/bin/env python3
"""
Ruff formatter hook for Claude Code.

Automatically formats Python files and sorts imports after edits.
Runs on PostToolUse event for Edit and Write tools.
"""
import json
import os
import subprocess
import sys


def run_ruff(file_path: str) -> int:
    """Run ruff check (with fixes) and format on a Python file."""
    # Only process Python files
    if not file_path.endswith(".py"):
        return 0

    # Skip if file doesn't exist (might have been deleted)
    if not os.path.exists(file_path):
        return 0

    try:
        # Run ruff check with --fix to auto-fix issues (includes import sorting with isort rules)
        subprocess.run(
            ["ruff", "check", "--fix", "--select", "I", file_path],
            capture_output=True,
            timeout=10,
            check=False,
        )

        # Run ruff format for code formatting
        subprocess.run(
            ["ruff", "format", file_path],
            capture_output=True,
            timeout=10,
            check=False,
        )

        return 0

    except FileNotFoundError:
        # ruff not installed - fail silently to not block Claude
        return 0

    except subprocess.TimeoutExpired:
        print(f"Warning: ruff timed out on {file_path}", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"Warning: Error formatting {file_path}: {e}", file=sys.stderr)
        return 0


def main() -> int:
    """Main entry point for the hook."""
    try:
        # Read hook input from stdin (JSON)
        input_data = json.load(sys.stdin)

        # Extract file path from tool input
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        if file_path:
            return run_ruff(file_path)

        return 0

    except json.JSONDecodeError:
        # Invalid JSON input - fail silently
        return 0

    except Exception:
        # Unexpected error - fail silently to not block Claude
        return 0


if __name__ == "__main__":
    sys.exit(main())
