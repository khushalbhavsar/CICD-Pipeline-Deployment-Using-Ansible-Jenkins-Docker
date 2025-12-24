# End-to-End CI/CD Pipeline Automation using Ansible, Jenkins, and Docker

## Overview

This project demonstrates a comprehensive CI/CD pipeline that automates the entire deployment process using Ansible, Jenkins, Docker, and a Python Flask application.

## Architecture Flow

```
GitHub Repository
    ↓ (Webhook/Poll)
Jenkins Server
    ├── Stage 1: Checkout code
    ├── Stage 2: Build Docker image
    ├── Stage 3: Run tests
    ├── Stage 4: Deploy container
    └── Stage 5: Verify health
    ↓
Docker Host
    └── Application running on port 5000
    ↑
Ansible (Infrastructure Provisioning)
    ├── Install Jenkins
    ├── Install Docker
    └── Configure permissions
```

## Project Structure

```
├── README.md                    # This file
├── .github/
│   └── copilot-instructions.md # Project checklist
├── ansible/                     # Infrastructure automation
│   ├── site.yml                # Main playbook
│   ├── inventory.ini           # Target servers
│   ├── README.md               # Ansible guide
│   └── roles/
│       ├── jenkins/            # Jenkins role
│       ├── docker/             # Docker role
│       └── deploy_app/         # App deployment
├── jenkins/                     # CI/CD pipeline
│   ├── Jenkinsfile             # Pipeline definition
│   └── README.md               # Jenkins guide
├── app/                        # Python application
│   ├── app.py                  # Flask app
│   ├── Dockerfile              # Container image
│   ├── requirements.txt        # Dependencies
│   ├── tests/                  # Unit tests
│   ├── README.md               # App guide
│   └── .env.example            # Environment vars
├── docs/
│   └── SETUP.md                # Complete setup guide
└── docker-compose.yml          # Local development
```

## Quick Start

### Prerequisites

- **Local**: Ansible 2.10+, Git, SSH
- **Target Servers**: Ubuntu 20.04+, 2+ vCPU, 4+ GB RAM
- **GitHub**: Repository access

### Setup (3 Steps)

1. **Configure Inventory**
   ```bash
   cd ansible/
   # Edit inventory.ini with your server IPs
   ```

2. **Run Ansible Playbook**
   ```bash
   ansible-playbook -i inventory.ini site.yml -v
   ```

3. **Configure Jenkins** (see docs/SETUP.md for details)

4. **Deploy** - Push to GitHub and watch it build!

## Key Features

- ✅ **Ansible**: Fully automated infrastructure provisioning
- ✅ **Jenkins**: Multi-stage CI/CD pipeline
- ✅ **Docker**: Production-ready container with health checks
- ✅ **Python**: Flask application with comprehensive tests
- ✅ **Security**: Non-root user, SSH keys, proper permissions
- ✅ **Monitoring**: Health check endpoints and logging
- ✅ **Scalable**: Ready for Kubernetes or cloud deployments

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Ansible | 2.10+ | Infrastructure automation |
| Jenkins | LTS | CI/CD orchestration |
| Docker | Latest | Containerization |
| Python | 3.9+ | Application runtime |
| Flask | 2.3.2 | Web framework |
| Ubuntu | 20.04+ | Operating system |

## Documentation

- [📖 Complete Setup Guide](docs/SETUP.md) - Step-by-step instructions
- [🔧 Ansible Configuration](ansible/README.md) - Infrastructure automation
- [🚀 Jenkins Pipeline](jenkins/README.md) - CI/CD pipeline details
- [📦 Application Guide](app/README.md) - Python Flask app documentation

## Local Development

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run tests
pytest app/tests/ -v
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Run tests
pytest app/tests/ -v

# Start app
cd app && python app.py
```

## Testing

### Run Tests

```bash
pytest app/tests/ -v
```

### Test Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Main endpoint
curl http://localhost:5000/

# Application info
curl http://localhost:5000/info
```

## Deployment

### Full Deployment

```bash
cd ansible/
ansible-playbook -i inventory.ini site.yml -v
```

### Specific Component

```bash
# Only Jenkins
ansible-playbook -i inventory.ini site.yml -t jenkins

# Only Docker
ansible-playbook -i inventory.ini site.yml -t docker

# Only app
ansible-playbook -i inventory.ini site.yml -t deploy
```

### Dry Run

```bash
ansible-playbook -i inventory.ini site.yml --check -v
```

## Performance

- **Setup Time**: 10-15 minutes
- **Build Time**: 2-3 minutes
- **Deploy Time**: <1 minute
- **Docker Image Size**: ~150MB

## Security

- Non-root Docker user
- SSH key-based authentication
- Firewall configuration
- Health checks for availability
- Minimal Docker images
- Environment-based configuration
- Secrets management

## Troubleshooting

### SSH Connection Issues

```bash
# Check SSH connectivity
ssh -v ubuntu@server-ip

# Verify key permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Jenkins Won't Start

```bash
# Check logs
sudo tail -f /var/log/jenkins/jenkins.log

# Restart service
sudo systemctl restart jenkins
```

### Docker Issues

```bash
# Check status
sudo systemctl status docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# View container logs
docker logs cicd-python-app
```

See [docs/SETUP.md#troubleshooting](docs/SETUP.md#troubleshooting) for more details.

## Interview Talking Points

**Problem Solved:**
"This project automates CI/CD infrastructure provisioning and application deployment, eliminating manual server configuration."

**Key Achievements:**
- Implemented infrastructure-as-code using Ansible roles
- Built multi-stage Jenkins pipeline with error handling
- Containerized Python app with Docker best practices
- Automated deployment from GitHub to running containers
- Comprehensive health checks and monitoring

**Technical Depth:**
- Ansible playbooks and roles for reusability
- Jenkinsfile as code for version control
- Docker multi-stage build and security hardening
- Proper error handling and retry logic
- Production-ready configurations

## Next Steps

1. **Monitoring**: Add Prometheus/Grafana
2. **SSL/TLS**: Configure HTTPS
3. **Database**: Add PostgreSQL integration
4. **Notifications**: Email/Slack alerts
5. **Security Scanning**: Container security checks
6. **Kubernetes**: Deploy to K8s clusters

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check [Troubleshooting Guide](docs/SETUP.md#troubleshooting)
2. Review component READMEs
3. Check component logs
4. Open GitHub issue

## Acknowledgments

- [Ansible Documentation](https://docs.ansible.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

<div align="center">

**Made with ❤️ for DevOps, SRE, and CI/CD professionals**

⭐ Star this repository if you find it helpful!

</div>
