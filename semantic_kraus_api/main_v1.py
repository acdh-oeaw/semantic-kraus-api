import math
from fastapi import APIRouter, Depends, HTTPException
from fastapi_versioning import versioned_api_route

from .query_parameters import Search, GetEntity
from .models_v1 import PaginatedResponseSubjects, Person
from .utils import flatten_rdf_data, get_query_from_triplestore, toggle_urls_encoding


router = APIRouter(route_class=versioned_api_route(1, 0))


@router.get(
    "/api/entities/search",
    response_model=PaginatedResponseSubjects,
    response_model_exclude_none=True,
    tags=["Entities endpoints"],
    description="Endpoint that allows to query and retrieve entities including \
    the node history. Depending on the objects found the return object is \
        different.",
)
async def query_entities(search: Search = Depends()):
    res = get_query_from_triplestore(search, "entities_search_v1.sparql")
    res = flatten_rdf_data(res)
    # pages = math.ceil(len(res) / search.limit) if len(res) > 0 else 0
    # count = len(res) if len(res) > 0 else 0
    pages = math.ceil(int(res[0]["count"]) / search.limit) if len(res) > 0 else 0
    count = int(res[0]["count"]) if len(res) > 0 else 0
    return {"page": search.page, "count": count, "pages": pages, "results": res}


@router.get(
    "/api/entities/person",
    response_model=Person,
    response_model_exclude_none=True,
    tags=["Entities endpoints"],
    description="Endpoint that allows to retrive a person by id.",
)
async def retrieve_person(query: GetEntity = Depends()):
    query_dict = asdict(query)
    res = get_query_from_triplestore_v2(query_dict, "get_person_v1.sparql")
    # res = FakeList(**{"results": flatten_rdf_data(res)})
    if len(res) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"_results": flatten_rdf_data(res)}
