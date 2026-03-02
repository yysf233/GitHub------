# GitHub日志可视化

**English Name:** GitHub Log Visualization

GitHub日志可视化是一个基于 GitHub Actions + GitHub Pages 的自动化任务平台。  
你可以在网页上管理 Python 任务配置，远程触发执行，并把每次运行日志沉淀为可检索的历史记录。

## 核心能力

- 任务配置可视化：在网页中编辑任务名称、脚本、定时策略、依赖包。
- 执行方式灵活：支持每 5 分钟定时触发和手动触发。
- 日志自动归档：每次运行后自动写入 `frontend/data.json` 并保留最近 50 条。
- 静态部署简单：使用 GitHub Pages 直接发布前端页面，无需额外服务器。

## 实现原理

1. 前端页面读取仓库里的 `workflows.json` 作为任务配置源。
2. 用户保存配置后，前端通过 GitHub Contents API 回写 `workflows.json`。
3. GitHub Actions（`GitHub Log Visualization Runner`）按定时或手动触发执行 `workflow_engine.py`。
4. `workflow_engine.py` 根据任务配置动态筛选并执行内嵌 Python 脚本。
5. 运行日志落盘到 `log.txt`，再由 `update_history.py` 追加到 `frontend/data.json`。
6. Actions 自动提交 `frontend/data.json`，页面刷新后即可看到最新历史记录。

## 目录结构

- `.github/workflows/main.yml`: 定时/手动触发、执行脚本、提交日志的 CI 编排。
- `workflow_engine.py`: 核心任务执行引擎（按 JSON 动态执行任务）。
- `workflows.json`: 任务配置文件（任务列表与脚本内容）。
- `update_history.py`: 日志归档脚本（写入 `frontend/data.json`）。
- `frontend/index.html`: 可视化管理台与日志查看页面。
- `frontend/data.json`: 历史日志数据库（由 Actions 自动维护）。
- `requirements.txt`: 执行环境基础依赖。

## 快速开始

1. 在 GitHub 创建仓库，建议仓库名使用 `github-log-visualization`。
2. 上传本项目代码到该仓库默认分支（建议 `main`）。
3. 启用 GitHub Pages：`Settings -> Pages -> Deploy from a branch -> main / frontend`。
4. 启用 Actions 写权限：`Settings -> Actions -> General -> Workflow permissions -> Read and write permissions`。
5. 打开 GitHub Pages 页面，输入并保存 GitHub Token。
6. 在任务管理页编辑任务并点击“保存配置”，然后点击“运行任务”或“运行所有任务”验证效果。

## tasks 配置字段说明

- `name`: 任务名称。
- `enabled`: 是否启用该任务。
- `run_on_schedule`: 是否允许定时触发运行。
- `run_on_dispatch`: 是否允许手动触发运行。
- `schedule_time`: 每日运行时间（北京时间 `HH:MM`，为空表示按 5 分钟轮询窗口执行）。
- `pip`: 运行前自动安装的依赖包，逗号分隔，例如 `requests,pandas`。
- `script`: 实际执行的 Python 脚本字符串。

## 示例配置

```json
[
  {
    "name": "Example Task",
    "enabled": true,
    "run_on_schedule": true,
    "run_on_dispatch": true,
    "schedule_time": "08:00",
    "pip": "requests",
    "script": "import requests\nprint('[LOG] hello from task')"
  }
]
```

## 常见问题

- `403 API Rate Limit Exceeded`: 未配置 Token 或 Token 权限不足。
- 手动触发成功但无任务输出: 任务可能是 `enabled=false` 或触发条件被禁用。
- 设置了 `schedule_time` 但未执行: 当前逻辑按“目标时间后 5 分钟窗口”匹配，请检查北京时间与任务时间。
- 看不到最新日志: 确认 Actions 成功执行且 `frontend/data.json` 有新提交。

## 安全说明

- 页面将 GitHub Token 存储在浏览器 `localStorage` 中，请仅在可信设备使用。
- 建议使用最小权限 Token，并定期轮换。
