# Troubleshooting Guide

This guide covers common issues you might encounter when setting up or using PPA Django Reuse.

## Setup Issues

### Devbox Path with Spaces Issue

**Problem**: Devbox 0.16.0 cannot handle paths containing spaces.

**Symptoms**:
- `devbox run` commands fail with "No such file or directory"
- Error message shows path truncated at first space
- Example: `/Users/ht8933/Documents/Documents - cdh-m5945fhwr7/` becomes `/Users/ht8933/Documents/Documents`

**Solutions**:

#### Option 1: Move Project (Recommended)
```bash
# Move to path without spaces
mv "/Users/ht8933/Documents/Documents - cdh-m5945fhwr7/dev/ppa-django-reuse" \
   "/Users/ht8933/dev/ppa-django-reuse"
cd /Users/ht8933/dev/ppa-django-reuse
devbox shell
```

#### Option 2: Use Manual Setup
```bash
# Don't use devbox commands, run scripts directly
source .venv/bin/activate
bash scripts/setup.sh
bash scripts/verify.sh
python manage.py runserver
```

#### Option 3: Create Symlink
```bash
# Create symlink without spaces
ln -s "/Users/ht8933/Documents/Documents - cdh-m5945fhwr7/dev/ppa-django-reuse" \
      "/Users/ht8933/ppa-django-reuse"
cd /Users/ht8933/ppa-django-reuse
devbox shell
```

### Port Conflicts

**Problem**: Ports 5432 (PostgreSQL) or 8983 (Solr) are already in use.

**Symptoms**:
- Docker containers fail to start
- Error: "port is already allocated"

**Solution**:
```bash
# Find what's using the port
lsof -i :5432
lsof -i :8983

# Stop conflicting services
docker ps
docker stop <container_id>

# Or stop all Docker containers
docker stop $(docker ps -q)
```

### Docker Services Not Starting

**Problem**: PostgreSQL or Solr containers won't start.

**Symptoms**:
- `docker compose ps` shows containers as "Exited"
- Verification script reports services not running

**Solution**:
```bash
# Check Docker service status
docker compose -f docker/docker-compose.dev.yml ps

# View logs for errors
docker compose -f docker/docker-compose.dev.yml logs db
docker compose -f docker/docker-compose.dev.yml logs solr

# Restart services
docker compose -f docker/docker-compose.dev.yml restart

# If that doesn't work, recreate containers
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d
```

### Database Connection Failed

**Problem**: Django cannot connect to PostgreSQL.

**Symptoms**:
- "could not connect to server" error
- Verification script reports database connection failed

**Solution**:
```bash
# Wait for PostgreSQL to be ready
docker compose -f docker/docker-compose.dev.yml exec db pg_isready -U ppa

# Check if database exists
docker compose -f docker/docker-compose.dev.yml exec db psql -U ppa -d ppa -c "\dt"

# Check DATABASE_URL environment variable
echo $DATABASE_URL

# Should be: postgresql://ppa:ppa@localhost:5432/ppa
```

### Python/Node.js Version Issues

**Problem**: Wrong Python or Node.js version installed.

**Symptoms**:
- Verification script shows version mismatch
- Import errors or syntax errors

**Solution with Devbox**:
```bash
# Exit and re-enter devbox shell
exit
devbox shell

# Verify versions
python --version  # Should be 3.12.x
node --version    # Should be v22.x
```

**Solution without Devbox**:
```bash
# Install correct Python version
brew install python@3.12

# Install correct Node.js version
brew install node@22

# Update PATH
export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
```

### Virtual Environment Issues

**Problem**: Virtual environment not activated or corrupted.

**Symptoms**:
- Python packages not found
- Wrong Python version in use

**Solution**:
```bash
# Remove old virtual environment
rm -rf .venv

# Create new virtual environment
python3.12 -m venv .venv

# Activate it
source .venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt -r dev-requirements.txt
```

### npm Dependencies Missing

**Problem**: Node modules not installed.

**Symptoms**:
- Static files not built
- npm commands fail

**Solution**:
```bash
# Remove old node_modules
rm -rf node_modules

# Reinstall dependencies
npm install

# Build static files
npm run build
```

## Runtime Issues

### Solr Not Responding

**Problem**: Solr API not accessible.

**Symptoms**:
- Search functionality not working
- Solr admin interface not loading at http://localhost:8983

**Solution**:
```bash
# Check if Solr container is running
docker compose -f docker/docker-compose.dev.yml ps solr

# Check Solr logs
docker compose -f docker/docker-compose.dev.yml logs solr

# Test Solr API
curl http://localhost:8983/solr/ppa/admin/ping

# Restart Solr
docker compose -f docker/docker-compose.dev.yml restart solr

# If core doesn't exist, recreate it
docker compose -f docker/docker-compose.dev.yml exec solr solr create_core -c ppa
```

### Adapter Validation Fails

**Problem**: Adapter configuration is invalid.

**Symptoms**:
- `python manage.py adapter validate` reports errors
- Application fails to load adapter

**Solution**:
```bash
# Validate adapter with detailed output
python manage.py adapter validate <adapter_name>

# Check adapter.yaml syntax
python -c "import yaml; yaml.safe_load(open('examples/adapters/<adapter_name>/adapter.yaml'))"

# Common issues:
# - Missing required fields (name, field_map)
# - Invalid YAML syntax
# - Incorrect field paths in field_map
```

### Template Not Found

**Problem**: Django cannot find adapter templates.

**Symptoms**:
- TemplateDoesNotExist error
- Pages render with default templates instead of adapter templates

**Solution**:
```bash
# Check adapter templates directory exists
ls -la examples/adapters/<adapter_name>/templates/

# Verify ARCHIVE_ADAPTER setting
python manage.py shell -c "from django.conf import settings; print(settings.ARCHIVE_ADAPTER)"

# Check template loader configuration
python manage.py shell -c "from django.conf import settings; print(settings.TEMPLATES[0]['DIRS'])"

# Restart server after template changes
```

### Migration Issues

**Problem**: Database migrations fail or are out of sync.

**Symptoms**:
- "No such table" errors
- Migration conflicts

**Solution**:
```bash
# Check migration status
python manage.py showmigrations

# Run pending migrations
python manage.py migrate

# If migrations are conflicted, reset database
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d
sleep 5
python manage.py migrate

# Recreate admin user
python manage.py createsuperuser
```

## Development Issues

### Pre-commit Hooks Failing

**Problem**: Git commits blocked by pre-commit hooks.

**Symptoms**:
- Commit fails with formatting errors
- Black, isort, or other tools report issues

**Solution**:
```bash
# Run pre-commit manually to see issues
pre-commit run --all-files

# Auto-fix formatting issues
black .
isort .

# If hooks are broken, reinstall
pre-commit uninstall
pre-commit install
```

### Tests Failing

**Problem**: pytest or npm tests fail.

**Symptoms**:
- Test suite reports failures
- CI/CD pipeline fails

**Solution**:
```bash
# Run tests with verbose output
pytest -v

# Run specific test
pytest ppa/archive/tests/test_models.py::TestDigitizedWork

# Check test database
python manage.py test --keepdb

# For JavaScript tests
npm test -- --verbose
```

## Complete Reset

If all else fails, perform a complete reset:

```bash
# Using Devbox
devbox run clean
devbox run setup

# Or manually
docker compose -f docker/docker-compose.dev.yml down -v
rm -rf .venv node_modules static/js static/css
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r dev-requirements.txt
npm install
bash scripts/setup.sh
```

## Getting More Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/Princeton-CDH/ppa-django-reuse/issues) for similar problems
2. Run the verification script: `bash scripts/verify.sh`
3. Check Docker logs: `docker compose -f docker/docker-compose.dev.yml logs`
4. Create a new issue with:
   - Your operating system and version
   - Python and Node.js versions
   - Complete error message
   - Steps to reproduce the issue
