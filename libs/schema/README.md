# PEG Scanner - Schema

This directory contains the data schemas, defined using Protocol Buffers (Protobuf). These schemas act as the Single Source of Truth (SSOT) for the data structures shared between the different components of the application (frontend, backend, data pipelines).

## Purpose

Using a centralized schema definition ensures data consistency and type safety across the entire system. It allows for the generation of data access classes in multiple languages (Python for the backend, and potentially TypeScript/JavaScript for the frontend).

## Schema Files

| File | Description |
| --- | --- |
| `stock.proto` | Core stock data structures (`Stock`, K-line data, valuation/indicator messages). |
| `ping.proto` | `PingResponse` payload for infra health checks. |
| `single_stock_page.proto` | API contract for the single-stock view (`SingleStockPageRequest/Response`, news items). |
