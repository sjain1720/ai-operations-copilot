# AI Operations Copilot

AI-powered backend service for helping operations teams answer customer and operational questions using reliable order data.

## Overview

The service accepts a natural-language operational question, retrieves the required information from PostgreSQL through controlled backend tools, and returns a concise answer grounded in that data.

Example questions include:

- What is the payment status for order `4521`?
- The customer paid for order `1289`, but delivery is not scheduled. What is going on?
- Give me a complete status summary for order `2231`.

The LLM is used for query understanding and response composition. It does not receive direct database access and cannot execute arbitrary SQL.

## Initial Scope

The first version assumes the service is used by trusted company administrators in an internal environment.

Authentication and authorization are intentionally out of scope for the initial implementation. They may be added later without changing the core operational services or database access boundaries.

Automated testing is also deferred for the current development phase. The application should still be structured with separate API, service, repository, and AI components so focused tests can be added later.

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- An LLM provider with tool/function-calling support

## Planned Features

- Natural-language copilot query endpoint
- Controlled tools for retrieving order, payment, delivery, and customer information
- Full order-status summaries
- Explicit handling for missing orders and missing operational records
- Reproducible PostgreSQL seed data for realistic operational scenarios
- Environment-based configuration for database credentials and LLM API keys

## Architecture

The planned request flow is:

```text
FastAPI route
    -> Copilot service
        -> LLM client and tool orchestration
            -> Controlled operational tools
                -> Application services
                    -> Repositories
                        -> SQLAlchemy
                            -> PostgreSQL
```

The LLM can request only predefined tools, such as:

- Get order details
- Get payment status
- Get delivery status
- Get complete order status

Database queries remain inside the backend repository and service layers.

## Planned API

### `POST /api/v1/copilot/query`

Accepts a natural-language question.

Example request:

```json
{
  "query": "Customer says they paid for order #1289 but delivery is not scheduled. What is going on?"
}
```

The response will contain the generated operational answer and may include structured metadata such as the relevant order number and the tools used.

### `GET /health`

Returns the service health status for local development and deployment checks.

Additional read-only operational endpoints may be added where they improve observability or demonstrate the underlying services.

## Data Model

The planned database contains the following core entities:

- **Customers**: customer identity and contact information.
- **Orders**: public order number, customer relationship, amount, and order status.
- **Payments**: payment status, amount, transaction reference, and failure details.
- **Deliveries**: delivery status, schedule, tracking information, and delivery timestamps.

The schema will enforce relationships and uniqueness for public order numbers. Monetary values will use fixed precision, and timestamps will be stored consistently.

## Seed Scenarios

The reproducible seed data will include examples of:

- Successful payment with scheduled delivery
- Successful payment with delivery not scheduled
- Pending payment
- Failed payment
- Delivery in progress
- Delivered order
- Cancelled order
- Operationally inconsistent records that should be reported clearly

Stable order numbers will make the example queries easy to demonstrate.

## Configuration

Secrets must be supplied through environment variables or a local environment file that is excluded from version control. Database credentials and LLM API keys must never be hardcoded or committed.

The exact variable names and local setup commands will be added when the implementation and provider are selected.

## Local Development

Implementation and setup instructions will be completed alongside the application foundation. The expected local prerequisites are:

- Python 3.x
- PostgreSQL
- An API key for the selected LLM provider

The final setup will cover dependency installation, database creation, migrations, seed data, starting FastAPI, and example requests.

## Error Handling

The API should return explicit errors for:

- Invalid or empty queries
- Unknown orders
- Missing payment or delivery information
- Database failures
- Invalid tool requests
- LLM provider failures or timeouts

The service must not present an invented answer when required operational data cannot be retrieved.

## Testing Status

Automated tests are planned but intentionally deferred at this stage. The future test suite should cover core business logic, API validation and errors, repository behavior, tool orchestration, and LLM interactions using mocks or fakes.

## Project Status

This repository currently contains the assignment requirements and architecture documentation. Application implementation will proceed incrementally through project setup, database models, seed data, backend services, AI tools, LLM integration, testing, and final documentation review.
