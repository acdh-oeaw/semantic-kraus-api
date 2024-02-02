import dataclasses

from fastapi import Query
from pydantic import PositiveInt
from enum import Enum
import typing


class EntityTypes(str, Enum):
    person = "crm:E21_Person"
    place = "crm:E53_Place"
    expression = "frbroo:F22_Self-Contained_Expression"
    publication = "frbroo:F24_Publication_Expression"
    information_object = "crm:E73_Information_Object"


@dataclasses.dataclass(kw_only=True)
class QueryBase:
    page: PositiveInt = Query(default=1, gte=1)
    limit: int = Query(default=50, le=1000, gte=1)
    _offset: int = Query(default=0, include_in_schema=False)

    def __post_init__(self):
        if hasattr(self, "page"):
            self._offset = (self.page - 1) * self.limit


@dataclasses.dataclass(kw_only=True)
class Search(QueryBase):
    q: str = Query(default=None, max_length=200, description="Searches across labels of all subjects")
    subject_types: typing.List[EntityTypes] = Query(
        default=[
            EntityTypes.person,
            EntityTypes.place,
            EntityTypes.expression,
            EntityTypes.publication,
            EntityTypes.information_object,
        ],
        description="Filter by entity type. Can be multiple",
    )


@dataclasses.dataclass(kw_only=True)
class GetEntity:
    id: str = Query(..., description="The id of the entity to retrieve")
