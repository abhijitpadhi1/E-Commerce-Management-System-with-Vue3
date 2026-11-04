from collections.abc import Iterable

from flask import current_app

from app.extensions import cache


PRODUCT_LIST_CACHE_KEY = "products:active:list"


def get_product_detail_cache_key(product_id: int) -> str:
    """Return the cache key for a product's detail response."""
    return f"product:detail:{product_id}"


def invalidate_product_caches(product_ids: Iterable[int] | None = None) -> None:
    """
    Invalidate the active product catalogue and selected product-detail caches.

    Cache invalidation is fail-open: Redis errors are logged but do not
    interrupt the database operation that triggered invalidation.
    """
    cache_keys = [PRODUCT_LIST_CACHE_KEY]

    if product_ids is not None:
        cache_keys.extend(
            get_product_detail_cache_key(product_id) for product_id in product_ids
        )

    for cache_key in cache_keys:
        try:
            cache.delete(cache_key)
        except Exception:
            current_app.logger.exception(
                "Failed to invalidate product cache key: %s", cache_key
            )
