# Contributing to Virtual AI Assistant

We use Conventional Commits to keep our project history clean and easy to understand. This guide explains how to format your commit messages.

## Commit Message Format

Each commit message should follow this structure:

```
<type>(<optional scope>): <description>

<optional body>

<optional footer>
```

### 1. Type

The `type` describes the kind of change you are making. You must use one of the following:

- **feat**: A new feature for the user.
- **fix**: A bug fix for the user.
- **refactor**: Rewriting code without changing its behavior.
- **perf**: A code change that improves performance.
- **style**: Formatting changes (e.g., tabs, spacing, semi-colons).
- **docs**: Changes to documentation only.
- **test**: Adding or correcting tests.
- **build**: Changes to the build system, CI/CD, or dependencies.
- **ops**: Changes related to infrastructure, deployment, or operations.
- **chore**: Other changes that don’t modify source or test files.

### 2. Scope (Optional)

The `scope` provides context for the change. It's a noun describing the part of the codebase affected.

Examples: `frontend`, `gateway`, `llm-worker`, `auth`, `chat`.

### 3. Description

The `description` is a short summary of the change.

- Use imperative, present tense (e.g., "add," "change," not "added," "changes").
- Do not capitalize the first letter.
- Do not end with a period (`.`).

### Breaking Changes

To indicate a change that breaks backward compatibility, add an `!` after the type/scope. The footer must also contain a `BREAKING CHANGE:` section explaining the change.

---

## Examples

**A new feature:**

```
feat(chat): add support for emoji reactions
```

**A bug fix:**

```
fix(gateway): resolve websocket connection timeout issue
```

**A documentation change:**

```
docs: update quick start guide for ollama models
```

**A breaking change:**

```
feat(api)!: remove deprecated user endpoint

BREAKING CHANGE: The `/api/v1/user` endpoint has been removed. Please use the `/api/v2/profile` endpoint instead.
```

**More Examples:**

```
feat: add email notifications on new direct messages
```

```
feat(shopping cart): add the amazing button
```

```
feat!: remove ticket list endpoint
refers to JIRA-1337
```

```
fix(shopping-cart): prevent order an empty shopping cart
```

```
fix(api): fix wrong calculation of request body checksum
```

```
fix: add missing parameter to service call

The error occurred due to <reasons>.
```

```
perf: decrease memory footprint for determine unique visitors by using HyperLogLog
```

```
build: update dependencies
```

```
build(release): bump version to 1.0.0
```

```
refactor: implement fibonacci number calculation as recursion
```

```
style: remove empty line
```
