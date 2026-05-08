import os
from ppa.adapters.loader import load_adapter


def test_load_example_adapter():
    here = os.path.dirname(__file__)
    # expect examples are located relative to repo root; try relative path up
    base = os.path.abspath(os.path.join(here, "..", "..", "..", "examples", "adapters"))
    adapter_dir = os.path.join(base, "cookbook")
    adapter = load_adapter(adapter_dir)
    assert adapter.name == "cookbook"
    assert "ingredients" in adapter.field_map
