# AI Operations Copilot

## Assignment

Build an AI-powered backend service that helps an operations team answer customer and operational queries.

Example queries:

* "What's the payment status for order #4521?"
* "Customer says they've paid for order #1289 but delivery isn't scheduled — what's going on?"
* "Give me a full status summary for order #2231."

The system should also support follow-up questions within a persistent conversation, allowing an operations user to continue discussing the same operational context across multiple turns.

## Goal

Build a backend service where an operations user can submit natural-language queries and receive accurate, useful answers based on operational data stored in PostgreSQL.

The AI should be able to:

1. Understand what information is needed.
2. Use controlled backend tools to retrieve that information.
3. Generate a clear response grounded in the retrieved data.
4. Maintain context across follow-up queries within the same conversation.

The LLM must not directly access the database.

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

The operational data is stored in PostgreSQL with appropriate relationships, constraints, indexes, and timestamps.

### 2. AI Copilot

Provide an API through which an operations user can submit a natural-language question.

The copilot should:

1. Understand the user's query.
2. Determine which operational information is required.
3. Call appropriate backend tools/functions.
4. Retrieve the required data from PostgreSQL through the backend.
5. Generate a concise, accurate answer.

The LLM must not directly access the database.

### 3. Multi-Turn Conversations

The copilot supports persistent conversations.

A conversation:

* Can contain multiple user and assistant messages.
* Is stored in PostgreSQL.
* Does not automatically end.
* Is independent of customers, orders, payments, and deliveries.
* Can be continued by providing its conversation ID to the copilot API.

For each query:

1. The existing conversation is retrieved, or a new conversation is created when no conversation ID is provided.
2. The current user message is persisted.
3. Recent previous messages are loaded for LLM context.
4. The LLM processes the query and uses backend tools when required.
5. The final assistant response is persisted.
6. The response includes the conversation ID so the conversation can be continued.

The full conversation remains stored in PostgreSQL, but only recent messages are provided to the LLM to keep the context manageable.

Only user and assistant messages are persisted as conversation messages. Tool calls and tool results remain internal to the request.

### 4. Backend Tools

Expose controlled tools/functions for retrieving operational information.

The current copilot can use backend tools for information such as:

* Order details
* Payment status
* Delivery status
* Complete order status

These tools use the existing backend services and data-access layer rather than allowing the LLM to access PostgreSQL directly.

### 5. APIs

Use FastAPI to expose the backend APIs.

The primary AI endpoint is:

`POST /api/v1/copilot/query`

The copilot request can include a conversation ID to continue an existing conversation. If no conversation ID is provided, a new conversation is created.

Conversation APIs provide functionality for:

* Creating conversations
* Listing conversations
* Retrieving conversation details
* Retrieving paginated conversation messages

Operational APIs are also available for directly retrieving operational information where appropriate.

### 6. Database

Use PostgreSQL with SQLAlchemy.

The database maintains consistent relationships between customers, orders, payments, and deliveries.

It also stores persistent conversation history through:

* Conversations
* Messages

Messages belong to a conversation and are retrieved using database-level pagination when older history is requested.

### 7. Seed Data

Create realistic seed data representing different operational scenarios.

The repository must contain a reproducible seed script.

Operational seed data includes useful cases such as:

* Successful payment with scheduled delivery
* Successful payment with delivery not scheduled
* Pending or failed payment
* Delivery in progress
* Delivered order
* Cancelled order
* Other realistic operational inconsistencies

The seed data also includes conversations and messages that can be used to demonstrate:

* Multi-turn conversations
* Follow-up questions
* Conversation isolation
* Message-history pagination

The data should make the example AI queries and conversation flows demonstrable.

### 8. Error Handling

Handle cases such as:

* Order not found
* Invalid input
* Missing operational information
* Database failures
* LLM/tool failures
* Missing or invalid conversation
* Invalid message pagination parameters

The API should return appropriate errors rather than silently producing unreliable answers.

If an LLM request fails, the system must not create a fake or empty assistant response.

### 9. Testing

Automated testing is planned as future scope.

When testing is added, it should cover important backend behaviour, error cases, database interactions, and AI/tool interactions where practical.

## Engineering Constraints

* Keep the architecture simple and appropriate for a 5-day backend assignment.
* Avoid unnecessary technologies and infrastructure.
* Do not expose database credentials or LLM API keys.
* Do not allow the LLM to execute arbitrary database queries.
* AI responses must be grounded in retrieved operational data.
* Prefer deterministic backend logic wherever possible.
* Use clear separation between API, business logic, database access, and AI components.
* Do not introduce RAG, vector databases, Redis, or other advanced memory infrastructure unless there is a clear future requirement.
* Conversation history should remain persisted in PostgreSQL.
* Only recent conversation history should be sent to the LLM.

## Authentication and Authorization

Authentication and authorization are future scope and are not part of the current implementation.

## Submission Requirements

The public GitHub repository must contain:

* Working source code
* `README.md` with setup instructions and API documentation
* `DESIGN.md` describing the system design
* Seed data/script

Automated tests are planned as future scope.

A 3–5 minute walkthrough video is optional.

## Current Development Approach

The project was built incrementally:

1. Project foundation
2. Database models and migrations
3. Seed data
4. Core backend services/APIs
5. AI tools
6. LLM integration
7. Persistent conversation and message history
8. Multi-turn conversation support
9. Pagination for conversation history
10. Implementation review and cleanup
11. Documentation

Testing, authentication, and authorization remain future development scope.

## Current Architecture Decisions

The following decisions are now established:

* PostgreSQL is used for both operational data and conversation history.
* SQLAlchemy is used for database access.
* The LLM is isolated behind an LLM/provider abstraction.
* The LLM never directly accesses PostgreSQL.
* Backend tools provide controlled access to operational information.
* Conversation history is stored using Conversation and Message entities.
* Conversations are independent of operational entities such as orders and customers.
* Conversations do not automatically end.
* Only user and assistant messages are persisted.
* Tool calls and tool results are not persisted as normal conversation messages.
* The full conversation remains available in PostgreSQL.
* Recent conversation history is provided to the LLM rather than the entire conversation.
* Older conversation messages are available through paginated APIs.
* The implementation intentionally avoids unnecessary memory infrastructure such as RAG, vector databases, and Redis.

## Future Scope

Potential future improvements include:

* Automated unit and integration testing
* Authentication
* Authorization
* Additional operational tools
* Further reliability and observability improvements