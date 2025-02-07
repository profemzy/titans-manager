# Titans Manager

A comprehensive business management system built with Django, featuring project management, client management, task tracking, and financial operations.

## Features

- **Client Management**: Track and manage client information and relationships
- **Project Management**: Create and manage projects with associated tasks
- **Task Management**: Organize and track tasks with custom workflows
- **Financial Management**:
  - Expense tracking
  - Income management
  - Invoice generation
  - Financial reporting
- **User Management**: Role-based access control and user authentication
- **Admin Interface**: Customized Django admin for efficient data management

## Tech Stack

- **Backend**: Django 5.1.5
- **Database**: PostgreSQL
- **Container**: Docker
- **Orchestration**: Kubernetes
- **API Documentation**: drf-spectacular
- **Admin Interface**: django-jazzmin
- **Storage**: django-storages with Azure Blob Storage
- **Authentication**: djangorestframework-simplejwt
- **Testing**: pytest, factory_boy
- **Code Quality**: black, flake8
- **Import/Export**: django-import-export
- **File Handling**: Pillow, reportlab
- **Development Tools**: Custom management commands for data seeding

### Key Dependencies

```txt
Django==5.1.5
djangorestframework==3.15.2
psycopg2-binary==2.9.10
django-jazzmin==3.0.1
django-storages==1.14.4
azure-storage-blob==12.24.1
drf-spectacular==0.28.0
django-filter==24.3
django-import-export==4.3.4
django-admin-rangefilter==0.13.2
gunicorn==23.0.0
pytest==8.3.4
factory_boy==3.3.3
black==25.1.0
flake8==7.1.1
Pillow==11.1.0
reportlab==4.3.0
whitenoise==6.8.2
```

Full dependencies are available in `requirements.txt`.

## Project Structure

```
core/
├── admin/          # Django admin customizations
├── models/         # Database models
├── services/       # Business logic layer
├── views/          # API endpoints
├── tests/          # Test suite
└── management/     # Custom management commands
```

## Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd TitansManager
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory with necessary configurations.

4. **Run migrations**

```bash
python manage.py migrate
```

5. **Start the development server**

```bash
python manage.py runserver
```

## Docker Deployment

1. **Build the image**

```bash
docker build -t titans-manager .
```

2. **Run with docker-compose**

```bash
docker-compose up
```

## Kubernetes Deployment

Kubernetes configuration files are available in the `kubernetes/` directory:

- `deployment.yaml`: Main application deployment
- `service.yaml`: Service configuration
- `ingress.yaml`: Ingress rules
- `configmap.yaml`: Configuration values
- `hpa.yaml`: Horizontal Pod Autoscaling
- `pvc.yaml`: Persistent Volume Claims
- `pgadmin.yaml`: PostgreSQL admin interface

Apply the configurations:

```bash
kubectl apply -f kubernetes/
```

## Project Organization

- `core/`: Main application code
  - `models/`: Database models organized by domain
  - `services/`: Business logic implementation
  - `views/`: API endpoints and view logic
  - `admin/`: Admin interface customizations
  - `migrations/`: Database migrations
  - `tests/`: Test suite and factories

- `templates/`: HTML templates
  - `admin/`: Custom admin templates
  - `base.html`: Base template
  - `landing_page.html`: Main landing page

- `static/`: Static files (images, CSS, JS)

## API Structure

The API is organized by domains:
- `/api/auth/`: Authentication endpoints
- `/api/clients/`: Client management
- `/api/projects/`: Project operations
- `/api/tasks/`: Task management
- `/api/finance/`: Financial operations
  - `/expenses/`: Expense tracking
  - `/income/`: Income management
  - `/invoices/`: Invoice handling

## Testing

Run the test suite:

```bash
pytest
```

## Code Style and Linting

The project uses flake8 for code linting with the following configuration:

```ini
[flake8]
max-line-length = 106
extend-ignore = E203, W503, E402
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    *.pyc,
    *.egg-info,
    .eggs,
    migrations,
    .env,
    .venv,
    env,
    venv,
    ENV,
    staticfiles,
    media
per-file-ignores =
    */__init__.py: F401
max-complexity = 10
statistics = True
count = True
```

To run the linter:

```bash
flake8 .
```

### Code Formatting

The project uses `black` for code formatting. To format your code:

```bash
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Ensure your code follows the style guide (run black and flake8)
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

## License

[License Information]

## Support

[Support Information]