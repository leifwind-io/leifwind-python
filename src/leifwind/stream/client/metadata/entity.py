# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Entity management for metadata system.

This module provides the core functionality for managing metadata entities,
including entity key interfaces and the main MetadataEntity class that handles
entity creation, field management, and Pydantic model generation.
"""

import abc
import collections
from functools import cached_property
from itertools import chain
from typing import Any, ClassVar, Literal, Self, override
from uuid import UUID

import pydantic
from pydantic import BaseModel

from .base import FIELD_NAME_PATTERN, MetadataBase
from .constants import RESTRICTED_FIELD_NAMES
from .field import MetadataField


class InterfaceEntityKey(BaseModel, abc.ABC):
    """Abstract base class for entity keys.

    This class defines the interface for entity keys, which are used to uniquely
    identify entities within the metadata system. Entity keys combine project_id,
    entity_id, and user-defined fields to create a unique identifier.

    Attributes:
        object_id: Optional UUID for the key when persisted to database
        project_id: UUID of the project this key belongs to
        entity_id: Optional UUID of the entity this key identifies
    """

    object_id: UUID | None = None
    project_id: UUID
    entity_id: UUID | None = None

    @pydantic.computed_field
    @property
    def unique_key(self) -> str:
        """Generate a unique key string for this entity key.

        The unique key is constructed by joining the project_id, entity_id,
        and all non-restricted field values with colons.

        Returns:
            A string representation of the unique key
        """
        key_fields = set(type(self).model_fields.keys()) - RESTRICTED_FIELD_NAMES
        return ":".join(
            str(getattr(self, field))
            for field in chain(["project_id", "entity_id"], key_fields)
        )


class MetadataEntity(MetadataBase):
    """Represents a metadata entity within a project.

    A metadata entity defines the structure and schema for a particular type of data
    within a project. It contains fields that define the data types and storage
    locations, and can generate Pydantic models for data validation.

    Attributes:
        project_id: UUID of the project this entity belongs to
        name: Unique name of the entity within the project
    """

    metadata_type: Literal["metadata_entity"] = "metadata_entity"
    _unique_fields: ClassVar[tuple[str, ...]] = ("project_id", "name")
    _fields: list["MetadataField"] = []
    project_id: UUID
    name: str = pydantic.Field(pattern=FIELD_NAME_PATTERN)

    @classmethod
    @override
    def parse_flat_db(cls, obj: dict[str, Any]) -> Self:
        return cls(
            object_id=obj["object_id"],
            project_id=obj["project_id"],
            name=obj["name"],
        )

    def reset_pydantic_model_cache(self) -> None:
        """Reset the cached Pydantic models, forcing them to be regenerated."""
        if hasattr(self, "pydantic_key_model"):
            del self.pydantic_key_model

        if hasattr(self, "pydantic_fragment_models"):
            del self.pydantic_fragment_models

        if hasattr(self, "pydantic_entity_model"):
            del self.pydantic_entity_model

    @cached_property
    def pydantic_entity_model(self) -> type[BaseModel]:
        """Get the Pydantic model for entities."""
        self.update_pydantic_model()
        return self.pydantic_entity_model

    @cached_property
    def pydantic_key_model(self) -> type[InterfaceEntityKey]:
        """Get the Pydantic model for entity keys.

        Returns:
            A dynamically generated Pydantic model class for entity keys
        """
        self.update_pydantic_model()
        return self.pydantic_key_model

    @cached_property
    def pydantic_fragment_models(self) -> dict[str, type[BaseModel]]:
        """Get the Pydantic models for entity fragments.

        Returns:
            A dictionary mapping fragment names to their Pydantic model classes
        """
        self.update_pydantic_model()
        return self.pydantic_fragment_models

    def get_pydantic_model(self) -> dict[str, type[BaseModel]]:
        """Get the Pydantic models for entity fragments.

        Note:
            This method is deprecated. Use the pydantic_fragment_models property instead.

        Returns:
            A dictionary mapping fragment names to their Pydantic model classes
        """
        return self.pydantic_fragment_models

    def update_pydantic_model(self) -> None:
        """Update the cached Pydantic models based on current field definitions.

        This method generates Pydantic models for both entity keys and fragments
        based on the current field configuration.

        Raises:
            RuntimeError: If an unexpected connection type is encountered
        """
        entity_key_field_model_kwargs = {}
        fragment_models_kwargs = collections.defaultdict(dict)
        for field in self._fields or []:
            if field.connection_type.connection_type == "FRAGMENT":
                fragment_models_kwargs[field.connection_type.fragment_name][
                    field.name
                ] = field.config.python_type
            elif field.connection_type.connection_type == "KEY":
                entity_key_field_model_kwargs[field.name] = field.config.python_type
            else:
                raise RuntimeError(
                    f"unexpected connection type {field.connection_type.connection_type}"
                )

        entity_key_model = pydantic.create_model(
            f"{self.name}_key",
            __base__=InterfaceEntityKey,
            **entity_key_field_model_kwargs,
        )
        entity_fields = {}
        fragment_models = {}
        for fragment_name, fragment_fields in fragment_models_kwargs.items():
            fragment_models[fragment_name] = pydantic.create_model(
                f"{self.name}_{fragment_name}_fragment",
                entity_key=entity_key_model | UUID,
                object_id=(UUID | None, None),
                project_id=UUID,
                **fragment_fields,
            )
            # On the combined entity model, fragment fields are optional:
            # an unpopulated fragment surfaces its columns as NULL
            entity_fields.update(
                {
                    name: (python_type | None, None)
                    for name, python_type in fragment_fields.items()
                }
            )

        self.pydantic_key_model = entity_key_model
        self.pydantic_fragment_models = fragment_models
        self.pydantic_entity_model = pydantic.create_model(
            f"{self.name}_entity",
            entity_key=entity_key_model | UUID,
            project_id=UUID,
            **entity_fields,
        )

    @property
    def key_fields(self) -> list[MetadataField]:
        """Get all fields that are part of the entity key.

        Returns:
            A list of MetadataField instances with connection_type "KEY"

        Raises:
            RuntimeError: If no fields are present on the entity
        """
        if not self._fields:
            raise RuntimeError("no fields present on entity")

        return [f for f in self._fields if f.connection_type.connection_type == "KEY"]

    @property
    def fragment_fields(self) -> dict[str, list[MetadataField]]:
        """Get all fields organized by fragment name.

        Returns:
            A dictionary mapping fragment names to lists of MetadataField instances

        Raises:
            RuntimeError: If no fields are present on the entity
        """
        if not self._fields:
            raise RuntimeError("no fields present on entity")

        fragment_fields = collections.defaultdict(list)
        for field in self._fields:
            if field.connection_type.connection_type == "FRAGMENT":
                fragment_fields[field.connection_type.fragment_name].append(field)
        return fragment_fields
