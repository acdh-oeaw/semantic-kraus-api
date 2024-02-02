import base64
from dataclasses import asdict
import datetime
import os
from urllib.parse import quote, unquote
from SPARQLWrapper import SPARQLWrapper, JSON
from jinja2 import Environment, FileSystemLoader

from semantic_kraus_api.query_parameters import QueryBase, Search


jinja_env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "sparql")), autoescape=False)
sparql_endpoint = os.environ.get("SPARQL_ENDPOINT")
sparql = SPARQLWrapper(sparql_endpoint)
sparql.setMethod("POST")
sparql.setReturnFormat(JSON)
if not sparql_endpoint.startswith("http://127.0.0.1:8080"):
    sparql.setHTTPAuth("BASIC")
    sparql.setCredentials(user=os.environ.get("SPARQL_USER"), passwd=os.environ.get("SPARQL_PASSWORD"))


def get_query_from_triplestore(search: Search | QueryBase, sparql_template: str):
    """creates the query from the template and the search parameters and returns the json
       from the triplestore. This is v2 and doesnt need the proto config anymore

    Args:
        search (Search): _description_
        sparql_template (str): _description_

    Returns:
        _type_: _description_
    """
    if type(search).__module__ == "semantic_kraus_api.query_parameters":
        search = asdict(search)
    query_template = jinja_env.get_template(sparql_template).render(**search)
    sparql.setQuery(query_template)
    res = sparql.queryAndConvert()
    return res["results"]["bindings"]


def flatten_rdf_data(data: dict) -> list:
    """Flatten the RDF data to a list of dicts.

    Args:
        data (dict): The RDF data

    Returns:
        list: A list of dicts
    """
    flattened_data = []
    for ent in data:
        d_res = {}
        for k, v in ent.items():
            if isinstance(v, dict):
                if "value" in v:
                    if "datatype" in v:
                        if v["datatype"] == "http://www.w3.org/2001/XMLSchema#dateTime":
                            try:
                                v["value"] = datetime.datetime.fromisoformat(str(v["value"]).replace("Z", "+00:00"))
                            except ValueError:
                                continue  # FIXME: this is removing dates before 0, should be fixed
                        elif v["datatype"] == "http://www.w3.org/2001/XMLSchema#integer":
                            v["value"] = int(v["value"])
                        elif v["datatype"] == "http://www.w3.org/2001/XMLSchema#boolean":
                            v["value"] = bool(v["value"])
                        elif v["datatype"] == "http://www.w3.org/2001/XMLSchema#float":
                            v["value"] = float(v["value"])
                    d_res[k] = v["value"]
                else:
                    d_res[k] = v
            else:
                d_res[k] = v
        flattened_data.append(d_res)
    return flattened_data


def toggle_urls_encoding(url):
    """Toggles the encoding of the url.

    Args:
        url (str): The url

    Returns:
        str: The encoded/decoded url
    """
    if "/" in url:
        return base64.urlsafe_b64encode(url.encode("utf-8")).decode("utf-8")
    else:
        return base64.urlsafe_b64decode(url.encode("utf-8")).decode("utf-8")


def calculate_date_range(start, end, intv):
    diff = (end - start) / intv
    for i in range(intv):
        yield (start + diff * i)
    yield end


def create_bins_from_range(start, end, intv):
    bins = list(calculate_date_range(start, end, intv))
    bins_fin = []
    for i in range(0, intv):
        bins_fin.append(
            {
                "values": (bins[i], bins[i + 1]),
                "label": f"{bins[i].strftime('%Y')} - {bins[i+1].strftime('%Y')}",
                "count": 0,
            }
        )
    return bins_fin
