from contentfactory.site import export_site


def test_export_site_bundles_public_pages(factory, tmp_path):
    res = export_site(factory, tmp_path / "site", base_url="https://f.example.com")
    out = tmp_path / "site"
    assert (out / "index.html").exists() and (out / "_headers").exists()
    slug = next(iter(factory.brands()))
    assert f"{slug}/index.html" in res["pages"]
    page = (out / slug / "index.html").read_text()
    assert "https://f.example.com" in page
