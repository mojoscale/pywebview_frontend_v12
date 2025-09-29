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
import json  # <-- needed for JSONField

import datetime

from .utils import get_app_dir, check_or_create_app_dir

# Ensure db folder exists
check_or_create_app_dir()

db_path = os.path.join(get_app_dir(), "core_db.db")
db = SqliteDatabase(db_path)


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

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


# ✅ Ensure tables exist
db.connect()
db.create_tables([Project])


def create_new_project(name, description):
    new_project = Project.create(name=name, description=description)
    return new_project  # no need to call .save() again


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
