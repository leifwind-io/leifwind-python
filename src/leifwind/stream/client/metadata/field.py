# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Field definitions and management for metadata entities."""

from typing import Any, ClassVar, Final, Literal, Union
from uuid import UUID

from pydantic import Field

from .base import FIELD_NAME_PATTERN, MetadataBase
from .field_types import (
    MetadataFieldBoolean,
    MetadataFieldConnectionFragment,
    MetadataFieldConnectionKey,
    MetadataFieldDate,
    MetadataFieldDecimal,
    MetadataFieldInteger,
    MetadataFieldText,
    MetadataFieldTime,
    MetadataFieldTimestamp,
    MetadataFieldUUID,
)

# Type aliases for better readability
FieldConfigType = Union[
    MetadataFieldText,
    MetadataFieldInteger,
    MetadataFieldDecimal,
    MetadataFieldBoolean,
    MetadataFieldDate,
    MetadataFieldTime,
    MetadataFieldTimestamp,
    MetadataFieldUUID,
]

ConnectionType = Union[MetadataFieldConnectionFragment, MetadataFieldConnectionKey]

# Mapping from data type strings to their corresponding field type classes
FIELD_TYPE_MAPPING: Final[dict[str, type[FieldConfigType]]] = {
    "TEXT": MetadataFieldText,
    "INTEGER": MetadataFieldInteger,
    "DECIMAL": MetadataFieldDecimal,
    "BOOLEAN": MetadataFieldBoolean,
    "DATE": MetadataFieldDate,
    "TIME": MetadataFieldTime,
    "TIMESTAMP": MetadataFieldTimestamp,
    "UUID": MetadataFieldUUID,
}

# Mapping from connection type strings to their corresponding connection classes
CONNECTION_MAPPING: Final[dict[str, type[ConnectionType]]] = {
    "FRAGMENT": MetadataFieldConnectionFragment,
    "KEY": MetadataFieldConnectionKey,
}


class MetadataField(MetadataBase):
    """Represents a field within a metadata entity.

    A metadata field defines the structure and type of data that can be stored
    in an entity. Each field has a configuration that specifies its data type
    and a connection type that determines where the field data is stored.

    Attributes:
        project_id: The UUID of the project this field belongs to
        entity_id: The UUID of the entity this field belongs to
        name: The name of the field
        config: Configuration specifying the field's data type and constraints
        connection_type: Specifies whether the field is stored in the key table or a fragment
    """

    metadata_type: Literal["metadata_field"] = "metadata_field"
    _unique_fields: ClassVar[tuple[str, ...]] = ("project_id", "entity_id", "name")
    project_id: UUID | None
    entity_id: UUID
    name: str = Field(pattern=FIELD_NAME_PATTERN)
    config: FieldConfigType = Field(discriminator="data_type")
    connection_type: ConnectionType = Field(discriminator="connection_type")

    @classmethod
    def parse_flat_db(cls, obj: dict[str, Any]) -> "MetadataField":
        """Parse a flat database record into a MetadataField instance.

        This method reconstructs a MetadataField from a flattened database representation,
        handling the complex nested structure of config and connection_type fields.

        Args:
            obj: Dictionary containing the flattened field data from the database

        Returns:
            A new MetadataField instance

        Raises:
            KeyError: If required keys are missing from the database record
            ValueError: If the data_type or connection_type values are invalid
        """
        # Create the field configuration based on data type
        if obj["data_type"] not in FIELD_TYPE_MAPPING:
            raise ValueError(f"Unknown data type: {obj['data_type']}")

        config = FIELD_TYPE_MAPPING[obj["data_type"]](
            data_type=obj["data_type"],
        )

        # Build connection type configuration
        connection_data = {
            "connection_type": obj["connection_type"],
        }
        if obj["connection_type"] == "FRAGMENT":
            connection_data["fragment_name"] = obj["fragment_name"]
        elif obj["connection_type"] not in CONNECTION_MAPPING:
            raise ValueError(f"Unknown connection type: {obj['connection_type']}")

        connection_type = CONNECTION_MAPPING[obj["connection_type"]](**connection_data)

        # Create and return the field instance
        return cls(
            object_id=obj["object_id"],
            project_id=obj["project_id"],
            entity_id=obj["entity_id"],
            name=obj["name"],
            config=config,
            connection_type=connection_type,
        )
