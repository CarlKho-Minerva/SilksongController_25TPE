# Contributing to Silksong Controller

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/CarlKho-Minerva/SilksongController_25TPE/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/CarlKho-Minerva/SilksongController_25TPE/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

### Android Development

1. Install Android Studio
2. Open the project in `AndroidStudio/` directory
3. Sync Gradle and build the project

### Python Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Code Style

### Android (Kotlin)

- Follow [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- Use Android Studio's built-in formatting (Ctrl+Alt+L)
- Follow [Android best practices](https://developer.android.com/guide)

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `black` for code formatting
- Use `flake8` for linting
- Use `mypy` for type checking

Run formatting and linting:
```bash
black .
flake8 .
mypy .
```

## Testing

### Android

- Write unit tests for business logic
- Write UI tests for user interactions
- Run tests with: `./gradlew test`

### Python

- Write unit tests using `pytest`
- Aim for high test coverage
- Run tests with: `pytest`

## Documentation

- Update README.md for any new features
- Add docstrings to Python functions and classes
- Add KDoc comments to Kotlin functions and classes
- Update API documentation when changing interfaces

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
