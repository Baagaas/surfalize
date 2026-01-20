import argparse
import sys

#!/usr/bin/env python3
"""
A command-line module for surfalize examples.
"""



def command_hello(args):
    """Handle hello command."""
    print(f"Hello, {args.name}!")


def command_info(args):
    """Handle info command."""
    print("BV Addons - Surfalize Example Module")
    print("Version: 1.0.0")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Surfalize BV Addons - Command-line tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Hello command
    hello_parser = subparsers.add_parser("hello", help="Greet someone")
    hello_parser.add_argument("name", help="Name to greet")
    hello_parser.set_defaults(func=command_hello)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show module info")
    info_parser.set_defaults(func=command_info)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()