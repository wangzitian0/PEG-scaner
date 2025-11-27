# PEG Scanner - Schema

This directory contains the GraphQL schema (`schema.graphql`) as the Single Source of Truth (SSOT) for data structures shared between the frontend, backend, and regression utilities.

## Purpose

Using a centralized GraphQL schema ensures data consistency and type safety across the system. It drives the backend resolvers and the frontend/clients (Apollo/TanStack Query or fetch) without ad-hoc JSON contracts.

## Schema Files

| File | Description |
| --- | --- |
| `schema.graphql` | GraphQL types and queries for ping/health, PEG watchlist, and single stock page. |
