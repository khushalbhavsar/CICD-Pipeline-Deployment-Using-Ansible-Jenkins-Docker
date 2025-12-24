# Amazon Linux 2 Deployment Guide

## Overview
The Ansible playbooks have been updated to support both **Debian-based** (Ubuntu) and **RHEL-based** (Amazon Linux, CentOS, RHEL) systems.

## What Was Fixed

### 1. **Package Manager Support**
- **Before**: Playbooks only used `apt` (Debian-only)
- **After**: Playbooks now use:
  - `apt` for Debian/Ubuntu systems
  - `yum` for RHEL/Amazon Linux/CentOS systems

### 2. **Repository Management**
- **Jenkins**: Updated to use `yum_repository` for RHEL-based systems
- **Docker**: Updated Docker CE repository for Amazon Linux 2
- **Automatic Detection**: Uses `ansible_os_family` variable for conditional execution

### 3. **Java Installation**
- **Ubuntu**: `openjdk-11-jdk` (apt)
- **Amazon Linux**: `java-11-openjdk-devel` (yum)

## Quick Start on Amazon Linux 2

### Prerequisites
```bash
# On your EC2 instance (Amazon Linux 2)
sudo yum install -y python3 python3-pip git
sudo pip3 install ansible

# Clone the repository
git clone <your-repo>
cd CICD-Pipeline-Deployment-Using-Ansible-Jenkins-Docker/ansible
```

### Run the Playbook Locally
```bash
# Test on localhost (local EC2 instance)
ansible-playbook site.yml -v

# Or with specific tags
ansible-playbook site.yml -v --tags jenkins
ansible-playbook site.yml -v --tags docker
ansible-playbook site.yml -v --tags deploy
```

### Run on Remote Servers
```bash
# Update inventory.ini with your server IPs and SSH key paths
# For Amazon Linux 2:
# 3.95.5.156 ansible_user=ec2-user

# Run playbook
ansible-playbook -i inventory.ini site.yml -v

# Or without sudo password prompt (for pre-configured sudo):
ansible-playbook -i inventory.ini site.yml -v
```

## Inventory Configuration Examples

### For Local Deployment (Amazon Linux 2)
```ini
[all]
localhost ansible_connection=local

[all:vars]
ansible_become=true
ansible_become_user=root
ansible_python_interpreter=/usr/bin/python3
```

### For Remote Amazon Linux 2 Servers
```ini
[all]
jenkins-server ansible_host=3.95.5.156 ansible_user=ec2-user
docker-server ansible_host=3.95.5.157 ansible_user=ec2-user

[all:vars]
ansible_become=true
ansible_become_user=root
ansible_python_interpreter=/usr/bin/python3
ansible_private_key_file=~/.ssh/your-key.pem
```

### For Mixed Environments (Ubuntu + Amazon Linux)
```ini
[ubuntu]
web1.example.com ansible_user=ubuntu

[amazon_linux]
3.95.5.156 ansible_user=ec2-user

[all:vars]
ansible_become=true
ansible_become_user=root
ansible_python_interpreter=/usr/bin/python3
```

## Key Files Updated

1. **ansible/site.yml**
   - Added RHEL package cache update task

2. **ansible/roles/jenkins/tasks/main.yml**
   - Split Java installation (apt vs yum)
   - Split Jenkins repository and installation (apt vs yum)
   - Conditional tasks based on OS family

3. **ansible/roles/docker/tasks/main.yml**
   - Split prerequisite packages (apt vs yum)
   - Split Docker repository configuration (apt vs yum)
   - Amazon Linux-specific Docker repository URL
   - Fixed Docker daemon wait logic

4. **ansible/inventory.ini**
   - Added example configurations for different OS types
   - Clarified variable structure

5. **ansible/ansible.cfg** (NEW)
   - SSH configuration optimized for EC2
   - Fact caching enabled for performance
   - Best practices for Ansible execution

## Troubleshooting

### Issue: "No such file or directory: apt-get"
**Solution**: Your system is RHEL-based. The playbooks now detect this and use `yum` instead.

### Issue: SSH Key Permission Denied
```bash
chmod 600 ~/.ssh/your-key.pem
```

### Issue: Python3 Not Found
```bash
sudo yum install -y python3
```

### Issue: Docker Socket Permission Denied (Jenkins user)
The playbook automatically adds the Jenkins user to the docker group. You may need to:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Verify Installation Success
```bash
# Check Java
java -version

# Check Jenkins
systemctl status jenkins
curl http://localhost:8080

# Check Docker
docker --version
docker ps

# Check Application
curl http://localhost:5000/health
```

## Performance Improvements

1. **Fact Caching**: Enabled to speed up repeated runs
2. **Pipelining**: Enabled for faster task execution
3. **Conditional Tasks**: Only relevant tasks run on each OS type
4. **Retry Logic**: Built-in retries for network-dependent tasks

## Next Steps

1. ✅ Update `inventory.ini` with your server details
2. ✅ Ensure SSH keys are properly configured
3. ✅ Run playbook with `-v` flag for detailed output
4. ✅ Check Jenkins UI at `http://<server-ip>:8080`
5. ✅ Verify application at `http://<server-ip>:5000`

## Support for Additional OS Types

The playbooks are structured to easily support:
- ✅ Ubuntu 18.04, 20.04, 22.04
- ✅ Amazon Linux 2
- ✅ Amazon Linux 2023
- ✅ CentOS 7, 8, 9
- ✅ RHEL 7, 8, 9
- ✅ Fedora (latest)

To add support for a new OS, update the `when` conditions in the playbooks.

---

For more details, see [SETUP.md](../docs/SETUP.md)
