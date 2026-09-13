# AI Operations Copilot — Claude Instructions

## Project

Build the Cars24 Backend Engineering Assignment: **AI Operations Copilot**.

Tech stack:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* LLM with tool/function calling

The copilot supports both single-turn operational queries and persistent multi-turn conversations.

## Engineering Principles

* Follow clean, production-quality backend engineering practices.
* Keep the architecture simple and appropriate for the assignment.
* Do not over-engineer or introduce unnecessary technologies.
* Prefer clear, readable, maintainable code over clever abstractions.
* Use proper separation of concerns between API, business logic, data access, and AI components.
* Use type hints throughout the Python codebase.
* Handle errors explicitly and return appropriate HTTP responses.
* Validate API inputs using Pydantic.
* Keep database access behind a repository/data-access layer where useful.
* Never let the LLM directly access the database.
* Expose controlled backend tools/functions to the LLM for retrieving operational data.
* Never hardcode secrets or API keys.

## AI

The AI copilot should answer operational/customer queries using reliable data from the backend.

The LLM should use backend tools/functions to retrieve required information such as:

* Order details
* Payment status
* Delivery status
* Customer information
* Full order status

The final response should be grounded in the retrieved backend data and should not invent operational information.

For multi-turn conversations:

* Conversations are persisted in PostgreSQL.
* User and assistant messages are stored against a conversation.
* A conversation does not automatically end.
* Follow-up queries within the same conversation should use recent conversation history for context.
* Only the required recent message history should be provided to the LLM rather than loading the entire conversation into the LLM context.
* Tool calls and tool results are internal to the request and are not persisted as normal conversation messages.

## Database

Use PostgreSQL with SQLAlchemy.

Use proper relationships, constraints, indexes, and timestamps where appropriate.

The database contains both operational data and conversation history.

Conversation history consists of:

* Conversations
* Messages belonging to conversations

Generate realistic seed data and include a reproducible seed script as required by the assignment.

## Testing

Testing is part of the future development scope.

When the testing phase begins, write meaningful tests for:

* Core business logic
* API behaviour
* Validation and error cases
* Database interactions where appropriate
* AI/tool behaviour where practical

Do not write tests merely to increase coverage.

Until the testing phase is explicitly started, do not add tests unnecessarily while implementing unrelated features.

## Authentication and Authorization

Authentication and authorization are future development scope.

Do not introduce authentication or authorization unless explicitly requested as part of a future implementation phase.

## Development Workflow

Before implementing a significant feature:

1. Inspect the existing code and project structure.
2. Understand the requirement.
3. Explain the proposed approach briefly.
4. Implement the smallest clean solution.
5. Add or update relevant tests when testing is part of the current development phase.
6. Check for regressions.

Do not rewrite working code unnecessarily.

## Documentation

Keep `PROJECT.md` aligned with the actual requirements, current features, and architectural decisions.

Create/update `DESIGN.md` and `README.md` when the architecture and implementation are sufficiently established.

Documentation must describe the actual implementation, not an idealised version.

When a major feature is added, ensure the project documentation reflects the final behaviour.

## Git

Git is controlled entirely by the user.

Claude must **never**:

* Create commits
* Amend commits
* Create or delete branches
* Push or pull
* Merge or rebase
* Reset, revert, or cherry-pick
* Modify Git configuration
* Stage or unstage files

Claude may inspect Git status/diffs when useful for understanding the current state.

After making code changes, Claude should:

* Show or summarise the files changed.
* Explain what was changed and why.
* Point out any potential issues.
* Leave all Git operations to the user.

The user will independently review, stage, commit, and push changes.