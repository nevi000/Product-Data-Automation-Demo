from app.services.shop.base import ShopClient, ShopProduct
from app.services.shop.mock_adapter import MockShopAdapter

__all__ = ["ShopClient", "ShopProduct", "MockShopAdapter", "get_shop"]

_shop_singleton: MockShopAdapter | None = None


def get_shop() -> ShopClient:
    """Return the shop client.

    Ships only the in-memory `MockShopAdapter`. A real adapter (Shopware,
    commercetools, a bespoke storefront API) implements `ShopClient` and is
    selected here.
    """
    global _shop_singleton
    if _shop_singleton is None:
        _shop_singleton = MockShopAdapter()
    return _shop_singleton
