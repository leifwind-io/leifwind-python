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
#

# Import from base module
from .base import DetailResponse, MetadataBase

# Import from collections module
from .collections import MetadataList

# Import from constants module
from .constants import RESTRICTED_FIELD_NAMES

# Import from entity module
from .entity import InterfaceEntityKey, MetadataEntity

# Import from field module
from .field import CONNECTION_MAPPING, FIELD_TYPE_MAPPING, MetadataField

# Import from field_types module
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

# Import from project module
from .project import MetadataProject

# Define __all__ to expose all public attributes
__all__ = [
    # From base module
    "DetailResponse",
    "MetadataBase",
    # From collections module
    "MetadataList",
    # From constants module
    "RESTRICTED_FIELD_NAMES",
    # From entity module
    "InterfaceEntityKey",
    "MetadataEntity",
    # From field module
    "MetadataField",
    "FIELD_TYPE_MAPPING",
    "CONNECTION_MAPPING",
    # From field_types module
    "MetadataFieldConnectionFragment",
    "MetadataFieldConnectionKey",
    "MetadataFieldText",
    "MetadataFieldInteger",
    "MetadataFieldDecimal",
    "MetadataFieldBoolean",
    "MetadataFieldDate",
    "MetadataFieldTime",
    "MetadataFieldTimestamp",
    "MetadataFieldUUID",
    # From project module
    "MetadataProject",
]
