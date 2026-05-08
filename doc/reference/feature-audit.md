PPA feature audit
=================

This file catalogs PPA-specific features, where they appear in the codebase,
and their external dependencies. It's intended to guide decisions about what
can be flagged off or moved to adapters.

High-level features and external dependencies
---------------------------------------------
- Solr indexing & search
  - Code locations:
    - `ppa/archive/models.py` (Collection.stats uses SolrQuerySet)
    - `ppa/archive/solr.py` (search querysets)
    - `ppa/dataset/management/commands/generate_textcorpus.py`
    - `ppa/archive/management/commands/index_pages.py`
    - `ppa/archive/admin.py`
  - External dependency: Solr (parasolr client)

- HathiTrust pairtree and API support
  - Code locations:
    - `ppa/archive/hathi.py` (Hathi API, HathiObject, METS parsing)
    - `ppa/archive/import_util.py` (HathiImporter)
    - `ppa/archive/management/commands/hathi_import.py` (rsync/pairtree commands)
  - External dependency: local Hathi pairtree data (HATHI_DATA)

- corppa (NLP / corpus tooling)
  - Code locations:
    - referenced in `requirements.txt` and `/doc/development/developer-notes.rst`
    - used for corpus filtering / export workflows
  - External dependency: `github.com/Princeton-CDH/ppa-nlp` (git dependency)

- PUCAS / CAS / LDAP auth
  - Code locations:
    - `ppa/settings/components/base.py` (INSTALLED_APPS includes pucas / django_cas_ng)
    - `ppa/urls.py` (includes `pucas.cas_urls`)
  - External dependency: CAS server / LDAP for auth

- Template branding and editorial content
  - Code locations:
    - `templates/` (PPA-specific templates)
    - `ppa/pages/` and `ppa/editorial/` (Wagtail page types and blocks)
  - External dependency: none, but tightly coupled to PPA fields and assumptions

- Pairtree / Hathi rsync tooling
  - Code locations:
    - `ppa/archive/management/commands/hathi_rsync.py`
    - `DEVELOPERNOTES.rst` docs
  - External dependency: local filesystem pairtree directories, rsync

Recommendations (short)
-----------------------
- Gate heavy features with runtime flags (Hathi, Solr, corppa, PUCAS).
- Move corppa out of core requirements to an extras file and provide a shim.
- Provide Docker Compose for local Solr/Postgres to simplify onboarding.
- Provide a FakeSolrClient factory used when Solr is disabled.



