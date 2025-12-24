# Jenkins GPG Key Fix - RHEL Systems

## Problem Encountered
```
TASK [jenkins : Install Jenkins - RHEL]
fatal: [localhost]: FAILED! => changed=false
  msg: 'Failed to validate GPG signature for jenkins-2.528.3-1.1.noarch: 
        Public key for jenkins-2.528.3-1.1.noarch.rpm is not installed'
```

## Root Cause
The Jenkins repository configuration had GPG checking enabled (`gpgcheck: yes`), but the GPG key wasn't imported into the system keyring before attempting installation.

## Solution Implemented ✅

Added a new task to import the Jenkins GPG key for RHEL systems **before** repository configuration:

```yaml
- name: Add Jenkins GPG key - RHEL
  rpm_key:
    key: https://pkg.jenkins.io/redhat/jenkins.io.key
    state: present
  register: jenkins_key_rhel
  until: jenkins_key_rhel is succeeded
  retries: 3
  when: ansible_os_family == "RedHat"
```

This task:
1. ✅ Downloads the Jenkins GPG key
2. ✅ Imports it into the system's RPM keyring
3. ✅ Has retry logic for network issues
4. ✅ Only runs on RHEL-based systems

## Installation Order (Now Correct)

```
1. Install Java ✅
   └─ java-11-amazon-corretto-devel installed successfully

2. Import Jenkins GPG Key ← NEW (This was missing!)
   └─ Key imported to system keyring

3. Add Jenkins Repository
   └─ Repository configuration added

4. Install Jenkins
   └─ GPG signature validation will now PASS
```

## What Changed

**File**: `ansible/roles/jenkins/tasks/main.yml`

**Added**:
- New task "Add Jenkins GPG key - RHEL" using `rpm_key` module
- Placed before the repository configuration task
- Includes retry logic and proper error handling

## Test the Fix

On your EC2 instance:

```bash
# Pull the latest changes
cd ~/CICD-Pipeline-Deployment-Using-Ansible-Jenkins-Docker/ansible
git pull

# Run the updated playbook
ansible-playbook site.yml -v
```

## Expected Output

```
TASK [java-11-amazon-corretto-devel installed]
ok: [localhost]

TASK [jenkins : Add Jenkins GPG key - RHEL] ← THIS IS NEW
changed: [localhost]
  msg: Key successfully imported

TASK [jenkins : Add Jenkins repository - RHEL]
changed: [localhost]

TASK [jenkins : Install Jenkins - RHEL] ← THIS WILL NOW SUCCEED
changed: [localhost]
  msg: ''
  rc: 0
  results:
  - 'Installed: jenkins-2.528.3-1.1.noarch'

TASK [jenkins : Start Jenkins service]
changed: [localhost]

PLAY RECAP
localhost: ok=X changed=Y unreachable=0 failed=0 ✅
```

## Verification After Installation

```bash
# Check Jenkins is running
systemctl status jenkins
# Expected: active (running)

# Access Jenkins web UI
curl http://localhost:8080
# Expected: Jenkins page (may require auth)

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

## Why This Works

1. **GPG Keys in RPM**: RPM package manager verifies packages with GPG keys
2. **Import First**: System needs the key in its keyring before validation
3. **rpm_key Module**: Ansible's `rpm_key` module handles key import
4. **Proper Sequencing**: Key import → Repo config → Package install

## Similar Pattern in Debian

The Debian side already had this pattern:
```yaml
- name: Add Jenkins GPG key - Debian
  apt_key:
    url: https://pkg.jenkins.io/debian/jenkins.io.key
    state: present
  ...
  when: ansible_os_family == "Debian"
```

We've now added the same for RHEL/Amazon Linux!

## File Modified

- ✅ `ansible/roles/jenkins/tasks/main.yml` - Added GPG key import task

## Next Steps

1. Pull the latest code: `git pull`
2. Run the playbook: `ansible-playbook site.yml -v`
3. This time Jenkins installation should succeed!

---

**Status**: ✅ GPG key issue fixed and ready for testing!

Expected time to complete: 5-10 minutes
Expected result: Full installation with all services running
