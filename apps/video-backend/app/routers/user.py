from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.user import (
    create_user,
    generate_token,
    get_user_by_username,
    update_user_password,
    update_user_profile,
    verify_user,
)
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.user import (
    UserAuthResponse,
    UserInfoResponse,
    UserLoginReq,
    UserProfileUpdateReq,
    UserUpdatePasswordReq,
)
from app.utils.auth import get_current_user
from app.utils.response import success_response
from app.utils.security import verify_password

# 新闻模块路由
router = APIRouter(prefix="/api/user", tags=["用户"])
current_user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)

# 用户注册
@router.post("/register", response_model=ApiResponse[UserAuthResponse])
async def register(user_data: UserLoginReq, db: AsyncSession = db_dependency):
    # 注册逻辑: 验证用户是否存在 -> 创建用户 -> 生成 Token -> 响应结果
    # 查询用户是否存在
    user = await get_user_by_username(db, user_data.username)
    if user:
        raise HTTPException(status_code=400, detail="用户已存在")

    # 新增用户
    user = await create_user(db, user_data)

    # 生成token
    token = await generate_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userinfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "email": user.email,
    #             "phone": user.phone
    #         }
    #     }
    # }

    return success_response(
        message="注册成功",
        data=UserAuthResponse(
            token=token,
            user_info=UserInfoResponse.model_validate(user)
        )
    )

# 用户登录
@router.post("/login", response_model=ApiResponse[UserAuthResponse])
async def login(user_data: UserLoginReq, db: AsyncSession = db_dependency):
    # 登录逻辑: 验证用户和密码是否正确 -> 生成 Token -> 响应结果
    user = await verify_user(db, user_data)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或密码错误")
    token = await generate_token(db, user.id)
    return success_response(
        message="登录成功",
        data=UserAuthResponse(
            token=token,
            user_info=UserInfoResponse.model_validate(user)
        )
    )

# 获取用户信息
@router.get("/info", response_model=ApiResponse[UserInfoResponse])
async def get_user_info(user: User = current_user_dependency):
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

# 修改用户信息
@router.put("/update", response_model=ApiResponse[UserInfoResponse])
async def update_user_info(
    user_data: UserProfileUpdateReq,
    user: User = current_user_dependency,
    db: AsyncSession = db_dependency
):
    # 修改用户信息逻辑: 验证用户 -> 修改用户信息 -> 响应结果
    update_user = await update_user_profile(db, user.username, user_data)
    return success_response(
        message="修改用户信息成功",
        data=UserInfoResponse.model_validate(update_user)
    )

# 修改用户密码
@router.put("/password", response_model=ApiResponse[None])
async def update_password(
    data: UserUpdatePasswordReq,
    user: User = current_user_dependency,
    db: AsyncSession = db_dependency
):
    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="当前密码错误")
    result = await update_user_password(db, user.username, data)
    if not result:
        raise HTTPException(status_code=400, detail="修改用户密码失败")
    return success_response(message="修改用户密码成功")
