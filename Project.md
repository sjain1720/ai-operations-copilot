# AI Operations Copilot

## Assignment

Build an AI-powered backend service that helps an operations team answer customer and operational queries.

Example queries:

* "What's the payment status for order #4521?"
* "Customer says they've paid for order #1289 but delivery isn't scheduled — what's going on?"
* "Give me a full status summary for order #2231."

## Goal

Build a backend service where an operations user can submit a natural-language query and receive an accurate, useful answer based on operational data stored in PostgreSQL.

The AI should be able to identify what information is needed, use controlled backend tools to retrieve that information, and generate a clear response.

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* LLM with tool/function calling

## Core Requirements

### 1. Operational Data

The system should contain realistic data required to answer operational queries, including relevant entities such as:

* Customers
* Orders
* Payments
* Deliveries

The exact schema should be designed based on the operational use cases.

### 2. AI Copilot

Provide an API through which an operations user can submit a natural-language question.

The copilot should:

1. Understand the user's query.
2. Determine which operational information is required.
3. Call appropriate backend tools/functions.
4. Retrieve the required data from PostgreSQL.
5. Generate a concise, accurate answer.

The LLM must not directly access the database.

### 3. Backend Tools

Expose controlled tools/functions for retrieving operational information.

Potential tools include:

* Get order details
* Get payment status
* Get delivery status
* Get customer/order information
* Get complete order status

Only implement tools that are actually required by the final design.

### 4. API

Use FastAPI to expose the backend APIs.

The primary AI endpoint should accept a natural-language query and return the generated answer.

Additional operational APIs may be provided where they improve the design or are required by the implementation.

### 5. Database

Use PostgreSQL with SQLAlchemy.

The database should maintain consistent relationships between customers, orders, payments, and deliveries.

### 6. Seed Data

Create realistic seed data representing different operational scenarios.

The repository must contain a reproducible seed script.

Seed data should include useful cases such as:

* Successful payment with scheduled delivery
* Successful payment with delivery not scheduled
* Pending or failed payment
* Delivery in progress
* Delivered order
* Cancelled order
* Other realistic operational inconsistencies

The data should make the example AI queries demonstrable.

### 7. Error Handling

Handle cases such as:

* Order not found
* Invalid input
* Missing operational information
* Database failures
* LLM/tool failures

The API should return appropriate errors rather than silently producing unreliable answers.

### 8. Testing

Include meaningful automated tests covering important backend behaviour, error cases, and AI/tool interactions where practical.

## Engineering Constraints

* Keep the architecture simple and appropriate for a 5-day backend assignment.
* Avoid unnecessary technologies and infrastructure.
* Do not expose database credentials or LLM API keys.
* Do not allow the LLM to execute arbitrary database queries.
* AI responses must be grounded in retrieved operational data.
* Prefer deterministic backend logic wherever possible.
* Use clear separation between API, business logic, database access, and AI components.

## Submission Requirements

The public GitHub repository must contain:

* Working source code
* `README.md` with setup instructions and API documentation
* `DESIGN.md` describing the system design
* Seed data/script
* Tests

A 3–5 minute walkthrough video is optional.

## Current Development Approach

Build incrementally:

1. Project foundation
2. Database models and migrations
3. Seed data
4. Core backend services/APIs
5. AI tools
6. LLM integration
7. Tests
8. `DESIGN.md`
9. `README.md`
10. Final review against assignment requirements

## Open Decisions

These should be decided during implementation rather than assumed prematurely:

* Exact database schema
* API contracts
* LLM provider
* Tool/function definitions
* Prompt structure
* Error-handling strategy
* Testing strategy
* Deployment/local development approach
