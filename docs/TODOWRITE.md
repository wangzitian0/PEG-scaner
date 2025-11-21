# TODOWRITE

This document tracks the requirements from `agent.md` and their completion status.

## 需求要求 (Requirements)

### 界面 (UI)
- [ ] **界面 1: 个股信息界面 (Individual Stock Info UI)**
- [X] 界面 1: 个股信息界面 (Individual Stock Info UI) - 日、周、月的 K线和交易量 (Daily, weekly, monthly K-lines and trading volume) (Backend data fetching implemented)
    - [ ] 新闻 (News)
    - [ ] company F10 (F10 financial data)
        - [ ] Earning Hub
        - [ ] Company Valuation: PS, PE, PB
        - [ ] operating data
        - [ ] revenue breakdown
        - [ ] financial estimates
        - [ ] financial indecators: EPS, FCF, Current Ratio, ROE
        - [ ] ... (other F10 data)
- [ ] **界面 2: 个股因子计算 (Individual Stock Factor Calculation)**
    - [ ] 例如给每个股票算 peg (e.g., calculate PEG for each stock)
- [ ] **界面 3: 数据管理页面 (Data Management Page)**
    - [ ] 背后对应我自己会建库，建设知识图谱来实现多数据源聚合 (Backend: build database, knowledge graph for multi-source data aggregation)
- [ ] **界面 4: 对话界面 (Chat Interface)**
    - [ ] 能够主动查询个股和因子 (Ability to actively query individual stocks and factors)
    - [ ] 目标: 量化选股，能够通过对话创建策略 (Goal: quantitative stock selection, create strategies via chat)
- [ ] **界面 5: 好的选股策略做推送 (Push notifications for good stock selection strategies)**

## 非需求要求 (Non-Requirements / Guidelines)

### 技术栈 (Tech Stack)
- [ ] FE: react-native (reduce dev cost, unified UI)
- [X] BE: python (seamless integration with backend, big data, ML)
- [ ] AI Models: gemini, codex, perplexity, deepseek available; open-router for online dialogue
- [ ] Hardware: 4090 machine for low-cost pre-computation
- [X] AI-Native App: Design agent reward mechanism, self-sufficient development/exploration（`docs/AI_EVALUATION.md` 已发布并写入 `AGENTS.md`）
- [ ] Project Management: Nx (Monorepo friendly)

### 流程管理 (Process Management)
- [X] Project progress in `docs/project/` folder, incrementing numbers
- [X] `agent.md` changes detection and recording to `docs/project/`（本次加入 AI 评价机制后已登记）
- [X] Append prompts exclusively to `docs/project/prompt_log.md` for traceability
- [X] Auto-generated outputs in `x-` prefixed folders (`x-log/`, `x-data/`), not modifiable by agent
- [X] Provide `tools/dev.sh start|stop` for ENV-aware one-click lifecycle management
- [ ] 坚持“工作前必须阅读 `docs/AI_EVALUATION.md` 并记录”自动化验证机制

### 数据管理 (Data Management)
- [ ] Data Confidence: Local data construction, verify with at least 3 sources via browser
- [ ] Prioritize null over incorrect data
- [ ] Avoid repeated crawling to prevent traffic control issues

### 代码管理 (Code Management)
- [X] Use `libs/schema` protobuf to split sub-applications
- [X] Maximize SSOT (Single Source of Truth) principle; related items in one folder/file

### 项目管理 (Project Management)
- [X] `README.md` for every directory
- [X] Update relevant `README.md`s on every change, from file to root; higher-level READMEs are indexes
- [X] Macro-level project progress in `docs/README.md`
- [X] Micro-level iterations in `docs/project/phrase_i.xxxx/` folders with plan, process, checklist, append_promot MDs
- [X] Proto/Nx infrastructure tasks isolated in `docs/project/phrase_0.infra/`

### 工程优化准则 (Engineering Optimization Principles)
- [ ] Maximize use of existing documentation and code before writing new
- [ ] Follow Linux writing principles
- [ ] Strict directory management: 6-7 directories + 3-4 files; reorganize if broken

### 质量管理 (Quality Management)
- [ ] Run tests on every code change; include data product basic verification
- [ ] Backend automated test coverage（`manage.py test` 现已包含 ping-pong 用例，但仍需扩充更多覆盖率）
- [ ] Integrate backend tests into CI/Nx workflows（`nx run backend:test` 已添加，需纳入常规流程）
- [ ] Check `AGENTS.md` for unfulfilled requirements and add to `docs/TODOWRITE.md` upon perceived completion
- [X] Establish `apps/regression/` for end-to-end flows (e.g., `ping_pong.py`); keep unit tests within each component
