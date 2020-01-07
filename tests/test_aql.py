import pytest
import responses

from pyartifactory import ArtifactoryAql
from pyartifactory.exception import AqlException
from pyartifactory.models import AuthModel, Aql

URL = "http://localhost:8080/artifactory"
AUTH = ("user", "password_or_apiKey")
AQL_RESPONSE = {
    "results": [
        {
            "repo": "libs-release-local",
            "path": "org/jfrog/artifactory",
            "name": "artifactory.war",
            "type": "item type",
            "size": "75500000",
            "created": "2015-01-01T10:10;10",
            "created_by": "Jfrog",
            "modified": "2015-01-01T10:10;10",
            "modified_by": "Jfrog",
            "updated": "2015-01-01T10:10;10",
        }
    ],
    "range": {"start_pos": 0, "end_pos": 1, "total": 1},
}


@responses.activate
def test_aql_success():
    responses.add(
        responses.POST, f"{URL}/api/search/aql", json=AQL_RESPONSE, status=200
    )

    artifactory_aql = ArtifactoryAql(AuthModel(url=URL, auth=AUTH))
    aql_obj = Aql(**{"find": {"repo": {"$eq": "libs-release-local"}}})
    result = artifactory_aql.query(aql_obj)
    assert result == AQL_RESPONSE["results"]


@responses.activate
def test_aql_fail_baq_query():
    responses.add(
        responses.POST, f"{URL}/api/search/aql", json=AQL_RESPONSE, status=400
    )

    artifactory_aql = ArtifactoryAql(AuthModel(url=URL, auth=AUTH))
    aql_obj = Aql(
        **{"include": ["artifact", "artifact.module", "artifact.module.build"]}
    )

    with pytest.raises(AqlException):
        artifactory_aql.query(aql_obj)
