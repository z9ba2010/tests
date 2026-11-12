import pytest
from pydantic import BaseModel, HttpUrl, Field
from core.config import config

class ClothingItem(BaseModel):
    """Pydantic model for schema validation of a parsed clothing item."""
    id: str = Field(..., description="Unique product ID or SKU")
    title: str = Field(..., min_length=1, description="Item title")
    brand: str = Field(..., min_length=1, description="Brand name")
    price: float = Field(..., gt=0, description="Product price")
    currency: str = Field(default="RUB", description="Currency code")
    category: str = Field(..., description="Apparel category")
    in_stock: bool = Field(default=True)
    image_url: HttpUrl | None = None

class ParserSearchResponse(BaseModel):
    """Top-level API contract schema."""
    status: str
    total_found: int
    items: list[ClothingItem]


@pytest.mark.api
class TestClothingParserAPI:
    """Integration test suite for Clothing Parser Backend Service."""

    @pytest.mark.parametrize("query, category", [
        ("кроссовки беговые", "shoes"),
        ("рашгард компрессионный", "training"),
        ("спортивный костюм", "apparel"),
    ])
    def test_search_clothing_items_returns_200_and_valid_schema(self, api_session, query, category):
        """
        Verify:
        1. API endpoint returns HTTP 200 OK.
        2. Response matches strict JSON contract structure (ParserSearchResponse).
        3. Parsed items list is not empty.
        4. Response latency is acceptable (< 3.0s).
        """
        url = f"{config.PARSER_API_BASE_URL}/v1/clothing/search"
        params = {
            "query": query,
            "category": category,
            "limit": 10,
        }

        response = api_session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)

        # 1. Status Code Check
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}. Response: {response.text}"
        )

        # 2. Content-Type Header Check
        assert "application/json" in response.headers.get("Content-Type", ""), (
            f"Expected JSON content-type, got: {response.headers.get('Content-Type')}"
        )

        # 3. Latency Check
        assert response.elapsed.total_seconds() < 3.0, (
            f"Response latency exceeded 3s: {response.elapsed.total_seconds()}s"
        )

        # 4. JSON Structure & Contract Validation
        json_data = response.json()
        validated_data = ParserSearchResponse.model_validate(json_data)

        assert validated_data.status == "ok", f"Expected status 'ok', got {validated_data.status}"
        assert validated_data.total_found >= 0
        assert len(validated_data.items) > 0, f"Expected at least 1 item for query '{query}'"

        # Validate specific item fields
        first_item = validated_data.items[0]
        assert first_item.price > 0
        assert len(first_item.title) > 0

    def test_search_clothing_empty_query_returns_400(self, api_session):
        """
        Negative test case:
        Verify API returns HTTP 400 Bad Request when search query is empty.
        """
        url = f"{config.PARSER_API_BASE_URL}/v1/clothing/search"
        params = {"query": ""}

        response = api_session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)

        assert response.status_code == 400, (
            f"Expected 400 for empty query, got {response.status_code}"
        )
        data = response.json()
        assert "error" in data or "message" in data

    def test_direct_parser_extract_url(self, api_session):
        """
        Integration test: parsing apparel details directly from target source URL.
        """
        url = f"{config.PARSER_API_BASE_URL}/v1/parser/extract"
        payload = {
            "target_url": "https://example-shop.com/catalog/sport/item-98721",
            "source_type": "marketplace"
        }

        response = api_session.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)

        assert response.status_code in [200, 201], (
            f"Extract endpoint failed with status {response.status_code}"
        )
        item = ClothingItem.model_validate(response.json().get("data"))
        assert item.id is not None
        assert item.price > 0
