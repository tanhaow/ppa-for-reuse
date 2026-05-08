# PPA Django Reuse Documentation

Welcome to the PPA Django Reuse documentation. This guide will help you get started, understand the architecture, and contribute to the project.

## Quick Links

- **New to PPA?** Start with [Quick Start Guide](getting-started/quickstart.md)
- **Creating an adapter?** See [Adapter Guide](adapters/creating-adapters.md)
- **Contributing?** Read [Contributing Guide](development/contributing.md)
- **Deploying?** Check [Deployment Guide](operations/deployment.md)

## Documentation Structure

### Getting Started
- [Quick Start](getting-started/quickstart.md) - Get up and running in 3 steps
- [Setup Guide](getting-started/setup-guide.md) - Detailed setup instructions
- [Troubleshooting](getting-started/troubleshooting.md) - Common issues and solutions
- [Verification](getting-started/verification.md) - Verify your setup

### Architecture
- [Overview](architecture/overview.md) - System architecture and design
- [Adapter System](architecture/adapter-system.md) - How adapters work
- [Solr Integration](architecture/solr-integration.md) - Search architecture

### Adapters
- [Creating Adapters](adapters/creating-adapters.md) - Step-by-step guide
- [Cookbook Example](adapters/cookbook-example.md) - Complete example walkthrough
- [Adapter CLI](adapters/adapter-cli.md) - Using the adapter management CLI

### Development
- [Developer Setup](development/developer-setup.md) - Development environment
- [Contributing](development/contributing.md) - Contribution guidelines
- [Testing](development/testing.md) - Testing procedures

### Operations
- [Deployment](operations/deployment.md) - Production deployment
- [Solr Setup](operations/solr-setup.md) - Solr configuration
- [Data Import](operations/data-import.md) - Importing data

### Reference
- [Changelog](reference/changelog.md) - Version history
- [CLI Commands](reference/cli-commands.md) - Management commands
- [Feature Switches](reference/feature-switches.md) - Feature toggle management

## Project Information

- **Repository**: https://github.com/Princeton-CDH/ppa-django-reuse
- **License**: Apache 2.0
- **Python**: 3.12+
- **Django**: 5.2+
- **Wagtail**: 7.0+

## About PPA Django Reuse

PPA Django Reuse is a generalized Django application for managing and displaying digital archives. Originally developed for the Princeton Prosody Archive, it has been adapted into a reusable platform that can host different types of archival collections through a flexible adapter system.

### Key Features

- **YAML-driven adapter system** for different archive types
- **Full-text search** with Solr integration
- **Wagtail CMS** for content management
- **Docker-based** development environment
- **Simplified setup** with Devbox
- **Configurable display fields** per adapter
- **Template override system** for customization

### Use Cases

PPA Django Reuse is ideal for:
- Digital humanities projects
- Historical document collections
- Archival research platforms
- Specialized library collections
- Academic research databases

## Getting Help

- [GitHub Issues](https://github.com/Princeton-CDH/ppa-django-reuse/issues) - Report bugs or request features
- [Contributing Guide](development/contributing.md) - Learn how to contribute
- [Troubleshooting](getting-started/troubleshooting.md) - Common problems and solutions
