# Contributing to OpenAI ToDo App

Thank you for your interest in contributing to the OpenAI ToDo App! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openai-todo-app.git
   cd openai-todo-app
   ```

3. **Set up the development environment**:
   ```bash
   nix-shell  # or nix develop
   just init
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** for your changes:
   ```bash
   just test
   ```

4. **Format your code**:
   ```bash
   just format
   ```

5. **Run linting**:
   ```bash
   just lint
   ```

6. **Commit your changes** with a clear commit message:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

## Commit Message Guidelines

We follow the Conventional Commits specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add due date support to todos
fix: resolve issue with todo deletion
docs: update README with new endpoints
test: add tests for storage module
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable names

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting a PR
- Aim for high test coverage
- Test both happy paths and edge cases

Run tests:
```bash
just test
```

## Pull Request Process

1. **Update documentation** if needed (README, docstrings, etc.)
2. **Ensure all tests pass** and code is formatted
3. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```
4. **Create a Pull Request** on GitHub
5. **Describe your changes** clearly in the PR description
6. **Link any related issues** using keywords like "Fixes #123"
7. **Wait for review** and address any feedback

## Pull Request Checklist

- [ ] Code follows the project style guidelines
- [ ] Tests have been added or updated
- [ ] All tests pass
- [ ] Documentation has been updated
- [ ] Commit messages follow the convention
- [ ] No unnecessary files are included
- [ ] Branch is up to date with main

## Adding New Features

When adding new features, consider:

1. **API Design**: Is the API intuitive and consistent?
2. **MCP Integration**: Does it work with the MCP protocol?
3. **UI/UX**: How will users interact with this feature?
4. **Performance**: Will this impact performance?
5. **Testing**: How will you test this feature?
6. **Documentation**: What documentation is needed?

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: OS, Python version, etc.
6. **Logs**: Any relevant error messages or logs

## Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly
3. **Explain the use case** - why is this needed?
4. **Provide examples** if applicable
5. **Consider implementation** - how might it work?

## Questions?

If you have questions about contributing:

1. Check the [README](README.md)
2. Review existing issues and PRs
3. Open a new issue with the "question" label

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the OpenAI ToDo App! 🎉
