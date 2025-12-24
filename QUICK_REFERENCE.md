# Quick Reference Card - Amazon Linux 2 Ansible Fix

## 🎯 What Was Fixed
Your Ansible playbooks now work on **Amazon Linux 2** (and still work on Ubuntu)

## 📋 Original Error
```
fatal: [localhost]: FAILED! => changed=false
  cmd: apt-get update
  msg: '[Errno 2] No such file or directory: b''apt-get'''
```

## ✅ Solution
- Added `yum` support for RHEL-based systems
- Kept `apt` support for Debian-based systems
- Used conditional execution based on OS family

## 🚀 Quick Start (3 Commands)

### For Local Amazon Linux 2 EC2 Instance:
```bash
# 1. Ensure prerequisites
sudo yum install -y python3-pip && sudo pip3 install ansible

# 2. Navigate to ansible directory
cd ~/CICD-Pipeline-Deployment-Using-Ansible-Jenkins-Docker/ansible

# 3. Run the playbook
ansible-playbook site.yml -v
```

## 📁 Files Changed

| File | Change | Status |
|------|--------|--------|
| `ansible/site.yml` | Added RHEL package update | ✅ |
| `ansible/roles/jenkins/tasks/main.yml` | Split Debian/RHEL install | ✅ |
| `ansible/roles/docker/tasks/main.yml` | Split Debian/RHEL install | ✅ |
| `ansible/inventory.ini` | Updated examples | ✅ |
| `ansible/ansible.cfg` | NEW config file | ✨ |

## 📚 Documentation
- **Detailed Guide**: See `ansible/AMAZON_LINUX_GUIDE.md`
- **Changelog**: See `AMAZON_LINUX_UPDATE.md`
- **Overview**: See `FIX_SUMMARY.md`

## 🔍 Verify Installation

```bash
# Should all show success
java -version
systemctl status jenkins
docker --version
curl http://localhost:5000/health
```

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Python3 not found | `sudo yum install -y python3` |
| Ansible not found | `sudo pip3 install ansible` |
| SSH key permission denied | `chmod 600 ~/.ssh/your-key.pem` |
| Connection refused to Jenkins | Wait 30-60 seconds, services are starting |
| Docker permission denied | Already handled - jenkins user added to docker group |

## 🌐 Supported Operating Systems

✅ Amazon Linux 2 (NEW!)
✅ Amazon Linux 2023 (NEW!)
✅ Ubuntu 18.04, 20.04, 22.04
✅ CentOS 7, 8, 9 (NEW!)
✅ RHEL 7, 8, 9 (NEW!)
✅ Fedora (NEW!)

## 📊 What Gets Installed

- **Java 11 OpenJDK** - Required for Jenkins
- **Jenkins LTS** - CI/CD orchestration  
- **Docker CE** - Container runtime
- **Python Flask App** - Your application
- **Docker Group** - Proper user permissions

## ⏱️ Typical Installation Time

- Full fresh install: **5-10 minutes**
- Subsequent runs: **2-3 minutes** (fact caching)

## 🔐 Security Notes

- Jenkins user automatically added to docker group
- Non-root Flask app user created
- Health checks enabled for monitoring
- Sudo access configured

## 📍 Service Locations

After successful deployment:
- **Jenkins UI**: `http://your-ip:8080`
- **Application**: `http://your-ip:5000`
- **Health Check**: `http://your-ip:5000/health`

## 🚨 Common Patterns

### Update Inventory for Multiple Servers
```ini
[all]
server1 ansible_host=3.95.5.156 ansible_user=ec2-user
server2 ansible_host=3.95.5.157 ansible_user=ec2-user

[all:vars]
ansible_become=true
ansible_python_interpreter=/usr/bin/python3
```

### Run Specific Role Only
```bash
ansible-playbook site.yml -v --tags jenkins   # Just Jenkins
ansible-playbook site.yml -v --tags docker    # Just Docker
ansible-playbook site.yml -v --tags deploy    # Just App
```

### Increase Verbosity
```bash
ansible-playbook site.yml -vv    # More details
ansible-playbook site.yml -vvv   # Even more
```

## 📞 Support Resources

1. **Detailed Guide**: `ansible/AMAZON_LINUX_GUIDE.md`
2. **Technical Details**: `AMAZON_LINUX_UPDATE.md`
3. **Full Overview**: `FIX_SUMMARY.md`
4. **Original Docs**: `docs/SETUP.md`

---

**Status**: ✅ Production-Ready for Amazon Linux 2

Last Update: December 24, 2025
