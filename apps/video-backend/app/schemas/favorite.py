from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.base import RequestSchema, ResponseSchema


# --- 请求结构 (Request) ---
class UpdateFavoriteRequest(RequestSchema):
  """修改收藏状态请求"""
  news_id: int = Field(..., alias="newsId", description="新闻ID")


# --- 响应结构 (Response) ---
class CheckFavoriteResponse(
    ResponseSchema
):
    """检查收藏状态响应"""
    is_favorite: bool = Field(..., description="是否收藏")

class FavoriteList(ResponseSchema):
    """收藏新闻列表"""
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    content: str = Field(..., description="新闻内容")
    image: Optional[str] = Field(None, description="新闻图片")
    author: Optional[str] = Field(None, description="新闻作者")
    publish_time: datetime = Field(..., description="新闻发布时间")
    category_id: int = Field(..., description="新闻类别ID")
    views: int = Field(..., description="新闻浏览量")
    favorite_time: datetime = Field(..., description="收藏时间")
    favorite_id: int = Field(..., description="收藏ID")

class FavoriteListResponse(
    ResponseSchema
):
    """收藏新闻列表响应"""
    list: List[FavoriteList] = Field(..., description="收藏新闻列表")
    total: int = Field(..., description="收藏新闻总数")
    hasMore: bool = Field(..., description="是否还有更多")