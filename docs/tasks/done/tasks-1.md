## Summary (tasks-1.md)

- **Tasks in this file**: 5
- **Task IDs**: 001 - 005

## Tasks

### Task ID: 001

- **Title**: Implement Tagging in AbstractTask
- **File**: core/taskSystem/AbstractTask.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Add tagging capability to AbstractTask.
**File to Create/Modify:** core/taskSystem/AbstractTask.py
**Detailed Instructions:**
1.  Add `self.tags: Set[str]` to `__init__`.
2.  Initialize `tags` with provided tags and automatically add `ClassName`.
3.  Add methods: `addTag(tag)`, `removeTag(tag)`, `hasTag(tag)`.
4.  Update `serialize()` and `deserialize()` to handle tags.
```

### Task ID: 002

- **Title**: Implement Auto-tagging in TaskChain
- **File**: core/taskSystem/TaskChain.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Automatically inject tags to children tasks in a chain.
**File to Create/Modify:** core/taskSystem/TaskChain.py
**Detailed Instructions:**
1.  When adding child tasks, inject `_ChainedChild` tag.
2.  Inject `Parent_{UUID}` tag to link back to parent chain.
```

### Task ID: 003

- **Title**: Implement Tag Index in TaskTracker
- **File**: core/taskSystem/TaskTracker.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Implement efficient Reverse Indexing for tags.
**File to Create/Modify:** core/taskSystem/TaskTracker.py
**Detailed Instructions:**
1.  Add `_tagIndex: Dict[str, Set[str]]` (Tag -> Set of UUIDs).
2.  Update `addTask` to index tags.
3.  Update `removeTask` to clean up tags.
4.  Add `getUuidsByTag(tag)` method.
5.  Ensure thread safety.
```

### Task ID: 004

- **Title**: Implement Bulk Ops in TaskManagerService
- **File**: core/taskSystem/TaskManagerService.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Add bulk operations using tags.
**File to Create/Modify:** core/taskSystem/TaskManagerService.py
**Detailed Instructions:**
1.  Add `stopTasksByTag(tag)`.
2.  Add `pauseTasksByTag(tag)`.
3.  Implement filtering logic (exclude `_ChainedChild` by default).
```

### Task ID: 005

- **Title**: Verification Tests
- **File**: tests/core/taskSystem/test_bulk_actions.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Verify the bulk action system.
**File to Create/Modify:** tests/core/taskSystem/test_bulk_actions.py
**Detailed Instructions:**
1.  Test tagging in AbstractTask.
2.  Test auto-tagging in TaskChain.
3.  Test TaskTracker indexing.
4.  Test TaskManagerService bulk operations.
```
