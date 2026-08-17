from collections.abc import Callable
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from chart_engine.domain.models import BirthData, NatalChart
from chart_engine.services.chart_service import ChartEngine

from chart_engine.services.context_builder import (
    build_chart_summary,
    build_rag_search_queries,
    build_llm_system_prompt,
)





class ChatRequest(BaseModel):
    chart_id: UUID
    user_query: str

class ChatResponse(BaseModel):
    prompt_generated: str
    rag_queries_used: list[str]

class ChartStore:
    """Temporary in-memory chart store, to be replaced by PostgreSQL in phase 9."""

    def __init__(self) -> None:
        self._charts: dict[UUID, NatalChart] = {}

    def save(self, chart: NatalChart) -> UUID:
        chart_id = uuid4()
        self._charts[chart_id] = chart
        return chart_id

    def get(self, chart_id: UUID) -> NatalChart | None:
        return self._charts.get(chart_id)


class ChartResponse(BaseModel):
    id: UUID
    chart: NatalChart


def create_app(
    engine_factory: Callable[[], ChartEngine] = ChartEngine,
    chart_store: ChartStore | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Chart Astrology Engine API",
        version="0.1.0",
        description="Deterministic natal-chart calculations powered by Swiss Ephemeris.",
    )
    store = chart_store or ChartStore()

    @app.post(
        "/charts",
        response_model=ChartResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["charts"],
    )
    def create_chart(birth_data: BirthData) -> ChartResponse:
        chart = engine_factory().calculate(birth_data)
        chart_id = store.save(chart)
        return ChartResponse(id=chart_id, chart=chart)

    @app.get("/charts/{chart_id}", response_model=ChartResponse, tags=["charts"])
    def get_chart(chart_id: UUID) -> ChartResponse:
        chart = store.get(chart_id)
        if chart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
        return ChartResponse(id=chart_id, chart=chart)
    
    
    
    
    
    @app.post("/chat", response_model=ChatResponse, tags=["chat"])
    def prepare_chat_context(request: ChatRequest) -> ChatResponse:
        chart = store.get(request.chart_id)
        if chart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
    
        chart_summary = build_chart_summary(chart)
        rag_queries = build_rag_search_queries(chart)
    
        rag_context_mock = "Aquí se inyectarán los fragments de texto recuperados de tu base de datos vectorial (Pinecone/pgvector) usando las 'rag_queries'."
    
        final_prompt = build_llm_system_prompt(
            user_query=request.user_query,
            chart_summary=chart_summary,
            rag_context=rag_context_mock
        )
        
        return ChatResponse(
        prompt_generated=final_prompt,
        rag_queries_used=rag_queries
    )


    return app


app = create_app()





