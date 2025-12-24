# Complete EC2 Deployment Guide for CI/CD Pipeline

## Table of Contents
1. [EC2 Instance Setup](#ec2-instance-setup)
2. [Prerequisites on Local Machine](#prerequisites-on-local-machine)
3. [Configure EC2 Instances](#configure-ec2-instances)
4. [Setup Ansible](#setup-ansible)
5. [Deploy with Ansible](#deploy-with-ansible)
6. [Configure Jenkins](#configure-jenkins)
7. [Setup GitHub Integration](#setup-github-integration)
8. [Verify Deployment](#verify-deployment)
9. [Access Application](#access-application)
10. [Troubleshooting](#troubleshooting)

---

## EC2 Instance Setup

### Step 1: Launch EC2 Instances on AWS

#### 1.1 Launch Instance for Jenkins Server

1. Go to **AWS Console** → **EC2** → **Launch Instances**
2. **AMI Selection**: Choose **Ubuntu 20.04 LTS** (free tier eligible)
3. **Instance Type**: 
   - Dev/Demo: `t2.micro` or `t2.small`
   - Production: `t2.medium` or `t3.medium`
4. **Instance Details**:
   - Number of instances: 1
   - Network: Default VPC
   - Auto-assign public IP: Enable
5. **Storage**: 20 GB (default is fine)
6. **Tags**: Add tag `Name: Jenkins-Server`
7. **Security Group**:
   - Create new: `jenkins-sg`
   - Add rules:
     - SSH (22): From your IP (e.g., 203.0.113.0/32)
     - HTTP (8080): From anywhere (0.0.0.0/0)
     - Custom TCP (5000): From anywhere (0.0.0.0/0) for app access
8. **Key Pair**: 
   - Create new: `cicd-deployment-key`
   - Download and save securely

#### 1.2 Launch Instance for Application Deployment Server (Optional)

You can use the same Jenkins instance or create a separate one:

1. Repeat steps above
2. **Tags**: Add tag `Name: App-Deployment-Server`
3. Use same security group or create `app-sg`

#### 1.3 Record Instance IPs

```
Jenkins Server:
  - Public IP: 54.XXX.XXX.XXX (example)
  - Private IP: 10.0.X.XX (example)
  - Instance ID: i-0xxxxx (example)

App Server (if separate):
  - Public IP: 52.XXX.XXX.XXX (example)
  - Private IP: 10.0.X.XX (example)
```

### Step 2: Security Group Configuration

Allow communication between instances (if using 2 instances):

1. Go to **EC2** → **Security Groups** → Select `jenkins-sg`
2. **Inbound Rules** → **Add rule**:
   - Type: All TCP
   - Source: Select `app-sg` (for app server)
3. Repeat for `app-sg` with Jenkins SG as source

---

## Prerequisites on Local Machine

### Step 1: Install Ansible (Windows)

**Option A: Using Windows Subsystem for Linux (WSL2) - Recommended**

```powershell
# Open PowerShell as Administrator
wsl --install

# After WSL installation, open Ubuntu terminal
sudo apt update
sudo apt install -y ansible
ansible --version
```

**Option B: Using Git Bash (Alternative)**

```bash
# Install via pip
pip install ansible

# Verify installation
ansible --version
```

### Step 2: Setup SSH Keys

```bash
# Generate SSH key (if not already done)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/cicd-key -N ""

# Output:
# Your identification has been saved in ~/.ssh/cicd-key
# Your public key has been saved in ~/.ssh/cicd-key.pub
```

### Step 3: Configure SSH for EC2

Create/edit `~/.ssh/config` (or `C:\Users\YourUsername\.ssh\config` on Windows):

```
Host jenkins-server
    HostName 54.XXX.XXX.XXX
    User ubuntu
    IdentityFile ~/.ssh/cicd-key
    StrictHostKeyChecking no

Host app-server
    HostName 52.XXX.XXX.XXX
    User ubuntu
    IdentityFile ~/.ssh/cicd-key
    StrictHostKeyChecking no
```

### Step 4: Add Your Key Pair to EC2

When launching instances, AWS provides a `.pem` file. Convert and use it:

```bash
# If you downloaded cicd-deployment-key.pem from AWS
cp ~/Downloads/cicd-deployment-key.pem ~/.ssh/
chmod 600 ~/.ssh/cicd-deployment-key.pem

# Add to SSH agent
ssh-add ~/.ssh/cicd-deployment-key.pem
```

---

## Configure EC2 Instances

### Step 1: Connect to EC2 Instance

```bash
# Using SSH directly
ssh -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX

# Or using SSH config
ssh jenkins-server
```

### Step 2: Initial System Setup (Run on EC2)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install sudo without password for ansible (optional but recommended)
sudo sed -i 's/^%sudo.*/%sudo ALL=(ALL) NOPASSWD:ALL/' /etc/sudoers

# Verify SSH key-based authentication works
exit
```

### Step 3: Enable SSH Key-Based Authentication

From your local machine:

```bash
# Copy your public key to EC2
ssh-copy-id -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX

# Test connection
ssh -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX "echo 'SSH successful'"
```

---

## Setup Ansible

### Step 1: Update Ansible Inventory

Edit `ansible/inventory.ini`:

```ini
[jenkins_servers]
jenkins-server ansible_host=54.XXX.XXX.XXX ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/cicd-deployment-key.pem

[app_servers]
app-server ansible_host=52.XXX.XXX.XXX ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/cicd-deployment-key.pem

# If using same server for Jenkins and App
[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

**OR** Single Server Setup:

```ini
[all_servers]
jenkins-app ansible_host=54.XXX.XXX.XXX ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/cicd-deployment-key.pem

[all_servers:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Step 2: Test Ansible Connectivity

```bash
# From your local machine
cd ansible/

# Test connection to all hosts
ansible all -i inventory.ini -m ping

# Expected output:
# jenkins-server | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

If ping fails:
- Check EC2 security group allows port 22
- Verify SSH key path is correct
- Check IP address is accurate

### Step 3: Verify Python on EC2

```bash
ansible all -i inventory.ini -m shell -a "python3 --version"
```

---

## Deploy with Ansible

### Step 1: Configure Variables (Optional)

Edit `ansible/site.yml` to customize:

```yaml
vars:
  app_repo_url: "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
  flask_env: "production"
  docker_container_name: "cicd-app"
  docker_container_port: "5000"
```

### Step 2: Run Ansible Playbook

```bash
# From ansible/ directory
cd ansible/

# Syntax check (no changes made)
ansible-playbook -i inventory.ini site.yml --syntax-check

# Dry run (shows what would happen)
ansible-playbook -i inventory.ini site.yml --check -v

# Actually deploy
ansible-playbook -i inventory.ini site.yml -v
```

### Step 3: Deployment Timeline

Expected deployment time: **5-10 minutes**

```
Phase 1: Java Installation (2-3 min)
Phase 2: Jenkins Installation (2-3 min)
Phase 3: Docker Installation (1-2 min)
Phase 4: App Deployment (1-2 min)
```

### Step 4: Monitor Deployment

Watch output for:
- ✅ Green "ok" or "changed" messages
- ❌ Red "failed" messages (investigate immediately)
- ⏳ "waiting" messages (normal, be patient)

---

## Configure Jenkins

### Step 1: Access Jenkins

1. Open browser: `http://54.XXX.XXX.XXX:8080`
2. Get initial password:

```bash
ssh -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Step 2: Jenkins Setup Wizard

1. **Paste initial password** on Jenkins page
2. **Install Suggested Plugins**
3. **Create Admin User**:
   - Username: `admin`
   - Password: Use strong password
   - Email: your@email.com
4. **Instance Configuration**: Keep default

### Step 3: Install Additional Plugins

1. **Manage Jenkins** → **Manage Plugins**
2. Search and install:
   - Docker Pipeline
   - GitHub
   - Email Extension
   - SSH Agent

### Step 4: Add GitHub Credentials

1. **Manage Jenkins** → **Manage Credentials**
2. **System** → **Global credentials**
3. **Add Credentials**:
   - Kind: Username with password
   - Username: Your GitHub username
   - Password: [Personal Access Token from GitHub](https://github.com/settings/tokens)
     - Scope needed: `repo`, `admin:repo_hook`
   - ID: `github-credentials`

### Step 5: Create Pipeline Job

1. **New Item**
2. **Job Name**: `cicd-python-app`
3. **Pipeline**
4. **OK**

### Step 6: Configure Pipeline

In **Pipeline** section:

```
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/YOUR_USERNAME/YOUR_REPO.git
Credentials: github-credentials
Branch: */main
Script Path: jenkins/Jenkinsfile
```

### Step 7: Configure Build Triggers

**Option A: Poll GitHub (Easiest)**

```
Poll SCM: H/5 * * * *
(Checks every 5 minutes)
```

**Option B: GitHub Webhook (Better)**

1. In Jenkins job: Check **GitHub hook trigger**
2. In GitHub repo settings:
   - **Settings** → **Webhooks**
   - **Add webhook**
   - Payload URL: `http://54.XXX.XXX.XXX:8080/github-webhook/`
   - Content type: `application/json`
   - Events: Push events
   - Active: ✓

---

## Setup GitHub Integration

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. **Generate new token**
3. **Name**: `Jenkins CI/CD`
4. **Scopes**:
   - ✓ repo (Full control of private repositories)
   - ✓ admin:repo_hook (Full control of repository hooks)
   - ✓ admin:org_hook (Full control of organization hooks)
5. **Generate token** and copy it

### Step 2: Push Code to GitHub

```bash
cd ~/your-project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Test Jenkins Trigger

```bash
# Make a small change to test
echo "# Test update" >> README.md
git add README.md
git commit -m "Test Jenkins webhook"
git push origin main

# Watch Jenkins build start automatically
```

---

## Verify Deployment

### Step 1: Check Services Status

```bash
# SSH to EC2 instance
ssh -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX

# Check Jenkins
sudo systemctl status jenkins

# Check Docker
sudo systemctl status docker

# Check running containers
docker ps
```

### Step 2: Verify Application

```bash
# Check if container is running
docker ps

# Check logs
docker logs -f cicd-app

# Test application endpoint
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/info
```

### Step 3: Test from Local Machine

```bash
# Replace IP with your EC2 public IP
curl http://54.XXX.XXX.XXX:5000/
curl http://54.XXX.XXX.XXX:5000/health
```

---

## Access Application

### From Browser

**Jenkins UI**: `http://54.XXX.XXX.XXX:8080`
- Username: admin
- Password: (set during setup)

**Application**: `http://54.XXX.XXX.XXX:5000`
- Home page: `/`
- Health check: `/health`
- Info endpoint: `/info`

### Via Command Line

```bash
# Jenkins status
curl http://54.XXX.XXX.XXX:8080

# Application health
curl http://54.XXX.XXX.XXX:5000/health

# Full application info
curl http://54.XXX.XXX.XXX:5000/info
```

---

## Troubleshooting

### Problem: SSH Connection Refused

**Solution**:
```bash
# Check key permissions
chmod 600 ~/.ssh/cicd-deployment-key.pem

# Check security group allows port 22
# Go to AWS → EC2 → Security Groups → Check inbound rules

# Test connectivity
ssh -vvv -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX
```

### Problem: Ansible Ping Fails

**Solution**:
```bash
# Check inventory file syntax
ansible-inventory -i inventory.ini --list

# Verify Python on target
ssh -i ~/.ssh/cicd-deployment-key.pem ubuntu@54.XXX.XXX.XXX "python3 --version"

# Check network connectivity
ping 54.XXX.XXX.XXX
```

### Problem: Jenkins Not Starting

**Solution**:
```bash
# SSH to EC2
ssh ubuntu@54.XXX.XXX.XXX

# Check logs
sudo tail -f /var/log/jenkins/jenkins.log

# Restart Jenkins
sudo systemctl restart jenkins

# Check status
sudo systemctl status jenkins
```

### Problem: Docker Container Not Running

**Solution**:
```bash
# Check logs
docker logs cicd-app

# Check all containers
docker ps -a

# Restart container
docker restart cicd-app

# Check ports
ss -tulpn | grep 5000
```

### Problem: Application Port Already in Use

**Solution**:
```bash
# Find process using port 5000
ss -tulpn | grep :5000

# Stop the container
docker stop cicd-app

# Remove the container
docker rm cicd-app

# Redeploy via Jenkins or manual: docker run ...
```

### Problem: Ansible Playbook Fails Midway

**Solution**:
```bash
# Run with verbose output
ansible-playbook -i inventory.ini site.yml -vvv

# Run specific role only (to skip past failed role)
ansible-playbook -i inventory.ini site.yml -t docker -v

# Check target system for issues
ssh ubuntu@54.XXX.XXX.XXX

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux
```

### Problem: GitHub Webhook Not Triggering

**Solution**:
1. Verify webhook URL: `http://54.XXX.XXX.XXX:8080/github-webhook/`
2. In GitHub repo → **Settings** → **Webhooks** → Click webhook
3. **Recent Deliveries** tab shows request/response
4. Check Jenkins logs: `sudo tail -f /var/log/jenkins/jenkins.log`
5. Verify credentials are correct in Jenkins
6. Check Jenkins security settings allow anonymous GitHub webhooks

### Problem: Connection Timeout from Outside

**Solution**:
```bash
# Check EC2 security group
# AWS → EC2 → Security Groups → jenkins-sg
# Verify inbound rules for:
# - Port 8080 (Jenkins): 0.0.0.0/0
# - Port 5000 (App): 0.0.0.0/0

# Test locally first
curl http://localhost:5000/

# Test from another machine
curl http://54.XXX.XXX.XXX:5000/
```

---

## Quick Reference: Essential Commands

```bash
# Local machine - Test connectivity
ansible all -i ansible/inventory.ini -m ping

# Local machine - Run deployment
ansible-playbook -i ansible/inventory.ini ansible/site.yml -v

# EC2 - Check Jenkins
sudo systemctl status jenkins
sudo systemctl restart jenkins

# EC2 - Check Docker
docker ps
docker logs -f cicd-app

# EC2 - Check application
curl http://localhost:5000/health

# EC2 - View Jenkins initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# EC2 - Monitor system resources
top
df -h
free -h
```

---

## Production Considerations

### Security Hardening

1. **Update Security Groups**:
   - Restrict Jenkins to specific IPs
   - Restrict SSH to specific IPs
   - Only expose port 5000 if needed

2. **Enable HTTPS**:
   - Use AWS Certificate Manager for SSL
   - Configure nginx reverse proxy
   - Install with: `ansible-playbook ... -e 'use_https=true'`

3. **Backup Important Data**:
   ```bash
   ssh ubuntu@54.XXX.XXX.XXX
   sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins/
   ```

### Monitoring & Logging

1. **Setup CloudWatch Monitoring**:
   - EC2 metrics (CPU, Memory, Disk)
   - Set alarms for high resource usage

2. **Enable Jenkins Logging**:
   - Jenkins → **Manage Jenkins** → **Log Recorders**
   - Send logs to CloudWatch or S3

3. **Application Monitoring**:
   - Add health check: `curl http://localhost:5000/health`
   - Setup CloudWatch alarms for failed checks

### Scaling

1. **Multiple App Servers**:
   - Update `ansible/inventory.ini` with multiple servers
   - Configure load balancer in front
   - Run playbook for each server

2. **Database Integration**:
   - Add RDS PostgreSQL instance
   - Update Flask app connection string
   - Update inventory with database credentials

---

## Next Steps

1. ✅ Complete EC2 setup
2. ✅ Run Ansible playbook
3. ✅ Configure Jenkins
4. ✅ Setup GitHub webhook
5. ✅ Test full CI/CD pipeline
6. ✅ Monitor application
7. 🔄 Scale as needed
8. 🔒 Implement security hardening

---

## Support & Documentation

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: December 2024
**Status**: Production Ready ✅
