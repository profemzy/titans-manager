# Titans Manager

A comprehensive business management system built with Django, featuring project management, client management, task tracking, and financial operations.

## Features

- **Client Management**: Track and manage client information and relationships
- **Project Management**: Create and manage projects with associated tasks
- **Task Management**: 
  - Task creation and assignment
  - Status tracking (pending, in_progress, review, completed, blocked)
  - Priority levels (low, medium, high, urgent)
  - Dependencies tracking
  - Time tracking
- **Financial Operations**:
  - Expense tracking
  - Income management
  - Invoice generation
  - Financial reporting

## Tech Stack

- **Backend**: Django 5.1
- **Database**: PostgreSQL 17.2
- **Container**: Docker
- **Orchestration**: Kubernetes
- **Azure Services**:
  - Azure Kubernetes Service (AKS)
  - Azure Container Registry (ACR)

## Project Structure

```
core/
├── admin/          # Django admin customizations
├── models/         # Database models
│   ├── client.py
│   ├── project.py
│   ├── task.py
│   └── finance/    # Financial models
├── services/       # Business logic layer
│   ├── base.py
│   ├── client_service.py
│   ├── project_service.py
│   └── task_service.py
├── tests/          # Test suite
└── views/          # API endpoints
```

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```env
DATABASE_NAME=tmsdb
DATABASE_USERNAME=dbuser
DATABASE_PASSWORD=dbpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

4. Run migrations:
```bash
python manage.py migrate
```

## Testing

The project uses pytest for testing. Tests are organized by service:

- Client Service Tests
- Project Service Tests
- Task Service Tests
- Financial Service Tests

Run tests with coverage:
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=70
```

### Test Design Principles:
- Each service has its own test file
- Factory Boy for test data generation
- Freezegun for datetime testing
- Clear test isolation
- Comprehensive coverage of edge cases

## CI/CD Pipeline

The project uses GitHub Actions for CI/CD with the following stages:

### Continuous Integration
- Linting with flake8
- Code formatting with Black
- Unit tests with pytest
- Coverage reporting

### Continuous Deployment
- Builds Docker image
- Pushes to Azure Container Registry
- Deploys to AKS
- Includes health checks and rollback procedures

## Kubernetes Deployment

Configuration files in `kubernetes/` directory:
- `deployment.yaml`: Main application deployment
- `service.yaml`: Service configuration
- `ingress.yaml`: Ingress rules
- `configmap.yaml`: Configuration values
- `hpa.yaml`: Horizontal Pod Autoscaling

## Project Standards

### Code Style
- Black for code formatting
- Maximum line length: 106 characters
- flake8 for linting with customized rules

### Testing Standards
- Minimum coverage requirement: 50%
- Test isolation
- Clear test naming conventions
- Comprehensive docstrings
- Factory Boy for test data

### Git Workflow
1. Develop features on feature branches
2. Submit PRs to develop branch
3. Merge to master triggers production deployment
4. All PRs must pass tests and meet coverage requirements

## Contributing

1. Fork the repository
2. Create a feature branch from develop
3. Update tests to cover new functionality
4. Ensure all tests pass and coverage requirements are met
5. Submit PR with clear description of changes

## License

[License Information]