from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.schemas.base import ResponseSchema


# --- 响应结构 (Response) ---
class CategoryItem(ResponseSchema):
    """新闻分类"""
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    sort_order: int = Field(..., description="排序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class CategoryListData(ResponseSchema):
    """新闻分类列表响应数据"""
    list: List[CategoryItem] = Field(..., description="分类列表")
    skip: int = Field(..., description="跳过的条数")
    limit: int = Field(..., description="本次查询的条数上限")


class NewsItem(ResponseSchema):
    """新闻列表项"""
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    description: Optional[str] = Field(None, description="新闻简介")
    content: str = Field(..., description="新闻内容")
    image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, description="作者")
    category_id: int = Field(..., description="新闻类别ID")
    views: int = Field(..., description="新闻浏览量")
    publish_time: datetime = Field(..., description="新闻发布时间")


class RelatedNewsItem(ResponseSchema):
    """相关新闻（不含新闻简介，与 crud.get_related_news 的返回字段保持一致）"""
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    content: str = Field(..., description="新闻内容")
    image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, description="作者")
    category_id: int = Field(..., description="新闻类别ID")
    views: int = Field(..., description="新闻浏览量")
    publish_time: datetime = Field(..., description="新闻发布时间")


class NewsListData(ResponseSchema):
    """新闻列表响应数据"""
    list: List[NewsItem] = Field(..., description="新闻列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数据条数")
    total: int = Field(..., description="新闻总数")
    has_more: bool = Field(..., description="是否还有更多")


class NewsDetailData(NewsItem):
    """新闻详情响应数据"""
    related_news: List[RelatedNewsItem] = Field(..., description="相关新闻")
