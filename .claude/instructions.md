# Mono App Monorepo 编码规范

## 项目结构

pnpm workspace monorepo，共3个业务项目 + 公共类型包

1. apps/video-backend：FastAPI Python后端，唯一数据源，Pydantic模型为类型真值
2. apps/video-game：H5移动端（Vite+React+TS）
3. apps/video-management：PC管理后台（Vite+React+TS）
4. packages/shared-types：公共TS类型包

- src/ 下所有 .ts 均为自动生成，**禁止手动修改**（文件头有标记）
  - api.ts：openapi-typescript 的原始产物（`paths`/`components`/`operations`）
  - common.ts / news.ts / user.ts / favorite.ts / history.ts：按路由前缀 `/api/<module>` 拆出的类型别名
  - index.ts：聚合全部模块，包入口
- 某类型被 ≥2 个模块引用时归入 common.ts，不要为了"就近"手工挪动

## 技术规范

1. TS项目全部继承 packages/tsconfig/base.json（extends `@monorepo/tsconfig/base.json`），不要重复写基础ts配置
   - base.json 只允许放 compilerOptions：extends 继承来的 include/exclude/files 等路径字段会按 base.json 所在目录解析（而非引用方目录），必须在各项目自己的 tsconfig 中声明
2. 代码校验分工（无冲突）
   - oxlint：仅代码质量、逻辑、最佳实践，关闭所有格式化规则
   - Prettier：全权代码排版格式化
3. Python后端 video-backend 不使用oxlint/prettier，使用ruff做lint+format
4. 类型流程：后端Pydantic模型 → dump openapi.json → 生成api.ts并按模块拆分 → H5/PC管理端直接import类型
   - `pnpm api:fetch-openapi` 直接调用 `app.openapi()` 落盘，**不需要先启动服务**，但需要 `apps/video-backend/.env` 里的 DATABASE_URL 存在（不校验真连）
   - `pnpm api:gen-types` = 生成 api.ts + 跑 `packages/shared-types/scripts/gen-modules.mjs` 拆模块，只跑前者会让分模块文件过期
   - 这两条脚本必须在**仓库根目录**执行，在子目录里跑会把产物写成嵌套路径（如 `packages/shared-types/packages/shared-types/src/api.ts`）
5. 禁止使用any，特殊场景必须加注释
6. 新增接口流程：后端写Pydantic模型 + 编写接口并添加 `response_model` → 执行 `api:fetch-openapi` + `api:gen-types` → 前端调用
   - **路由必须声明 `response_model`**，否则该接口在 OpenAPI 里响应 schema 为空，前端只能生成空类型
   - 响应统一用 `ApiResponse[T]` 信封（`app/schemas/base.py`），用 `success_response(data=..., message=...)` 构造；业务错误直接 `raise HTTPException`，由异常处理器输出同结构的三键信封
   - 成功响应的 HTTP 状态码恒为 200，`code` 是业务状态码

## 项目脚本

- 安装前端依赖：pnpm install
- 安装后端依赖：pnpm api:install
- H5移动端：pnpm game:dev / pnpm game:build
- PC管理后台：pnpm mgmt:dev / pnpm mgmt:build
- 后端服务：pnpm api:dev
- 同步后端类型：pnpm api:fetch-openapi && pnpm api:gen-types
- 代码质量校验：pnpm lint
- 自动修复lint：pnpm lint:fix
- 格式化：pnpm format
- 类型检查：pnpm typecheck
- 并行启动dev：pnpm dev

## 提交前检查

pnpm format && pnpm lint:fix && pnpm typecheck
