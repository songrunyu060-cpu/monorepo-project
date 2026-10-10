from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.news import get_categories, get_news_list, get_category_news_count, get_news_detail, increase_news_views, \
    get_related_news
from app.schemas.base import ApiResponse
from app.schemas.news import CategoryListData, NewsDetailData, NewsListData
from app.utils.response import success_response

# 新闻模块路由
router = APIRouter(prefix="/api/news", tags=["新闻"])

@router.get("/all", response_model=ApiResponse[None])
async def get_all_news():
    return success_response(message="获取所有新闻成功")

# 获取新闻分类
@router.get("/categories", response_model=ApiResponse[CategoryListData])
async def get_news_category(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    categories = await get_categories(db, skip, limit)
    return success_response(
        message="获取新闻分类成功",
        data=CategoryListData(list=categories, skip=skip, limit=limit)
    )

# 获取新闻列表
@router.get("/list", response_model=ApiResponse[NewsListData])
async def get_new_list(
        category_id: int = Query(None, description="新闻分类", alias="categoryId"),
        page: int = Query(1, description="当前页码", alias="page"),
        page_size: int = Query(10, description="每页数据条数", alias="pageSize"),
        db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表
       :param category_id: 新闻分类 ID
       :param page: 当前页码
       :param page_size: 每页数据条数
       :param db: 数据库异步会话
       :return: 分页格式的新闻列表响应
    """
    offset = (page - 1) * page_size
    news_list = await get_news_list(db, category_id, offset, page_size)
    total = await get_category_news_count(db, category_id)
    has_more = total > offset + len(news_list)
    return success_response(
        message="获取新闻列表成功",
        data=NewsListData(
            list=news_list,
            page=page,
            page_size=page_size,
            total=total,
            has_more=has_more
        )
    )

# 获取单条新闻详情
@router.get("/detail", response_model=ApiResponse[NewsDetailData])
async def get_detail(
        news_id: int = Query(None, description="新闻 ID", alias="id"),
        db: AsyncSession = Depends(get_db)
):
    # 获取新闻详情
    news_detail = await get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail=f"id: {news_id} 的新闻详情不存在")
    # 浏览量 + 1
    increase_result = await increase_news_views(db, news_detail.id)
    if not increase_result:
        raise HTTPException(status_code=404, detail="更新浏览量失败")
    # 获取相关新闻
    related_news = await get_related_news(db, news_detail.id, news_detail.category_id)
    return success_response(
        message="获取新闻详情成功",
        data=NewsDetailData(
            id=news_detail.id,
            title=news_detail.title,
            description=news_detail.description,
            content=news_detail.content,
            image=news_detail.image,
            author=news_detail.author,
            category_id=news_detail.category_id,
            views=news_detail.views,
            publish_time=news_detail.publish_time,
            related_news=related_news
        )
    )
