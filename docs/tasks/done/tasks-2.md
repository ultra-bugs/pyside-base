## Summary (tasks-2.md)

- **Tasks in this file**: 4
- **Task IDs**: 006 - 009

## Tasks

### Task ID: 006

- **Title**: Update AbstractTask Documentation with Tagging
- **File**: docs/new-core-refs/13-abstract-task.md
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Document the new Tagging API in AbstractTask.
**File to Create/Modify:** docs/new-core-refs/13-abstract-task.md
**Detailed Instructions:**
1.  Add `tags` parameter to Constructor documentation.
2.  Add `addTag`, `removeTag`, `hasTag` to API Reference methods.
3.  Add "Tagging" section with usage examples.
```

### Task ID: 007

- **Title**: Update TaskChain Documentation with Auto-tagging
- **File**: docs/new-core-refs/14-task-chain.md
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Document auto-tagging behavior in TaskChain.
**File to Create/Modify:** docs/new-core-refs/14-task-chain.md
**Detailed Instructions:**
1.  Mention `_ChainedChild` and `Parent_{UUID}` tags in the Overview or API Reference.
2.  Explain how this facilitates bulk operations filtering.
```

### Task ID: 008

- **Title**: Update TaskManager Documentation with Bulk Ops
- **File**: docs/new-core-refs/15-task-manager.md
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Document Bulk Operations in TaskManagerService.
**File to Create/Modify:** docs/new-core-refs/15-task-manager.md
**Detailed Instructions:**
1.  Add `stopTasksByTag` and `pauseTasksByTag` to API Reference.
2.  Explain the `includeChainedChildren` parameter and default filtering logic.
3.  Add usage examples for bulk actions.
```

### Task ID: 009

- **Title**: Update Task System Overview
- **File**: docs/new-core-refs/12-task-system-overview.md
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Add "Bulk Actions" feature to Overview.
**File to Create/Modify:** docs/new-core-refs/12-task-system-overview.md
**Detailed Instructions:**
1.  Add "Bulk Actions" or "Tagging & Filtering" to Key Features.
2.  Briefly mention efficient reverse indexing in TaskTracker component description.
```
