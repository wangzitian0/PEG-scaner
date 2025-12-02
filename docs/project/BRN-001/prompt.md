# Project Prompt Log

Per the latest instruction, all prompts are tracked directly under `docs/project/BRN-001/` so that every iteration has a single source of truth. When `AGENTS.md` or other directives change, append the new prompt in this file before working.

## Prompt 1 (Initial Instruction from AGENTS.md)

```
我想做一个股票软件，量化选股，主要是美股。
!!请你每次改动都要完整检查非需求要求!!
# 需求要求
## 界面
界面 1：个股信息界面，参考 moomoo
- 日、周、月的 K线和交易量
- 新闻
- company F10
  - Earning Hub
  - Company Valuation: PS, PE, PB
  - operating data
  - revenue breakdown
  - financial estimates
  - financial indecators: EPS, FCF, Current Ratio, ROE
  - ...
界面 2：个股因子计算，例如给每个股票算 peg
界面 3：数据管理页面。背后对应我自己会建库，建设知识图谱来实现多数据源聚合
界面 4：对话界面，能够主动查询个股和因子。目的是量化选股，能够通过对话创建策略。
界面 5：好的选股策略做推送


# 非需求要求
## 技术栈
- fe 使用 react-native，降低三端开发成本并且统一界面
- be 使用 python，能无缝衔接后端、大数据、机器学习三技术栈
- 开发过程我有 gemini，codex，perplexity，deepseek 四个大模型可用，线上的对话使用 open-router。
- 我自己有一个 4090 的机器，可以做低成本预计算。
- 这是个 ai-native 的应用，帮我设计好多 agent 的奖励机制。能相对自助的发展和探索。
- 使用 Nx 管理包，Monorepo友好。
## 流程管理
- 项目进度相关的东西，集中放在 `docs/project/` 文件夹里面，编号递增。
- 我的指令主要是 agent.md，你要有能力检测agent.md的变化，并且记录到project。
- 我后续追加的提示词，请你写到prompts/append_promot.md，方便追溯
- 程序自动跑出来的东西，请都放在 x-开头的文件夹，这部分东西 agent 是不允许修改的，如 x-log/., x-data/.
## 数据管理
- 拉数据为了保证置信度，应当本地构建数据之后，浏览器去至少 3 个来源看一下是否强置信。
- 宁可为空，不要使用错的数据
- 避免反复爬同一个数据出发流量控制。
## 代码管理
- 因为是复杂应用，请你通过 schema/protobuf 来分割子应用。
- 最大化的遵循 SSOT 原则，本质相同的东西放到一个文件夹或者一个文件。
## 项目管理
- 每个目录都要有字节的 readme.md。
- 每次改动都要修改相关目录的 readme.md，从对应的文件改到根目录。更上层的 readme 应该是包含子目录的索引。
- 项目类宏观层面的进度请放在 docs/readme.md，能够 onepage 知道现在做到哪里了。
- 微观层面的迭代每个 phrase 请放在一个文件夹，命名为phrase_i.xxxx/..，里面放对应的 plan,迭代流程，checklist，append_promot各种 md 文件
## 工程优化准则
- 每次迭代前，都要尽可能利用存量的文档和代码。不要上来就写一个全新的然后删掉。
- 尽可能遵循 Linux 写东西的基本准则
- 请严格管理目录，符合人类阅读习惯的组织结构就是 6～7 个目录+ 3～4 个文件。打破了就要重新组织。
## 质量管理
- 每次改代码都要跑测试，测试不仅仅是测试代码，还有数据产物的基本校验。
- 每次你认为你完成的时候，请你检查 agent.md 的要求，将未满足的要求追加到 `docs/project/BRN-001/todowrite.md` 里面。
```

## Prompt 2

```
请你阅读 AGENTS.md , 现在傻逼 gemini 卡住了调不通，你能比他厉害么？
```

## Prompt 3

```
你不知道接下来要干啥？
```

## Prompt 4

```
先做 1 吧
```

## Prompt 5

```
先做 1 吧，等一下，你怎么保证不同的模型都来读这个文件？在 agents.md 里面说明？
```

## Prompt 6

```
我修改了下 agents.md，请你再调整下路径
```

## Prompt 7

```
和 proto，nx 相关的基础设施放在 phrase_0.infra 里面哦
```

## Prompt 8

```
有毒吧你。新建一个目录叫做 regression_tests/吧，这种端到端测试放里面，单元测试和局部测试，各个文件夹自己管理就好
```

## Prompt 9

```
交付标准是，流程跑通。
```

## Prompt 10

```
交付标准是，流程跑通。
- ping-pong 也应该基于 protobuf，FE BE 都应该基于 protobuf 交互
- 有一个一键启动和关闭服务的脚本，能够读$ENV环境变量
```

## Prompt 11

```
你在 @docs/phrase_0.infra/ 里面加一个 deploy.md，把这个当做 TODOwrite 吧。一步步来，每一步要有测试标准，我来遵照你的指令
```

## Prompt 12

```
# docs 目录组织原则
分三块
```
docs/
├── index.md    # 价值索引表格，每行大概是|i.BRD|summary|i.TRD, i.DRD|status|
├── arch.md    # 这部分非常基础，会很大程度上决定后续的方向。每一个技术点要求讲清楚5W1H(Who, What, Where, When, Why, How) **核心原则**：任何技术决定需要从现状出发，所以阅读docs/arch.md是必须的。
├── origin/       (State: Immutable Input)
│   └── BRN-001.core_infra_ping.md  # 原始决策录（!!AI只能读不可修改）
│
├── specs/        (State: Definitive Guide)
│   ├── product/    # PRD -> apps, PRD-001.md
│   ├── tech/       # TRD -> libs, TRD-001.md
│   ├── data/       # DRD -> ops, DRD-003.md
│   └── infra/      # IRD -> tools, IRD-012.md
│
└── project/       (State: Dynamic Execution)
    ├── BRN-001/     # 当前正在发生的迭代
    │   ├── prompt.md (记录提示词)
    │   ├── todowrite.md (AI 任务队列)
    │   └── context.md   (当前上下文)
    └── BRN-002/    
```

## Prompt 13

```
docs/project/BRN-001/phrase_1.single_stock_page 帮我写一个 10 行的 BRN-003，对应 PRD-001。然后把整个目录按照 agents.md 的标准组织。
BRN-002 是定义好协议，通信方式，依赖关系。15 行以内表述。建好 TRD-002
```

## Prompt 14

```
请你实现 docs/origin/BRN-002.md 的要求。全面替换成 graphQL。先跑通 ping-pong，再把原有的 protobuf 从代码库里面删除
```

按照这个调整目录啊？
```

## 历史提示片段回填（来自已归档的 append_promot.md）

- Phase 0 infra：
  1. “和 proto，nx 相关的基础设施放在 phrase_0.infra 里面哦”
  2. “有毒吧你。新建一个目录叫做 regression_tests/吧，这种端到端测试放里面，单元测试和局部测试，各个文件夹自己管理就好”
  3. “交付标准是，流程跑通。”
  4. “交付标准是，流程跑通。- ping-pong 也应该基于 protobuf …”
  5. “你在 @docs/phrase_0.infra/ 里面加一个 deploy.md，把这个当做 TODOwrite 吧。一步步来，每一步要有测试标准，我来遵照你的指令”
  6. “BRN-002 是定义好协议，通信方式，依赖关系。15 行以内表述。建好 TRD-002”

- Phase 1 single_stock_page：
  1. “请你阅读 AGENTS.md , 现在傻逼 gemini 卡住了调不通，你能比他厉害么？”
  2. “你不知道接下来要干啥？”
  3. “先做 1 吧”
  4. “先做 1 吧，等一下，你怎么保证不同的模型都来读这个文件？在 agents.md 里面说明？”
  5. “我修改了下 agents.md，请你再调整下路径”
  6. “和 proto，nx 相关的基础设施放在 phrase_0.infra 里面哦”
  7. “docs/project/BRN-001/phrase_1.single_stock_page 帮我写一个 10 行的 BRN-003，对应 PRD-001。然后把整个目录按照 agents.md 的标准组织。”
