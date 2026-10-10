from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.base import RequestSchema, ResponseSchema

# --- 请求结构 (Request) ---
class AddHistoryRequest(RequestSchema):
  """添加浏览记录请求"""
  news_id: int = Field(..., alias="newsId", description="新闻ID")


# --- 响应结构 (Response) ---
class HistoryList(ResponseSchema):
    """浏览历史新闻列表"""
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="新闻标题")
    content: str = Field(..., description="新闻内容")
    image: Optional[str] = Field(None, description="新闻图片")
    author: Optional[str] = Field(None, description="新闻作者")
    publish_time: datetime = Field(..., description="新闻发布时间")
    category_id: int = Field(..., description="新闻类别ID")
    views: int = Field(..., description="新闻浏览量")
    view_time: datetime = Field(..., description="浏览时间")
    history_id: int = Field(..., description="浏览历史ID")

class HistoryListResponse(
    ResponseSchema
):
    """浏览历史列表响应"""
    list: List[HistoryList] = Field(..., description="浏览历史列表")
    total: int = Field(..., description="浏览历史总数")
    hasMore: bool = Field(..., description="是否还有更多")
