import argparse
from typing import List
import sys

from cpm import command

def get_command(argv: List[str] = sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Card Package Manager CLI utility."
    )
    subparsers = parser.add_subparsers()

    ls_parser = subparsers.add_parser(
        "search",
        help="List items in the catalog"
    )
    ls_parser.set_defaults(func=command.search)
    ls_parser.add_argument(
        "--tags", "-t", default=None,
    )
    ls_parser.add_argument(
        "--page", "-p", default=0, type=int,
        help="page of the catalog--10 items per page"
    )
    ls_parser.add_argument(
        "--name", "-n", default=None, type=str,
    )

    info_parser = subparsers.add_parser(
        "info",
        help="Print information about an item",
    )
    info_parser.set_defaults(func=command.info)
    info_parser.add_argument(
        "name", type=str,
    )

    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload information about a package to the repository."
    )
    upload_parser.set_defaults(func=command.upload)
    upload_parser.add_argument(
        "--file", "-f", type=str,
        help="YAML file to fetch the data from.",
    )
    
    update_parser = subparsers.add_parser(
        "update",
        help="Update the information about a package to the repository."
    )
    update_parser.set_defaults(func=command.update)
    update_parser.add_argument(
        "name", type=str,
        help="Item name",
    )
    update_parser.add_argument(
        "--file", "-f", type=str,
        help="yaml file to fetch the data from.",
    )

    download_parser = subparsers.add_parser(
        "download",
        help="Download a package."
    )
    download_parser.set_defaults(func=command.download)
    download_parser.add_argument(
        "name", type=str,
        help="Item name",
    )

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a package."
    )
    compile_parser.set_defaults(func=command.compile)
    compile_parser.add_argument(
        "name", type=str,
        help="Item name",
    )
    compile_parser.add_argument(
        "--file", "-f", type=str, default="compiled.lorebook",
        help="Place the output in this file"
    )

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    get_command()
