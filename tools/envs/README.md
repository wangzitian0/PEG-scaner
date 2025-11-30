# Environment Templates

环境变量模板目录。

## 文件说明

| 文件 | 用途 |
|------|------|
| `env.ci` | **契约文件** - 生产/CI 环境的完整变量列表 |

## 使用方法

```bash
# 复制到项目根目录
cp tools/envs/env.ci .env

# 编辑填入实际值
vim .env
```

## 规则

1. `.env` 文件不进版本库 (gitignore)
2. `env.ci` 是唯一来源 (SSOT)
3. 新增变量必须同步更新 `env.ci`

