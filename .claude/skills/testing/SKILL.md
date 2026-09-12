# Testing Skill

Use these instructions when automated testing is added to the AI Operations Copilot. Testing is currently deferred, but new tests should follow these rules.

## Test Goals

- Test behavior and failure handling that matters to operations users.
- Prefer a small number of meaningful tests over coverage-only tests.
- Keep tests deterministic and independent of a live external LLM provider.
- Match the project layers: API, services, repositories, database, and AI orchestration.

## pytest Structure

- Use pytest and descriptive test names that state the behavior under test.
- Organize tests by responsibility, for example `unit`, `api`, `integration`, and `ai`.
- Keep fixtures focused and reusable; avoid large fixtures that hide setup behavior.
- Use parametrization for related status and validation cases.
- Mock external provider calls and time-dependent behavior where appropriate.

## Unit Tests

Test pure or mostly deterministic logic without a database:

- Query and order-number validation
- Payment and delivery status rules
- Full-order status aggregation
- Missing and contradictory operational data
- Tool-name and tool-argument validation
- Application exception mapping

Unit tests should not verify SQLAlchemy internals or make network calls.

## API Tests

Use FastAPI's test client or async equivalent to verify:

- Valid copilot requests and response schemas
- Empty, malformed, and overlong queries
- Unknown orders and missing operational information
- Correct HTTP status codes and error bodies
- Database and LLM failures at the API boundary
- Health endpoint behavior

Replace services or dependencies through FastAPI dependency overrides rather than requiring real infrastructure for every API test.

## Database and Integration Tests

- Use a dedicated test PostgreSQL database for repository and integration behavior.
- Never run tests against development or production data.
- Keep each test isolated with transaction rollback, database cleanup, or disposable test data.
- Verify relationships, uniqueness, foreign keys, status constraints, and representative seed scenarios.
- Test repository queries for existing orders, unknown orders, missing payments, missing deliveries, and complete summaries.
- Include at least one end-to-end application flow through the API, tool dispatcher, service layer, and test database.

## AI and Tool Tests

- Mock the LLM client and assert that the expected tool definitions are supplied.
- Verify tool names and arguments are validated before execution.
- Verify tool results are returned to the LLM and that multiple required tools can be coordinated.
- Reject unknown tools, malformed provider responses, excessive tool rounds, and provider failures.
- Test that final responses are based on retrieved tool data and that missing data is not replaced with invented facts.
- Do not make real provider calls in the default test suite.

## Fixtures and Isolation

- Use factories or small fixture builders for customers, orders, payments, and deliveries.
- Make seeded identifiers explicit and avoid relying on implicit database ordering.
- Reset mutable state between tests.
- Keep tests safe to run repeatedly and in parallel where the database strategy supports it.
- Avoid asserting unstable wording from an LLM; assert structured tool behavior and essential response facts instead.

## Coverage Judgment

Coverage is a signal, not the goal. Prioritize core operational rules, public API behavior, failure paths, database integrity, tool boundaries, and grounding guarantees. Do not add tests solely to raise a percentage.
