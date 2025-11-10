# Technology Stack

## Language & Runtime

- **Python 3.x** - Primary development language
- Windows environment (cmd shell)

## Frameworks & Libraries

- **PyQt/PySide** - GUI framework (inferred from UI components)
- Standard Python libraries for data processing and utilities

## Project Structure

- `src/` - Source code directory
  - `ui/` - User interface components
  - `services/` - Business logic and service layer
  - `utils/` - Utility functions and helpers
  - `data_sources/` - Data access layer
  - `integrations/` - External system integrations
- `docs/` - Documentation
- `data/` - Data files
- `.kiro/` - Kiro AI assistant configuration

## Common Commands

### Running the Application
```bash
python main.py
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Type checking (if using)
mypy src/
```

## Build System

- Standard Python package management (pip)
- Virtual environment recommended for dependency isolation
