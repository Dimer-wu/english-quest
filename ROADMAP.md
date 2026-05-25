# English Quest 开发路线图

> 最后更新：2026-05-25 · 下一里程碑：首次上线

## 总览

| 阶段 | 目标 | 预计文件变更 | 状态 |
|------|------|-------------|------|
| P0 · 上线准备 | 服务器可对外服务 | app.py, deploy.py, 新增 systemd unit | ✅ 完成 |
| P1 · 音频生产 | L1 全部场景可听 | gen_audio.py, static/audio/ | ✅ 完成 |
| P2 · 体验打磨 | 真实用户可用 | app.js, index.html | ✅ 完成 |
| P3 · L2 内容 | 日常生活 10 场景 | seed_data.py (追加) | 🟡 待开始 |
| P4 · L3-L5 内容 | 剩余 30 场景 | seed_data.py (追加) | ⚪ 远期 |
| P5 · 生产优化 | Tailwind 构建、systemd | index.html, 新增 systemd unit | ⚪ 远期 |

---

## P0 · 上线准备 🔴

**目标**：服务器上可正常运行，通过 HTTPS 域名访问。

### 前置条件
- [x] 代码已通过 Playwright 全流程测试
- [x] 安全审查完成（密钥已从源码移除）
- [x] Git 仓库已建立（github.com/Dimer-wu/english-quest）
- [ ] 服务器上 Python 依赖已安装
- [ ] 服务器上 `.env` 已正确配置

### 任务清单
- [x] **P0.1** 打包部署到服务器 `47.239.122.123:/opt/english-quest/` → 已验证 API 200
- [x] **P0.2** Cloudflare Tunnel `dimerenglish.top` → HTTPS 200，cloudflared systemd 运行中
- [x] **P0.3** systemd unit `/etc/systemd/system/english-quest.service` → enabled + active
- [x] **P0.4** 外部 HTTPS 访问测试 → 全部 7 组 API curl 验证通过

### 验收标准
- `curl https://dimerenglish.top/api/scenarios` 返回 JSON
- 手机浏览器可完成：注册 → 进入场景 → AI 对话 → 收藏语块
- 服务器 `reboot` 后 1 分钟内自动恢复服务

---

## P1 · 音频生产 🔴

**目标**：L1 全部 10 个场景的对话和语块都有可播放的 MP3。

### 当前状态
- `static/audio/l1_s1_dialogue.mp3` 存在（场景 1 对话）
- 其余 9 个场景无音频文件
- 每个场景预期产出：1 个完整对话 MP3 + 5 个语块 MP3 + 逐句 MP3

### 技术决策
- **方案选定**：豆包 TTS API（已集成，服务端缓存）
- Edge TTS（`gen_audio.py`）在国内网络不可用，标记为备用方案
- 音频文件纳入 Git（非 LFS），总量预估 10 场景 × ~15 文件 × ~50KB ≈ 7.5MB，可接受

### Pre-audio generation (164 files total)
- [x] 豆包 TTS 批量脚本（gen_audio_doubao.py）
- [x] 切换为 BV002_streaming 音色（tts.py）
- [x] L1 全部 10 场景音频生成完毕（0 缺失）
- [x] 生产服务器验证：全部 HTTP 200

### 验收标准
- 10 个场景 × 6 个音频文件（1 对话 + 5 语块）= 60 个 MP3
- 前端播放按钮全部可播放，无 404

---

## P2 · 体验打磨 🟡

**目标**：修复交互粗糙点，让真实用户能顺利走通学习闭环。

### 已知问题
- [x] **P2.0** 首页场景异步加载导致短暂空白 → 骨架屏占位卡片
- [x] **P2.1** AI 对话全量 innerHTML 重建 → 增量 append 消息节点
- [x] **P2.2** 语音输入浏览器不兼容 → 不支持时隐藏按钮
- [x] **P2.3** 限时反应缺少倒计时 → 30 秒倒计时条 + 超时自动结束
- [x] **P2.4** Can-Do 弹窗关闭后数据未刷新 → 关闭时调用 loadScenarios()
- [x] **P2.5** 移动端键盘遮挡输入框 → scrollIntoView 自动滚动

### 验收标准
- 用户在 30 分钟内能独立完成一个完整场景（六步全部走完）
- 移动端聊天输入不遮挡、焦点不丢失

---

## P3 · L2 内容开发 🟡

**目标**：新增"日常生活"等级 10 个场景。

### L2 场景清单（CEFR A2）
| # | 场景 | 英文标题 | 核心句型 |
|---|------|---------|---------|
| 1 | 点餐 | Ordering Food | I'll have the ___ / Could I get ___ |
| 2 | 购物 | Shopping | How much is ___ / Do you have ___ in ___ |
| 3 | 问路 | Asking Directions | How do I get to ___ / Is it far from here |
| 4 | 打车 | Taking a Taxi | To ___ please / How much will it be |
| 5 | 酒店入住 | Hotel Check-in | I have a reservation / What time is checkout |
| 6 | 看医生 | At the Doctor | I've been feeling ___ / How long have you had this |
| 7 | 打电话 | On the Phone | Can I speak to ___ / I'll call you back |
| 8 | 约时间 | Making Plans | Are you free on ___ / How about ___ |
| 9 | 天气深入 | Weather Conversation | It's supposed to ___ / The forecast says ___ |
| 10 | 聊家庭 | Talking About Family | I have ___ siblings / My ___ is a ___ |

### 任务清单
- [ ] **P3.1** 编写 L2 全部 10 场景内容（每场景：对话脚本、语块、句型聚焦、反应题、Can-Do）
  - 对话遵循 i+1 原则：90% 词汇来自 L1 + 10% 新内容
- [ ] **P3.2** 追加到 `seed_data.py`（`L2_SCENARIOS` 列表）
- [ ] **P3.3** 生成 L2 音频
- [ ] **P3.4** 前端支持等级切换（首页 Tab：L1 | L2 | L3 | L4 | L5）
  - 当前首页仅显示当前等级的 10 个场景
  - 修改 `renderHome()` 添加等级筛选 UI

### 验收标准
- 用户完成 L1 全部 10 场景后，可解锁 L2
- L2 场景首页可见，内容与前 10 场景无重复

---

## P4 · L3-L5 内容开发 ⚪

**目标**：完成全部 50 场景，覆盖 CEFR A1-B2。

| 等级 | 场景数 | 主题 |
|------|--------|------|
| L3 · 社交进阶 B1 | 10 | 旅行、电影音乐、运动、表达观点、委婉拒绝、安慰、给建议、讲述经历、文化差异 |
| L4 · 职场初级 B1+ | 10 | 介绍工作、项目描述、开会发言、邮件、同事午饭、请假、请求帮助、确认理解、分歧 |
| L5 · 自如交流 B2 | 10 | 讲故事、即兴表达、幽默回应、处理误解、深入讨论、正式/非正式切换、电话、面试 |

**与 P3 相同流程**：编写内容 → 追加 seed_data → 生成音频 → 更新等级切换 UI。

---

## P5 · 生产优化 ⚪

**目标**：性能、稳定性、可维护性达到生产标准。

### 任务清单
- [ ] **P5.1** Tailwind CSS 构建产物替换 CDN
  - 安装 `tailwindcss` CLI，扫描 `index.html` 和 `app.js` 中的类名
  - 输出 `static/tailwind.min.css`（预计 < 30KB vs 当前 350KB）
- [ ] **P5.2** `@app.on_event("startup")` 迁移到 `lifespan`（app.py:43）
- [ ] **P5.3** `UserProgress` 步骤列从 6 个独立列改为 JSON 字段（models.py:53-58）
  - 需编写迁移脚本（读取旧数据 → 转换 → 写入新结构）
- [ ] **P5.4** API 速率限制（`/api/chat` 和 `/api/tts`）
- [ ] **P5.5** 添加 FastAPI CORSMiddleware
- [ ] **P5.6** 设计实际 PWA 图标（替换当前纯色方块 icon-192.png / icon-512.png）

---

## 依赖关系

```
P0（上线准备）──→ P1（音频）──→ P2（体验打磨）──→ 首次公开发布
                                        │
                                        └──→ P3（L2 内容）──→ P4（L3-L5）
                                                              │
                                        P5（生产优化）←────────┘
```

P0 和 P1 可以并行推进。P2 依赖 P1（没有音频无法测试体验）。P3-P4 在发布后可逐步追加。

---

## 技术决策记录

| 决策 | 结论 | 日期 |
|------|------|------|
| TTS 方案 | 豆包 API 为主，浏览器 SpeechSynthesis 为回退 | 2026-05-25 |
| 音频存储 | 纳入 Git（非 LFS），总量 < 10MB 可接受 | 2026-05-25 |
| 前端架构 | 保持单文件 SPA 模式，不做框架迁移 | 2026-05-25 |
| 步骤建模 | 当前保持 6 列硬编码，P5 再做 JSON 迁移 | 2026-05-25 |
| 安全策略 | 所有密钥通过 .env 注入，源码不含任何默认值 | 2026-05-25 |
