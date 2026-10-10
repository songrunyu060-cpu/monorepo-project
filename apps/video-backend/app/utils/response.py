from app.schemas.base import ApiResponse


def success_response[T](
    data: T | None = None, message: str = "success", code: int = 200
) -> ApiResponse[T]:
    """构造统一成功响应体

    直接返回 Pydantic 模型而非 JSONResponse，让 FastAPI 能按路由声明的
    response_model 做校验与序列化（同时 OpenAPI 才能生成前端需要的类型）。
    注意 code 是业务状态码，HTTP 状态码恒为 200；业务错误请直接 raise HTTPException。
    """
    return ApiResponse[T](code=code, message=message, data=data)
