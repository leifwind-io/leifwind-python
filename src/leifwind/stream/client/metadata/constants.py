# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Constants used throughout the metadata package."""

from typing import Final

# Field names that are reserved by the system and cannot be used in user-defined metadata fields
RESTRICTED_FIELD_NAMES: Final[set[str]] = {
    "created_at",  # Timestamp when the record was created
    "entity_id",  # Internal entity identifier
    "entity_key",  # User-defined entity key
    "fragment_key",  # Fragment identifier
    "object_id",  # Primary key identifier
    "project_id",  # Project identifier
    "unique_key",  # Computed unique key for the entity
    "updated_at",  # Timestamp when the record was last updated
    "dry_run",  # Dry Run is a parameter, which can't be used as field name
}
