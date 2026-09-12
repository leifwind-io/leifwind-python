# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Annotated

from pydantic import BaseModel, Field

from .entity import MetadataEntity
from .field import MetadataField
from .project import MetadataProject

AbstractMetadata = (
    Annotated[
        MetadataProject | MetadataEntity | MetadataField,
        Field(discriminator="metadata_type"),
    ],
)


class MetadataList(BaseModel):
    cursor: str | None
    objects: list[AbstractMetadata]
