# Jenkins Configuration Guide

## Overview
This directory contains Jenkins configuration files and pipeline definitions for the CI/CD pipeline.

## Files

- **Jenkinsfile**: Pipeline definition using Groovy DSL

## Jenkinsfile Overview

The Jenkinsfile defines a complete CI/CD pipeline with the following stages:

### Pipeline Stages

1. **Checkout**
   - Clones the repository from GitHub
   - Requires GitHub credentials configured in Jenkins

2. **Build**
   - Builds Docker image with tags
   - Tags include build number and "latest"

3. **Test**
   - Runs pytest (if available)
   - Non-blocking if tests aren't found

4. **Stop Old Container**
   - Stops and removes previous container
   - Prevents port conflicts

5. **Deploy**
   - Runs new container with restart policy
   - Sets environment variables
   - Exposes port 5000

6. **Verify Deployment**
   - Waits up to 60 seconds for app to respond
   - Checks health endpoint
   - Fails pipeline if app doesn't respond

## Setup Instructions

### 1. Initial Jenkins Setup

Once Jenkins is running:

1. Navigate to `http://your-jenkins-server:8080`
2. Complete initial setup wizard
3. Create admin user account
4. Install recommended plugins

### 2. Install Required Plugins

Go to **Manage Jenkins > Manage Plugins > Available**

Search and install:
- **Docker Pipeline** - For Docker support in pipelines
- **GitHub** - For GitHub integration
- **Pipeline** - Already included, but verify
- **Timestamper** - For timestamped console output
- **Email Extension** - For email notifications (optional)
- **Slack Notification** - For Slack notifications (optional)

### 3. Configure Credentials

Go to **Manage Jenkins > Manage Credentials > System > Global credentials**

Add GitHub credentials:
1. Click **Add Credentials**
2. Kind: **Username with password**
3. Scope: **Global**
4. Username: Your GitHub username
5. Password: Your GitHub personal access token
6. ID: `github-credentials`
7. Description: GitHub credentials for CI/CD

### 4. Create Pipeline Job

1. **New Item**
2. Enter job name: `cicd-python-app`
3. Select **Pipeline**
4. Click **OK**

### 5. Configure Pipeline

In the Pipeline section:

- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/yourusername/cicd-python-app.git`
- **Credentials**: Select GitHub credentials
- **Branch Specifier**: `*/main`
- **Script Path**: `jenkins/Jenkinsfile`

### 6. Configure Build Triggers (Optional)

**Option A: Poll SCM** (Check GitHub every X minutes)
- Check **Poll SCM**
- Schedule: `H/15 * * * *` (every 15 minutes)

**Option B: GitHub Hook Trigger**
- Check **GitHub hook trigger for GITScm polling**
- Configure GitHub webhook (see below)

### 7. Configure GitHub Webhook

To trigger builds automatically when code is pushed:

**In GitHub:**
1. Go to repository Settings
2. Select **Webhooks**
3. Click **Add webhook**
4. Payload URL: `http://your-jenkins-server:8080/github-webhook/`
5. Content type: `application/json`
6. Events: Just the push event
7. Click **Add webhook**

## Environment Variables

The pipeline uses these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `APP_NAME` | `cicd-python-app` | Application name |
| `DOCKER_REGISTRY` | `docker.io` | Docker registry |
| `DOCKER_IMAGE_NAME` | `${REGISTRY}/${APP_NAME}` | Full image name |
| `DOCKER_IMAGE_TAG` | Build number | Unique tag per build |
| `PYTHON_VERSION` | `3.9` | Python version in Docker |

## Build Process Flow

```
GitHub Push
    ↓
Jenkins Webhook
    ↓
Start Build
    ↓
Checkout Code
    ↓
Build Docker Image
    ↓
Run Tests
    ↓
Stop Old Container
    ↓
Deploy New Container
    ↓
Verify Deployment
    ↓
Build Success/Failure
    ↓
Clean Workspace
```

## Viewing Build Logs

1. Click on build number in build history
2. Click **Console Output**
3. View real-time logs with timestamps

## Running Manual Builds

1. Go to job
2. Click **Build Now**
3. Monitor progress in build history

## Configuring Notifications

### Email Notifications

1. Go to **Manage Jenkins > Configure System**
2. Scroll to **Extended E-mail Notification**
3. Configure SMTP settings
4. In job configuration, add post-build action

### Slack Notifications

1. Install Slack Notification plugin
2. Go to **Manage Jenkins > Configure System**
3. Configure Slack workspace and token
4. Add Slack notification step to Jenkinsfile

Example:
```groovy
post {
    success {
        slackSend(color: 'good', message: 'Build succeeded!')
    }
    failure {
        slackSend(color: 'danger', message: 'Build failed!')
    }
}
```

## Troubleshooting

### Build Fails at Clone Stage

**Problem**: Git clone fails with authentication error

**Solution**:
1. Verify GitHub credentials in Jenkins
2. Check repository URL is correct
3. Verify GitHub account has access to repository
4. Test credentials: `ssh -T git@github.com`

### Build Fails at Docker Build

**Problem**: Docker image fails to build

**Solution**:
1. Check Dockerfile syntax
2. Verify Docker is running: `docker ps`
3. Check Jenkins user can run docker: `sudo usermod -aG docker jenkins`
4. Restart Jenkins: `sudo systemctl restart jenkins`

### Build Fails at Deploy Stage

**Problem**: Container fails to start

**Solution**:
1. Check port 5000 is not already in use: `netstat -tuln | grep 5000`
2. Check Docker logs: `docker logs cicd-python-app`
3. Verify image built correctly: `docker images`
4. Test locally: `docker run -p 5000:5000 cicd-python-app:latest`

### Verification Fails

**Problem**: Application doesn't respond to health check

**Solution**:
1. Check container is running: `docker ps`
2. Check logs: `docker logs cicd-python-app`
3. Test manually: `curl http://localhost:5000/health`
4. Check if app is listening: `docker exec cicd-python-app netstat -tuln`

## Security Best Practices

1. **Use GitHub tokens instead of passwords**
2. **Enable Build Name Updater** for better tracking
3. **Use Jenkins credentials** for all secrets
4. **Restrict job permissions** to authorized users
5. **Enable audit logs** for compliance
6. **Use HTTPS** for Jenkins UI in production
7. **Keep Jenkins updated** with latest patches

## Advanced Configuration

### Custom Workspace

```groovy
agent {
    node {
        label 'docker'
        customWorkspace '/var/jenkins_workspace/cicd-python-app'
    }
}
```

### Parallel Stages

```groovy
stages {
    stage('Test & Security') {
        parallel {
            stage('Unit Tests') {
                steps {
                    // Test commands
                }
            }
            stage('Security Scan') {
                steps {
                    // Security scan commands
                }
            }
        }
    }
}
```

### Conditional Execution

```groovy
when {
    branch 'main'
}
```

## Performance Optimization

1. **Clean old builds**: Configure build discarder
2. **Use caching**: Cache Docker layers with buildkit
3. **Parallel execution**: Run tests in parallel when possible
4. **Minimize artifacts**: Clean workspace after builds

## Integration with Other Tools

### SonarQube Integration

```groovy
stage('Code Quality') {
    steps {
        withSonarQubeEnv('SonarQube') {
            sh 'sonar-scanner'
        }
    }
}
```

### ArgoCD Integration

```groovy
stage('Deploy to K8s') {
    steps {
        sh 'argocd app sync cicd-python-app'
    }
}
```

## Monitoring and Metrics

- **Jenkins Metrics Plugin**: Track build times and success rates
- **GitHub Commit Status**: Show build status on commits
- **Build Time Trend Graph**: Available in job dashboard

## Backup and Restore

### Backup Jenkins Configuration

```bash
# Backup Jenkins home directory
sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins/

# Copy to safe location
sudo cp jenkins-backup.tar.gz /backup/
```

### Restore Jenkins Configuration

```bash
sudo systemctl stop jenkins
sudo tar -xzf jenkins-backup.tar.gz -C /
sudo systemctl start jenkins
```

## Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Jenkinsfile Syntax](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Pipeline Examples](https://www.jenkins.io/doc/pipeline/tour/overview/)
- [Docker in Jenkins](https://plugins.jenkins.io/docker-workflow/)
