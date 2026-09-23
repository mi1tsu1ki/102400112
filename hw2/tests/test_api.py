import unittest
from pathlib import Path
from tempfile import gettempdir
from unittest.mock import patch

from backend.api import app
from backend import storage


class ReadApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True)
        cls.client = app.test_client()

    def test_search_returns_limited_results(self):
        response = self.client.get("/search?q=diffusion")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertGreater(body["count"], 0)
        self.assertLessEqual(len(body["results"]), 20)

    def test_trend_is_aggregated_and_bounded(self):
        response = self.client.get("/trend?top=3")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["years"], [2022, 2023, 2024])
        self.assertLessEqual(len(body["keywords"]), 3)
        self.assertLessEqual(len(body["series"]), 6)
        self.assertTrue(all(len(item["data"]) == 3 for item in body["series"]))

    def test_invalid_trend_limit_returns_bad_request(self):
        response = self.client.get("/trend?top=31")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_analysis_endpoints_return_displayable_data(self):
        self.assertEqual(self.client.get("/").status_code, 200)

        topics = self.client.get("/topics")
        self.assertEqual(topics.status_code, 200)
        self.assertEqual(len(topics.get_json()["topics"]), 10)

        network = self.client.get("/keyword-network")
        self.assertEqual(network.status_code, 200)
        body = network.get_json()
        self.assertGreater(len(body["nodes"]), 0)
        self.assertLessEqual(len(body["nodes"]), 100)

        conference_trend = self.client.get("/trend?top=3&conference=CVPR")
        self.assertEqual(conference_trend.status_code, 200)
        self.assertEqual(conference_trend.get_json()["conferences"], ["CVPR"])


class CrudApiTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.paper_file = Path(gettempdir()) / "cvpr_hw2_test_papers.json"
        if self.paper_file.exists():
            self.paper_file.unlink()
        self.storage_patch = patch.object(storage, "PAPER_FILE", self.paper_file)
        self.storage_patch.start()
        storage.save_papers([])

    def tearDown(self):
        self.storage_patch.stop()
        if self.paper_file.exists():
            self.paper_file.unlink()

    def test_crud_validation_and_consistency(self):
        invalid = self.client.post("/paper", json={})
        self.assertEqual(invalid.status_code, 400)

        paper = {
            "title": "Test Canonical Paper",
            "authors": ["Test Author"],
            "year": 2024,
            "conference": "CVPR",
            "pdf": "",
            "url": "https://example.test/paper",
        }
        created = self.client.post("/paper", json=paper)
        self.assertEqual(created.status_code, 201)

        duplicate = self.client.post("/paper", json=paper)
        self.assertEqual(duplicate.status_code, 409)

        searched = self.client.get("/search?q=canonical")
        self.assertEqual(searched.status_code, 200)
        self.assertEqual(searched.get_json()["count"], 1)

        detailed = self.client.get("/paper/Test%20Canonical%20Paper")
        self.assertEqual(detailed.status_code, 200)
        self.assertEqual(detailed.get_json()["title"], paper["title"])

        updated = self.client.put(
            "/paper/Test%20Canonical%20Paper",
            json={"conference": "ICCV"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["conference"], "ICCV")

        deleted = self.client.delete("/paper/Test%20Canonical%20Paper")
        self.assertEqual(deleted.status_code, 200)
        self.assertTrue(deleted.get_json()["success"])

        missing = self.client.delete("/paper/Test%20Canonical%20Paper")
        self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
