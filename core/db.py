from peewee import (
    CharField,
    ForeignKeyField,
    DateTimeField,
    UUIDField,
    SqliteDatabase,
    Model,
    TextField,
    BooleanField,
)
from playhouse.shortcuts import model_to_dict

import datetime
import os
import uuid
import json
import sqlite3

import datetime
import re
from core.utils import (
    get_app_dir,
    check_or_create_app_dir,
    STARTER_CODE,
    get_platform_for_board_id,
)

# Ensure db folder exists
check_or_create_app_dir()

db_path = os.path.join(get_app_dir(), "core_db.db")
db = SqliteDatabase(db_path)


def create_project_files(project_id):
    """
    Create a new project folder structure:
    - <app_dir>/projects/<project_id>/
        └── main.py (with starter code)
    """

    app_folder = get_app_dir()
    projects_folder = os.path.join(app_folder, "projects")
    project_folder = os.path.join(projects_folder, project_id)

    # Ensure base projects directory exists
    os.makedirs(projects_folder, exist_ok=True)

    # Ensure project directory exists
    os.makedirs(project_folder, exist_ok=True)

    # Path to main.py
    main_file = os.path.join(project_folder, "main.py")

    # Write starter code only if file doesn’t exist
    if not os.path.exists(main_file):
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(STARTER_CODE)

    return project_folder


def get_core_db_conn():
    return sqlite3.connect(db_path)


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value) if value is not None else None

    def python_value(self, value):
        return json.loads(value) if value is not None else None


class BaseModel(Model):
    class Meta:
        database = db


class Project(BaseModel):
    project_id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField()
    description = TextField()
    is_active = BooleanField(default=True)
    metadata = JSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    project_type = CharField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


# ✅ Ensure tables exist
db.connect()
db.create_tables([Project])


def create_new_project(name, description, metadata={}):
    new_project = Project.create(
        name=name,
        description=description,
        project_type="sketch",
        metadata=metadata,
    )

    create_project_files(str(new_project.project_id))

    return new_project  # no need to call .save() again


def update_project_details(payload: dict):
    project_id = payload.get("project_id")
    project = Project.get(project_id=project_id)
    print(
        f"project is {type(project)} and project_id is {project_id} amd name {project.name}"
    )
    if "name" in payload:
        project.name = payload["name"]

    if "description" in payload:
        project.description = payload["description"]

    if "board_name_id" in payload:
        board_name_id = payload["board_name_id"]
        print(f"new board name id is {board_name_id}")
        if board_name_id != "":
            match = re.match(r"^(.*)\s+\((.*)\)$", board_name_id)
            board_name = match.group(1).strip()
            board_id = match.group(2).strip()
            platform = get_platform_for_board_id(board_id)
            print(f"{board_name}-{board_id}-{platform}")

            metadata = project.metadata
            print(f"metadata is {metadata}")
            metadata["board_name"] = board_name
            metadata["board_id"] = board_id
            metadata["platform"] = platform
            print(f"new metadata is {metadata}")

            project.metadata = metadata

    project.save()
    return


def _serialize_value(value):
    """Convert Peewee/complex objects into JSON-safe types."""
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def _serialize_row(row: dict) -> dict:
    """Apply serialization to every field in a row dict."""
    return {k: _serialize_value(v) for k, v in row.items()}


def get_all_projects():
    query = Project.select()
    rows = [model_to_dict(p) for p in query]
    return [_serialize_row(row) for row in rows]


def get_project_from_id(project_id):
    project = Project.get(Project.project_id == project_id)
    data = model_to_dict(project)
    return _serialize_row(data)


def update_project_files(project_id, code):
    app_folder = get_app_dir()
    # Path to the project folder
    project_folder = os.path.join(app_folder, "projects", project_id)
    os.makedirs(project_folder, exist_ok=True)

    # Path to main.py inside the project folder
    main_file = os.path.join(project_folder, "main.py")

    # Write the new code
    with open(main_file, "w", encoding="utf-8") as f:
        f.write(code)

    project = Project(project_id=project_id)
    project.save()


def get_project_code_from_id(project_id: str) -> str:
    app_folder = get_app_dir()
    project_path = os.path.join(app_folder, "projects", project_id, "main.py")

    if not os.path.exists(project_path):
        raise FileNotFoundError(
            f"main.py not found for project {project_id} at {project_path}"
        )

    with open(project_path, "r", encoding="utf-8") as f:
        return f.read()
