# cloudflare-dns-update

> 声明式、幂等、可审计地把外部域名清单持续同步到 Cloudflare Zero Trust Gateway Lists。

`cloudflare-dns-update` 是一个 CI 友好的同步引擎：从可配置的规则源拉取域名，清洗去重后，幂等地对齐到 Cloudflare Gateway 的域名列表，并输出「新增 / 移除 / 总数」变更报告与失败告警。它脱胎于 `cloudflare-gateway-adblocking`，并重构为更通用、可扩展的架构（见 [`设计文档`](cloudflare-dns-update-design.md) 的同名蓝图）。

## 核心目标

- **幂等可重入**：每天跑都安全，列表 ID 稳定，策略全程在线，绝不堆积重复列表。
- **配置即代码**：规则源、白名单、目标、护栏全部写在 `config/sync.yml`。
- **可观测**：每次运行输出变更数量与结构化报告；失败必有告警。
- **可扩展**：新增数据源 / 输出后端 / 通知渠道只需实现约定接口。

## 安装

要求 Python `>=3.10`。

```bash
# 可编辑安装（开发）
python -m pip install -e ".[dev]"

# 或仅安装运行依赖
python -m pip install -e .
```

本地调试时可把凭据放进 `.env`（参考 `.env.example`）：

```bash
cp .env.example .env
# 编辑 .env 填入 CLOUDFLARE_ACCOUNT_ID 与 CLOUDFLARE_TOKEN
```

## 使用

### 1. 配置 Secrets（GitHub Actions）

在仓库 **Settings → Secrets and variables → Actions** 添加：

| Secret | 说明 |
| --- | --- |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账号 ID |
| `CLOUDFLARE_TOKEN` | API Token，需 `Zero Trust: Edit`、`Account Firewall Access Rules: Edit`、`Access: Apps and Policies: Edit` |

### 2. 准备配置

编辑 `config/sync.yml`，按需增删规则源（`sources`）、白名单与 `targets`（目标组）。默认已包含广告拦截示例。

### 3. 校验配置

```bash
python -m cloudflare_dns_update validate-config
# 或： cloudflare-dns-update validate-config
```

### 4. 运行

```bash
# 试运行：完整解析与差分，但不写入 Cloudflare
python -m cloudflare_dns_update sync --dry-run

# 预览本次相对云端的变更（读基线但不写）
python -m cloudflare_dns_update plan

# 真实同步
python -m cloudflare_dns_update sync
```

本地手动运行会从环境变量 / `.env` 读取 `CLOUDFLARE_ACCOUNT_ID` 与 `CLOUDFLARE_TOKEN`，**绝不**经命令行参数传入。

### 5. 自动化

`.github/workflows/sync.yml` 默认每天 UTC 03:17 定时同步，同时支持手动触发（`workflow_dispatch`，可传 `dry_run` / `force` / `log_level`）。失败时自动开 / 更新一个告警 Issue。

> GitHub 会在仓库连续 60 天无提交后自动停用 `schedule` 触发器。

## 配置参考

`config/sync.yml` 顶层含三段：

- `settings`：网络、重试、分片大小、命名前缀、护栏阈值。
- `whitelist`：全局白名单（内联 + 远程源，精确 + 父域匹配）。
- `targets`：一个或多个目标组，每组含 `list_prefix`、`policy_name`、`sources`、`whitelist`。

完整字段与取值见 `config/sync.yml` 内联注释。

## 架构概览

```
config/sync.yml
  → config loader（校验）
    → 对每个 target：
        sources ─(Provider 并发抓取+归一化)→ domain set
        whitelist ─→ 剔除
        guard（最低条数 / 删除比例 / 全源失败）
        baseline（GatewaySink.read_remote）→ diff
        dry-run? ─ yes ─→ 仅报告
                  └ no ─→ Sink.apply（原地更新/新建/删旧）+ 策略 upsert
      → reporter（JSON + Summary + 产物）
      → notifier（失败时）
```

模块划分（当前为脚手架阶段）：

| 包 | 职责 |
| --- | --- |
| `cloudflare_dns_update.config` | 配置模型与严格校验（已实现） |
| `cloudflare_dns_update.core` | 抓取 / 归一化 / 白名单 / 差分（规划中） |
| `cloudflare_dns_update.providers` | 规则源 Provider（hosts / domains / adblock / registry） |
| `cloudflare_dns_update.sinks` | 输出后端（Gateway / File） |
| `cloudflare_dns_update.notifiers` | 失败通知（GitHub Issue / Webhook） |
| `cloudflare_dns_update.reporting` | 结构化报告与渲染 |
| `cloudflare_dns_update.pipeline` | 编排 |

## 路线图

- [x] M1 脚手架与配置校验
- [ ] M2 核心同步（抓取 / 归一化 / 幂等 Gateway 客户端）
- [ ] M3 CLI 与 dry-run / plan
- [ ] M4 自动化工作流与失败通知
- [ ] M5 通知与多 target 验证
- [ ] M6 测试与发布

## 许可证

[MIT](LICENSE)
