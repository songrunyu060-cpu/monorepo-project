# 新闻相关的缓存方法
from typing import Any

from app.core.cache import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"

# 读取缓存-新闻分类
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

# 写入缓存-新闻分类 key = news:categories + 分类数据 + 过期时间
# 分类、配置 7200；列表： 600； 详情： 1800；验证码：120 -- 数据越稳定，缓存越持久
# 避免所有key同时过期 引起缓存雪崩
async def set_cache_categories(data: list[dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)