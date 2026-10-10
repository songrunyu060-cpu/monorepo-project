from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.news import News


async def get_favorite_info(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    query = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.news_id == news_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def toggle_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    is_favorite = await get_favorite_info(db, user_id, news_id)
    if is_favorite:
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id, Favorite.news_id == news_id
        )
        await db.execute(stmt)
        new_status = False
    else:
        db.add(Favorite(user_id=user_id, news_id=news_id))
        new_status = True
    await db.commit()
    return new_status


# 获取收藏列表
async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
):
    # 还要获取总数
    count_query = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    if total is None:
        total = 0
    # 获取收藏列表 - 联表查询 join() + 收藏时间排序 + 分页
    # select(查询主体模型类, 字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 别名： Favorite.created_at.label("favorite_time")
    # [
    #   (新闻对象, 收藏时间, 收藏id)
    # ]
    query = (
        select(
            News,
            Favorite.created_at.label("favorite_time"),
            Favorite.id.label("favorite_id"),
        )
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


async def clear_favorite(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(delete(Favorite).where(Favorite.user_id == user_id))
    await db.commit()
    return result.rowcount or 0
