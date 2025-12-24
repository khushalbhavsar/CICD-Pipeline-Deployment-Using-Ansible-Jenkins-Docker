# Ansible Configuration Guide

## Overview
This directory contains Ansible playbooks and roles for automating the deployment of Jenkins, Docker, and the Python application.

## Directory Structure

```
ansible/
├── site.yml                 # Main playbook
├── inventory.ini           # Inventory file with target hosts
├── roles/
│   ├── jenkins/
│   │   ├── tasks/
│   │   │   └── main.yml    # Jenkins installation tasks
│   │   └── handlers/
│   │       └── main.yml    # Jenkins restart handler
│   ├── docker/
│   │   ├── tasks/
│   │   │   └── main.yml    # Docker installation tasks
│   │   └── handlers/
│   │       └── main.yml    # Docker restart handler
│   └── deploy_app/
│       └── tasks/
│           └── main.yml    # Application deployment tasks
└── README.md               # This file
```

## Role Descriptions

### Jenkins Role
Installs and configures Jenkins CI/CD server:
- Installs OpenJDK 11 (required by Jenkins)
- Adds Jenkins repository
- Installs Jenkins
- Starts and enables Jenkins service
- Configures Jenkins to work with Docker
- Waits for Jenkins to be ready

### Docker Role
Installs and configures Docker:
- Installs Docker CE and required packages
- Adds Docker repository
- Configures Docker daemon
- Enables Docker service
- Sets up docker group for non-root users

### Deploy App Role
Deploys the Python application:
- Clones application repository from GitHub
- Builds Docker image from Dockerfile
- Stops any existing container
- Runs new container with proper configuration
- Verifies container is running and responsive

## Usage

### Basic Usage

Run the entire playbook:
```bash
cd ansible/
ansible-playbook -i inventory.ini site.yml -v
```

### Run Specific Roles

Deploy only Jenkins:
```bash
ansible-playbook -i inventory.ini site.yml -t jenkins -v
```

Deploy only Docker:
```bash
ansible-playbook -i inventory.ini site.yml -t docker -v
```

Deploy only application:
```bash
ansible-playbook -i inventory.ini site.yml -t deploy -v
```

### Pass Variables from Command Line

```bash
ansible-playbook -i inventory.ini site.yml \
  -e "app_repo_url=https://github.com/youruser/yourrepo.git" \
  -e "flask_env=development" \
  -v
```

### Dry Run (Check Mode)

See what would be changed without making actual changes:
```bash
ansible-playbook -i inventory.ini site.yml --check -v
```

## Configuration

### Inventory File (inventory.ini)

Update hosts:
```ini
[all]
your-server-1.com ansible_user=ubuntu
your-server-2.com ansible_user=ubuntu

[all:vars]
app_name=cicd-python-app
app_port=5000
flask_env=production
```

### Variables

Default variables are defined in `site.yml`. Override them:

1. **In inventory.ini**:
   ```ini
   [all:vars]
   app_port=8000
   ```

2. **Via command line**:
   ```bash
   ansible-playbook -i inventory.ini site.yml -e "app_port=8000"
   ```

3. **In group_vars or host_vars** (create if needed):
   ```
   group_vars/
   └── all.yml
   ```

## Important Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | `cicd-python-app` | Application name |
| `app_port` | `5000` | Port for Flask app |
| `docker_image` | `cicd-python-app:latest` | Docker image name |
| `flask_env` | `production` | Flask environment (development/production) |
| `app_repo_url` | GitHub URL | Repository to clone from |

## Requirements

- Python 3.6+
- Ansible 2.10+
- SSH access to target servers with key-based authentication
- Target servers: Ubuntu 20.04+ or similar Debian-based systems

### Install Ansible

```bash
# Using pip
pip install ansible>=2.10

# Using apt (Ubuntu/Debian)
sudo apt-get install ansible
```

## Troubleshooting

### SSH Authentication Fails
```bash
# Verify SSH key exists and has correct permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Test SSH connection
ssh -i ~/.ssh/id_rsa ubuntu@server-ip
```

### Ansible Python Interpreter Error
```bash
# Install Python on target server
ssh ubuntu@server-ip "sudo apt-get update && sudo apt-get install python3 -y"

# Or specify in inventory
[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Role Fails with Permission Error
```bash
# Ensure user has sudo privileges
ssh ubuntu@server-ip "sudo visudo"
# User should be in sudoers file

# Or run with specific user
ansible-playbook -i inventory.ini site.yml --become-user=root
```

## Tags

Run only specific tagged tasks:

```bash
# Install only
ansible-playbook -i inventory.ini site.yml -t jenkins,docker

# Skip specific roles
ansible-playbook -i inventory.ini site.yml --skip-tags deploy
```

## Idempotence

All tasks are idempotent - running the playbook multiple times produces the same result.

## Debugging

Increase verbosity:
```bash
# -v for basic output
ansible-playbook -i inventory.ini site.yml -v

# -vv for more details
ansible-playbook -i inventory.ini site.yml -vv

# -vvv for maximum verbosity
ansible-playbook -i inventory.ini site.yml -vvv
```

Get debug information:
```bash
# Show variable values
ansible all -i inventory.ini -e "ansible_verbosity=4" -m debug -a "msg={{ hostvars[inventory_hostname] }}"

# Test connectivity
ansible all -i inventory.ini -m ping -v

# Check Python version
ansible all -i inventory.ini -m raw -a "python3 --version"
```

## Best Practices

1. **Always test with --check first**
2. **Use version control for inventory and playbooks**
3. **Keep secrets in separate files and use `ansible-vault`**
4. **Test on a staging environment before production**
5. **Document any custom modifications**
6. **Use roles for code organization and reusability**
7. **Keep playbooks simple and focused**

## Advanced Topics

### Using Vault for Secrets

```bash
# Create encrypted variables file
ansible-vault create group_vars/all/vault.yml

# Run playbook with vault
ansible-playbook -i inventory.ini site.yml --ask-vault-pass
```

### Custom Handlers

Edit `roles/*/handlers/main.yml` to add custom restart/reload handlers.

### Adding New Roles

```bash
# Create new role structure
mkdir -p roles/my-role/{tasks,handlers,templates,files,vars}
touch roles/my-role/tasks/main.yml
```

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Galaxy](https://galaxy.ansible.com/) - Community roles
