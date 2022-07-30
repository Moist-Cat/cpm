"""
Functions that parse the string from the CLI and hand it over to the command fucntions go here
"""
import argparse
from typing import List
import sys

from cpm import command


def get_command(argv: List[str] = sys.argv[1:]): # pylint: disable=W0102
    """"""
    parser = argparse.ArgumentParser(description="Card Package Manager CLI utility.")
    parser.set_defaults(func=lambda args: parser.parse_args(["-h"]))

    subparsers = parser.add_subparsers()

    search_parser = subparsers.add_parser("search", help=command.search.__doc__)
    search_parser.set_defaults(func=command.search)
    search_parser.add_argument(
        "--tags",
        "-t",
        default=None,
    )
    search_parser.add_argument(
        "--page",
        "-p",
        default=0,
        type=int,
        help="Search this page of the patalog (10 items per page)",
    )
    search_parser.add_argument(
        "--name",
        "-n",
        default=None,
        type=str,
    )

    info_parser = subparsers.add_parser("info", help=command.info.__doc__)
    info_parser.set_defaults(func=command.info)
    info_parser.add_argument(
        "name",
        type=str,
    )

    upload_parser = subparsers.add_parser("upload", help=command.upload.__doc__)
    upload_parser.set_defaults(func=command.upload)
    upload_parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="YAML file to fetch the data from.",
    )

    update_parser = subparsers.add_parser("update", help=command.update.__doc__)
    update_parser.set_defaults(func=command.update)
    update_parser.add_argument(
        "name",
        type=str,
        help="Item name",
    )
    update_parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="yaml file to fetch the data from.",
    )

    download_parser = subparsers.add_parser("download", help=command.download.__doc__)
    download_parser.set_defaults(func=command.download)
    download_parser.add_argument(
        "name",
        type=str,
        help="Item name",
    )

    compile_parser = subparsers.add_parser(
        "compile",
        help=command.compile.__doc__,
    )
    compile_parser.set_defaults(func=command.compile)
    compile_parser.add_argument(
        "name",
        type=str,
        help="Item name",
    )
    compile_parser.add_argument(
        "--file",
        "-f",
        type=str,
        default="compiled.lorebook",
        help="Place the output in this file",
    )

    debug_parser = subparsers.add_parser(
        "debug",
        help=command.debug.__doc__
    )
    debug_parser.set_defaults(func=command.debug)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    get_command()
