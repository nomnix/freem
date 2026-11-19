"""The help command."""

from __future__ import annotations

import sys

from . import cli

SYNOPSIS = "Shows the list of commands, or help for a single command."
DESCRIPTION = (
    "Without an argument, prints every available command.\n"
    'With a command name, prints its help (the same as passing -? to the command).'
)
EPILOG = """examples:
  python mgr.py help
  python mgr.py help gen
"""


def add_arguments(parser):
    parser.add_argument("command", nargs="?", metavar="COMMAND", help="command to show help for")


def run(args, extra):
    if args.command:
        name, module_name = cli.find_command(args.command)

        if not name:
            print(f"mgr: invalid command '{args.command}' - run 'python mgr.py help' for help", file=sys.stderr)
            return 1

        cli.print_command_help(name, cli.load_module(module_name))

        return 0

    print("# mgr: the cfx.re developer utility")
    print("# https://cfx.re/")
    print()
    print("usage: python mgr.py <subcommand> [args]")

    for name, module_name in cli.command_modules().items():
        print(f"- python mgr.py {name}: {cli.load_module(module_name).SYNOPSIS}")

    print()
    print('run "python mgr.py <subcommand> -?" for help with a specific command')

    return 0
