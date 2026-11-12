import random
from locust import HttpUser, task, between

class ClothingParserLoadUser(HttpUser):
    """
    Locust load testing template for Clothing Parser backend.
    Simulates user searches and item extractions.
    """
    wait_time = between(1, 3)

    search_queries = [
        "кроссовки беговые",
        "спортивный топ",
        "рашгард",
        "лосины для фитнеса",
        "шорты спортивные",
        "ветровка влагозащитная"
    ]

    @task(3)
    def test_search_endpoint(self):
        """Simulate high volume search requests."""
        query = random.choice(self.search_queries)
        headers = {"Accept": "application/json"}
        with self.client.get(
            f"/v1/clothing/search?query={query}&limit=20",
            headers=headers,
            name="/v1/clothing/search",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def test_parser_extract_endpoint(self):
        """Simulate parsing extract workload."""
        payload = {
            "target_url": f"https://example-shop.com/catalog/item-{random.randint(1000, 9999)}",
            "source_type": "marketplace"
        }
        with self.client.post(
            "/v1/parser/extract",
            json=payload,
            name="/v1/parser/extract",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed extraction with status {response.status_code}")
