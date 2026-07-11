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

"""Project management for metadata system."""

from typing import Any, ClassVar, Literal, Self, override

from pydantic import Field

from .base import FIELD_NAME_PATTERN, MetadataBase


class MetadataProject(MetadataBase):
    """Represents a metadata project.

    A project is a container for metadata entities and provides namespace isolation.
    Each project has a unique name and can contain multiple entities with their
    associated fields and fragments.

    Attributes:
        name: The unique name of the project
    """

    metadata_type: Literal["metadata_project"] = "metadata_project"
    _unique_fields: ClassVar[tuple[str, ...]] = ("name",)
    name: str = Field(pattern=FIELD_NAME_PATTERN)

    @classmethod
    @override
    def parse_flat_db(cls, obj: dict[str, Any]) -> Self:
        return cls(
            object_id=obj["object_id"],
            name=obj["name"],
        )
