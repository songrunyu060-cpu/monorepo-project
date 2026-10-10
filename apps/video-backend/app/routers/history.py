from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, Depends, Path

from app.core.database import get_db
from app.crud import history
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.history import AddHistoryRequest, HistoryListResponse, HistoryList
from app.utils.auth import get_current_user
from app.utils.response import success_response

# 浏览历史模块路由
router = APIRouter(prefix="/api/history", tags=["浏览历史"])

# 添加浏览记录
@router.post("/add", response_model=ApiResponse[None])
async def add_history(
    data: AddHistoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加浏览记录成功")

# 删除单条浏览记录
@router.delete("/delete/{history_id}", response_model=ApiResponse[None])
async def delete_history(
    history_id: int = Path(..., description="浏览历史ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await history.delete_history(db, user.id, history_id)
    return success_response(message=f"删除浏览记录成功, 共{count}条数据")

# 获取浏览历史列表
@router.get("/list", response_model=ApiResponse[HistoryListResponse])
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = []
    for news, view_time, history_id in rows:
        news.view_time = view_time
        news.history_id = history_id
        history_list.append(HistoryList.model_validate(news))
    has_more = total > page * page_size

    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)

# 清空浏览历史列表
@router.delete("/clear", response_model=ApiResponse[None])
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await history.clear_history(db, user.id)
    return success_response(message=f"清空浏览历史列表成功, 共{count}条数据")
