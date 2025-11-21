# 需求要求
## 长期奖励目标
实现稳定的收益
## 子目标
- 个股拥有足够准确的基础数据，采样 M7 就行。
- 覆盖SP500+kweb+VGT三个ETF 的个股。
- 方便的引入一种新数据源并且比对和调整置信源
- 策略界面的答案质量高
- 交易的策略简单且稳定
## 对应的界面
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
