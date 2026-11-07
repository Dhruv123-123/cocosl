from fastapi.testclient import TestClient


def test_report_page(home, monkeypatch):
    monkeypatch.setenv("DASHBOARD_TOKEN", "t")
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    from contentfactory.web.app import create_app
    c = TestClient(create_app(Factory.create(Settings.load(home))))
    h = {"Authorization": "Bearer t"}
    r = c.get("/report", headers=h)
    assert r.status_code == 200 and "Next actions" in r.text
    r = c.post("/report/save", headers=h, follow_redirects=False)
    assert r.status_code == 303 and "Saved" in r.headers["location"]
