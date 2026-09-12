# Code Review Skill

Use these instructions when reviewing changes to the AI Operations Copilot. Lead with concrete correctness and risk findings, ordered by severity.

## Review Order

1. Confirm the change satisfies the assignment and stated project scope.
2. Check correctness and failure behavior.
3. Check architecture and boundary violations.
4. Check security, data integrity, API quality, AI reliability, tests, maintainability, and performance.
5. Identify unnecessary complexity and missing documentation.

Report actionable findings with file and line references where available. Separate confirmed issues from questions or assumptions.

## Assignment and Architecture

- Does the change support natural-language operational queries and the required order, customer, payment, and delivery data?
- Does it preserve the FastAPI -> service -> repository/database separation?
- Are route handlers thin and dependencies injectable?
- Is the implementation consistent with PostgreSQL, SQLAlchemy, and Pydantic?
- Does it stay within the five-day assignment scope without speculative infrastructure?
- Does documentation describe actual behavior rather than planned behavior?

## Correctness and Error Handling

- Are order, payment, and delivery statuses interpreted correctly?
- Are missing records and inconsistent records reported explicitly?
- Are unknown orders distinct from missing related information?
- Are validation, database, tool, timeout, and provider failures mapped to appropriate responses?
- Could an exception be swallowed and produce a misleading successful answer?
- Are transactions and session lifecycles correct?

## Security and Data Protection

- Are database credentials and LLM keys excluded from source code and logs?
- Can user or LLM input become arbitrary SQL or an unsafe tool invocation?
- Are tool names allowlisted and arguments validated?
- Does error output expose SQL, credentials, provider internals, or unnecessary customer data?
- Remember that authentication and authorization are intentionally out of scope for the initial release, but do not excuse unsafe database or secret handling.

## Database and API Quality

- Are foreign keys, uniqueness constraints, indexes, timestamps, and money types appropriate?
- Are queries efficient, bounded, and free of avoidable N+1 behavior?
- Does the API use explicit Pydantic schemas, stable versioned paths, and consistent errors?
- Are response fields sufficient for an operations user without exposing internal implementation details?
- Are timeouts, pagination, or result limits needed for the changed endpoint?

## AI Reliability

- Can the LLM access only controlled backend tools?
- Is the final answer grounded in actual tool results?
- Can the model answer without retrieving required operational data?
- Are malformed tool calls, unknown tools, provider failures, and tool-call loops handled safely?
- Are prompts and schemas clear enough to prevent status invention or unsupported conclusions?
- Is deterministic business logic kept outside the LLM where possible?

## Tests and Maintainability

- Are important behavior and error paths covered, or is testing still deliberately deferred?
- Would the change be straightforward to test through dependency injection and mocked provider boundaries?
- Are names, types, module responsibilities, and configuration clear?
- Is there duplication that should be removed, or abstraction that adds complexity without value?
- Are comments and documentation limited to decisions that are not obvious from the code?

## Performance Review

- Are database sessions and connections released reliably?
- Are async and blocking operations used consistently?
- Are LLM calls bounded by timeouts, token limits, and maximum tool rounds?
- Does the change add unnecessary network calls, repeated queries, or unbounded data loading?
- Is caching or background processing actually justified by a measured requirement?
