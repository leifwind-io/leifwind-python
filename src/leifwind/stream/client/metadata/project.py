# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
