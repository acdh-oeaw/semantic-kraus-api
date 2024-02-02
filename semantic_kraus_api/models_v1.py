from tkinter import SE
import typing

from pydantic import Field, HttpUrl, NonNegativeInt
from rdf_fastapi_utils.models import FieldConfigurationRDF, RDFUtilsModelBaseClass
from fastapi_versioning import version, versioned_api_route
from fastapi import APIRouter, Depends, HTTPException

graph_mapping = {
    "https://sk.acdh.oeaw.ac.at/project/dritte-walpurgisnacht": "Dritte Walpurgisnacht",
    "https://sk.acdh.oeaw.ac.at/project/legal-kraus": "Legal Kraus Project",
    "https://sk.acdh.oeaw.ac.at/project/fackel": "Die Fackel online",
}


def pp_source_professional_occupation(field, item, data) -> dict:
    print("test")
    return item


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

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        super().__init__(**data)


class SameAs(SemanticKrausBackendBaseModel):
    """Used to provide source information"""

    id: HttpUrl = Field(..., rdfconfig=FieldConfigurationRDF(path="sameAs", anchor=True))
    object_label: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="objectLabel"))
    graph: HttpUrl | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graph"))
    graph_label: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graphLabel"))

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        if "graph" in data:
            data["graphLabel"] = graph_mapping.get(data["graph"], data["graph"])
        super().__init__(**data)


class ProfessionalOccupation(SemanticKrausBackendBaseModel):
    """Used to provide professional occupation information"""

    id: HttpUrl = Field(..., rdfconfig=FieldConfigurationRDF(path="occ", anchor=True))
    label: InternationalizedLabel = Field(
        ..., rdfconfig=FieldConfigurationRDF(path="occupation", default_dict_key="default")
    )
    time: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="time"))
    employer: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="employer"))


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
    graph: HttpUrl | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graph_subject"))
    graph_label: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graph_subjectLabel"))
    SameAs: typing.List[SameAs] | None

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        if "graph_subject" in data:
            data["graph_subjectLabel"] = graph_mapping.get(data["graph_subject"], None)
        super().__init__(**data)


class PersonName(SemanticKrausBackendBaseModel):
    id: str = Field(..., rdfconfig=FieldConfigurationRDF(path="appellation", anchor=True))
    label: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="name"))
    type: list[str] | None = Field(None, rdfconfig=FieldConfigurationRDF(path="typeLabel"))

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        if type(data["typeLabel"]) == str:
            data["typeLabel"] = [data["typeLabel"]]
        super().__init__(**data)


class Person(SemanticKrausBackendBaseModel):
    id: str = Field(
        ...,
        rdfconfig=FieldConfigurationRDF(path="person", anchor=True),
    )
    label: list[PersonName] | None
    professions: typing.List[ProfessionalOccupation] | None
    graph: HttpUrl | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graph_subject"))
    graph_label: str | None = Field(None, rdfconfig=FieldConfigurationRDF(path="graph_subjectLabel"))
    SameAs: typing.List[SameAs] | None

    def __init__(__pydantic_self__, **data: typing.Any) -> None:
        if "graph_subject" in data:
            data["graph_subjectLabel"] = graph_mapping.get(data["graph_subject"], None)
        super().__init__(**data)


class PaginatedResponseBase(SemanticKrausBackendBaseModel):
    count: NonNegativeInt = 0
    page: NonNegativeInt = 0
    pages: NonNegativeInt = 0


class PaginatedResponseSubjects(PaginatedResponseBase):
    results: typing.List[Entity] = Field([], rdfconfig=FieldConfigurationRDF(path="results"))

    class Config(PaginatedResponseBase.Config):
        sort_key = {"original key": "subject", "object list": "results"}
