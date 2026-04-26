# Application Core Reference Index

> **Directory of core architectural references with short summaries**

## 1. Application Architecture & Dependency Injection

| File | Description |
|------|-------------|
| [01-application-context.md](./01-application-context.md) | The central orchestrator for the application lifecycle, context, and environment bootstrap. |
| [02-dependency-injection.md](./02-dependency-injection.md) | Dependency injection principles utilizing `ServiceLocator` to decouple service dependencies. |
| [25-service-providers.md](./25-service-providers.md) | ServiceProvider architecture using topological sorting to safely register services at bootstrap. |

## 2. Controllers & UI Patterns

| File | Description |
|------|-------------|
| [04-controller-architecture.md](./04-controller-architecture.md) | Guidelines for the core `BaseController` architecture isolating business logic from UI elements. |
| [05-widget-management.md](./05-widget-management.md) | Safely caching, querying, and updating `.ui` components using `WidgetManager`. |
| [COMPONENTS.md](./COMPONENTS.md) | Comprehensive breakdown of creating independent, reusable components leveraging `.ui` files and handlers. |

## 3. Event System & Interactions

| File | Description |
|------|-------------|
| [03-observer-pattern.md](./03-observer-pattern.md) | Publisher-Subscriber structure with smart parameter injection and handler isolation. |
| [08-network-manager.md](./08-network-manager.md) | Safe HTTP access integration utilizing `QNetworkAccessManager` for requests and REST responses. |

## 4. Task System

| File | Description |
|------|-------------|
| [12-task-system-overview.md](./12-task-system-overview.md) | Complete overview of the internal background task system encompassing queues, schedulers, and tracking. |
| [13-abstract-task.md](./13-abstract-task.md) | Outlines the base abstract properties, serialization structure, and capabilities of an enqueued task. |
| [14-task-chain.md](./14-task-chain.md) | How to link multiple segmented tasks safely, transferring generic contexts or falling back via configurable fail states. |
| [15-task-manager.md](./15-task-manager.md) | API orchestrating all background worker capabilities including limits and external scheduling routines. |
| [16-acknowledgment-system.md](./16-acknowledgment-system.md) | Ensures safely synced task executions passing verification guarantees to components post-completion. |

## 5. System Utilities & Foundation

| File | Description |
|------|-------------|
| [06-configuration.md](./06-configuration.md) | Usage context surrounding the configuration system resolving secrets and runtime dynamic settings safely. |
| [07-logging.md](./07-logging.md) | Standardized Loguru-powered logging conventions standardizing debugging formats and verbosity flags. |
| [09-exceptions.md](./09-exceptions.md) | Base overarching `ExceptionHandler` implementation covering global safety nets for unhandled thread crashes. |
| [10-utilities.md](./10-utilities.md) | Shared globally generic helper methods. |
| [11-decorators.md](./11-decorators.md) | Custom Python decorators streamlining retries, performance checks, and threading synchronization mechanisms. |
| [17-contracts.md](./17-contracts.md) | Base foundational interface traits enforcing static-typing protocols. |
| [18-extends.md](./18-extends.md) | Reusable mixins extending class behaviors dynamically without strictly enforcing deep heritage. |
| [19-model.md](./19-model.md) | Structuring Pydantic dataclasses cleanly mapping persistent or networking shapes safely. |
| [26-threading.md](./26-threading.md) | Reusable threading primitives for background execution, including `DaemonWorker`. |

## 6. Development & Deployment

| File | Description |
|------|-------------|
| [20-common-use-cases.md](./20-common-use-cases.md) | Real-world scenario snippets applying these architectures inside practical UI or task flows. |
| [21-improvement-suggestions.md](./21-improvement-suggestions.md) | Pending conceptual architectural refactors and planned efficiency developments. |
| [22-pixi-guide.md](./22-pixi-guide.md) | Quick reference standardizing Pixi package management inside this project. |
| [23-cli-scripts.md](./23-cli-scripts.md) | Tooling outlining the custom generator scripts inside the scaffolding command structure. |
| [24-testing.md](./24-testing.md) | Pytest suite scaffolding standardizing unit mock logic and UI integration tests. |
