# PEG Scanner - Backend

This directory contains the Python backend application, responsible for data fetching, processing, and providing API services for the frontend.

## Structure

*   `src/`: Contains the main application logic, including data fetching scripts and API definitions.
*   `project.json`: Nx project configuration for the backend application.

## Getting Started

To run the backend application (currently a placeholder):

```bash
nx serve backend
```

This will execute `backend/src/main.py`.

## Key Responsibilities

*   **Data Acquisition:** Fetching raw stock market data from various sources (e.g., K-lines, financial statements, news).
*   **Data Processing:** Cleaning, transforming, and enriching raw data.
*   **Factor Calculation:** Implementing algorithms for calculating financial factors (e.g., PEG, PS, PE).
*   **API Services:** Exposing data and functionality to the frontend via well-defined APIs.
*   **Machine Learning/AI Integration:** Future integration with ML models for quantitative analysis and strategy generation.
