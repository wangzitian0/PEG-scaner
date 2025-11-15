# Tests 测试套件

**上级文档**：[返回项目README](../README.md)

---

## 📊 测试状态

```bash
✅ 46/46 passed, 1 skipped
✅ Coverage: 42%
✅ All modules working
```

---

## 🧪 测试文件

### test_validation_rules.py
**测试覆盖**: `core/schemas/validation_rules.py` (95% coverage)

测试内容：
- ✅ PE 验证（正常、负数、过高、警告）
- ✅ PEG 验证（正常、低估、异常）
- ✅ 增长率验证（正常、负数、异常）
- ✅ 价格验证（正常、过低）
- ✅ 利润验证（阈值判断）
- ✅ 交叉验证（偏差检查）
- ✅ 数据拒绝逻辑

**测试数量**: 22个测试

---

### test_format_utils.py
**测试覆盖**: `core/format_utils.py` (59% coverage)

测试内容：
- ✅ 利润格式化（Billions, Millions, HKD, 零值）
- ✅ 公司名格式化（美股、港股、未知）
- ✅ 增长率格式化（正负、None）
- ✅ 股票代码标准化（美股、港股、去零）
- ✅ 货币识别（USD, HKD）

**测试数量**: 14个测试

---

### test_data_collection.py
**测试覆盖**: `data_collection/` 模块 (18-69% coverage)

测试内容：
- ✅ YFinance 数据获取（真实数据、无效ticker）
- ✅ 数据验证（有效/无效价格）
- ✅ 缓存管理（set/get、过期、清理）
- ✅ 数据聚合器（交叉验证、单源回退）

**测试数量**: 9个测试（1个跳过：需要网络）

---

## 🚀 运行测试

### 运行全部测试

```bash
uv run pytest tests/ -v
```

### 运行特定测试文件

```bash
# 验证规则测试
uv run pytest tests/test_validation_rules.py -v

# 格式化工具测试
uv run pytest tests/test_format_utils.py -v

# 数据采集测试
uv run pytest tests/test_data_collection.py -v
```

### 生成覆盖率报告

```bash
# 终端显示
uv run pytest tests/ --cov=core --cov=data_collection --cov-report=term

# HTML报告（在 htmlcov/ 目录）
uv run pytest tests/ --cov=core --cov=data_collection --cov-report=html
```

---

## 📈 覆盖率详情

| 模块 | 语句数 | 未覆盖 | 覆盖率 |
|------|--------|--------|--------|
| `core/schemas/validation_rules.py` | 81 | 4 | **95%** 🏆 |
| `core/models.py` | 33 | 4 | **88%** |
| `core/schemas/stock_schema.py` | 77 | 22 | **71%** |
| `data_collection/cache_manager.py` | 85 | 26 | **69%** |
| `core/format_utils.py` | 64 | 26 | **59%** |
| `data_collection/data_aggregator.py` | 86 | 38 | **56%** |
| `data_collection/fetch_yfinance.py` | 122 | 94 | **23%** |
| `data_collection/fetch_alpha_vantage.py` | 103 | 84 | **18%** |
| **总计** | **857** | **499** | **42%** |

---

## 🎯 测试原则

遵循 [agent.md](../agent.md) 中的原则：

1. **每次改代码都要跑测试**
   - 所有改动后立即运行 `pytest`
   - 确保没有破坏现有功能

2. **数据质量优先**
   - 严格验证规则（95%覆盖率）
   - 宁可为空，不要使用错的数据

3. **全面测试**
   - 单元测试：核心逻辑
   - 集成测试：数据采集流程
   - 边界测试：异常情况处理

---

## 📝 添加新测试

### 测试文件命名规范

```
tests/
├── test_{module_name}.py     # 对应模块的测试
├── test_{feature}_integration.py  # 集成测试
└── test_{feature}_e2e.py     # 端到端测试
```

### 测试类命名规范

```python
class Test{ClassName}:
    """测试 {ClassName} 类的功能"""
    
    def test_{method_name}_{scenario}(self):
        """测试 {method_name} 在 {scenario} 场景下的行为"""
        # Arrange
        # Act
        # Assert
```

### 示例

```python
# tests/test_new_module.py
import pytest
from new_module import NewClass

class TestNewClass:
    """测试 NewClass 的功能"""
    
    def test_method_with_valid_input(self):
        """测试 method 在有效输入下的行为"""
        # Arrange
        obj = NewClass()
        
        # Act
        result = obj.method("valid")
        
        # Assert
        assert result == expected
```

---

## 🐛 调试测试

### 显示打印输出

```bash
uv run pytest tests/ -v -s
```

### 只运行失败的测试

```bash
uv run pytest tests/ --lf
```

### 详细错误信息

```bash
uv run pytest tests/ -v --tb=long
```

### 跳过慢速测试

```bash
uv run pytest tests/ -v -m "not slow"
```

---

## 📚 相关文档

- [项目README](../README.md) - 项目概览
- [系统设计](../agent.md) - 测试原则
- [核心模块](../core/README.md) - 被测试的核心代码
- [数据采集](../data_collection/README.md) - 被测试的数据模块

---

## 🎉 测试里程碑

| 时间 | 测试数 | 覆盖率 | 里程碑 |
|------|--------|--------|--------|
| Phase 1 完成 | 46 | 42% | ✅ 基础测试覆盖 |
| Iteration 1 | 38 | 95% (validation) | ✅ 验证规则完全覆盖 |
| Iteration 2 | 46 | 42% | ✅ 双数据源测试 |
| Iteration 3 | 46 | 42% | ✅ 集成测试完善 |

---

**上级文档**：[返回项目README](../README.md)

