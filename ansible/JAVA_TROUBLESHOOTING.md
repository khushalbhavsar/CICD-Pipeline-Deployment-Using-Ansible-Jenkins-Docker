# Java Package Installation Troubleshooting

## Issue: "No package java-11-openjdk-devel available"

### What Happened
On Amazon Linux 2023, the Java package names differ from earlier versions. The playbook now tries multiple fallback options:

1. ✅ `java-11-openjdk-devel` (Primary - Standard OpenJDK)
2. ✅ `java-11-amazon-corretto-devel` (Fallback 1 - Amazon's distribution)
3. ✅ `java-11-openjdk` (Fallback 2 - Without devel tools)
4. ✅ `java-17-amazon-corretto` (Fallback 3 - Newer version)

### Solution
The updated playbook now includes automatic fallback logic. Just run the playbook again:

```bash
ansible-playbook site.yml -v
```

### Manual Fix (If Needed)

If you want to manually install Java first:

```bash
# Check what Java packages are available
yum search java-11

# Install one of these:
sudo yum install -y java-11-openjdk-devel         # Standard OpenJDK
# OR
sudo yum install -y java-11-amazon-corretto-devel # Amazon Corretto
# OR  
sudo yum install -y java-17-amazon-corretto       # Java 17 (newer)
```

### Verify Installation

```bash
java -version
javac -version
```

Both should show Java 11 or 17.

### Available Java Packages on Amazon Linux 2023

Run this to see what's available:
```bash
yum search java-11 | grep Available
yum list available java-11*
yum list available java-17*
```

### Jenkins Requirements

Jenkins needs Java with the development tools (includes javac). Any of these will work:
- Java 11 OpenJDK
- Java 11 Amazon Corretto
- Java 17 Amazon Corretto
- Java 17 OpenJDK

### Testing the Playbook

```bash
# Run with full verbosity to see which Java version gets installed
ansible-playbook site.yml -vv

# Check which Java was installed
java -version

# Verify Jenkins can start
systemctl status jenkins
```

---

**Note**: The playbook now automatically handles this with fallback logic. Run it again and it should succeed!
