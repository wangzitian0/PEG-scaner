"""
GraphQL Resolvers - Strawberry type definitions

Exports the merged Query type for use in main.py.
"""

import strawberry

from .ping import PingQuery
from .stock import StockQuery


@strawberry.type
class Query(PingQuery, StockQuery):
    """Root Query type - aggregates all domain queries."""
    pass


__all__ = ["Query"]

