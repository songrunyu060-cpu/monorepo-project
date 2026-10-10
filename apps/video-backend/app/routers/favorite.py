from app.core.database import get_db
from app.crud import favorite
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.favorite import (
    CheckFavoriteResponse,
    FavoriteList,
    FavoriteListResponse,
    UpdateFavoriteRequest,
)
from app.utils.auth import get_current_user
from app.utils.response import success_response
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

# 收藏模块路由
router = APIRouter(prefix="/api/favorite", tags=["收藏"])


# 获取收藏状态
@router.get("/check", response_model=ApiResponse[CheckFavoriteResponse])
async def check_favorite(
    news_id: int = Query(..., alias="newsId", description="新闻ID"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_favorite = await favorite.get_favorite_info(db, user.id, news_id)
    return success_response(
        message="获取收藏状态成功", data=CheckFavoriteResponse(is_favorite=is_favorite)
    )


# 修改收藏状态
@router.post("/toggle", response_model=ApiResponse[CheckFavoriteResponse])
async def toggle_favorite(
    data: UpdateFavoriteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_favorite = await favorite.toggle_favorite(db, user.id, data.news_id)
    return success_response(
        message="修改收藏状态成功", data=CheckFavoriteResponse(is_favorite=is_favorite)
    )


# 获取新闻列表
@router.get("/list", response_model=ApiResponse[FavoriteListResponse])
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = []
    for news, favorite_time, favorite_id in rows:
        news.favorite_time = favorite_time
        news.favorite_id = favorite_id
        favorite_list.append(FavoriteList.model_validate(news))
    has_more = total > page * page_size

    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)


# 清空收藏列表
@router.delete("/clear", response_model=ApiResponse[None])
async def clear_favorite(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    count = await favorite.clear_favorite(db, user.id)
    return success_response(message=f"清空收藏列表成功, 共{count}条数据")
