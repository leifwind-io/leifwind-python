from typing import Annotated, Union

from pydantic import BaseModel, Field

from .entity import MetadataEntity
from .field import MetadataField
from .project import MetadataProject

AbstractMetadata = (
    Annotated[
        Union[
            MetadataProject,
            MetadataEntity,
            MetadataField,
        ],
        Field(discriminator="metadata_type"),
    ],
)


class MetadataList(BaseModel):
    cursor: str | None
    objects: list[AbstractMetadata]
