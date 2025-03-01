# Contributing to Wealth Manager

Thank you for your interest in contributing to Wealth Manager! We welcome contributions that help improve this project. By participating in this project, you agree to abide by our code of conduct and these contributing guidelines.

## How to Contribute

There are several ways to contribute to the project:

- **Reporting Bugs:** If you encounter any issues, please open an issue with a clear description and steps to reproduce the problem.
- **Suggesting Enhancements:** If you have an idea for a new feature or an improvement, please open an issue to discuss it before submitting a pull request.
- **Submitting Pull Requests:** If you would like to contribute code, please fork the repository, create a new branch for your feature or bug fix, and submit a pull request (PR).

## Pull Request Process

1. **Fork the Repository:**  
   Create your own fork of the repository on GitHub.

2. **Create a Feature Branch:**  
   Use a descriptive branch name, for example:  
   `feature/<short-description>` or `bugfix/<short-description>`.

3. **Make Your Changes:**  
   Ensure that your changes follow the project's coding standards.  
   Write tests for any new features or bug fixes, and ensure existing tests pass.

4. **Commit Your Changes:**  
   Write clear, concise commit messages that describe your changes.

5. **Submit a Pull Request:**  
   Open a PR against the `main` branch of the original repository. Include a summary of your changes and link to any relevant issues.

6. **Review Process:**  
   Once submitted, a maintainer will review your PR. Be sure to address any requested changes during the review.

## Code Style and Guidelines

- **Python Version:** Use Python 3.12.6 as configured in the project.
- **Formatting:** Follow PEP 8 guidelines. We recommend using a linter such as `flake8` to help automatically check your code.
- **Testing:**  
  Write tests for your changes using pytest. You can run tests and generate a coverage report with:
  ```bash
  pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
  ```
- **Commit Messages:**  
  Use clear, meaningful commit messages. If applicable, reference the relevant issue by its number (e.g., "Fixes #12").

## Reporting Issues

When reporting an issue, please include as much detail as possible:

- A brief summary of the issue.
- Steps to reproduce the issue.
- Expected and actual results.
- Environment details (OS, Python version, etc.).

## Additional Resources

- [README.md](README.md) — for an overview of the project.

## Questions?

If you have any questions or need further clarification about contributing to Wealth Manager, feel free to open an issue or contact the maintainers.

Thank you for helping make Wealth Manager better!