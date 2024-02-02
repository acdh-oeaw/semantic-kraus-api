from tkinter import SE
import typing

from pydantic import Field, HttpUrl, NonNegativeInt
from rdf_fastapi_utils.models import FieldConfigurationRDF, RDFUtilsModelBaseClass
from fastapi_versioning import version, versioned_api_route
from fastapi import APIRouter, Depends, HTTPException


class SemanticKrausBackendBaseModel(RDFUtilsModelBaseClass):
    errors: typing.List[str] | None = None

    class Config:
        RDF_utils_catch_errors = True
        RDF_utils_error_field_name = "errors"
        RDF_utils_move_errors_to_top = True


class InternationalizedLabel(SemanticKrausBackendBaseModel):
    """Used to provide internationalized labels"""

    default: str
    en: typing.Optional[str]
    de: str | None = None
    fi: str | None = None
    si: str | None = None
    du: str | None = None

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        super().__init__(**data)


class Entity(SemanticKrausBackendBaseModel):
    id: str = Field(
        ...,
        rdfconfig=FieldConfigurationRDF(path="subject", anchor=True),
    )
    label: InternationalizedLabel | None = Field(
        None, rdfconfig=FieldConfigurationRDF(path="label", default_dict_key="default")
    )
    entity_class: HttpUrl = Field(..., rdfconfig=FieldConfigurationRDF(path="type"))
    entity_class_label: str = Field(..., rdfconfig=FieldConfigurationRDF(path="typeLabel"))


class PaginatedResponseBase(SemanticKrausBackendBaseModel):
    count: NonNegativeInt = 0
    page: NonNegativeInt = 0
    pages: NonNegativeInt = 0


class PaginatedResponseSubjects(PaginatedResponseBase):
    results: typing.List[Entity] = Field([], rdfconfig=FieldConfigurationRDF(path="results"))

    class Config(PaginatedResponseBase.Config):
        sort_key = {"original key": "subject", "object list": "results"}
