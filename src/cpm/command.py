"""
CLI commands go here.
"""

import os
import json
import zipfile

import yaml

from cpm.client import Client
from cpm.logging import get_logger
from cpm import settings

logger = get_logger("audit.command")
logger_user = get_logger("user_info.command")
logger_err = get_logger("error.command")

client = Client()


def _compile(template: dict, packages: dict):
    compiled = template
    for lore in packages.values():
        lore = json.loads(lore)
        compiled["entries"].extend(lore["entries"])
        compiled["categories"].extend(lore["categories"])
    return compiled


def _display(data):
    """Display information about a package on the terminal"""
    print(
        f"""
    Name: {data['name']}
    ============================================================
    Description: {data['desc']}
    Tags: {', '.join(data['tags'])}
    Depends on: {', '.join(data['deps'])}
    Image: {data['image']}
    File: {data['file']}
    Date created: {data['date_created']}
    Date updated: {data['date_updated']}
    """
    )


def _dump_file(url, filename):
    """
    Dump a file specified on a package metadata to the filesystem.
    In case of failure, warn and exit.
    """
    if not url or not url.startswith("http"):
        logger.warning("%s is not a valid url", url)
        return None
    try:
        res = client.get(url)
    except Exception as exc:
        logger_err.error(exc)
        return None
    if not res.ok:
        return None

    with open(filename, "w+b") as file:
        file.write(res.content)
    return res.content  # res.text is too slow and json.load accepts bytes


def _download(name, packages=None):
    """Low level implementation of download."""
    logger.info("Downloading the %s package.", name)
    logger_user.info("Downloading the %s package.", name)

    packages = packages or {}
    data = client.get_item(name)

    image_url = data["image"]
    file_url = data["file"]
    name = data["name"]
    files = []

    if image_url:
        image_name = name + "." + image_url.split(".")[-1]
        if _dump_file(image_url, image_name):  # in case it gets deleted or bad url
            files.append(image_name)
    file_name = name + ".lorebook"
    json_name = name + ".json"
    files.extend((file_name, json_name))

    with open(json_name, "w") as jfile:
        json.dump(data, jfile)
    packages[name] = _dump_file(file_url, file_name)

    _package(files, name + ".zip")

    for dep in data["deps"]:
        if dep not in packages.keys() and dep != name:
            packages.update(_download(dep, packages))
        else:
            logger.info("Found duplicate dependency %s. Ignoring...", dep)
    return packages


def _get_data(file):
    """Fetch and sanitize data from the user."""
    if file:
        with open(file) as yfile:
            data = yaml.safe_load(yfile)
    else:
        data = {
            "name": input("name: ").strip(),
            "deps": input("dependencies: "),
            "tags": input("tags: "),
            "image": input("image url: ").strip(),
            "desc": input("description: ").strip(),
            "file": input("file url: ").strip(),
            "service": input("service: ").strip(),
        }
    if "tags" in data and data["tags"]:
        data["tags"] = [tag.strip() for tag in data["tags"].split(",")]
    if "deps" in data and data["deps"]:
        data["deps"] = [dep.strip() for dep in data["deps"].split(",")]

    logger.debug("%d keys before purging empty values", len(data.keys()))
    for key, val in data.copy().items():
        if not val:
            del data[key]
    logger.debug("%d keys after purging empty values", len(data.keys()))

    return data


def _package(files, filename):
    """Compress files, delete them afterwards"""
    logger.info("Zipping %s into a package", files)
    logger_user.info("Zipping %s into a package", files)
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zfile:
        for name in files:
            zfile.write(name)
            os.remove(name)

def _tail(name):
    with open(name) as file:
        eof = file.seek(0, 2) # end
        file.seek(0)
        if eof - 50*200 > 0: # ~ 200 entries 
            file.seek(eof - 50*200)
        return file.read()


def search(args):
    """Search packages on the repository"""
    page = args.page
    tags = args.tags.split(",") if args.tags else None
    name = args.name
    while True:
        data = client.list_item(page, tags, name)
        for item in data:
            print(item["name"])
        if len(data) < 10:
            break
        print("======================================")
        try:
            input("Press enter to see the next page...")
        except KeyboardInterrupt:
            break
        page +=1


def info(args):
    """Display information about a package"""
    data = client.get_item(args.name)
    _display(data)


def upload(args):
    """Upload metadata about a package to the repository"""
    data = {}
    file = args.file

    data = _get_data(file)
    res = client.create_item(data)

    _display(res)


def update(args):
    """Update the metadata of a package"""
    data = client.get_item(args.name)
    file = args.file

    data.update(_get_data(file))
    del data["id"]
    res = client.update_item(data, args.name)

    _display(res)


def compile(args):
    """Download all packages and compile them into a single file"""
    file = args.file
    packages = download(args)
    first = args.name.split(",")[0]

    template = json.loads(packages[first])
    compiled = _compile(template, packages)

    with open(file, "w") as jfile:
        json.dump(compiled, jfile)
    return compiled

def debug(args):
    print()
    print("### BEGIN DEBUG LOGS ###")
    print(_tail(settings.LOG_FILE))
    print("### END DEBUG LOGS ###")
    print(f"Log file: {settings.LOG_FILE}")
    print()


def download(args):
    """
    Download one or more packages from the repository. Resolving dependencies and zipping
    all files.
    """
    names = [_.strip() for _ in args.name.split(",")]
    packages = {}
    for name in names:
        if name not in packages.keys():
            packages = _download(name, packages)
        else:
            logger.info("Found duplicate package %s. Ignoring...", name)
    return packages
