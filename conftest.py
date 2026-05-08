import pytest


@pytest.fixture(autouse=True)
def enable_solr_switch(db):
    """Enable the enable_solr_indexing waffle switch for all tests.

    This ensures SolrClientFactory and SolrQuerySetFactory return real
    parasolr clients when a Solr service is available (e.g. in CI).
    """
    from waffle.models import Switch
    Switch.objects.update_or_create(
        name="enable_solr_indexing", defaults={"active": True}
    )
