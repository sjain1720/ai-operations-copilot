# AI Operations Copilot Design

## 1. Purpose

AI Operations Copilot is a backend service that helps an operations team answer customer and operational questions about orders.

A user submits a natural-language question. The system identifies the operational information needed, retrieves it from PostgreSQL through controlled backend tools, and generates a concise response grounded in the retrieved records. The system supports persistent multi-turn conversations, allowing follow-up questions within the same operational context.

The design is intentionally small enough for a five-day backend assignment while preserving clear boundaries for future changes.

## 2. Scope and Assumptions

### Included in the current implementation

- Natural-language operational queries
- Order, customer, payment, and delivery data
- PostgreSQL persistence through SQLAlchemy
- FastAPI HTTP API
- LLM integration with tool/function calling
- Controlled backend tools for operational lookups
- Reproducible seed data
- Explicit error handling
- Persistent conversations in PostgreSQL
- Multi-turn conversation support
- Conversation/message history
- Cursor-based message pagination
- Recent-message context strategy for LLM

### Intentionally deferred

- Authentication
- Authorization and role management
- Write operations such as changing payment or delivery status
- Automated tests during the current implementation phase
- Advanced analytics, reporting, and event processing
- RAG, vector databases, Redis, or other advanced memory infrastructure

The service assumes trusted company administrators using an internal application. Authentication and authorization can be added later at the API boundary without allowing the LLM to bypass backend controls.

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
- Conversation history is persisted in PostgreSQL rather than using external memory systems.
- Only recent conversation history is sent to the LLM to keep context manageable.

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
  +--> Conversation service
  |       |
  |       +--> Conversation repository
  |       +--> Message repository
  |
  +--> LLM client (Gemini)
  |       |
  |       +--> fixed tool definitions
  |
  +--> Backend tool executor
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
- Invoke the copilot and conversation services.
- Convert known application failures into appropriate HTTP responses.
- Avoid embedding database queries or LLM orchestration in route handlers.

### Copilot service

Responsible for the AI workflow:

1. Accept the validated user query and optional conversation history.
2. Send the query and allowed tool definitions to the LLM.
3. Validate requested tool names and arguments.
4. Execute tools through backend services.
5. Return tool results to the LLM.
6. Produce the final grounded answer.
7. Stop and report an explicit error when required data or an external dependency is unavailable.

A maximum number of tool-call rounds is enforced (default: 4) to prevent loops.

### Conversation service

Responsible for conversation persistence and history management:

1. Create new conversations or retrieve existing ones by ID.
2. Persist user and assistant messages.
3. Retrieve recent message history for LLM context (latest 20 messages).
4. Support cursor-based pagination for older message retrieval.
5. Update conversation timestamps on message additions.

### Operational services

Contain deterministic use cases such as retrieving a complete order status or identifying a payment and delivery mismatch. These services do not depend on the LLM.

### Repositories

Contain SQLAlchemy queries and persistence concerns. Repositories return structured domain data rather than allowing the LLM or API layer to construct SQL.

### AI integration

The AI layer isolates provider-specific request and response formats behind a small client interface. Tool schemas are explicit and narrow. Provider credentials, model selection, timeouts, and other settings come from configuration. The current implementation uses Google Gemini.

## 5. Normal Copilot Request Flow

For a query without an existing conversation (new conversation):

1. FastAPI validates the query payload.
2. The conversation service creates a new conversation.
3. The conversation service persists the user message.
4. The copilot service sends the query with the allowed tool definitions to the LLM.
5. The LLM requests operational information (e.g., payment and delivery for order `1289`).
6. The backend tool executor validates tool names and arguments.
7. Backend services retrieve the records through repositories.
8. Structured tool results are returned to the LLM.
9. The LLM produces a concise explanation based only on those results.
10. The conversation service persists the assistant message.
11. FastAPI returns the answer and conversation ID to the caller.

## 6. Multi-Turn Request Flow

For a follow-up query with an existing conversation ID:

1. FastAPI validates the query payload and conversation ID.
2. The conversation service retrieves the existing conversation (404 if not found).
3. The conversation service loads the latest 20 messages for LLM context.
4. The conversation service persists the current user message.
5. The copilot service builds the LLM context from the message history.
6. The copilot service sends the context with the allowed tool definitions to the LLM.
7. The LLM may request operational information using backend tools.
8. The backend tool executor validates and executes tool requests.
9. Backend services retrieve records through repositories.
10. Tool results are returned to the LLM.
11. The LLM produces a concise explanation based on the context and tool results.
12. The conversation service persists the assistant message.
13. FastAPI returns the answer and conversation ID to the caller.

The backend remains the authority for operational facts. The LLM interprets and explains those facts.

## 7. Controlled Tools

The current tool set includes:

### `get_order`

Returns the order details for a public order number.

### `get_payment_status`

Returns payment status, amount, transaction reference, timestamps, and relevant failure information for an order.

### `get_delivery_status`

Returns delivery status, schedule, tracking reference, and delivery timestamps for an order.

### `get_order_summary`

Returns a structured summary of the order, customer, payment, and delivery records for summary queries.

Tool inputs use validated public order numbers. Unknown tools, malformed arguments, arbitrary SQL, and unsupported operations are rejected.

## 8. API Design

### Copilot endpoint

`POST /api/v1/copilot/query`

Accepts a natural-language query with an optional conversation ID.

Request:

```json
{
  "query": "What is the payment status for order 4521?",
  "conversation_id": 1
}
```

- `query` (required): The natural-language question
- `conversation_id` (optional): ID of an existing conversation to continue. If omitted, a new conversation is created.

Response:

```json
{
  "conversation_id": 1,
  "answer": "Payment for order 4521 was successful.",
  "tools_used": ["get_payment_status"],
  "metadata": {
    "tool_rounds": 1
  }
}
```

### Conversation endpoints

`POST /api/v1/conversations`

Creates a new conversation.

`GET /api/v1/conversations`

Lists recent conversations with cursor-based pagination.

`GET /api/v1/conversations/{conversation_id}`

Retrieves a specific conversation by ID.

`GET /api/v1/conversations/{conversation_id}/messages`

Retrieves messages from a conversation with cursor-based pagination.

### Operational endpoints

The following read-only endpoints are implemented to demonstrate deterministic backend behavior:

- `GET /api/v1/orders/{order_number}`
- `GET /api/v1/orders/{order_number}/payment`
- `GET /api/v1/orders/{order_number}/delivery`
- `GET /api/v1/orders/{order_number}/summary`

These endpoints reuse application services rather than duplicate repository logic.

### Health endpoint

`GET /health`

Provides a lightweight service health response. It does not expose secrets or internal connection details.

## 9. Data Model

### Customer

Stores customer identity and contact details. A customer can have multiple orders.

### Order

Stores the public order number, customer reference, amount, currency, lifecycle status, and timestamps. The public order number must be unique and indexed.

### Payment

Stores the payment relationship to an order, status, amount, method, provider transaction reference, timestamps, and failure or refund details.

### Delivery

Stores the delivery relationship to an order, status, scheduled time, tracking reference, actual delivery time, and failure or cancellation details.

### Conversation

Stores conversation metadata for multi-turn conversations:

- `id`: Primary key
- `title`: Optional title (max 200 characters)
- `created_at`: Timestamp when conversation was created
- `updated_at`: Timestamp when conversation was last updated (updated on each message addition)
- Index on `updated_at` for efficient recent-conversation listing

### Message

Stores user and assistant messages within a conversation:

- `id`: Primary key
- `conversation_id`: Foreign key to conversations with CASCADE delete
- `role`: Enum (`user` or `assistant`)
- `content`: Message text (non-empty, validated by check constraint)
- `created_at`: Timestamp when message was created
- Composite index on `(conversation_id, created_at, id)` for efficient pagination
- Check constraint ensuring content is not empty

Foreign keys and constraints preserve referential integrity. The design models one current payment and one current delivery per order, while allowing the records to be absent when operational information is missing. If payment history or split payments become requirements, those can be introduced later.

## 10. Status and Consistency Rules

The system represents facts separately from inferred conclusions. Examples:

- A successful payment with `not_scheduled` delivery should be reported as a delivery scheduling gap.
- A pending or failed payment should not be described as successful.
- A cancelled order should be identified even if related records exist.
- Missing payment or delivery records should be reported explicitly.
- Contradictory records should be surfaced as inconsistencies rather than resolved by the LLM.

These rules belong in deterministic backend services where possible.

## 11. Conversation History Strategy

### Full Persistence

The full conversation history is persisted in PostgreSQL through the Conversation and Message entities. This ensures:

- Complete audit trail of all user and assistant messages
- Ability to retrieve older messages through pagination
- No data loss even if the LLM context window is limited

### Recent-Message Context

Only the latest 20 messages are sent to the LLM for context. This strategy:

- Keeps the LLM prompt size manageable
- Avoids unnecessary token usage for old messages
- Focuses the LLM on recent operational context
- Allows conversations to grow indefinitely without affecting LLM performance

### Tool Call Handling

Tool calls and tool results are internal to the request and are not persisted as normal conversation messages. This:

- Keeps the conversation focused on user/assistant dialogue
- Avoids cluttering the message history with intermediate tool data
- Simplifies the conversation model for display purposes

## 12. Pagination

### Cursor-Based Pagination

The conversation and message APIs use cursor-based pagination to efficiently retrieve data without loading entire collections.

### Conversation Pagination

Conversations are paginated using `(updated_at, id)` as the cursor:

- Index on `updated_at` supports efficient recent-conversation queries
- The cursor encodes the timestamp and ID of the last item in the current page
- Subsequent requests use the cursor to fetch older conversations

### Message Pagination

Messages are paginated within a conversation using `(created_at, id)` as the cursor:

- Composite index on `(conversation_id, created_at, id)` supports efficient queries
- The cursor encodes the timestamp and ID of the first message in the current page
- Subsequent requests use the cursor to fetch older messages
- The repository validates that the cursor belongs to the requested conversation

### Pagination Benefits

- Efficient database queries using indexed columns
- No offset-based pagination performance issues
- Stable cursors even if new data is added
- Ability to handle large conversations without loading all messages

## 13. Error Handling

Expected application errors are represented explicitly and mapped at the API boundary:

- Invalid request: `400` or `422`
- Unknown order/conversation: `404`
- Missing required operational data: clear error message
- Invalid pagination cursor: `422`
- Database failure: `500`
- LLM timeout/provider failure: `502` or `503`
- Invalid tool request: controlled application error, never arbitrary execution

### Failed LLM Requests

If an LLM request fails after the user message has been persisted:

- The user message remains in the database
- No fake or empty assistant message is created
- The conversation state remains valid
- The user can retry the query in the same conversation

This approach avoids complex rollback mechanisms while maintaining data consistency.

Error responses are useful to the caller without exposing credentials, SQL, provider internals, or sensitive implementation details.

## 14. Database and Query Considerations

### Important Relationships

- Customer → Orders (one-to-many)
- Order → Payment (one-to-one, optional)
- Order → Delivery (one-to-one, optional)
- Conversation → Messages (one-to-many, cascade delete)

### Constraints and Indexes

- `orders.order_number`: Unique constraint and index
- `orders.customer_id`: Foreign key with index
- `customers.email`: Unique constraint
- `payments.order_id`: Unique constraint
- `deliveries.order_id`: Unique constraint
- `conversations.updated_at`: Index for recent-conversation listing
- `messages`: Composite index on `(conversation_id, created_at, id)` for pagination

### Efficient Queries

- Message history retrieval uses `LIMIT` and the composite index to fetch only the required messages
- Conversation listing uses cursor-based pagination with the `updated_at` index
- Order lookups use the unique `order_number` index
- No N+1 query issues detected in the current implementation

### Seed Data

The seed process is repeatable and includes stable examples for:

- Successful payment with scheduled delivery (Order 4521)
- Successful payment with delivery not scheduled (Order 1289) - demonstrates operational gap
- Pending payment (Order 3340)
- Failed payment (Order 5678)
- Delivery in progress (Order 2231)
- Delivered order (Order 7812)
- Cancelled order (Order 9044)
- Failed delivery (Order 6150)
- Three seeded conversations demonstrating multi-turn flows and pagination

Monetary values use fixed precision. Foreign keys, unique constraints, indexes, and timezone-aware timestamps are defined deliberately.

## 15. Design Decisions

### PostgreSQL vs NoSQL

PostgreSQL was chosen for:

- Strong relational model for operational data (customers, orders, payments, deliveries)
- ACID guarantees for data consistency
- Mature tooling (SQLAlchemy, Alembic)
- Ability to handle both operational data and conversation history in a single database
- No need for complex document structures or schema flexibility

### Repository/Service Separation

Repositories contain SQLAlchemy queries and data access. Services contain business logic. This separation:

- Keeps data access isolated
- Makes testing easier (mock repositories)
- Allows business logic to evolve independently of data access
- Provides clear boundaries for future changes

### LLM Abstraction

The LLM is abstracted behind a protocol-based client interface (`LLMClient`) with a concrete Gemini implementation (`_geminiClient`). This:

- Isolates provider-specific logic
- Allows provider switching without changing business logic
- Makes testing easier with mock LLM clients
- Keeps tool definitions provider-agnostic

### Controlled Backend Tools

The LLM can only call predefined backend tools. This:

- Prevents arbitrary SQL execution
- Ensures all data access goes through validated services
- Makes the system auditable and secure
- Allows fine-grained control over what information the LLM can retrieve

### Persistent Conversations in PostgreSQL

Conversation history is stored in PostgreSQL rather than external memory systems because:

- PostgreSQL is already the system of record
- No additional infrastructure required (no Redis, vector databases)
- Full history is available for audit and retrieval
- Pagination efficiently handles large conversations
- Simpler deployment and operational overhead

### Recent-Message Strategy

Only recent messages are sent to the LLM because:

- LLM context windows have limits
- Older messages are less relevant for current queries
- Token costs increase with context size
- Full history is still available through pagination
- Avoids unnecessary complexity of RAG or vector search

### PostgreSQL-Based Message Pagination

Cursor-based pagination with composite indexes was chosen because:

- Efficient for large datasets
- No offset performance issues
- Stable cursors even with new data
- Leverages existing database infrastructure
- Simpler than implementing external pagination systems

### Avoiding Advanced Memory Infrastructure

The implementation intentionally avoids RAG, vector databases, and Redis because:

- Recent-message strategy is sufficient for the current requirements
- PostgreSQL can handle the conversation history efficiently
- Additional infrastructure would increase complexity
- These can be added later if requirements justify them
- Keeps the deployment simple for a backend assignment

## 16. Current Limitations / Future Scope

### Not Currently Implemented

- **Automated testing**: Unit tests, integration tests, API tests, and LLM interaction tests are planned but not implemented
- **Authentication**: User authentication at the API boundary is future scope
- **Authorization**: Role-based access control for operational actions is future scope

These features are intentionally deferred to keep the initial implementation focused on the core requirements. They can be added later without changing the fundamental architecture.
