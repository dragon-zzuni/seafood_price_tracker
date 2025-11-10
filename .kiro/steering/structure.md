# Project Structure

## Directory Organization

```
/
├── .kiro/              # Kiro AI configuration
│   ├── steering/       # AI guidance documents
│   └── specs/          # Feature specifications
├── src/                # Source code
│   ├── ui/             # User interface components
│   │   ├── panels/     # UI panels
│   │   ├── dialogs/    # Dialog windows
│   │   └── widgets/    # Reusable UI widgets
│   ├── services/       # Business logic services
│   ├── utils/          # Utility functions
│   ├── data_sources/   # Data access layer
│   ├── integrations/   # External integrations
│   └── nlp/            # Natural language processing
├── docs/               # Documentation
├── data/               # Data files
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Code Organization Principles

### Layered Architecture

1. **UI Layer** (`src/ui/`) - Presentation logic only
2. **Service Layer** (`src/services/`) - Business logic and orchestration
3. **Data Layer** (`src/data_sources/`) - Data access and persistence
4. **Integration Layer** (`src/integrations/`) - External system communication

### Module Responsibilities

- **UI components** should be thin, delegating logic to services
- **Services** contain business logic and coordinate between layers
- **Utils** provide reusable helper functions
- **Data sources** abstract data access patterns

## File Naming Conventions

- Use snake_case for Python files: `my_module.py`
- Use descriptive names that indicate purpose
- Group related functionality in subdirectories
- Test files should mirror source structure

## Import Guidelines

- Use absolute imports from project root
- Group imports: stdlib, third-party, local
- Avoid circular dependencies between modules
