# AI Operations Copilot

AI-powered backend service for helping operations teams answer customer and operational questions using reliable order data. The system supports both single-turn queries and persistent multi-turn conversations.

## Overview

The AI Operations Copilot is a backend service that accepts natural-language operational questions, retrieves required information from PostgreSQL through controlled backend tools, and returns concise answers grounded in that data. The system supports persistent conversations, allowing follow-up questions within the same operational context.

Example queries include:

- What is the payment status for order `4521`?
- The customer paid for order `1289`, but delivery is not scheduled. What is going on?
- Give me a complete status summary for order `2231`.
- When was order `7812` delivered?
- Which orders have failed payments?

The LLM is used for query understanding and response composition. It does not receive direct database access and cannot execute arbitrary SQL. All operational data retrieval happens through controlled backend tools that use existing services and repositories.

## Features

### Implemented Features

- **Natural-language operational queries**: Submit questions in plain language and receive grounded answers
- **Controlled LLM tool/function calling**: The LLM can only call predefined backend tools for data retrieval
- **PostgreSQL-backed operational data**: Customers, orders, payments, and deliveries stored with proper relationships and constraints
- **Persistent conversations**: Conversation history is stored in PostgreSQL
- **Multi-turn follow-up questions**: Continue discussing the same operational context across multiple turns
- **Conversation/message history**: Full conversation history persisted with paginated retrieval
- **Message pagination**: Efficient cursor-based pagination for retrieving older conversation messages
- **Recent-message context**: Only recent messages are sent to the LLM to keep context manageable
- **Deterministic seed data**: Reproducible seed data with realistic operational scenarios and conversation examples
- **Appropriate error handling**: Clear errors for missing resources, invalid input, and LLM failures

### Future Scope

The following features are planned for future development but are not currently implemented:

- Automated testing (unit, integration, API tests)
- Authentication
- Authorization

## Technology Stack

- **Python 3.9+**
- **FastAPI**: Web framework for HTTP API
- **PostgreSQL 16**: Relational database for operational data and conversation history
- **SQLAlchemy 2.0**: ORM and database toolkit
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **Google Gemini**: LLM provider with tool/function-calling support
- **Docker & Docker Compose**: For local PostgreSQL development

## Architecture Overview

### Normal Copilot Flow

```text
User query
    → FastAPI (validation)
    → Copilot service
    → LLM client (Gemini)
    → Backend tool executor
    → Operational services
    → Repositories
    → PostgreSQL
    → Tool results
    → LLM
    → Final answer
```

### Conversation-Aware Flow

```text
Conversation ID + query
    → Load recent previous messages
    → Persist current user message
    → Build LLM context (recent messages)
    → LLM with backend tools (if required)
    → Generate final answer
    → Persist assistant message
    → Return response + conversation ID
```

### Component Responsibilities

- **FastAPI layer**: HTTP request/response handling, input validation, error mapping
- **Copilot service**: Orchestrates LLM calls, tool execution, and conversation persistence
- **LLM client**: Abstracts Gemini API, handles tool calling protocol
- **Backend tool executor**: Validates and executes tool requests through operational services
- **Operational services**: Deterministic business logic for order, payment, and delivery lookups
- **Repositories**: SQLAlchemy queries and data access
- **PostgreSQL**: Persistent storage for operational data and conversation history

## Project Structure

```
ai-operations-copilot/
├── app/
│   ├── ai/                 # LLM integration and tools
│   │   ├── client.py       # Gemini LLM client
│   │   ├── copilot.py      # Copilot orchestration service
│   │   ├── tools.py        # Backend tool definitions and executor
│   │   └── prompts.py      # System prompt
│   ├── api/                # FastAPI routes and dependencies
│   │   ├── routes/
│   │   │   ├── copilot.py
│   │   │   ├── conversations.py
│   │   │   └── orders.py
│   │   ├── dependencies.py
│   │   └── pagination.py
│   ├── core/               # Configuration and exceptions
│   ├── db/                 # Database session management
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access layer
│   ├── schemas/            # Pydantic request/response schemas
│   └── services/           # Business logic layer
├── alembic/                # Database migrations
├── scripts/                # Seed data script
├── .env.example            # Environment variables template
├── docker-compose.yml      # PostgreSQL container
├── pyproject.toml          # Python dependencies
├── CLAUDE.md               # Development instructions
├── PROJECT.md              # Project requirements
├── DESIGN.md               # Technical design
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for PostgreSQL)
- A Google Gemini API key

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd ai-operations-copilot
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -e .
```

4. **Configure environment variables**

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `POSTGRES_PASSWORD`: A secure password for PostgreSQL
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DATABASE_URL`: Update with your password if changed

5. **Start PostgreSQL**

```bash
docker-compose up -d
```

6. **Run database migrations**

```bash
alembic upgrade head
```

7. **Load seed data**

```bash
python scripts/seed.py
```

8. **Start the FastAPI application**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

### Copilot Query

#### `POST /api/v1/copilot/query`

Submit a natural-language operational query. Creates a new conversation if no `conversation_id` is provided, or continues an existing conversation.

**Request:**

```json
{
  "query": "What is the payment status for order 4521?",
  "conversation_id": 1
}
```

- `query` (required, string, 1-4000 characters): The natural-language question
- `conversation_id` (optional, integer): ID of an existing conversation to continue. If omitted, a new conversation is created.

**Response:**

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

- `conversation_id`: The conversation ID (new or existing)
- `answer`: The generated operational answer
- `tools_used`: List of backend tools called during the request
- `metadata`: Additional metadata about tool execution

**Errors:**

- `422`: Invalid request (empty query, invalid conversation_id)
- `404`: Conversation not found (if conversation_id provided but does not exist)
- `500`: Internal server error (database or LLM failure)

### Conversations

#### `POST /api/v1/conversations`

Create a new conversation.

**Request:**

```json
{
  "title": "Order 4521 Support"
}
```

- `title` (optional, string, max 200 characters): Optional conversation title

**Response:**

```json
{
  "id": 1,
  "title": "Order 4521 Support",
  "created_at": "2026-09-12T12:00:00Z",
  "updated_at": "2026-09-12T12:00:00Z"
}
```

#### `GET /api/v1/conversations`

List recent conversations with cursor-based pagination.

**Query Parameters:**

- `limit` (optional, integer, 1-100, default: 20): Number of conversations to return
- `before` (optional, string): Base64-encoded cursor for pagination

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "title": "Order 4521 Support",
      "created_at": "2026-09-12T12:00:00Z",
      "updated_at": "2026-09-12T12:05:00Z"
    }
  ],
  "next_cursor": "eyJ0aW1lc3RhbXAiOiIyMDI2LTA5LTEyVDEyOjAwOjAwWiIsImlkIjoxfQ",
  "has_more": true
}
```

#### `GET /api/v1/conversations/{conversation_id}`

Retrieve a specific conversation by ID.

**Response:**

```json
{
  "id": 1,
  "title": "Order 4521 Support",
  "created_at": "2026-09-12T12:00:00Z",
  "updated_at": "2026-09-12T12:05:00Z"
}
```

**Errors:**

- `404`: Conversation not found

#### `GET /api/v1/conversations/{conversation_id}/messages`

Retrieve messages from a conversation with cursor-based pagination.

**Path Parameters:**

- `conversation_id` (required, integer): The conversation ID

**Query Parameters:**

- `limit` (optional, integer, 1-100, default: 20): Number of messages to return
- `before` (optional, string): Base64-encoded cursor for pagination. If omitted, returns the latest messages.

**Response:**

```json
{
  "conversation_id": 1,
  "items": [
    {
      "id": 1,
      "role": "user",
      "content": "What is the payment status for order 4521?",
      "created_at": "2026-09-12T12:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Payment for order 4521 was successful.",
      "created_at": "2026-09-12T12:00:05Z"
    }
  ],
  "next_cursor": "eyJ0aW1lc3RhbXAiOiIyMDI2LTA5LTEyVDEyOjAwOjAwWiIsImlkIjoxfQ",
  "has_more": false
}
```

**Errors:**

- `404`: Conversation not found
- `422`: Invalid pagination cursor

### Operational APIs

#### `GET /api/v1/orders/{order_number}`

Retrieve order details by public order number.

**Response:**

```json
{
  "id": 1,
  "order_number": 4521,
  "customer_id": 1,
  "status": "confirmed",
  "total_amount": "185000.00",
  "currency": "INR",
  "created_at": "2026-09-01T10:00:00Z",
  "updated_at": "2026-09-01T10:00:00Z"
}
```

#### `GET /api/v1/orders/{order_number}/payment`

Retrieve payment status for an order.

**Response:**

```json
{
  "id": 1,
  "order_id": 1,
  "status": "successful",
  "amount": "185000.00",
  "payment_method": "upi",
  "transaction_reference": "PAY-4521-SUCCESS",
  "paid_at": "2026-09-02T10:30:00Z",
  "failure_reason": null,
  "created_at": "2026-09-02T10:30:00Z",
  "updated_at": "2026-09-02T10:30:00Z"
}
```

#### `GET /api/v1/orders/{order_number}/delivery`

Retrieve delivery status for an order.

**Response:**

```json
{
  "id": 1,
  "order_id": 1,
  "status": "scheduled",
  "scheduled_at": "2026-09-15T09:00:00Z",
  "tracking_reference": "DEL-4521-SCHEDULED",
  "delivered_at": null,
  "failure_reason": null,
  "created_at": "2026-09-02T10:30:00Z",
  "updated_at": "2026-09-02T10:30:00Z"
}
```

#### `GET /api/v1/orders/{order_number}/summary`

Retrieve complete order summary including customer, payment, and delivery information.

**Response:**

```json
{
  "order": {
    "id": 1,
    "order_number": 4521,
    "status": "confirmed",
    "total_amount": "185000.00",
    "currency": "INR"
  },
  "customer": {
    "id": 1,
    "name": "Aarav Mehta",
    "email": "aarav.mehta@example.com",
    "phone": "+91-9876500001"
  },
  "payment": {
    "status": "successful",
    "amount": "185000.00",
    "payment_method": "upi",
    "transaction_reference": "PAY-4521-SUCCESS",
    "paid_at": "2026-09-02T10:30:00Z"
  },
  "delivery": {
    "status": "scheduled",
    "scheduled_at": "2026-09-15T09:00:00Z",
    "tracking_reference": "DEL-4521-SCHEDULED"
  }
}
```

### Health Check

#### `GET /health`

Simple health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```

## Multi-Turn Conversation Behaviour

### Conversation Lifecycle

- A conversation does not automatically end. It persists indefinitely in PostgreSQL.
- A new conversation can be created explicitly via the conversation API or automatically when the copilot query endpoint is called without a `conversation_id`.
- Follow-up queries use the same `conversation_id` to maintain context.

### Message Persistence

- User and assistant messages are persisted in the `messages` table.
- Each message belongs to a conversation and has a role (`user` or `assistant`).
- Tool calls and tool results are internal to the request and are not persisted as normal conversation messages.
- The full conversation history remains available in PostgreSQL.

### LLM Context Strategy

- Only recent message history (latest 20 messages) is sent to the LLM for context.
- This avoids unnecessarily sending the entire conversation to the LLM.
- Older messages can be retrieved through the paginated conversation-message API.

### Example Multi-Turn Flow

```bash
# First query (creates new conversation)
curl -X POST http://localhost:8000/api/v1/copilot/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the payment status for order 4521?"}'
# Response: {"conversation_id": 1, "answer": "Payment for order 4521 was successful.", ...}

# Follow-up query (continues conversation)
curl -X POST http://localhost:8000/api/v1/copilot/query \
  -H "Content-Type: application/json" \
  -d '{"query": "When was it paid?", "conversation_id": 1}'
# Response: {"conversation_id": 1, "answer": "Payment was completed on 2026-09-02 at 10:30 UTC.", ...}
```

## Seed Data

The seed script (`scripts/seed.py`) creates realistic operational scenarios and conversation examples.

### Operational Scenarios

The following order scenarios are included:

- **Order 4521**: Successful payment, scheduled delivery (Aarav Mehta)
- **Order 1289**: Successful payment, delivery not scheduled (Priya Sharma) - demonstrates operational gap
- **Order 3340**: Pending payment, delivery not scheduled (Rohan Desai)
- **Order 5678**: Failed payment, delivery not scheduled (Neha Kapoor)
- **Order 2231**: Successful payment, in transit (Vikram Singh)
- **Order 7812**: Successful payment, delivered (Ishita Rao)
- **Order 9044**: Cancelled order, refunded payment (Kabir Malhotra)
- **Order 6150**: Successful payment, delivery failed (Ananya Iyer)

### Conversation Seed Data

Three seeded conversations demonstrate multi-turn flows:

1. **Conversation A** (Order 4521 Support): 4 exchanges about payment timing and delivery scheduling
2. **Conversation B** (Order 1289 Delivery): 2 exchanges about the payment-success/delivery-not-scheduled gap
3. **Conversation C** (Pagination Demo): 24 exchanges across multiple orders to demonstrate message pagination

Run the seed script to load this data:

```bash
python scripts/seed.py
```

## Error Handling

The API returns appropriate HTTP status codes for various error conditions:

- `400`/`422`: Invalid request (empty query, invalid parameters, malformed cursor)
- `404`: Resource not found (order, conversation, payment, delivery)
- `500`: Internal server error (database failure, unexpected error)
- `502`/`503`: LLM provider failure or timeout

### Failed LLM Requests

If an LLM request fails after the user message has been persisted:
- The user message remains in the database
- No fake or empty assistant message is created
- The conversation state remains valid
- The user can retry the query in the same conversation

## Future Scope

The following features are planned for future development:

- **Automated testing**: Unit tests, integration tests, API tests, and LLM interaction tests
- **Authentication**: User authentication at the API boundary
- **Authorization**: Role-based access control for operational actions

These are not currently implemented and will be added in future development phases.
