# Project Plan for PEG Scanner

> **职责**：高层开发路线图（Phase 1-5 规划）
> 
> **与 project/README.md 的关系**：本文件是规划，`project/README.md` 是执行状态

This document outlines the high-level plan and phased approach for developing the PEG Scanner application. Each phase builds upon the previous one, focusing on core functionalities and gradually introducing more complex features.

## Phase 1: Foundation & Data Infrastructure

**Goal:** Establish the core monorepo structure, define essential data models using Protobuf, and set up basic data acquisition mechanisms.

**Key Deliverables:**
*   Initialized Nx workspace (completed, as per `agent.md` setup).
*   Defined core Protobuf schemas (`stock.proto` etc.) for `Stock`, `KLineData`, `CompanyInfo`, `Financials`, etc. (Next Step).
*   Basic Python module for data fetching (e.g., daily K-lines for initial symbols). (Implemented inside the Flask backend’s crawler helpers).
*   Initial data storage setup (e.g., local database for historical data).
*   Minimal API endpoint in the backend for serving raw stock data.

## Phase 2: Core Feature Development - Individual Stock Information

**Goal:** Implement the primary User Interface (UI) for individual stock information and its corresponding backend APIs.

**Key Deliverables:**
*   React Native application scaffolded within the Nx monorepo.
*   Basic UI component for displaying individual stock information (e.g., K-lines, trading volume).
*   Backend API endpoints for retrieving K-line data and essential company information.
*   Integration of frontend with backend to display fetched stock data.

## Phase 3: Factor Calculation & Management

**Goal:** Develop the functionality for calculating custom financial factors and create the data management interface.

**Key Deliverables:**
*   Python module for calculating custom factors (e.g., PEG, PS, PE, PB).
*   Backend APIs for triggering factor calculations and retrieving results.
*   React Native UI components for displaying calculated factors for a given stock.
*   Data management UI and backend for configuring data sources, monitoring data ingestion, and aggregation.

## Phase 4: AI-Powered Conversation & Strategy

**Goal:** Implement the conversational interface, enabling users to query stock information and create quantitative strategies through natural language.

**Key Deliverables:**
*   Integration with an LLM via Open-router for natural language processing.
*   Development of an AI agent capable of understanding user queries related to stock data and financial factors.
*   Framework for translating conversational input into executable quantitative stock selection strategies.
*   React Native UI for the conversational chat interface.

## Phase 5: Strategy Push & Refinement

**Goal:** Implement the execution, basic backtesting, and notification system for user-defined strategies.

**Key Deliverables:**
*   Mechanism for running user-created stock selection strategies.
*   Basic backtesting functionality to evaluate strategy performance against historical data.
*   Push notification system for alerting users about strategy triggers or selected stocks.
*   Continuous UI/UX refinement and performance optimization across the application.
