# Contributing to DocLingo

Thank you for your interest in contributing to DocLingo! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/DocLingo.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install dev dependencies: `pip install -r requirements_enhanced.txt`

## Development Workflow

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages: `git commit -m "Add feature: description"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Add docstrings following Google style:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """Brief description of the function.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
      """
  ```
- Keep functions focused and modular
- Use meaningful variable names

## Testing

- Test your changes thoroughly before submitting
- Include test cases for new features when possible
- Verify multilingual functionality works correctly
- Test with different PDF types (text-based, scanned, complex layouts)

## Documentation

- Update documentation for any new features
- Keep README.md current
- Add docstrings to all new functions and classes
- Update relevant files in `/docs` folder

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Keep PRs focused on a single feature or fix

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

## Questions?

Feel free to open an issue for questions or discussion about contributing.

Thank you for helping make DocLingo better!
