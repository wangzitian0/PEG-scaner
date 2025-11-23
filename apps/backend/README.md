# PEG Scanner - Django Backend

This directory contains the Django backend application, responsible for providing API services, managing data, and handling business logic for the PEG Scanner application.

## Structure

*   `.venv/`: Python virtual environment for isolated dependency management (created inside `apps/backend/`).
*   `requirements.txt`: Python package dependencies for the Django project.
*   `manage.py`: Django's command-line utility for administrative tasks.
*   `pegscanner_backend/`: The main Django project directory, containing settings, URL configurations, etc.
*   `project.json`: Nx project configuration for the Django backend.

## Getting Started

1.  **Install Dependencies:**
    ```bash
    npx nx install backend
    ```
    This command will create the virtual environment, install Django and other necessary packages.

2.  **Run Migrations:**
    ```bash
    npx nx migrate backend
    ```
    This will apply any database migrations.

3.  **Start the Development Server:**
    ```bash
    npx nx start backend
    ```
    The Django development server will start, typically accessible at `http://127.0.0.1:8000/`.

## Key Responsibilities

*   **API Services:** Exposing data and functionality to the frontend (React Native mobile application).
*   **Data Management:** Interacting with the database for storing and retrieving stock data, user profiles, and other application-specific information.
*   **Business Logic:** Implementing the core logic for quantitative stock selection, factor calculation, and strategy management.
*   **Admin Interface:** Leveraging Django's built-in administrative interface for easy data management.
*   **Proto Contracts:** The SSOT for all payloads lives in `libs/schema/*.proto`. Regenerate Python bindings via `npx nx run backend:generate-proto` whenever the schema changes.
*   **Crawler App + Neo4j:** The `crawler` Django app manages crawler jobs through the default admin UI and persists graph data to Neo4j. Configure `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` through environment variables. Run a job via `python manage.py run_crawler_job --symbol AAPL` to seed data.
*   **Single Stock Page API:** `/api/single-stock-page/?symbol=XYZ` serializes `pegscanner.single_stock_page.SingleStockPageResponse` (stock metadata, recent K-line, news). The view first fetches enriched data from Neo4j and falls back to the relational models when the graph is empty.
*   **Testing:** Run `npx nx run backend:test` (or `./apps/backend/.venv/bin/python3 apps/backend/manage.py test`) to execute the protobuf-based ping regression test and future suites.
