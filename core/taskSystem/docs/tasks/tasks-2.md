## Summary (tasks-2.md)

- **Tasks in this file**: 1
- **Task IDs**: 017
- **Status**: Pending ⏳

## Tasks

### Task ID: 017

- **Title**: Integrate Legacy Workflows with TaskManagerService
- **Primary Docs**:
  - [Task System Integration Plan](mdc:core/taskSystem/docs/task-system-integration-plan.md)
  - [Task System Plan (Oct 2025)](mdc:core/taskSystem/docs/task-system-plan-oct-2025.md)
  - [Task System Migration Summary](mdc:core/taskSystem/docs/task-system-migration.md)
  - [Task System API Documentation](mdc:core/taskSystem/docs/task-system-api.md)
  - [Architecture Guide](mdc:core/taskSystem/docs/architecture.md)
  - [Testing Guide](mdc:core/taskSystem/docs/testing.md)
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective**: Refactor remaining task producers/consumers to rely exclusively on the new TaskSystem stack (`TaskManagerService`, `TaskQueue`, `TaskScheduler`, `TaskTracker`). Ensure all workflows follow the Observer-driven orchestration and comply with serialization, retry, and logging policies defined for AbstractTask subclasses.

**Implementation Scope**:
- Identify legacy entry points still bypassing `TaskManagerService` (direct queue usage, manual threading, or ad-hoc schedulers) and route them through Observer events handled by `TaskManagerService.onTaskRequestEvent`.
- Update task definitions to inherit `AbstractTask`, implement `serialize()` / `deserialize()`, and honour cancellation, retry, and progress semantics.
- Replace manual scheduling with `TaskScheduler.addScheduledTask`, persisting job metadata via `core.Config`.
- Wire UI/handler updates to `TaskManagerService` signals instead of polling or direct controller interactions.
- Audit logging to ensure `logger.bind(component="TaskSystem", …)` usage with contextual identifiers (e.g., `taskUuid`, `threadId`).
- Persist queue/tracker state through `saveState()` on shutdown; confirm `isPersistent` flags for tasks that must survive restarts.

**Requirements**:
- **Architecture**: Preserve UI-first and Observer patterns; no direct controller-to-controller calls. All business logic remains in services/handlers.
- **Naming & Style**: Follow Qt naming conventions (PascalCase files/classes, camelCase methods/variables). No snake_case. Include type hints.
- **Logging**: Replace any `print`/raw logging with `core.Logging.logger` bound to `TaskSystem`, adding contextual identifiers for async flows.
- **Testing**: Extend/author pytest coverage (see `docs/testing.md`), including queue/scheduler integration and Observer-driven end-to-end scenarios. Use `scripts/run_pytest.py` for Windows runs.
- **Documentation**: Update relevant docs in `docs/` to reflect new integration, especially noting any deviations from the integration plan.

**Acceptance Criteria**:
- All legacy code paths now enqueue tasks via `TaskManagerService` (direct queue or thread pool access removed).
- AbstractTask subclasses support serialization/deserialization, cancellation, retry, and emit required Qt signals.
- Scheduler jobs persist and survive application restarts; manual timers removed/migrated.
- UI reflects live task status/progress via subscribed signals without polling.
- Logger usage conforms to project policy with contextual data; no `print` statements remain.
- Pytest suite updated with passing coverage for new flows (`tests_auto/task_system/`).
- Documentation updated to reflect final architecture and integration touchpoints.
```


