from app.models.history import History
from app.models.news import News
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


# 添加浏览记录
async def add_history(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    return history


# 删除单条浏览记录
async def delete_history(
    db: AsyncSession,
    user_id: int,
    history_id: int,
):
    result = await db.execute(
        delete(History).where(History.user_id == user_id, History.id == history_id)
    )
    await db.commit()
    return result.rowcount or 0


# 获取浏览历史列表
async def get_history_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
):
    count_query = select(func.count(History.id)).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    if total is None:
        total = 0

    query = (
        select(
            News, History.view_time.label("view_time"), History.id.label("history_id")
        )
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 清空浏览历史列表
async def clear_history(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(delete(History).where(History.user_id == user_id))
    await db.commit()
    return result.rowcount or 0
