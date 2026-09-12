# AI Operations Copilot Design

## 1. Purpose

AI Operations Copilot is a backend service that helps an operations team answer customer and operational questions about orders.

A user submits a natural-language question. The system identifies the operational information needed, retrieves it from PostgreSQL through controlled backend tools, and generates a concise response grounded in the retrieved records.

The design is intentionally small enough for a five-day backend assignment while preserving clear boundaries for future changes.

## 2. Scope and Assumptions

### Included in the initial version

- Natural-language operational queries
- Order, customer, payment, and delivery data
- PostgreSQL persistence through SQLAlchemy
- FastAPI HTTP API
- LLM integration with tool/function calling
- Controlled backend tools for operational lookups
- Reproducible seed data
- Explicit error handling

### Intentionally deferred

- Authentication
- Authorization and role management
- Multi-turn conversation state
- Write operations such as changing payment or delivery status
- Automated tests during the current implementation phase
- Advanced analytics, reporting, and event processing

The initial service assumes trusted company administrators using an internal application. Authentication and authorization can be added later at the API boundary without allowing the LLM to bypass backend controls.

Testing is deferred for now, but the architecture keeps dependencies separated so unit, API, integration, and AI-orchestration tests can be introduced later.

## 3. Design Principles

- The LLM never accesses PostgreSQL directly.
- The LLM can call only explicitly defined backend tools.
- Database access is isolated behind repositories or application services.
- Deterministic backend logic owns data retrieval and validation.
- Responses must be based on retrieved operational data.
- Missing or contradictory data is reported rather than silently inferred.
- Secrets are provided through environment configuration, never source code.
- The implementation should favor simple, readable components over unnecessary infrastructure.

## 4. High-Level Architecture

```text
Client
  |
  v
FastAPI API layer
  |
  v
Copilot application service
  |
  +--> LLM client
  |       |
  |       +--> fixed tool definitions
  |
  +--> tool dispatcher
          |
          v
    Operational services
          |
          v
     Repositories
          |
          v
    SQLAlchemy session
          |
          v
      PostgreSQL
```

### API layer

Responsible for HTTP concerns:

- Parse and validate request bodies with Pydantic.
- Invoke the copilot service.
- Convert known application failures into appropriate HTTP responses.
- Avoid embedding database queries or LLM orchestration in route handlers.

### Copilot service

Responsible for the application workflow:

1. Accept the validated user query.
2. Send the query and allowed tool definitions to the LLM.
3. Validate requested tool names and arguments.
4. Execute tools through backend services.
5. Return tool results to the LLM.
6. Produce the final grounded answer.
7. Stop and report an explicit error when required data or an external dependency is unavailable.

A maximum number of tool-call rounds should be enforced to prevent loops.

### Operational services

Contain deterministic use cases such as retrieving a complete order status or identifying a payment and delivery mismatch. These services should not depend on the LLM.

### Repositories

Contain SQLAlchemy queries and persistence concerns. Repositories should return structured domain data rather than allowing the LLM or API layer to construct SQL.

### AI integration

The AI layer should isolate provider-specific request and response formats behind a small client interface. Tool schemas should be explicit and narrow. Provider credentials, model selection, timeouts, and other settings should come from configuration.

## 5. Request Flow

For a query such as "The customer paid for order 1289, but delivery is not scheduled":

1. FastAPI validates the query payload.
2. The copilot service sends the query with the allowed tool definitions.
3. The LLM requests payment and delivery information for order `1289`.
4. The tool dispatcher validates the order number.
5. Backend services retrieve the records through repositories.
6. Structured tool results are returned to the LLM.
7. The LLM produces a concise explanation based only on those results.
8. FastAPI returns the answer to the caller.

The backend remains the authority for operational facts. The LLM interprets and explains those facts.

## 6. Controlled Tools

The initial tool set should remain small:

### `get_order_details`

Returns the order and customer information for a public order number.

### `get_payment_status`

Returns payment status, amount, transaction reference, timestamps, and relevant failure information.

### `get_delivery_status`

Returns delivery status, schedule, tracking reference, and delivery timestamps.

### `get_full_order_status`

Returns a structured summary of the order, customer, payment, and delivery records for summary queries.

Tool inputs should use validated public order numbers. Unknown tools, malformed arguments, arbitrary SQL, and unsupported operations must be rejected.

## 7. API Design

### Primary endpoint

`POST /api/v1/copilot/query`

Request:

```json
{
  "query": "What is the payment status for order #4521?"
}
```

The response should include a natural-language answer and may include structured context such as the identified order number and relevant information categories.

### Health endpoint

`GET /health`

Provides a lightweight service health response. It should not expose secrets or internal connection details.

### Optional read-only endpoints

The following may be added to demonstrate and inspect deterministic backend behavior:

- `GET /api/v1/orders/{order_number}`
- `GET /api/v1/orders/{order_number}/payment`
- `GET /api/v1/orders/{order_number}/delivery`
- `GET /api/v1/orders/{order_number}/status`

These endpoints should reuse application services rather than duplicate repository logic.

## 8. Data Model

### Customer

Stores customer identity and contact details. A customer can have multiple orders.

### Order

Stores the public order number, customer reference, amount, currency, lifecycle status, and timestamps. The public order number must be unique and indexed.

### Payment

Stores the payment relationship to an order, status, amount, method, provider transaction reference, timestamps, and failure or refund details.

### Delivery

Stores the delivery relationship to an order, status, scheduled time, tracking reference, actual delivery time, and failure or cancellation details.

Foreign keys and constraints should preserve referential integrity. The initial design can model one current payment and one current delivery per order, while allowing the records to be absent when operational information is missing. If payment history or split payments become requirements, those can be introduced later.

## 9. Status and Consistency Rules

The system should represent facts separately from inferred conclusions. Examples:

- A successful payment with `not_scheduled` delivery should be reported as a delivery scheduling gap.
- A pending or failed payment should not be described as successful.
- A cancelled order should be identified even if related records exist.
- Missing payment or delivery records should be reported explicitly.
- Contradictory records should be surfaced as inconsistencies rather than resolved by the LLM.

These rules belong in deterministic backend services where possible.

## 10. Database and Seed Data

PostgreSQL is the system of record. SQLAlchemy manages connections and model access. Schema migrations should be used so database changes are reproducible.

The seed process should be repeatable and include stable examples for:

- Successful payment with scheduled delivery
- Successful payment with delivery not scheduled
- Pending payment
- Failed payment
- Delivery in progress
- Delivered order
- Cancelled order
- Missing or inconsistent operational information

Monetary values should use fixed precision. Foreign keys, unique constraints, indexes, and timezone-aware timestamps should be defined deliberately.

## 11. Error Handling

Expected application errors should be represented explicitly and mapped at the API boundary:

- Invalid request: `400` or `422`
- Unknown order: `404`
- Missing required operational data: a clear domain error or structured partial result
- Database failure: `500` or an appropriate service-unavailable response
- LLM timeout/provider failure: `502` or `503`
- Invalid tool request: controlled application error, never arbitrary execution

Error responses should be useful to the caller without exposing credentials, SQL, provider internals, or sensitive implementation details.

## 12. Security Boundaries

Authentication and authorization are not part of the initial release. The deployment assumption is a trusted company-admin-only internal environment.

Even under that assumption:

- Database credentials must come from environment configuration.
- LLM API keys must never be hardcoded.
- User input must not become executable SQL.
- The tool dispatcher must allowlist tool names.
- Tool arguments must be validated.
- Provider and database errors must not leak secrets.

When authentication is added, it should be implemented at the API boundary and supplemented with authorization checks for operational actions.

## 13. Reliability and Scalability Considerations

The initial version can remain a synchronous request-response service. It should still define sensible timeouts for database and LLM calls, use SQLAlchemy connection pooling, and limit LLM tool-call iterations.

Future concerns include:

- LLM latency and provider rate limits
- Database connection pool exhaustion
- Repeated retrieval of the same order summaries
- Response and prompt size limits
- Auditing tool calls and answers
- Horizontal scaling of stateless API instances
- Provider fallback or model changes

Caching and asynchronous workflows are not required for the assignment unless measured needs justify them.

## 14. Testing Plan

Automated testing is intentionally deferred from the current phase. The planned test structure is:

- Unit tests for validation, status rules, and aggregation logic
- Repository tests against a test PostgreSQL database
- API tests for successful requests and error responses
- Tool-dispatch tests for allowlisting and argument validation
- Mocked LLM tests for tool-call orchestration and grounded responses
- One integration flow from API request through tools to final response

The separation between routes, services, repositories, and the AI client is intended to make these tests straightforward to add later.

## 15. Future Extensions

Potential later additions include:

- Authentication and role-based authorization
- Payment and delivery history
- Status-change audit logs
- More operational tools
- Conversation history
- Metrics and tracing
- LLM provider fallback
- Admin dashboards

These should be introduced only when they support a demonstrated requirement.
