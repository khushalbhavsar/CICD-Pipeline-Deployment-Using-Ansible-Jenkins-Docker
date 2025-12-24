# CI/CD Pipeline Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step 1: Prepare Target Servers](#step-1-prepare-target-servers)
4. [Step 2: Configure Ansible](#step-2-configure-ansible)
5. [Step 3: Deploy Infrastructure](#step-3-deploy-infrastructure)
6. [Step 4: Configure Jenkins](#step-4-configure-jenkins)
7. [Step 5: Verify Deployment](#step-5-verify-deployment)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- **Local Machine**: 
  - Ansible 2.10+ installed
  - Git installed
  - SSH access to target servers
  - Basic Linux/Bash knowledge

- **Target Servers** (Ubuntu 20.04+):
  - SSH access with key-based authentication
  - `sudo` privileges for the deployment user
  - Internet connectivity for package downloads
  - Recommended: 2+ vCPU, 4+ GB RAM, 20+ GB storage

- **GitHub Repository**:
  - Your Python app code pushed to GitHub
  - README with setup instructions

## Architecture Overview

```
┌─────────────┐
│   GitHub    │
└──────┬──────┘
       │ (webhooks/polling)
       ▼
┌─────────────────────────────────────────┐
│    Jenkins Server (Automated Setup)      │
│  ┌──────────────────────────────────────┐│
│  │ • Clones code from GitHub            ││
│  │ • Builds Docker image                ││
│  │ • Runs tests                         ││
│  │ • Pushes to Docker registry (opt)    ││
│  │ • Triggers deployment                ││
│  └──────────────────────────────────────┘│
└─────────────────────────────────────────┘
       │ (Docker build artifacts)
       ▼
┌─────────────────────────────────────────┐
│    Docker Host (Deployment Server)      │
│  ┌──────────────────────────────────────┐│
│  │ • Docker container running app       ││
│  │ • App accessible on port 5000        ││
│  │ • Auto-restart enabled               ││
│  └──────────────────────────────────────┘│
└─────────────────────────────────────────┘
       ▲
       │ (Ansible automation)
┌──────┴─────────────────────────────────┐
│  Ansible Control Machine (Your PC)     │
│  ┌──────────────────────────────────────┐
│  │ • Playbooks for setup                │
│  │ • Inventory of target servers        │
│  │ • Roles for Jenkins, Docker, App     │
│  └──────────────────────────────────────┘
└─────────────────────────────────────────┘
```

## Step 1: Prepare Target Servers

### 1.1 Create SSH Keys (if not already done)

On your local machine:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### 1.2 Add SSH Public Key to Target Servers

For each server:
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub username@server-ip
```

### 1.3 Test SSH Connectivity

```bash
ssh username@server-ip "echo 'SSH connection successful'"
```

## Step 2: Configure Ansible

### 2.1 Update Inventory File

Edit `ansible/inventory.ini` and add your target servers:

```ini
[all]
jenkins-server.example.com ansible_user=ubuntu
docker-server.example.com ansible_user=ubuntu

[all:vars]
ansible_become_user=root
ansible_python_interpreter=/usr/bin/python3
app_name=cicd-python-app
app_port=5000
flask_env=production
app_repo_url=https://github.com/yourusername/cicd-python-app.git
```

### 2.2 Test Ansible Connectivity

```bash
cd ansible/
ansible all -i inventory.ini -m ping
```

Expected output:
```
jenkins-server.example.com | SUCCESS => {
    "ping": "pong"
}
docker-server.example.com | SUCCESS => {
    "ping": "pong"
}
```

## Step 3: Deploy Infrastructure

### 3.1 Run Ansible Playbook

Deploy Jenkins and Docker on your target servers:

```bash
cd ansible/
ansible-playbook -i inventory.ini site.yml -v
```

### 3.2 Run Specific Roles (Optional)

Deploy only Jenkins:
```bash
ansible-playbook -i inventory.ini site.yml -t jenkins -v
```

Deploy only Docker:
```bash
ansible-playbook -i inventory.ini site.yml -t docker -v
```

### 3.3 Wait for Completion

The deployment typically takes 10-15 minutes. Monitor the Ansible output for:
- ✓ All tasks completed successfully
- ✓ Jenkins and Docker services started
- ✓ Deployment summary showing service URLs

## Step 4: Configure Jenkins

### 4.1 Access Jenkins Web UI

Open your browser and navigate to:
```
http://jenkins-server-ip:8080
```

### 4.2 Initial Setup

1. **Unlock Jenkins**:
   - SSH to Jenkins server
   - Get initial admin password:
     ```bash
     sudo cat /var/lib/jenkins/secrets/initialAdminPassword
     ```
   - Paste password in web UI

2. **Install Suggested Plugins**:
   - Choose "Install suggested plugins"
   - Wait for installation to complete

3. **Create Admin User**:
   - Fill in admin account details
   - Click "Save and Continue"

### 4.3 Create CI/CD Pipeline Job

1. Click "Create a job"
2. Enter job name: `cicd-python-app`
3. Select "Pipeline"
4. Click "OK"

5. In the Pipeline section:
   - Select "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/yourusername/cicd-python-app.git`
   - Branch: `*/main`
   - Script Path: `jenkins/Jenkinsfile`

6. Click "Save"

### 4.4 Run First Build

1. Click "Build Now"
2. Monitor build in "Build History"
3. Check console output for any errors

### 4.5 Configure GitHub Webhook (Optional but Recommended)

For automatic builds on code push:

1. **In Jenkins**:
   - Go to job > Configure
   - Check "GitHub hook trigger for GITScm polling"
   - Click "Save"

2. **In GitHub**:
   - Go to repository > Settings > Webhooks
   - Click "Add webhook"
   - Payload URL: `http://jenkins-server-ip:8080/github-webhook/`
   - Content type: `application/json`
   - Select "Just the push event"
   - Click "Add webhook"

## Step 5: Verify Deployment

### 5.1 Check Jenkins Status

```bash
ssh ubuntu@jenkins-server-ip
sudo systemctl status jenkins
```

Should show: `active (running)`

### 5.2 Check Docker Status

```bash
ssh ubuntu@docker-server-ip
sudo systemctl status docker
docker ps
```

### 5.3 Test Application

```bash
# If Jenkins and Docker are on same server
curl http://localhost:5000/health
curl http://localhost:5000/info

# If on different servers
curl http://docker-server-ip:5000/health
```

Expected response:
```json
{
    "status": "healthy",
    "service": "cicd-python-app",
    "environment": "production"
}
```

### 5.4 View Docker Logs

```bash
ssh ubuntu@docker-server-ip
docker logs cicd-python-app -f
```

## Troubleshooting

### Ansible Issues

**SSH Connection Refused**
```bash
# Check SSH connectivity
ssh -v ubuntu@server-ip

# Verify SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

**Ansible Command Not Found**
```bash
# Install Ansible
pip install --upgrade ansible

# Or using apt (Ubuntu)
sudo apt-get install ansible
```

### Jenkins Issues

**Jenkins Won't Start**
```bash
# Check logs
sudo tail -f /var/log/jenkins/jenkins.log

# Restart service
sudo systemctl restart jenkins
```

**Can't Access Jenkins UI**
```bash
# Check if Jenkins is listening
sudo netstat -tuln | grep 8080

# Check firewall
sudo ufw allow 8080
```

### Docker Issues

**Docker Daemon Not Running**
```bash
sudo systemctl restart docker
docker ps
```

**Container Won't Start**
```bash
# Check image
docker images

# View container logs
docker logs cicd-python-app

# Rebuild image
docker build -t cicd-python-app .
```

**Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Application Issues

**Application Not Responding**
```bash
# Check if container is running
docker ps | grep cicd-python-app

# Check logs
docker logs cicd-python-app

# Test health endpoint
curl -v http://localhost:5000/health
```

## Next Steps

1. **Set Up Monitoring**: Add Prometheus/Grafana for metrics
2. **Add SSL/TLS**: Configure HTTPS for production
3. **Database Integration**: Add PostgreSQL or MongoDB if needed
4. **Email Notifications**: Configure Jenkins email for build alerts
5. **Slack Integration**: Send build notifications to Slack
6. **CI/CD Improvements**: Add code quality checks, security scans

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

