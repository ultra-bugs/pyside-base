# Application Core Reference Index

> **Directory of core architectural references with short summaries**

## 1. Application Architecture & Dependency Injection

| File | Description | Last Synced |
|------|-------------|-------------|
| [01-application-context.md](./01-application-context.md) | The central orchestrator for the application lifecycle, context, and environment bootstrap. | `2026-06-09` |
| [02-dependency-injection.md](./02-dependency-injection.md) | Dependency injection principles utilizing `ServiceLocator` to decouple service dependencies. | `2026-06-09` |
| [25-service-providers.md](./25-service-providers.md) | ServiceProvider architecture using topological sorting to safely register services at bootstrap. | `2026-05-25` |

## 2. Controllers & UI Patterns

| File | Description | Last Synced |
|------|-------------|-------------|
| [04-controller-architecture.md](./04-controller-architecture.md) | Guidelines for the core `BaseController` architecture isolating business logic from UI elements. | `2026-06-09` |
| [05-widget-management.md](./05-widget-management.md) | Safely caching, querying, and updating `.ui` components using `WidgetManager`. | `2026-06-09` |
| [COMPONENTS.md](./COMPONENTS.md) | Comprehensive breakdown of creating independent, reusable components leveraging `.ui` files and handlers. | `2026-06-09` |

## 3. Event System & Interactions

| File | Description | Last Synced |
|------|-------------|-------------|
| [03-observer-pattern.md](./03-observer-pattern.md) | Publisher-Subscriber structure with smart parameter injection and handler isolation. | `2026-05-26` |
| [08-network-manager.md](./08-network-manager.md) | Safe HTTP access integration utilizing `QNetworkAccessManager` for requests and REST responses. | `2026-06-09` |

## 4. Task System

| File | Description | Last Synced |
|------|-------------|-------------|
| [12-task-system-overview.md](./12-task-system-overview.md) | Complete overview of the internal background task system encompassing queues, schedulers, and tracking. | `2026-06-09` |
| [13-abstract-task.md](./13-abstract-task.md) | Outlines the base abstract properties, serialization structure, and capabilities of an enqueued task. | `2026-06-09` |
| [14-task-chain.md](./14-task-chain.md) | How to link multiple segmented tasks safely, transferring generic contexts or falling back via configurable fail states. | `2026-06-09` |
| [15-task-manager.md](./15-task-manager.md) | API orchestrating all background worker capabilities including limits and external scheduling routines. | `2026-06-09` |
| [16-acknowledgment-system.md](./16-acknowledgment-system.md) | Ensures safely synced task executions passing verification guarantees to components post-completion. | `2026-06-09` |
| [27-schedule-info.md](./27-schedule-info.md) | Typed scheduling containers (`DateScheduleInfo`, `IntervalScheduleInfo`, `CronScheduleInfo`) with fluent API replacing raw dicts. | `2026-06-09` |
| [28-task-state.md](./28-task-state.md) | Thread-safe injectable lifecycle state object powering cancellation, pause/resume, and cooperative stop checks in services. | `2026-06-09` |
| [29-task-storage.md](./29-task-storage.md) | Storage layer (`BaseStorage`, `JsonStorage`) and Unit of Work pattern (`WorkingSet`) for atomic task persistence. | `2026-06-09` |

## 5. System Utilities & Foundation

| File | Description | Last Synced |
|------|-------------|-------------|
| [06-configuration.md](./06-configuration.md) | Usage context surrounding the configuration system resolving secrets and runtime dynamic settings safely. | `2026-06-09` |
| [07-logging.md](./07-logging.md) | Standardized Loguru-powered logging conventions standardizing debugging formats and verbosity flags. | `2026-06-09` |
| [09-exceptions.md](./09-exceptions.md) | Base overarching `ExceptionHandler` implementation covering global safety nets for unhandled thread crashes. | `2026-06-09` |
| [10-utilities.md](./10-utilities.md) | Shared globally generic helper methods. | `2026-06-09` |
| [11-decorators.md](./11-decorators.md) | Custom Python decorators streamlining retries, performance checks, and threading synchronization mechanisms. | `2026-06-09` |
| [17-contracts.md](./17-contracts.md) | Base foundational interface traits enforcing static-typing protocols. | `2026-06-09` |
| [18-extends.md](./18-extends.md) | Anti-detection HTTP session (`AntiDetectSession`) using `curl_cffi` with browser impersonation and profile rotation. | `2026-06-09` |
| [19-model.md](./19-model.md) | Base models: `BaseAttributeModel` for attribute access and `DataTrackingMixin` for Qt model dirty tracking. | `2026-06-09` |
| [26-threading.md](./26-threading.md) | Reusable threading primitives for background execution, including `DaemonWorker`. | `2026-05-26` |

## 6. Development & Deployment

| File | Description | Last Synced |
|------|-------------|-------------|
| [20-common-use-cases.md](./20-common-use-cases.md) | Real-world scenario snippets applying these architectures inside practical UI or task flows. | `2026-06-09` |
| [22-pixi-guide.md](./22-pixi-guide.md) | Quick reference standardizing Pixi package management inside this project. | `2026-06-09` |
| [23-cli-scripts.md](./23-cli-scripts.md) | Tooling outlining the custom generator scripts inside the scaffolding command structure. | `2026-06-09` |
| [24-testing.md](./24-testing.md) | Pytest suite scaffolding standardizing unit mock logic and UI integration tests. | `2026-06-09` |
