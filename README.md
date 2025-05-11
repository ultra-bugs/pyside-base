# UltraBugz pyside_base - Desktop application ship faster

> Also have a Tiếng Việt version of this README: [README.vi.md](./README.vi.md)

## Inspired Mindset

This base Qt application is not just a code scaffold but a mindset for software development: clear separation of
responsibilities, leveraging the Observer Pattern, and automating workflows, so you can focus on creativity. Every line
of code here is designed to encourage flexibility, reusability, and long-term scalability.

---

## 1. Table of Contents

1. [Philosophy & Mindset](#philosophy--mindset)
2. [Project Initialization](#project-initialization)
3. [Structure & Modular Spirit](#structure--modular-spirit)
4. [Core Components & Mindset](#core-components--mindset)

   * Controller & Handler: Separate UI and events
   * Service: Pure logic, UI-agnostic
   * Component & Widget Manager: Reusable, stateful
   * Task System & Middleware: Automated, non-blocking UI
5. [CLI Scaffolding: Speed & Consistency](#cli-scaffolding-speed--consistency)
6. [Theme & Configuration: Self-Service](#theme--configuration-self-service)
7. [Observer Pattern: Decoupled Communication](#observer-pattern-decoupled-communication)
8. [Best Practices & Coding Philosophy](#best-practices--coding-philosophy)
9. [Contributing](#contributing)
10. [License](#license-1)

There are other components also documented. See in [Docs](./docs).

---

## Philosophy & Mindset

1. **Separation of Concerns**: Each module has a single responsibility—UI displays, Service handles logic, Handler
   responds to events. This keeps code maintainable and scalable.
2. **Automation First**: The Task System and CLI scaffolding accelerate development, reduce manual errors, and let you
   focus on core algorithms.
3. **Observer Pattern**: Reduces coupling between classes; components communicate via events, ensuring extensibility and
   flexible changes.
4. **Modularity & Reusability**: Everything is a plugin or small component—easy to replace, test, and reuse across
   projects.

---

## Project Initialization

Get your app skeleton ready with the right mindset:
1. Use template:

   ```bash
   gh repo create my-app --template=https://github.com/ultra-bugs/pyside-base
   ```

2. **Clone & Install**

   ```bash
   git clone <your-new-repo-url> my-app
   cd my-app
   pip install -r requirements.txt
   ```

3. **Set Basic Info**

   ```bash
   python scripts/set_app_info.py --name "My App" --version "1.0.0"
   ```

4. **Generate Main Controller & UI**

   ```bash
   python scripts/generate.py controller YourController
   python scripts/compile_ui.py
   ```

> **Mindset**: Automate setup, save time, and ensure every project starts with a consistent structure.

---

## Structure & Modular Spirit

```
base/
├── core/             # Framework & template patterns
├── windows/          # Views, controllers and event handlers
│   ├── components/   # Reusable UI components (widgets)
│   └── main/         # Main window
├── services/         # Independent business logic
├── models/           # Reusable UI components
├── scripts/          # CLI tools & scaffolding
├── assets/           # Resources (images, sounds, translations)
│   └── icon.png      # Default application icon
├── data/             # User data and embedded app data
│   ├── config/       # Configuration files
│   └── logs/         # Log files
├── vendor/           # Third-party resources
└── plugins/          # App plugins
```

> **Mindset**: Each folder is an independent module, easy to test, develop in parallel, and swap without affecting the
> system.

---

## Core Components & Mindset

### Controller & Handler: Separate UI and Events

* **Controller** wires up UI to events using a `slot_map`, without embedding business logic.
* **Handler (Subscriber)** listens for events, processes them, and responds, completely decoupled from UI concerns.

```python
# in controller
class MyController(BaseController):
   # Mapping show: when `pushButton` has been `clicked`. The method named `on_open_btn_click` on handler will be called
   slot_map = {
      'open_btn_click': ['pushButton', 'clicked']
   }

# in handler
class MyControllerHandler(Subscriber):
   def on_open_btn_click(self, data = None):
      # Event handling logic
      pass
```

> **Mindset**: Keep business logic out of UI events—Controllers merely proxy events.

---

### Service: Pure Logic

* Receives input, processes it, returns results—has no knowledge of the UI.
* Fully unit-testable and reusable.

```python
class MyService:
   def fetch_data(self) -> List[Dict]:
      # Data processing logic
      return []
```

> **Mindset**: Treat each service as a microservice within the repo—independent and maintainable.

---

### Widget Manager: Reusable & Stateful


* **WidgetManager** provides dot-notation access, suppresses signals during updates, and auto-saves configuration.

```python
widget_manager.set('slider.value', 50, save_to_config=True)
```

> **Mindset**: Each component has a clear responsibility; state is managed centrally to avoid side effects.

---

### Task System & Middleware: Automated & Non-Blocking UI

* Supports multi-threading, scheduling, and chainable middleware.
* Breaks workflows into `TaskStep`s for easy monitoring, retries, logging, and captcha handling.

```python
task = task_manager.create_task("SyncData")
task.add_step(FetchStep())
task.add_step(ProcessStep())
task_manager.run_task(task)
```

> **Mindset**: Offload heavy tasks to the background; keep the UI responsive.

---

## CLI Scaffolding: Speed & Consistency

Quickly scaffold Controllers, Services, Components, Tasks, and Steps with a single command:

```bash
python scripts/generate.py controller MyController
python scripts/generate.py service MyService
```

> **Mindset**: Enforce naming and structure conventions, reduce boilerplate time.
> 
For full list scripts/commands. See [CLI.md](./docs/CLI.md)

---

## Theme & Configuration: Self-Service

Leverage `qdarktheme` with `auto | light | dark` modes. Configuration is done via the `Config` class.

```python
config.set('ui.theme', 'dark')
qdarktheme.setup_theme(config.get('ui.theme'))
```

> **Mindset**: Empower both end-users and developers to customize without hardcoding.

---

## Observer Pattern: Decoupled Communication

* **Publisher**: A singleton that connects Qt signals into a unified event system.
* **Subscriber (Handler)**: Registers `on_<event_name>` handlers—add or remove listeners without touching Controllers.

```python
def on_button_clicked(self, data = None):
   # Event handling logic
   pass
```

> **Mindset**: Modules know only about events, not each other—enabling easy system expansion.

---

## Best Practices & Coding Philosophy

1. **Single Responsibility**: Each file and class has one reason to change.
2. **Testable**: Write unit tests for Services and Middleware.
3. **Config-Driven**: Alter behavior via configuration, not code changes.
4. **Logging & Error Handling**: Use middleware to capture errors, retry logic, and contextual logging.
5. **Documentation**: Provide clear help for every component, service, and CLI command.

---

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for guidelines.

---

## License

Released under the MIT License. See the `LICENSE` file for details.
