## Messaging App

This is an app where users can hold conversations.

#### Testing its Functionality on Postman.


```bash
Messaging App Tests
    Authentication
        POST /login
        Refress Token
        Logout
    Conversations
        Create Conversation
        List Conversation
        Get Conversation
        Filter Conversation
    Messages
        Send Messages
        List Messages
        Update Messages
        Delete Messages
        Filter Messages
    Error Handling
        Unauthorized Tests
        Permission Tests  
```
#### Creating  a Test User.
* **Admin**
```bash
python manage.py createsuperuser
```
* **Basic User**
```bash
python manage.py shell
```
Then inside the Python Shell
```bash
from chats.models import User
user1 = User.objects.create_user(username='testuser3', email='testuser3@test.com', password='testpass123')
user2 = User.objects.create_user(username='testuser4', email='testuser4@test.com', password='testpass123')
```

#### Authentication testing.

* **Login/Get Token(POST)**
URL - `/api/token`
Body(raw JSON)
```bash
{
    "username": "testuser3",
    "password": "testpass123"
}
```

* **Refresh Token(POST)**
URL - `/api/token/refresh`
```bash
{
    "refresh": "{{refresh_token}}"
}
```

* **Logout(POST)**
URL - `/api/logout`
```bash
{
    "token": "{{refresh_token}}"
}
```

* **Create Conversations(POST)**
URL - `/api/conversations/`
```bash
{
    "title": "Test Conversation"
}
```

* **List User Conversations(GET)**
URL - `/api/conversations/`
Headers: `Authorization: Bearer {{access_token}}`

---

## Docker & Kubernetes Utilization

### DOCKER

#### 1. Dockerfile
- **Base image**: Python 3.10
- **Environment variables**: 
  - `PYTHONDONTWRITEBYTECODE=1` (prevents .pyc file creation)
  - `PYTHONUNBUFFERED=1` (ensures logs are output immediately)
- **System dependencies**: MySQL dev libraries, gcc
- **Installs**: Python requirements from `requirements.txt`
- **Exposed port**: 8000 for Django application
- **Command**: Runs Django development server with `runserver 0.0.0.0:8000`

#### 2. Docker Compose (docker-compose.yml)
- **Services**:
  - `db`: MySQL 8.0 container with health checks and data persistence
  - `web`: Django app container that depends on db service
- **Features**:
  - Environment-based configuration (DB_NAME, DB_USER, DB_PASSWORD via `.env`)
  - Auto-migration and server startup on container start
  - Volume mounting for code changes during development
  - Health checks for database readiness before app starts

### KUBERNETES

#### 1. Deployments
- **Blue Deployment** (`blue_deployment.yaml`):
  - 3 replicas of the messaging app
  - Image: `messaging-app:2.0` with `imagePullPolicy: Never` (local images only)
  - Resource limits: CPU (250m requests, 500m limits), Memory (256Mi requests, 512Mi limits)
  - Environment variables for configuration (DEBUG, DB_HOST, DB_PORT, SECRET_KEY, etc.)

#### 2. Services (kubeservice.yaml)
- **Three service definitions**:
  - `messaging-app-blue-service`: Routes to blue deployment pods (stable version)
  - `messaging-app-green-service`: Routes to green deployment pods (new version)
  - `messaging-app-service`: Main service that initially points to blue version
  - All use ClusterIP type on port 8000

#### 3. Deployment Strategies
- **Blue-Green Deployment** (`kubctl-0x02`):
  - Runs blue version (current/stable) with 3 replicas
  - Deploys green version (new) in parallel
  - Checks deployment readiness
  - Monitors pod logs for errors
  - Switches traffic via service selector update when ready
  - Allows rollback by switching selector back to blue

- **Rolling Update** (`kubctl-0x03`):
  - Tests new version (2.0) with continuous health checks
  - Implements zero-downtime updates by gradually replacing old pods
  - Monitors rollout status with `kubectl rollout status`
  - Performs continuous testing (HTTP requests every 2 seconds)
  - Tracks success rate and detects any downtime

### CI/CD PIPELINE (Jenkins)

The Jenkinsfile automates the entire workflow:

1. **Checkout** - Pulls code from GitHub
2. **Setup Environment** - Creates Python venv, installs dependencies
3. **Lint Code** - Runs flake8 for code quality (E9, F63, F7, F82 checks)
4. **Run Tests** - Pytest with coverage reports and HTML output
5. **Generate Reports** - Publishes test and coverage reports
6. **Build & Push Docker Image** - Builds image with build number tag and pushes to Docker Hub
7. **Cleanup** - Removes local images after push

**Registry**: Pushes to `leonemunyao/messaging-app:<BUILD_NUMBER>` and `:latest`

### KEY INSIGHTS

**High Availability**: 3 replicas ensure service availability  
**Zero-Downtime Deployments**: Blue-green and rolling update strategies  
**Local Development**: Docker Compose with MySQL for local testing  
**Resource Management**: Defined CPU/memory requests and limits  
**Continuous Testing**: Automated health checks during deployments  
**Automated CI/CD**: Full pipeline from code to Docker Hub to Kubernetes  
**Environment Config**: Uses environment variables for flexibility
