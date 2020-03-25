from typing import List, Optional, Union
import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
import jinja2

app = FastAPI(version='0.0.1')
config_path = os.path.abspath(os.environ.get('FILE_NAVIGATOR_CONFIG', 'config.json'))
JS_PATH = os.path.abspath('js')


class FileBase(BaseModel):
    name: str
    id: int
    content_path: str


class File(FileBase):
    next: Optional[FileBase]
    last: Optional[FileBase]

    def to_base(self):
        return FileBase(
            name=self.name,
            id=self.id,
            content_path=self.content_path,
        )


class Folder(BaseModel):
    name: str
    items: List[File]
    path: str


def get_directory_files(folder_id, directory):
    files = []
    for i, name in enumerate(sorted(os.path.os.listdir(directory))):
        file = File(
            id=i+1,
            name=name,
            content_path=f"/folder/{folder_id}/file/{i+1}/contents",
        )
        if i:
            file.last = files[i-1].to_base()
        files.append(file)
    for i in range(len(files)):
        if i+1 < len(files):
            files[i].next = files[i+1].to_base()
    return files


def load_folders_from_config():
    with open(config_path, 'r') as f:
        config = json.load(f)
    folders = {}
    for id, (folder_name, path) in enumerate(config.items(), 1):
        folders[id] = Folder(name=folder_name, path=path, items=get_directory_files(id, path))
    return folders


def folder_name_to_id(name):
    if isinstance(name, int):
        return name
    for id, folder in load_folders_from_config().items():
        if folder.name == name:
            return int(id)


def _get_folder(id: int):
    id = folder_name_to_id(id)
    folder = load_folders_from_config().get(id)
    if not folder:
        raise HTTPException(
            status_code=404,
            detail="Folder not found",
        )
    return folder


def _get_file(folder_id: int, file_id: int):
    folder_id = folder_name_to_id(folder_id)
    folder = _get_folder(folder_id)
    print(len(folder.items), folder_id)
    if len(folder.items) < file_id:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )
    return folder.items[file_id-1]


def _get_file_contents(folder_id: int, file_id: int):
    file = _get_file(folder_id, file_id)
    folder = _get_folder(folder_id)
    with open(os.path.join(folder.path, file.name), 'r') as f:
        return f.read()


def load_scripts(path, **kwargs):
    scripts = []
    for name in os.path.os.listdir(path):
        with open(os.path.join(path, name), 'r') as f:
            src = f.read()
            template = jinja2.Template(src)
            scripts.append(template.render(**kwargs))
    return scripts


@app.get("/folder/{id}", response_model=Folder)
def get_folder(id: int) -> Folder:
    """Get Folder by ID."""
    return _get_folder(id)


@app.get("/folder/{folder_id}/file/{file_id}", response_model=File)
def get_file(folder_id: Union[int, str], file_id: int):
    """Get a file from a folder."""
    return _get_file(folder_id, file_id)


@app.get("/folder/{folder_id}/file/{file_id}/contents")
def get_file_contents(folder_id: Union[int, str], file_id: int):
    """Get a file from a folder."""
    folder_id = folder_name_to_id(folder_id)
    html = _get_file_contents(folder_id, file_id)
    soup = BeautifulSoup(html, 'lxml')
    for script in load_scripts(JS_PATH, folder_id=folder_id, file_id=file_id):
        script_o = soup.new_tag("script")
        script_o.string = script
        soup.head.append(script_o)
    return HTMLResponse(
        content=soup,
        status_code=200,
    )
