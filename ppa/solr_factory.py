"""Factory shim to return either real parasolr classes or fake fallbacks
depending on settings.ENABLE_SOLR_INDEXING.

Patch points in code should import from `ppa.solr_factory` instead of
`parasolr.django` so behavior can be toggled at runtime.
"""
import logging

logger = logging.getLogger(__name__)


# Defer Solr flag check to avoid circular import during model loading
def _is_solr_enabled():
    """Check if Solr indexing is enabled via waffle switch."""
    try:
        from ppa.flags import is_flag_enabled

        return is_flag_enabled("ENABLE_SOLR_INDEXING")
    except Exception:
        # If waffle isn't ready yet, default to False
        return False


# Always attempt to import real parasolr classes so they're available at runtime
RealSolrClient = None
RealSolrQuerySet = None
RealAliasedSolrQuerySet = None
try:
    from parasolr.django import (
        SolrClient as RealSolrClient,
        SolrQuerySet as RealSolrQuerySet,
        AliasedSolrQuerySet as RealAliasedSolrQuerySet,
    )
except Exception:
    logger.exception("Failed to import parasolr; will use fake clients")


class FakeSolrClient:
    class _Update:
        def index(self, *args, **kwargs):
            logger.debug("FakeSolrClient.index called; no-op")

        def delete_by_query(self, *args, **kwargs):
            logger.debug("FakeSolrClient.delete_by_query called; no-op")

    def __init__(self, *args, **kwargs):
        self.update = self._Update()


class FakeSolrQuerySet:
    """Minimal fake SolrQuerySet that returns empty results and supports all methods."""

    def __init__(self, *args, **kwargs):
        self._filters = {}

    # Query building methods - all return self for chaining
    def stats(self, *args, **kwargs):
        return self

    def facet(self, *args, **kwargs):
        return self

    def facet_range(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.facet_range called; returning self")
        return self

    def facet_field(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.facet_field called; returning self")
        return self

    def facet_pivot(self, *args, **kwargs):
        return {}

    def highlight(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.highlight called; returning self")
        return self

    def group(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.group called; returning self")
        return self

    def order_by(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.order_by called; returning self")
        return self

    def filter(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.filter called; returning self")
        return self

    def search(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.search called; returning self")
        return self

    def raw_query_parameters(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.raw_query_parameters called; returning self")
        return self

    def only(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.only called; returning self")
        return self

    def also(self, *args, **kwargs):
        logger.debug("FakeSolrQuerySet.also called; returning self")
        return self

    def all(self):
        return self

    def none(self):
        return self

    # Result retrieval methods
    def count(self):
        return 0

    def get_facets(self):
        """Return minimal object with facet attributes.

        The facet_pivot needs to support both attribute and dictionary access
        because different parts of the code use it differently.
        """

        class _FacetPivot(dict):
            """Facet pivot that supports both dict and attribute access."""

            def __init__(self):
                super().__init__()
                self["collections_exact"] = []
                self.collections_exact = []

        class _Facets:
            """Minimal facets object with all required attributes."""

            def __init__(self):
                self.facet_pivot = _FacetPivot()
                # facet_ranges needs to have 'pub_date' key with 'start', 'end', 'gap' structure
                self.facet_ranges = {
                    "pub_date": {"start": 1800, "end": 2000, "gap": 10, "counts": []}
                }
                # facet_fields needs to have the facet field names as keys
                # Each value should be a dict (not a list) for forms.py line 365-366
                self.facet_fields = {
                    "collections_exact": {},
                    "author_exact": {},
                    "pub_place": {},
                }

        return _Facets()

    def get_results(self):
        """Return empty results."""
        logger.debug("FakeSolrQuerySet.get_results called; returning empty dict")
        return {"docs": [], "numFound": 0}

    def get_highlighting(self):
        """Return empty highlighting."""
        logger.debug("FakeSolrQuerySet.get_highlighting called; returning empty dict")
        return {}

    # Magic methods
    def __iter__(self):
        """Return empty iterator."""
        return iter([])

    def __getitem__(self, key):
        """Support slicing and indexing.

        For slicing (e.g., qs[0:10]), return self to maintain chainability.
        For indexing (e.g., qs[0]), return empty list.
        """
        if isinstance(key, slice):
            # Return self for slicing to maintain queryset behavior
            logger.debug("FakeSolrQuerySet.__getitem__ (slice) called; returning self")
            return self
        else:
            # Return empty list for single item access
            logger.debug("FakeSolrQuerySet.__getitem__ (index) called; returning []")
            return []

    def __len__(self):
        """Return 0 for length."""
        return 0

    # Properties
    @property
    def groups(self):
        """Return empty groups for grouped queries."""
        return []


def SolrClientFactory(*args, **kwargs):
    if _is_solr_enabled() and RealSolrClient is not None:
        return RealSolrClient(*args, **kwargs)
    return FakeSolrClient()


def SolrQuerySetFactory(*args, **kwargs):
    if _is_solr_enabled() and RealSolrQuerySet is not None:
        return RealSolrQuerySet(*args, **kwargs)
    return FakeSolrQuerySet()


# Export names for backward-compatible imports
SolrClient = SolrClientFactory
SolrQuerySet = SolrQuerySetFactory
# AliasedSolrQuerySet must be a class (not factory) for inheritance to work
# Always use real class if available; runtime behavior controlled by SolrClient factory
if RealAliasedSolrQuerySet is not None:
    AliasedSolrQuerySet = RealAliasedSolrQuerySet
else:
    AliasedSolrQuerySet = FakeSolrQuerySet


def _resolve_instance_value(instance, path):
    """Resolve a dotted path like 'metadata.ingredients' or 'title' on instance."""
    if not path:
        return None
    if path.startswith("metadata."):
        # instance is expected to have get_adapter_field
        getter = getattr(instance, "get_adapter_field", None)
        if getter:
            return getter(path)
        # fallback: inspect metadata attribute
        meta = getattr(instance, "metadata", None)
        if isinstance(meta, dict):
            parts = path.split(".")[1:]
            cur = meta
            for p in parts:
                if isinstance(cur, dict) and p in cur:
                    cur = cur[p]
                else:
                    return None
            return cur
        return None
    # otherwise plain attribute
    return getattr(instance, path, None)


def map_model_to_solr(instance, adapter=None):
    """
    Map a model instance to Solr document using adapter field mappings.

    If adapter is None, determines applicable adapters from the instance's
    collections and merges fields from all adapters.

    Args:
        instance: DigitizedWork instance
        adapter: Optional single Adapter to use (for backward compatibility)

    Returns:
        Dict of Solr field mappings
    """
    doc = {}

    try:
        # If specific adapter provided, use it (backward compatibility)
        if adapter is not None:
            adapters = [adapter] if adapter else []
        else:
            # Get all adapters for this work's collections
            from ppa.adapters.loader import get_adapters_for_work

            adapters = get_adapters_for_work(instance)
    except Exception:
        adapters = []

    # Merge fields from all applicable adapters
    for adapter in adapters:
        if not getattr(adapter, "field_map", None):
            continue

        for solr_field, model_path in adapter.field_map.items():
            val = _resolve_instance_value(instance, model_path)
            if val is not None:
                # Later adapters can override earlier ones
                # (in case of field conflicts)
                doc[solr_field] = val

    return doc
