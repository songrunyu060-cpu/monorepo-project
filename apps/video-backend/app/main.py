from fastapi import FastAPI
from app.routers import news, user, favorite, history
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.base import ApiResponse
from app.utils.exception_handlers import register_exception_handlers
from app.utils.response import success_response

app = FastAPI()

# 注册异常处理
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有来源
    allow_credentials=True, # 允许携带Cookie
    allow_methods=["*"], # 允许所有方法
    allow_headers=["*"], # 允许所有头
)

# 注册路由
app.include_router(news.router)
app.include_router(user.router)
app.include_router(favorite.router)
app.include_router(history.router)

@app.get("/", response_model=ApiResponse[str])
async def root():
    return success_response(data="Hello World")

