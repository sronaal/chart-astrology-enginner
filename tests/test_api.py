from fastapi.testclient import TestClient

from chart_engine.api.app import ChartStore, create_app


class FakeChartEngine:
    def calculate(self, birth_data):
        from chart_engine import ChartEngine

        return ChartEngine().calculate(birth_data)


def test_create_chart_returns_natal_chart_json() -> None:
    client = TestClient(create_app(engine_factory=FakeChartEngine, chart_store=ChartStore()))

    response = client.post(
        "/charts",
        json={
            "date": "2001-09-02",
            "time": "11:02:00",
            "latitude": 4.7110,
            "longitude": -74.0721,
            "timezone": "America/Bogota",
        },
    )

    assert response.status_code == 201
    assert response.json().keys() == {"id", "chart"}
    assert response.json()["chart"].keys() == {
        "birth_data", "planets", "houses", "ascendant", "midheaven", "aspects"
    }
    get_response = client.get(f"/charts/{response.json()['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == response.json()


def test_openapi_documents_chart_routes() -> None:
    client = TestClient(create_app(engine_factory=FakeChartEngine, chart_store=ChartStore()))

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert set(response.json()["paths"]) == {"/charts", "/charts/{chart_id}"}


def test_get_unknown_chart_returns_not_found() -> None:
    client = TestClient(create_app(engine_factory=FakeChartEngine, chart_store=ChartStore()))

    response = client.get("/charts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Chart not found"}
