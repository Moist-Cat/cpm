import os
import json
import zipfile

import yaml

from cpm.client import Client

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
    for key, val in data.copy().items():
        if not val:
            del data[key]
    return data

def search(args):
    page = args.page
    tags = args.tags.split(",") if args.tags else None
    name = args.name
    data = client.list_item(page, tags, name)
    for item in data:
        print(item["name"])

def info(args):
    data = client.get_item(args.name)
    print(f"""
    Name: {data['name']}
    ============================================================
    Description: {data['desc']}
    Tags: {', '.join(data['tags'])}
    Depends on: {', '.join(data['deps'])}
    File: {data['file']}
    Date created: {data['date_created']}
    Date updated: {data['date_updated']}
    """)

def upload(args):
    data = {}
    file = args.file

    data = _get_data(file)
    client.create_item(data)

def update(args):
    data = client.get_item(args.name)
    file = args.file

    data.update(_get_data(file))
    del data["id"]
    client.update_item(data, args.name)

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
    return res.text

def _package(files, filename):
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zfile:
        for name in files:
            zfile.write(name)
            os.remove(name)

def _download(name, packages=None):
    packages = packages or {}
    data = client.get_item(name)

    image_url = data["image"]
    file_url = data["file"]
    name = data["name"]
    files = []

    if image_url:
        image_name = name + "." + image_url.split(".")[-1]
        _dump_file(image_url, image_name)
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
    return packages

def download(args):
    names = [_.strip() for _ in  args.name.split(",")]
    packages = {}
    for name in names:
        if name not in packages.keys():
            packages = _download(name, packages)

def compile(args):
    """Download all packages and """
    file = args.file

    packages = download(args)
    compiled = json.loads(packages.pop())
    for lore in packages:
        lore = json.loads(lore)
        compiled["entries"].extend(lore["entries"])
    with open(file, "w") as jfile:
        json.dump(compiled, jfile)
