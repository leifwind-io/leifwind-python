# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
