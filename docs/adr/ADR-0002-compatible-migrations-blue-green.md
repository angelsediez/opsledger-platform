# ADR-0002: Backward-compatible migrations for blue/green and rollback

## Status
Accepted

## Context
The project will use Alembic together with blue/green deployment and rollback.

## Decision
Schema changes must be designed to remain compatible across the old and new application versions during a blue/green transition window.

## Rules
- prefer additive changes first
- avoid destructive schema changes in the same release where rollback is still expected
- treat rollback as an application rollback first, not as an immediate destructive schema rollback
- document migration caveats in runbooks

## Consequences
### Positive
- safer rollback
- fewer deployment surprises
- better operational discipline

### Negative
- some schema cleanups may need a later follow-up migration

