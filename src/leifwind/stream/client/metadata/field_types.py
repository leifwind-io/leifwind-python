#
#  Copyright (C)  2025 bbruhn(leifwind)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Field type definitions for metadata fields.

This module defines the various field types that can be used in metadata entities,
including both data types and connection types.
"""

import decimal
from datetime import date, datetime, time
from typing import ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .base import FIELD_NAME_PATTERN


class MetadataFieldConnectionFragment(BaseModel):
    """Connection type for fields that reference a specific fragment of an entity.

    This connection type is used when a field should store data in a separate
    fragment table rather than the main entity table.

    Attributes:
        connection_type: Always "FRAGMENT" for this connection type
        fragment_name: Name of the fragment where the field data will be stored
    """

    connection_type: Literal["FRAGMENT"]
    fragment_name: str = Field(pattern=FIELD_NAME_PATTERN)


class MetadataFieldConnectionKey(BaseModel):
    """Connection type for fields that are part of the entity key.

    This connection type is used for fields that should be stored in the main
    entity key table and contribute to entity identification.

    Attributes:
        connection_type: Always "KEY" for this connection type
    """

    connection_type: Literal["KEY"]


class MetadataFieldText(BaseModel):
    """Text field type for storing string values.

    Attributes:
        data_type: Always "TEXT" for this field type
        python_type: The corresponding Python type (str)
    """

    data_type: Literal["TEXT"]
    python_type: ClassVar[type] = str


class MetadataFieldInteger(BaseModel):
    """Integer field type for storing whole number values.

    Attributes:
        data_type: Always "INTEGER" for this field type
        python_type: The corresponding Python type (int)
    """

    data_type: Literal["INTEGER"]
    python_type: ClassVar[type] = int


class MetadataFieldDecimal(BaseModel):
    """Decimal field type for storing precise decimal values.

    Attributes:
        data_type: Always "DECIMAL" for this field type
        python_type: The corresponding Python type (decimal.Decimal)
    """

    data_type: Literal["DECIMAL"]
    python_type: ClassVar[type] = decimal.Decimal


class MetadataFieldBoolean(BaseModel):
    """Boolean field type for storing true/false values.

    Attributes:
        data_type: Always "BOOLEAN" for this field type
        python_type: The corresponding Python type (bool)
    """

    data_type: Literal["BOOLEAN"]
    python_type: ClassVar[type] = bool


class MetadataFieldDate(BaseModel):
    """Date field type for storing date values (without time).

    Attributes:
        data_type: Always "DATE" for this field type
        python_type: The corresponding Python type (datetime.date)
    """

    data_type: Literal["DATE"]
    python_type: ClassVar[type] = date


class MetadataFieldTime(BaseModel):
    """Time field type for storing time values (without date).

    Attributes:
        data_type: Always "TIME" for this field type
        python_type: The corresponding Python type (datetime.time)
    """

    data_type: Literal["TIME"]
    python_type: ClassVar[type] = time


class MetadataFieldTimestamp(BaseModel):
    """Timestamp field type for storing date and time values.

    Attributes:
        data_type: Always "TIMESTAMP" for this field type
        python_type: The corresponding Python type (datetime.datetime)
    """

    data_type: Literal["TIMESTAMP"]
    python_type: ClassVar[type] = datetime


class MetadataFieldUUID(BaseModel):
    """UUID field type for storing universally unique identifier values.

    Attributes:
        data_type: Always "UUID" for this field type
        python_type: The corresponding Python type (uuid.UUID)
    """

    data_type: Literal["UUID"]
    python_type: ClassVar[type] = UUID
