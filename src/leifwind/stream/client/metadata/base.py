# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Base classes for metadata models."""

from typing import Any, ClassVar, Literal, Self, get_args, get_origin
from uuid import UUID

from pydantic import BaseModel, computed_field

FIELD_NAME_PATTERN = "^[a-zA-Z_][a-zA-Z0-9_]{0,62}$"


class DetailResponse(BaseModel):
    """Success counterpart of FastAPI's HTTPException body ({"detail": ...})."""

    detail: str


class MetadataBase(BaseModel):
    """Base class for all metadata models.

    This class provides common functionality for metadata entities including
    unique key generation based on specified fields.

    Attributes:
        object_id: Optional UUID that serves as the primary key when persisted to database
    """

    object_id: UUID | None = None

    # Subclasses should define this to specify which fields contribute to the unique key
    _unique_fields: ClassVar[tuple[str, ...]] = ()

    metadata_type: str  # placeholder; subclasses MUST narrow to Literal["..."]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Allow intermediate abstract classes by opting out:
        if getattr(cls, "_typed_abstract", False):
            return
        ann = cls.__annotations__.get("metadata_type")
        if ann is None:
            raise TypeError(
                f"{cls.__name__} must annotate `metadata_type` as Literal['<tag>']"
            )
        if get_origin(ann) is not Literal:
            raise TypeError(
                f"{cls.__name__}.type must be Literal['<tag>'], got {ann!r}"
            )
        args = get_args(ann)
        if not (len(args) == 1 and isinstance(args[0], str)):
            raise TypeError(
                f"{cls.__name__}.type must be Literal with exactly one str tag"
            )

    @classmethod
    def parse_flat_db(cls, obj: dict[str, Any]) -> Self:
        """Build an instance from a flat DB row. Subclasses must override."""
        raise NotImplementedError()

    @computed_field
    @property
    def unique_key(self) -> str:
        """Generate a unique key by joining the values of fields specified in _unique_fields.

        Returns:
            A string representation of the unique key, with field values joined by colons.

        Raises:
            AttributeError: If _unique_fields is not defined in the subclass or if any
                          specified field doesn't exist on the instance.
        """
        if not self._unique_fields:
            raise AttributeError(
                f"{self.__class__.__name__} must define _unique_fields class variable"
            )

        return ":".join(str(getattr(self, field)) for field in self._unique_fields)
