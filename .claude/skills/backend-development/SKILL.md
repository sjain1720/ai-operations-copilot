# Backend Development Skill

Use these instructions when implementing or changing the AI Operations Copilot backend.

## Project Boundaries

- Use Python, FastAPI, SQLAlchemy, PostgreSQL, and Pydantic consistently with the project design.
- Keep the initial scope focused on read-only operational queries for trusted company administrators.
- Do not add authentication, authorization, multi-turn state, or unrelated infrastructure unless the project scope changes.
- Prefer the smallest clear implementation that satisfies the assignment.

## Layering

Keep responsibilities separate:

- **API layer:** routes, HTTP status codes, request/response schemas, and dependency wiring.
- **Application services:** use cases, workflow coordination, and deterministic operational rules.
- **Repositories:** SQLAlchemy queries and persistence access only.
- **AI layer:** provider client, prompts, tool schemas, and tool-call orchestration.
- **Database layer:** engine, sessions, models, migrations, and seed data.

Do not put SQL in route handlers, provider-specific logic in domain services, or business rules in Pydantic schemas.

## FastAPI and Pydantic

- Define explicit Pydantic request and response models.
- Reject empty, whitespace-only, malformed, or overlong copilot queries.
- Use dependency injection for database sessions, configuration, repositories, services, and the LLM client.
- Keep route handlers thin and delegate behavior to application services.
- Use versioned API paths and consistent JSON error responses.
- Map known domain failures to deliberate HTTP responses instead of exposing raw exceptions.

## SQLAlchemy and PostgreSQL

- Use typed SQLAlchemy models and explicit relationships, foreign keys, constraints, and indexes.
- Keep public order numbers unique and indexed.
- Use fixed-precision numeric types for money and timezone-aware timestamps.
- Select only the columns needed by a use case and avoid accidental lazy-loading or N+1 queries.
- Use joins or deliberate eager loading for order summaries when appropriate.
- Keep database sessions request-scoped and close them reliably.
- Use transactions for multi-step writes or seed operations; keep the initial operational APIs read-only.
- Do not build SQL from user or LLM-provided strings.

## Async Usage

- Use async FastAPI handlers only when the database and provider clients are async-compatible.
- Do not call blocking SQLAlchemy or LLM code directly from an async event loop without an appropriate boundary.
- Add explicit timeouts to database and LLM calls.
- Avoid introducing async complexity solely for style; consistency with the selected libraries matters more.

## Operational and AI Rules

- The LLM must never access PostgreSQL or execute arbitrary SQL.
- Expose only allowlisted tools such as order details, payment status, delivery status, and full order status.
- Validate tool names and arguments before dispatching them.
- Return structured tool results to the LLM and require final answers to use retrieved facts only.
- Enforce a maximum number of tool-call rounds.
- Surface missing or contradictory payment, delivery, and order data explicitly rather than guessing.
- Keep provider credentials, model settings, and database URLs in configuration, never source code.

## Error Handling

- Define meaningful application exceptions for not-found, missing-data, validation, database, tool, and provider failures.
- Log useful diagnostic context without secrets, raw credentials, or unnecessary personal data.
- Do not turn database or provider failures into plausible-looking operational answers.
- Preserve the distinction between an order not found and an order with missing related records.

## Abstraction and Delivery

- Reuse existing project patterns before introducing abstractions.
- Avoid generic repositories, premature event systems, unnecessary caching, and speculative integrations.
- Add a helper or service only when it owns a real repeated responsibility or boundary.
- Keep documentation aligned with the implemented behavior, not the intended future design.
