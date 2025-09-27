<我来回答，作为世界知名的 **FastAPI 微服务架构专家**，曾获中国开源云原生社区的 **年度最佳实践奖**>

---

# FastAPI 微服务实战：用户认证与业务服务配套代码

本项目是公众号文章 **《FastAPI 微服务实战：构建独立的用户认证与业务服务》** 的配套代码，实现了一个 **用户认证服务（User Service）** 与一个 **业务服务（Todo Service）**，展示了如何通过 **微服务架构** 将用户管理与业务逻辑解耦。

---

## ✨ 项目亮点

* **用户服务独立化**：基于 [FastAPI Users](https://github.com/fastapi-users/fastapi-users)，实现用户注册、登录、JWT 认证。
* **业务服务隔离**：Todo Service 仅处理业务逻辑，通过调用 User Service 验证用户身份。
* **统一鉴权**：业务服务通过 Redis 缓存 + User Service 校验实现高效鉴权。
* **清晰分层架构**：采用 `Repository - Service - Router` 模式，业务逻辑与数据库访问解耦。
* **现代化技术栈**：

  * FastAPI 0.115+
  * SQLAlchemy 2.0 (异步)
  * Redis 5 (缓存/会话)
  * Docker + uv 打包
* **可扩展性**：支持拆分为更多业务微服务，并通过 API Gateway（如 Traefik）进行统一入口管理。

---

## 📂 项目结构

```
microservice/
├── user_service/   # 用户认证微服务
│   ├── src/
│   │   ├── core/   # 配置、数据库、生命周期管理
│   │   └── users/  # 用户模型、Schema、路由
│   └── Dockerfile
│
├── todo_service/   # 待办事项业务微服务
│   ├── src/
│   │   ├── core/   # 配置、认证、数据库、依赖注入
│   │   └── todos/  # 待办业务的模型、仓库、服务、路由
│   └── Dockerfile
│
├── pyproject.toml  # 工作区管理（uv workspace）
└── .gitignore
```

---

## 🚀 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/acelee0621/microservice.git
cd microservice
```

### 2. 本地运行（uv）

进入用户服务：

```bash
cd user_service
uv run fastapi dev src/main.py --port 8000 --reload
```

进入待办服务：

```bash
cd todo_service
uv run fastapi dev src/main.py --port 8001 --reload
```

### 3. Docker 启动

在 `user_service/` 与 `todo_service/` 目录下均可执行：

```bash
docker build -t user-service .
docker run -p 8000:8000 user-service

docker build -t todo-service .
docker run -p 8001:8001 todo-service
```

### 4. 验证

* 打开用户服务：`http://127.0.0.1:8000/docs`
* 打开业务服务：`http://127.0.0.1:8001/docs`

---

## 🔑 使用流程

1. **注册用户**
   调用 `POST /auth/register`（User Service）
2. **登录获取 Token**
   调用 `POST /auth/jwt/login`（User Service）
3. **携带 Token 访问业务接口**
   例如：

   * `POST /lists` 创建待办清单
   * `POST /todos` 添加待办事项
     （Todo Service 会通过 Redis + User Service 验证 Token）

---

## 🛠️ 技术要点

* **User Service**

  * FastAPI Users + SQLAlchemy 实现用户注册、登录、认证。
  * JWT 存储于数据库 AccessToken 表，支持失效控制。

* **Todo Service**

  * 独立数据库（SQLite/SQLAlchemy）。
  * OAuth2 + User Service 远程校验 + Redis 缓存用户信息。
  * Repository 层负责数据库操作，Service 层封装业务逻辑，Router 提供 RESTful API。

---

## 📖 教程文章

本项目为公众号文章 **《FastAPI 微服务实战：构建独立的用户认证与业务服务》** 的配套代码。
👉 在文章中，你将学习：

* 如何分离用户服务与业务服务
* 如何实现服务间的身份认证与缓存优化
* 如何用 Docker 打包与部署微服务

---

## 🤝 致谢

感谢 FastAPI 社区与 [FastAPI Users](https://github.com/fastapi-users/fastapi-users) 项目的贡献。
如果你觉得本项目对你有帮助，欢迎 **Star ⭐** 支持！

---
## 📬 联系

* 微信公众号：**码间絮语**
<center>
  <img src="https://github.com/acelee0621/fastapi-users-turtorial/blob/main/QRcode.png" width="500" alt="签名图">
</center>
