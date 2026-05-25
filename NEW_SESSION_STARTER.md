# English Quest 新对话启动提示词

直接复制下面整段话到新 Claude Code 对话框中即可继续开发。

---

我正在继续开发 **English Quest（英语闯关）** 项目，这是一个面向零基础成人的英语学习 PWA，已部署在 https://dimerenglish.top 。

## 项目概览

- **技术栈**：FastAPI + SQLite + 单文件 SPA（vanilla JS）+ Tailwind CSS + Cloudflare Tunnel
- **设计风格**：Neubrutalism（黑边框+硬阴影+橙色强调色 #FF6B00）
- **部署**：阿里云 ECS 47.239.122.123，端口 8001，目录 `/opt/english-quest/`
- **本地路径**：`d:/cluade code/english-quest/`
- **六步学习法**：语块预习 → 对话影子跟读 → AI角色扮演 → 语块收集 → 限时反应 → 句型聚焦
- **教学方法论**：CEFR、Paul Nation四股绳、词汇教学法、Krashen i+1、艾宾浩斯间隔复习、地道口语
- **发音方案**：浏览器内置 speechSynthesis API（Edge TTS 在国内被墙无法使用）

## 项目文件结构

```
english-quest/
├── app.py              # FastAPI 入口，435行，7组 REST API + PWA 静态文件服务
├── config.py           # 配置：数据库URL、DeepSeek API、SRS间隔
├── models.py           # 5个模型：User/Scenario/UserProgress/UserChunk/ChatLog
├── deps.py             # get_current_user 依赖（session-based auth）
├── deploy.py           # paramiko SFTP 部署脚本
├── requirements.txt    # fastapi, uvicorn, sqlalchemy 等
├── .env.example        # 环境变量模板
├── .env                # 本地环境变量（含 API key）
├── data/
│   └── english_quest.db  # SQLite 数据库
├── static/
│   ├── app.js          # 完整 SPA，858行，6步学习流程 + 浏览器TTS
│   ├── sw.js           # Service Worker（离线缓存）
│   ├── manifest.json   # PWA manifest
│   ├── icon-192.png    # PWA 图标（纯色橙色方块）
│   ├── icon-512.png
│   └── audio/          # 音频目录（空，当前用浏览器TTS）
├── templates/
│   └── index.html      # PWA 外壳，Neubrutalism 样式
├── scripts/
│   ├── seed_data.py    # L1 10个场景种子数据（483行）
│   └── gen_audio.py    # Edge TTS 批量生成（已废弃，国内不可用）
└── design/             # 设计文档
```

## 当前状态

### 已完成
- FastAPI 后端 7 组 API（认证/场景/进度/语块/AI对话/统计/PWA）
- L1 全部 10 个场景（问候/天气/爱好/工作/邀请/告别/道歉/赞美/闲聊/复习）
- 6 步学习流程完整实现
- AI 角色扮演对话（DeepSeek deepseek-chat）
- 间隔复习系统（1天/1周/1月）
- PWA 能力（离线访问、添加到主屏幕）
- Cloudflare Tunnel HTTPS（dimerenglish.top）
- 部署脚本 deploy.py
- 管理员账号：Dimer（密码见服务器 .env 中 ADMIN_PASSWORD）

### 待开发
- L2-L5 场景内容（40个场景）
- 替换 PWA 图标为实际设计
- 后端 app.py:42 的 `@app.on_event("startup")` 迁移到 lifespan
- Python 应用的 systemd 服务（当前用 nohup，服务器重启后不会自动启动）

## 服务器信息

- IP: 47.239.122.123
- 应用端口: 8001（通过 cloudflared Tunnel 对外 HTTPS）
- 工作台端口: 8000（另一个项目 /opt/workbench/）
- 部署路径: /opt/english-quest/
- cloudflared: systemd 服务，已设置开机自启
- Python 进程: nohup python3 app.py（需手动重启）
- 数据库: /opt/english-quest/data/english_quest.db

## 部署命令

```bash
cd "d:/cluade code"
tar -czf english-quest-deploy.tar.gz --exclude='__pycache__' --exclude='data' --exclude='.env' --exclude='node_modules' --exclude='design' english-quest/
python english-quest/deploy.py
```

请先阅读 `d:/cluade code/english-quest/` 下的所有关键文件了解代码细节，然后告诉我就绪，我们继续开发。
