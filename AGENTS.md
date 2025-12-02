!!! AI 不可以自动修改本文件。当AI认为完工了，应当逐项检查本文档，所有要求都满足了才可以宣布完成。

# 🚨 强制规则（每次动手前必读）

| 规则 | 检查问题 |
|------|----------|
| 先读后写 | 修改任何目录/文件前必须先阅读该层 README |
| 跑测试 | 每次改代码都要跑测试（代码 + 数据产物校验） |
| 检查遗漏 | 完成后检查 agent.md，未满足的追加到 `docs/project/BRN-001/todowrite.md` |
| 宁空勿错 | 数据不确定就留空，不要用错的 |
| 利用存量 | 先读存量文档和代码，不要上来就重写 |
| Anti: Over-engineering | 是否引入了用户没要求的抽象层/框架？ |
| Anti: Scope creep | 是否只做了用户明确要求的事？ |
| Anti: Verbose output | 核心问题是否真的解决了？ |

---

# 组织哲学

我们的代码库不是由“团队”分割的，而是由**“驱动力 (Drivers)”** 分割的。
每一个物理目录的存在，都是为了响应某种特定性质的目标 (Goal)。

核心链条：
目标 (Goal) -> 执行逻辑 (Logic) -> 执行层 (Layer) -> 定义类型 (Definition) -> 文档类型 (Doc Type)

| 目标 (Goal) | 执行逻辑 (Logic) | 执行层 (Layer) | 定义类型 (Definition) | 文档类型 (Doc Type) |
| :--- | :--- | :--- | :--- | :--- |
| **Value**<br>(创造商业价值) | **Decision**<br>(决策与点子) | `docs/` | **Origin**<br>(原点) | **BRN**<br>(Business Request Note) |
| **Experience**<br>(交付用户体验) | **Assembly**<br>(拼装与交互) | `apps/` | **Product**<br>(产品) | **PRD**<br>(Product Req Doc) |
| **Capability**<br>(构建核心能力) | **Abstraction**<br>(复用与算法) | `libs/` | **Tech**<br>(技术) | **TRD**<br>(Tech Req Doc) |
| **Trust**<br>(确保数据置信) | **Verification**<br>(验证与对抗) | `ops/` | **Data**<br>(数据) | **DRD**<br>(Data Req Doc) |
| **Efficiency**<br>(提升生产效率) | **Automation**<br>(杠杆与基建) | `tools/` | **Infra**<br>(基建) | **IRD**<br>(Infra Req Doc) |

# docs 目录组织原则
**编号规则**：BRN 编号统领，XRD 继承同编号（如 BRN-002 → TRD-002/PRD-002/DRD-002）
**标准流程**：当我让你实现一个需求的时候，你要先完成 docs/目录，等我确认方案之后，再去改代码库。
**注重设计**：spec 的重点是讲清楚做的方式，极其具体的选型组合，可以给一些伪代码，不用大段的写代码。
**运营方案**：绝大部分需求都要写 DRD，上线的影响，相关操作的执行顺序、部署顺序等等，会影响线上服务表现的东西。

```
docs/
├── index.md       # 索引表格：|BRN|summary|XRD|status|
├── arch.md        # 架构决策（5W1H），从现状出发
├── origin/        # BRN-NNN.md（用户决策录，AI只读）
├── specs/
│   ├── product/   # PRD-NNN.md（产品需求）
│   ├── tech/      # TRD-NNN.md（技术规范，包含实施计划）
│   ├── BI/        # DRD-NNN.md（数据运营、BI需求）
│   └── infra/     # IRD-NNN.md（基础设施）
└── project/
    └── BRN-NNN/   # 迭代执行（仅限：prompt.md, context.md, todowrite.md, README.md）
```

## 文档类型职责

### BRN (Business Request Note) - origin/
- ✅ 写：Why（业务价值）、What（目标范围）、验收标准
- ❌ 不写：技术方案、实现细节

### PRD (Product Requirement Doc) - specs/product/
- ✅ 写：用户画像、界面线框图、操作流程、交互反馈
- ❌ 不写：GraphQL Query、API 定义、数据库 Schema

### TRD (Tech Requirement Doc) - specs/tech/
- ✅ 写：架构图（Mermaid）、层次调用关系、技术选型对比表、接口伪代码（5-10行）、Neo4j Schema/ER图
- ❌ 不写：完整实现代码（>50行的放代码仓库）

### DRD (Data Requirement Doc) - specs/data/
- ✅ 写：数据覆盖范围（如SP500股票池）、数据源配置（yfinance/SEC）、多源校验规则（≥3来源）、质量监控（缺失率/延迟SLA）、BI Dashboard需求
- ❌ 不写：数据库Schema（属于TRD）、查询代码（属于代码仓库）

### IRD (Infra Requirement Doc) - specs/infra/
- ✅ 写：部署架构图、CI/CD Pipeline、监控告警规则、成本估算
- ❌ 不写：业务逻辑、数据模型

## 二、代码与目录规范

### 代码管理
- 因为是复杂应用，请你通过 `libs/schema/` 中的 GraphQL schema 来分割子应用。
- 最大化的遵循 SSOT 原则，本质相同的东西放到一个文件夹或者一个文件。
- “在我机器上能跑”通常是因为本地有一些未记录的环境变量。`.env.ci` 是唯一的契约 (Contract)。任何不在契约中的变量，都不应存在于生产或 CI 环境中。

### 目录管理
- 每个目录都要有自己的 readme.md。
- 每次改动都要修改相关目录的 readme.md，从对应的文件改到根目录。更上层的 readme 应该是包含子目录的索引。
- 请严格管理目录，符合人类阅读习惯的组织结构就是 6～7 个目录+ 3～4 个文件。打破了就要重新组织。

### 工程品味
- 引入一个库的时候，去 github 看看说明文档或者技术文档。找一找有没有 sample，尽可能使用业内反复尝试的最佳实践。
- 始终要思考怎么写可维护性最好。文档和模块，既要避免找不到地方重新造轮子或者重复一段话，又要避免过度引用改一点点东西需要改一大堆文件。
- 当我让你整理什么东西的时候。你不可以抽样，必须全文阅读，把信息或者代码放到对的地方。避免删掉重要的东西。
- 尽可能遵循 Linux 写东西的基本准则，尽可能遵守 DRY 原则，尽可能写 Pythonic 风格的代码。
- 这是个 ai-native 的应用，帮我设计好多 agent 的奖励机制。能相对自助的发展和探索。所有 Agent 在动手前必须阅读 `docs/specs/infra/IRD-001.md` 并按照里面的打分/奖励机制执行。

### 文档管理
- 文档是非常珍贵的材料，不可以直接无脑删除一大段。这个会导致丢东西。
- 让你整理文档，是希望你把相关的内容放到对的位置。并且不断加强“对的位置”的定义。
- 如果发现内容重复了，这种时候确实应该删除冗余的那一份。
- 请你在`docs/index.md`仔细定义对的位置。

## 三、流程与项目管理

### 项目进度
- 项目类宏观层面的进度请放在 docs/index.md，能够 onepage 知道现在做到哪里了。
- 项目进度相关的东西，集中放在 `docs/project/` 文件夹里面，编号递增。
- 微观层面的迭代每个 phrase 请放在一个文件夹，命名为phrase_i.xxxx/..，里面放对应的 plan,迭代流程，checklist，append_prompt各种 md 文件

### 指令与追溯
- 我的指令主要是 agent.md，你要有能力检测agent.md的变化，并且记录到 `docs/project/BRN-*/prompt.md`.
- 我后续追加的提示词，请你写到 `docs/project/BRN-*/phrase_i.xxxx/append_promot.md`，方便追溯（不要再维护其他位置的副本）

### 自动产物
- 程序自动跑出来的东西，请都放在 x- 开头的文件夹，这部分东西 agent 是不允许修改的，如 x-log/., x-data/.
- 一键启动/关闭脚本放在 `tools/dev.sh`，能读取 `$ENV` 指定的环境变量文件（没有就用默认）

## 四、数据管理

- 拉数据为了保证置信度，应当本地构建数据之后，浏览器去至少 3 个来源看一下是否强置信。
- 宁可为空，不要使用错的数据
- 避免反复爬同一个数据触发流量控制。

## 五、测试管理

- 端到端/回归测试统一放在 `apps/regression/` 目录，单元测试/局部测试由各自目录维护
- 每次改代码都要跑测试，测试不仅仅是测试代码，还有数据产物的基本校验。

---

# 评分机制

| 维度 | 权重 | 标准 |
|------|------|------|
| **Impact** | 70% | 用户的主要问题解决了吗？ |
| **Quality** | 30% | 代码能跑、有测试、文档更新了吗？ |

详细评价流程见 `docs/specs/infra/IRD-001.md`。
