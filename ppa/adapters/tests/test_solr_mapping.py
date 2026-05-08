class DummyWork:
    def __init__(self):
        self.title = "Test Title"
        self.metadata = {"ingredients": ["salt", "pepper"], "cook_time": "30m"}

    def get_adapter_field(self, path, default=None):
        parts = path.split(".")
        if parts[0] != "metadata":
            return getattr(self, path, default)
        cur = self.metadata
        for p in parts[1:]:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return default
        return cur


def test_map_model_to_solr_with_adapter(tmp_path):
    # Create a temporary adapter dir with adapter.yaml
    adapter_dir = tmp_path / "cookbook"
    adapter_dir.mkdir()
    adapter_yaml = adapter_dir / "adapter.yaml"
    adapter_yaml.write_text(
        """name: cookbook
field_map:
  ingredients_exact: metadata.ingredients
  ctxt: title
"""
    )

    from ppa.adapters.loader import load_adapter
    from ppa.solr_factory import map_model_to_solr

    adapter = load_adapter(str(adapter_dir))
    work = DummyWork()
    doc = map_model_to_solr(work, adapter=adapter)
    assert "ingredients_exact" in doc
    assert doc["ingredients_exact"] == ["salt", "pepper"]
