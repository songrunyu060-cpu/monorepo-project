import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 缺变量时 create_async_engine(None) 抛的底层错误难以定位，这里显式拦下
    raise RuntimeError(
        "缺少环境变量 DATABASE_URL：请从仓库根目录的 .env.example 复制出 apps/video-backend/.env 并填写数据库连接串"
    )


# 使用数据库步骤 1 创建异步引擎 2 定义数据类 3 在app生命周期中使用异步引擎创建表 4 创建会话 5 执行操作
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10, # 连接池大小
    max_overflow=20, # 连接池最大溢出数
)

# 创建异步 Session 工厂 (推荐使用 async_sessionmaker)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession, # 指定会话类为 AsyncSession
    expire_on_commit=False, # 会话提交后不自动过期
    autoflush=False # 禁用自动刷新
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session