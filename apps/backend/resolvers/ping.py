"""
Ping Resolver - Health check / infrastructure connectivity.

Corresponds to: libs/schema/common/types.graphql
"""

import time

import strawberry
from strawberry.types import Info


@strawberry.type
class Ping:
    """Ping/health check response."""
    message: str
    agent: str
    timestamp_ms: float = strawberry.field(name="timestampMs")


@strawberry.type
class PingQuery:
    """Ping query resolver."""
    
    @strawberry.field
    def ping(self, info: Info) -> Ping:
        """Health check / infrastructure ping."""
        repo = info.context["repo"]
        settings = info.context["settings"]
        
        # Record tracking
        repo.record_tracking()
        
        return Ping(
            message="pong",
            agent=settings.agent_name,
            timestamp_ms=float(int(time.time() * 1000)),
        )

