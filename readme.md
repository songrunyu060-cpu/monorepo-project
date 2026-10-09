# 创建一个monorepo项目步骤 (pnpm workspace)

### 1. 创建文件夹并初始化
    ```bash
    mkdir monorepo-project
    cd monorepo-project
    pnpm init
    ```

### 2. 创建 `pnpm-workspace.yaml` 文件
    ```yaml
    packages:
      - "packages/*"
    ```

### 3. 修改根目录的 `package.json` 文件

- 添加脚本 scripts中的脚本 按实际需求修改
- 管理版本 按实际需求修改
- 添加公共依赖 按实际需求修改

### 4. 配置 .gitignore 和 .editorconfig 文件


### 5. 安装配置 turbo

用来定义任务流水线、缓存、依赖、输出等
常用配置
- $schema IDE（VSCode）自动提示、校验 turbo.json 语法
- globalDependencies 全局依赖
- globalEnv 全局环境变量
- tasks 任务流水线
    - dependsOn 依赖任务
    - outputs 输出文件
    - inputs 输入文件
    - env 环境变量
    - cache 缓存
    - persistent 缓存持久化

- pnpm add turbo --save-dev -w
- 创建 turbo.json 文件
- 根 package.json scripts 追加turbo命令



### 6. git初始化
    ```bash
    git init
    git add .
    git commit -m "init monorepo project"
    ```
