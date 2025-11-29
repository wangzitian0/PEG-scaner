# 架构文档（先读现状再决策，按 apps/libs/tools/docs/ops 分层）

> 5W1H 提示：每个二级模块都写清楚 Why/What/Where/When/Who/How，决策必须基于现状。

## apps（可运行目标）

### 运行目标与布局
- Why：集中可运行目标，清晰依赖与部署边界。
- What：
  - `apps/backend` (Backend: Python)
    - Seamless integration with Backend, Big Data, ML
    - Communication: GraphQL (Ariadne) for API; Neo4j for storage
  - `apps/mobile`（React Native + Vite for web preview）。
  - `apps/regression`（回归/Playwright）。
- Where：`apps/` 目录；Nx `project.json` 各自管理。
- When：开发/CI 通过 Nx 目标（例 `backend:test`、`regression:ping`、`regression:web-e2e`、`mobile:typecheck`）；本地一键 `npm run dev`。
- Who：终端用户、开发/QA。
- How：GraphQL `/graphql` 提供 ping/数据查询；Vite 产出静态资源；Playwright 校验 ping/UI。

### 数据与测试
- Why：保障数据可信与回归稳定。
- What：Neo4j 图谱数据；回归脚本在 `apps/regression`。
- Where：数据挂载 `x-data/neo4j/`，日志 `x-log/`。
- When：抓取/入库需≥3来源校验，避免重复抓取；改动后跑回归。
- Who：数据采集/因子计算/前端展示。
- How：使用 neomodel/bolt 读写；`nx run regression:*` 做健康/端到端。

## libs（共享契约与组件）

### 共享契约与组件
- Why：SSOT，避免重复与漂移。
- What：`libs/schema/` 持有 GraphQL SDL；后续可加 UI/feature/util 库。
- Where：`libs/` 根；Schema 直接被前后端/回归加载。
- When：业务字段新增/调整时先改 SDL，再更新客户端/服务端实现。
- Who：全部应用依赖。
- How：用 Nx dep graph + tags 限制引用；仅从 libs → apps，避免反向。

### 接口与协议 (GraphQL)
- Why：图谱同构（Graph DB -> Graph API -> Graph UI），按需查询，消除阻抗失配。
- What：GraphQL SDL (`.graphql`) 作为 SSOT；GraphQL over HTTP。
- Where：Schema 定义在 `libs/schema/`；后端使用 Ariadne/Strawberry；前端使用 Apollo/TanStack Query。
- When：Schema 变更后，前端重新生成类型/Hooks，后端更新 Resolver。
- Who：前端/后端/回归共用。
- How：以 `libs/schema/*.graphql` 为唯一真理；禁止 Ad-hoc 接口；利用 GraphiQL 调试。

### 依赖与版本
- Why：控制技术栈一致性。
- What：Node/Nx 版本锁在 `package.json`；Python 依赖在 backend 侧。
- Where：根锁文件与各项目虚拟环境。
- When：升级需评估对生成/工具链影响。
- Who：负责依赖的开发/运维。
- How：遵循 Nx 升级指南，先小范围验证再合并。

## tools（脚本与自动化）

### 启动与环境管理
- Why：统一入口，降低环境差异。
- What：`tools/envs/manage.py`（dev/start/restart/bootstrap），`tools/dev.sh`（ENV 感知一键启停）。
- Where：`tools/` 目录；`.env` 由环境侧提供，不入仓。
- When：开发/部署/调试前后使用；结构校验 `npm run lint:structure`。
- Who：开发/运维。
- How：ENV 注入、Neo4j Docker 管理、启动 backend/Metro/Vite，均调用 Nx 目标。

### 系统检查与生成
- Why：确保依赖齐全与生成链路正常。
- What：系统依赖检查脚本、未来可能的生成器/执行器。
- Where：`tools/`。
- When：新环境初始化、CI 预检查。
- Who：DevOps/Agent。
- How：按脚本指引运行，缺依赖时给出安装建议。

## docs（文档体系）

### 文档分层与索引
- Why：快速找到“对的位置”，减少沟通成本。
- What：`docs/index.md` 导航；`arch.md`（本文件）；`origin/` 不可变；`specs/`（PRD/TRD/DRD/IRD）；`project/BRN-*`（prompt/context/todowrite/phase_*）。
- Where：`docs/` 根；当前迭代在 `project/BRN-001/`。
- When：迭代前先读 `arch.md` + `specs/infra/IRD-001.ai_evaluation.md`；新增文档同步到各级 README。
- Who：全部 Agent/开发/产品。
- How：遵循“每级 README 做索引”，提示词记 `project/BRN-*/prompt.md` 与对应 `phase/append_promot.md`，避免多处副本。

### 评价与流程
- Why：AI-native 需要可量化的流程约束。
- What：评分/奖励机制在 `docs/specs/infra/IRD-001.ai_evaluation.md`，并在 `AGENTS.md` 强制引用。
- Where：`docs/specs/infra/`。
- When：每次动手前确认已读；评分<0.8 补 `todowrite`。
- Who：全部 Agent。
- How：按 IRD-001 的 Impact/Quality 执行与打分。

## ops（数据置信与验证）

### 数据来源与置信
- Why：确保数据可信，符合“宁空勿错”与“≥3 来源校验”。
- What：行情/新闻/财报等数据需至少三源比对；不可信则留空。
- Where：抓取流程挂钩到 Neo4j 入库前，校验规则与日志记录在 `x-log/`。
- When：每次抓取/入库前执行；异常时阻断入库。
- Who：数据采集与数据工程。
- How：浏览器/脚本多源比对，记录来源与时间戳，未通过校验的数据不写入 `x-data/neo4j/`。

### 去重与流量控制
- Why：避免重复抓取和被目标源限流。
- What：抓取任务需去重（按 symbol+源+时间窗口）；设置频率上限。
- Where：任务队列/调度逻辑；状态写入 `x-log/` 以便追踪。
- When：每次调度前检查最近抓取记录。
- Who：数据工程/Agent。
- How：维护抓取指纹，遇到重复则跳过或延迟；对外请求加退避/重试策略。

### 数据产物校验与回归
- Why：防止脏数据或破坏下游 UI/因子计算。
- What：基础校验（字段完整性/范围）、Schema 校验（Proto 反序列化）、回归脚本（`apps/regression` 针对数据路径）。
- Where：入库前/出库前；CI 或定期任务跑回归。
- When：每次数据批次或部署前；CI 触发。
- Who：数据工程/QA。
- How：使用 Proto 作为 Schema 门槛；必要时生成快照对比；失败阻断发布并写入 `todowrite`。

### 备份与追溯
- Why：支持回滚与审计。
- What：Neo4j 数据卷备份；日志保留抓取/校验记录。
- Where：`x-data/neo4j/` 备份到安全存储；`x-log/` 保存校验与抓取结果。
- When：定期备份；重大变更前后强制备份。
- Who：运维/数据工程。
- How：rsync/对象存储；保留元信息（版本、时间、来源）；恢复需校验一致性。
