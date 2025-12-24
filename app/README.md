# Python Application Guide

## Overview
This directory contains the Python Flask application that gets deployed via the CI/CD pipeline.

## Application Structure

```
app/
├── app.py           # Flask application
├── Dockerfile       # Docker image definition
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Application Details

### app.py

Flask web application with multiple endpoints:

- **`/`** - Main endpoint, returns application info
- **`/health`** - Health check endpoint for monitoring
- **`/info`** - Application metadata

### Endpoints

#### GET /
Returns application information:
```json
{
    "message": "Hello from CI/CD Python App!",
    "version": "1.0.0",
    "environment": "production",
    "status": "running"
}
```

#### GET /health
Health check endpoint for monitoring and load balancers:
```json
{
    "status": "healthy",
    "service": "cicd-python-app",
    "environment": "production"
}
```

#### GET /info
Detailed application information:
```json
{
    "app_name": "cicd-python-app",
    "version": "1.0.0",
    "description": "CI/CD Pipeline Deployment Demo",
    "endpoints": {
        "/": "Main endpoint",
        "/health": "Health check",
        "/info": "Application info"
    }
}
```

## Development Setup

### Local Development

#### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run Application

```bash
export FLASK_ENV=development
python app.py
```

Application runs on `http://localhost:5000`

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## Docker

### Building Docker Image

```bash
# Build image
docker build -t cicd-python-app .

# Build with tag
docker build -t cicd-python-app:latest .
```

### Running Docker Container

```bash
# Run container
docker run -d -p 5000:5000 --name cicd-python-app cicd-python-app

# Run with environment variables
docker run -d -p 5000:5000 \
    -e FLASK_ENV=production \
    --name cicd-python-app \
    cicd-python-app

# Run with volume mount (for development)
docker run -d -p 5000:5000 \
    -v $(pwd):/app \
    --name cicd-python-app \
    cicd-python-app
```

### Checking Container

```bash
# List running containers
docker ps

# View logs
docker logs cicd-python-app

# View logs in real-time
docker logs -f cicd-python-app

# Execute command in container
docker exec -it cicd-python-app bash

# Check health
docker ps --filter="name=cicd-python-app" --format="table {{.Names}}\t{{.Status}}"
```

### Stopping Container

```bash
# Stop container
docker stop cicd-python-app

# Remove container
docker rm cicd-python-app

# Stop and remove
docker stop cicd-python-app && docker rm cicd-python-app
```

## Dockerfile Overview

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs Python dependencies
2. **Production Stage**: 
   - Creates non-root user for security
   - Copies dependencies from builder
   - Sets up health checks
   - Runs application as non-root user

### Features

- **Security**: Non-root user (appuser)
- **Health Checks**: Automatic container health monitoring
- **Optimization**: Multi-stage build reduces image size
- **Environment**: Configurable via environment variables

## Requirements

### Python Dependencies

- **Flask 2.3.2**: Web framework
- **Werkzeug 2.3.6**: WSGI utilities
- **python-dotenv 1.0.0**: Environment variable management
- **pytest 7.4.0**: Testing framework

View [requirements.txt](requirements.txt) for exact versions.

## Environment Variables

- **FLASK_ENV**: `development` or `production` (default: production)
- **FLASK_APP**: Flask application file (default: app.py)
- **PYTHONUNBUFFERED**: Disable Python output buffering (set to 1)

### Setting Environment Variables

In container:
```bash
docker run -e FLASK_ENV=development cicd-python-app
```

Locally:
```bash
export FLASK_ENV=development
python app.py
```

## Testing

### Unit Tests

Create `tests/test_app.py`:

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_info(client):
    response = client.get('/info')
    assert response.status_code == 200
    assert 'app_name' in response.json

def test_main(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'message' in response.json
```

Run tests:
```bash
pytest tests/ -v
```

## Deployment

### Via Ansible

The application is deployed using Ansible roles. See [../ansible/README.md](../ansible/README.md)

### Manual Deployment

1. Clone repository
2. Build Docker image
3. Run container
4. Verify health endpoints

### Kubernetes Deployment

Example deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cicd-python-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cicd-python-app
  template:
    metadata:
      labels:
        app: cicd-python-app
    spec:
      containers:
      - name: cicd-python-app
        image: cicd-python-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Performance Optimization

### Docker Image Optimization

- Multi-stage build reduces final image size
- Non-root user improves security
- Health checks enable monitoring

### Application Optimization

- WSGI server (Gunicorn) for production
- Connection pooling for databases
- Caching strategies

### Production Recommendations

Use Gunicorn for production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Update Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

1. **Non-root User**: Application runs as `appuser` (UID 1000)
2. **Read-only Filesystem**: Consider using read-only mounts
3. **Environment Secrets**: Use Docker secrets or external vault
4. **Image Scanning**: Scan with tools like Trivy or Grype
5. **Keep Dependencies Updated**: Regular dependency updates

## Logging

Application logs are output to stdout, visible via:

```bash
docker logs cicd-python-app
```

For structured logging, consider adding:

```python
import json
import logging

# Configure JSON logging
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Log as JSON
logger.info(json.dumps({
    "timestamp": datetime.now().isoformat(),
    "level": "INFO",
    "message": "Application started"
}))
```

## Monitoring

### Health Check Endpoint

Monitoring tools can use `/health`:

```bash
curl -s http://localhost:5000/health | jq .
```

### Metrics Collection

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.route('/')
def hello():
    request_count.inc()
    return jsonify({...})
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs cicd-python-app

# Verify image
docker images | grep cicd-python-app

# Test locally
python app.py
```

### Port Already in Use

```bash
# Find what's using port 5000
lsof -i :5000

# Use different port
docker run -p 5001:5000 cicd-python-app
```

### Application Crashes

```bash
# Check exit code
docker inspect cicd-python-app | grep -i exitcode

# View full logs
docker logs cicd-python-app --tail=100
```

## Extending the Application

### Add New Endpoint

```python
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "data": [1, 2, 3],
        "status": "success"
    }), 200
```

### Add Database

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@db:5432/app'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
```

### Add Authentication

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Verify logic
    return username == 'admin' and password == 'secret'

@app.route('/protected')
@auth.login_required
def protected():
    return jsonify({"message": f"Hello, {auth.current_user()}"})
```

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Best Practices](https://pep8.org/)
- [WSGI Application Deployment](https://wsgi.readthedocs.io/)
