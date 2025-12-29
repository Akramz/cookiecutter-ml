#!/usr/bin/env python3
"""
Google Earth Engine authentication helper.

Usage:
    # Interactive authentication (opens browser)
    python authenticate.py

    # Service account authentication (for servers/CI)
    python authenticate.py --service-account path/to/key.json

    # Check current authentication status
    python authenticate.py --check
"""

import argparse
import sys

try:
    import ee
except ImportError:
    print("Error: earthengine-api not installed.")
    print("Install with: pip install earthengine-api")
    sys.exit(1)


def check_auth() -> bool:
    """Check if already authenticated with GEE."""
    try:
        ee.Initialize()
        # Try a simple operation to verify credentials work
        ee.Number(1).getInfo()
        return True
    except Exception:
        return False


def authenticate_interactive():
    """Run interactive OAuth authentication."""
    print("Starting interactive authentication...")
    print("This will open a browser window for Google sign-in.\n")

    try:
        ee.Authenticate()
        ee.Initialize()
        print("\nAuthentication successful!")
        print("Credentials saved to ~/.config/earthengine/credentials")
        return True
    except Exception as e:
        print(f"\nAuthentication failed: {e}")
        return False


def authenticate_service_account(key_file: str, project: str = None):
    """Authenticate using a service account key file.

    Args:
        key_file: Path to service account JSON key file
        project: GCP project ID (optional, read from key file if not provided)
    """
    import json

    print(f"Authenticating with service account: {key_file}")

    try:
        with open(key_file) as f:
            key_data = json.load(f)

        service_account = key_data.get("client_email")
        project_id = project or key_data.get("project_id")

        if not service_account:
            print("Error: Invalid service account key file")
            return False

        credentials = ee.ServiceAccountCredentials(service_account, key_file)
        ee.Initialize(credentials, project=project_id)

        # Verify it works
        ee.Number(1).getInfo()

        print(f"\nAuthentication successful!")
        print(f"Service account: {service_account}")
        print(f"Project: {project_id}")
        return True

    except FileNotFoundError:
        print(f"Error: Key file not found: {key_file}")
        return False
    except Exception as e:
        print(f"\nAuthentication failed: {e}")
        return False


def print_auth_info():
    """Print information about current authentication."""
    print("=" * 50)
    print("Google Earth Engine Authentication Status")
    print("=" * 50)

    if check_auth():
        print("Status: AUTHENTICATED")

        # Try to get project info
        try:
            # Get the current project
            import google.auth
            creds, project = google.auth.default()
            if project:
                print(f"Project: {project}")
        except Exception:
            pass

        print("\nCredentials location: ~/.config/earthengine/credentials")
        print("\nYou can now use Earth Engine!")
    else:
        print("Status: NOT AUTHENTICATED")
        print("\nTo authenticate, run one of:")
        print("  python authenticate.py              # Interactive (browser)")
        print("  earthengine authenticate            # CLI equivalent")
        print("  python authenticate.py --service-account key.json  # Service account")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Google Earth Engine authentication helper"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check authentication status without authenticating",
    )
    parser.add_argument(
        "--service-account",
        type=str,
        metavar="KEY_FILE",
        help="Path to service account JSON key file",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="GCP project ID (for service account auth)",
    )
    args = parser.parse_args()

    if args.check:
        print_auth_info()
        sys.exit(0 if check_auth() else 1)

    # Check if already authenticated
    if check_auth():
        print("Already authenticated with Google Earth Engine!")
        print("Use --check to see details, or continue to re-authenticate.\n")
        response = input("Re-authenticate? (y/N): ").strip().lower()
        if response != "y":
            print_auth_info()
            return

    # Authenticate
    if args.service_account:
        success = authenticate_service_account(args.service_account, args.project)
    else:
        success = authenticate_interactive()

    if success:
        print_auth_info()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
