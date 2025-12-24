#!/bin/bash
# Quick Setup Script for Amazon Linux 2 EC2 Instance
# This script prepares your EC2 instance for running the Ansible playbooks

set -e

echo "=================================================="
echo "CICD Pipeline - Amazon Linux 2 Setup"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install prerequisites
echo "📦 Installing prerequisites..."
sudo yum install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    vim \
    unzip

# Install Ansible
echo "🤖 Installing Ansible..."
sudo pip3 install ansible

# Verify installations
echo ""
echo "✅ Verification:"
echo "Python: $(python3 --version)"
echo "Pip: $(pip3 --version)"
echo "Ansible: $(ansible --version | head -1)"
echo "Git: $(git --version)"

# Clone repository (optional - uncomment and adjust as needed)
# echo ""
# echo "📥 Cloning repository..."
# git clone <YOUR_REPO_URL>
# cd CICD-Pipeline-Deployment-Using-Ansible-Jenkins-Docker

# Display next steps
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next Steps:"
echo "1. Clone the repository:"
echo "   git clone <YOUR_REPO_URL>"
echo ""
echo "2. Navigate to ansible directory:"
echo "   cd CICD-Pipeline-Deployment-Using-Ansible-Jenkins-Docker/ansible"
echo ""
echo "3. Run the playbook:"
echo "   ansible-playbook site.yml -v"
echo ""
echo "4. Monitor progress - installation takes 5-10 minutes"
echo ""
echo "5. After completion, verify:"
echo "   - Jenkins: curl http://localhost:8080"
echo "   - Docker: docker --version"
echo "   - App: curl http://localhost:5000/health"
echo ""
echo "=================================================="
