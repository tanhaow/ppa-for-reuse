import pytest


@pytest.fixture(autouse=True)
def enable_solr_switch(request):
    """Enable the enable_solr_indexing waffle switch for all tests that use the DB.

    This ensures SolrClientFactory and SolrQuerySetFactory return real
    parasolr clients when a Solr service is available (e.g. in CI).
    Skipped for SimpleTestCase subclasses that don't allow DB access.
    """
    # Only run if the test has database access (not SimpleTestCase)
    if "db" not in request.fixturenames and "django_db_setup" not in request.fixturenames:
        return
    from waffle.models import Switch
    Switch.objects.update_or_create(
        name="enable_solr_indexing", defaults={"active": True}
    )
