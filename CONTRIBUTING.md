# Contributing to AlgoBizSuite

First off, thank you for considering contributing to AlgoBizSuite! It's people like you that make this project a great tool for the Odoo and Algorand communities.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Numbered steps to reproduce the behavior
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS: [e.g., macOS 13, Ubuntu 22.04]
  - Odoo Version: [e.g., 19.0]
  - Docker Version: [e.g., 20.10]
  - Module Version: [e.g., 19.0.1.0.0]
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** and description
- **Use case**: Why is this enhancement useful?
- **Proposed solution**: How you envision it working
- **Alternatives considered**: Other solutions you've thought about

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed
3. **Test your changes**:
   - Test on both TestNet and MainNet (if applicable)
   - Ensure existing tests pass
   - Add new tests for new features
4. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issues and PRs liberally
5. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Git
- Python 3.13 (for local development)

### Getting Started

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/algobizsuite.git
   cd algobizsuite
   ```

2. Create `.env` file from template:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Access Odoo at http://localhost:8069

### Running Tests

```bash
# Run Odoo tests for the module
docker-compose exec odoo19 odoo -d mydb -u algorand_pera_payment --test-enable --stop-after-init
```

## Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Maximum line length: 88 characters (Black default)

### Odoo-Specific

- Follow [OCA guidelines](https://github.com/OCA/maintainer-tools)
- Use Odoo's standard module structure
- Include proper `__manifest__.py` metadata
- Add proper security rules (`ir.model.access.csv`)

### JavaScript

- Use modern ES6+ syntax
- Follow Odoo's JavaScript style guide
- Use `eslint` for linting

### XML

- Proper indentation (4 spaces)
- Descriptive IDs
- Follow Odoo's view inheritance patterns

## Documentation

- Update README.md if you change functionality
- Add docstrings to Python functions and classes
- Update the module's `readme/` fragments if applicable
- Regenerate README.rst using `oca-gen-addon-readme`

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(payment): add support for ASA payments

Add support for Algorand Standard Assets (ASA) payments
including USDC on both TestNet and MainNet.

Closes #123
```

```
fix(transaction): resolve race condition in payment status

Fix race condition where payment status page showed stale
transaction data due to session not being saved properly.

Fixes #456
```

## Module-Specific Guidelines

### Algorand Pera Payment Module

- Test on both TestNet and MainNet
- Verify USDC opt-in flows
- Check transaction verification
- Ensure error handling is comprehensive
- Test wallet connection/disconnection
- Verify cart clearing behavior

## Review Process

1. All pull requests require review
2. Automated checks must pass (when CI/CD is set up)
3. At least one maintainer approval required
4. Changes should be tested in a development environment
5. Documentation must be updated

## Community

- **Issues**: Report bugs and suggest features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute code and documentation

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
- The project README
- Module contributor lists
- Release notes

Thank you for contributing! 🎉

