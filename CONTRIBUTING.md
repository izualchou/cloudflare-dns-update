# 贡献指南

感谢你考虑为 `cloudflare-dns-update` 做贡献。

## 开发环境

要求 Python `>=3.10`。

```bash
git clone <your-fork>
cd cloudflare-dns-update
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## 代码风格

- 格式化与检查：`ruff check .` 与 `black .`（配置见 `pyproject.toml`）。
- 提交前请运行 `pytest`。
- 全程类型注解，公共函数写 docstring。

## 目录与扩展点

| 想扩展什么 | 怎么做 |
| --- | --- |
| 新的规则源格式 | 在 `src/cloudflare_dns_update/providers/` 新增 `XxxProvider(SourceProvider)`，并在 `registry.py` 注册 |
| 新的输出后端 | 在 `src/cloudflare_dns_update/sinks/` 新增 `XxxSink(Sink)`，实现 `read_remote` / `apply` |
| 新的通知渠道 | 在 `src/cloudflare_dns_update/notifiers/` 新增 `XxxNotifier(Notifier)`，实现 `notify(report)` |

## 里程碑

当前处于 **M1（脚手架 + 配置校验）**。各模块占位见 `src/cloudflare_dns_update/`：
实施中的阶段会替换对应的 `NotImplementedError` 桩。请勿在桩文件里引入循环依赖。

## Pull Request 清单

- [ ] 类型注解完整、通过 `ruff` / `black`
- [ ] 新增能力附带测试（`tests/`）
- [ ] 凭据只走环境变量，不出现在命令行参数或日志
- [ ] 更新 README / 设计文档中相关说明
- [ ] 提交信息清晰（建议 Conventional Commits）

## 议题与分支

- Bug / 功能建议请开 Issue，并标注相应标签。
- 分支约定：`feat/`、`fix/`、`docs/`、`chore/`。
