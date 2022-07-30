import os
import json
import zipfile

import yaml

from cpm.client import Client
from cpm.logging import get_logger

logger = get_logger("audit.command")
logger_user = get_logger("user_info.command")

client = Client()


def _get_data(file):
    if file:
        with open(file) as f:
            data = yaml.safe_load(f)
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


def search(args):
    page = args.page
    tags = args.tags.split(",") if args.tags else None
    name = args.name
    data = client.list_item(page, tags, name)
    for item in data:
        print(item["name"])


def _display(data):
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


def info(args):
    data = client.get_item(args.name)
    _display(data)


def upload(args):
    data = {}
    file = args.file

    data = _get_data(file)
    res = client.create_item(data)

    _display(res)


def update(args):
    data = client.get_item(args.name)
    file = args.file

    data.update(_get_data(file))
    del data["id"]
    res = client.update_item(data, args.name)

    _display(res)


def _dump_file(url, filename):
    if not url or not url.startswith("http"):
        print(f"{url} is not a valid url")
        return
    try:
        res = client.get(url)
    except Exception as exc:
        print(exc)
        return
    if not res.ok:
        return
    with open(filename, "w+b") as file:
        file.write(res.content)
    return res.content # res.text is too slow and json.load accepts bytes


def _package(files, filename):
    logger.info("Zipping %s into a package", files)
    logger_user.info("Zipping %s into a package", files)
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zfile:
        for name in files:
            zfile.write(name)
            os.remove(name)


def _download(name, packages=None):
    logger.info("Downloading the %s package.")
    logger_user.info("Downloading the %s package.")

    packages = packages or {}
    data = client.get_item(name)

    image_url = data["image"]
    file_url = data["file"]
    name = data["name"]
    files = []

    if image_url:
        image_name = name + "." + image_url.split(".")[-1]
        if _dump_file(image_url, image_name): # in case it gets deleted or bad url
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
            logger.info("Found bad dependency %s. Ignoring...", dep)
    return packages


def download(args):
    names = [_.strip() for _ in args.name.split(",")]
    packages = {}
    for name in names:
        if name not in packages.keys():
            packages = _download(name, packages)
        else:
            logger.info("Found bad package %s. Ignoring...", name)
    return packages


def compile(args):
    """Download all packages and compile them into a single file"""
    file = args.file
    packages = download(args)
    first = args.name.split(",")[0]

    compiled = json.loads(packages[first])
    for lore in packages.values():
        lore = json.loads(lore)
        compiled["entries"].extend(lore["entries"])
        compiled["categories"].extend(lore["categories"])
    with open(file, "w") as jfile:
        json.dump(compiled, jfile)
