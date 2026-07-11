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
