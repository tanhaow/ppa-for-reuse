import pytest


@pytest.fixture(autouse=True)
def enable_solr_switch(request):
    """Enable the enable_solr_indexing waffle switch for all tests that use the DB.

    This ensures SolrClientFactory and SolrQuerySetFactory return real
    parasolr clients when a Solr service is available (e.g. in CI).
    Silently skipped for tests that don't allow DB access (e.g. SimpleTestCase).
    """
    try:
        from waffle.models import Switch
        Switch.objects.update_or_create(
            name="enable_solr_indexing", defaults={"active": True}
        )
    except Exception:
        # DB not available for this test (e.g. SimpleTestCase) — skip silently
        pass
