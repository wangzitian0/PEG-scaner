"""
FastAPI + Strawberry GraphQL Entry Point

Usage:
    uvicorn apps.backend.main:app --reload
"""

from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from neo4j_repo import StockRepository, lifespan as neo4j_lifespan
from neo4j_repo.connection import get_settings

from .resolvers import Query
from .services.stock_service import StockService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize services."""
    settings = get_settings()
    
    # Initialize repository and service
    repo = StockRepository()
    service = StockService(repo)
    
    # Seed default data
    from .services.seed import get_seed_payloads
    repo.seed_if_needed(get_seed_payloads())
    
    # Store in app state for resolver access
    app.state.stock_service = service
    app.state.repo = repo
    
    async with neo4j_lifespan(app):
        yield


def create_app() -> FastAPI:
    """Create FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="PEG Scanner API",
        description="GraphQL API for stock analysis",
        version="0.2.0",
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # GraphQL schema
    schema = strawberry.Schema(query=Query)
    
    # Context factory for resolvers
    async def get_context():
        return {
            "stock_service": app.state.stock_service,
            "repo": app.state.repo,
            "settings": settings,
        }
    
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql" if settings.debug else None,  # Playground only in dev
    )
    
    app.include_router(graphql_app, prefix="/graphql")
    
    @app.get("/")
    async def root():
        return {"status": "ok", "graphql": "/graphql"}
    
    return app


# Application instance
app = create_app()

