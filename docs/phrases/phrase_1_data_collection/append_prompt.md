# 追加提示词记录

本文件记录所有后续人类追加的提示词，便于追溯（agent.md Line 47）

---

## 2025-11-15

### Prompt 1: Data目录重构
**原文**: 不怎么对，请你review，并且整体修改 data 目录 ，还有相关代码的 io@agent.md (30-31)

**要求**:
- 按schema组织数据（不是按处理阶段）
- 命名规则: schema-name-source-date.csv
- 本质相同的数据放一个文件夹

**结果**:
- ✅ 创建了core/data_io.py (321行)
- ✅ 重构data目录为schema-based organization
- ✅ 实现了统一命名规范
- ✅ 46/46 tests passed

---

### Prompt 2: 工程质量加强
**原文**: @agent.md (41-48) 我做了写修改。请你对整个工程进行质量加强

**agent.md新增要求**:
- Line 43: 利用存量文档和代码
- Line 44: 遵循Linux准则
- Line 45: 测试+数据产物校验
- Line 46: 6-7个目录+3-4个文件
- Line 47: 创建append_prompt.md追溯提示词
- Line 48: 程序生成的放x-开头文件夹

**执行中**:
- ✅ 创建x-data/, x-log/, x-coverage/
- ✅ 移动data/ → x-data/
- ✅ 移动htmlcov/ → x-coverage/
- ✅ 创建append_prompt.md
- 🔄 更新路径引用
- 🔄 添加数据质量测试
- 🔄 精简根目录到6-7目录+3-4文件

---

## 格式说明

每次追加提示词请按以下格式记录：

```markdown
### Prompt N: [简短标题]
**原文**: [用户原始提示词]

**要求**:
- [提取的关键要求1]
- [提取的关键要求2]

**结果**:
- ✅/❌/🔄 [执行结果]
```

---

**上级文档**: [agent.md](./agent.md)

