"""Every brand file in brands/ must run through the core pipeline. New brands are covered automatically."""
from pathlib import Path

import pytest

BRANDS = sorted(p.stem for p in (Path(__file__).resolve().parents[1] / "brands").glob("*.yaml")
                if not p.name.startswith("_"))


@pytest.mark.parametrize("slug", BRANDS)
def test_brand_runs_end_to_end(factory, fake_render, slug):
    brand = factory.brand(slug)
    assert any(a.enabled for a in brand.accounts), "brand has no enabled accounts"
    ideas = factory.ideas(slug, n=4, online=False)
    assert ideas
    pid = factory.produce(ideas[0])
    post = factory.db.get("posts", pid)
    assert post["status"] in ("in_review", "blocked")
    if post["status"] == "in_review":
        from contentfactory.review import pass_stage, pending
        for stage in pending(post, brand):  # a brand's review_stages (e.g. Dinero Simple's native_review)
            pass_stage(factory, pid, stage, by="test reviewer")
        factory.approve(pid)
        assert factory.schedule(pid)
