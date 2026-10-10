# Mono App Monorepo 编码规范

## 项目结构

pnpm workspace monorepo，共3个业务项目 + 公共类型包

1. apps/videoBackend：FastAPI Python后端，唯一数据源，Pydantic模型为类型真值
2. apps/videoGame：H5移动端（Vite+React+TS）
3. apps/videoManagement：PC管理后台（Vite+React+TS）
4. packages/shared-types：公共TS类型包

- src/api.ts：由openapi-typescript自动从后端OpenAPI生成，**禁止手动修改**

## 技术规范

1. TS项目全部继承 packages/tsconfig/base.json（extends `@monorepo/tsconfig/base.json`），不要重复写基础ts配置
   - base.json 只允许放 compilerOptions：extends 继承来的 include/exclude/files 等路径字段会按 base.json 所在目录解析（而非引用方目录），必须在各项目自己的 tsconfig 中声明
2. 代码校验分工（无冲突）
   - oxlint：仅代码质量、逻辑、最佳实践，关闭所有格式化规则
   - Prettier：全权代码排版格式化
3. Python后端 videoBackend 不使用oxlint/prettier，使用ruff做lint+format
4. 类型流程：后端Pydantic模型 → 启动后端 → 拉取openapi.json → 生成api.ts → H5/PC管理端直接import类型
5. 禁止使用any，特殊场景必须加注释
6. 新增接口流程：后端写Pydantic模型 + 编写接口并添加response_model → 启动后端 → 执行api:fetch-openapi + api:gen-types → 前端调用

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
