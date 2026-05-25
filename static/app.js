// ── English Quest SPA ──────────────────────────────────
// ── 浏览器语音合成（优先自然语音）──────────────────────
let _bestVoice = null;
let _voicesLoaded = false;
let _ttsUnavailable = false;

function pickBestVoice(voices) {
    const enVoices = voices.filter(v => v.lang.startsWith("en-"));
    if (enVoices.length === 0) return null;
    return enVoices.find(v => v.name.includes("Natural"))
        || enVoices.find(v => v.name === "Samantha" || v.name === "Alex")
        || enVoices.find(v => v.name.startsWith("Google") && v.lang === "en-US")
        || enVoices.find(v => v.name.toLowerCase().includes("premium"))
        || enVoices.find(v => v.lang === "en-US")
        || enVoices[0];
}

function initVoices() {
    if (_voicesLoaded || _ttsUnavailable) return;
    if (!("speechSynthesis" in window)) {
        _ttsUnavailable = true;
        return;
    }
    const voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) return;
    _voicesLoaded = true;
    _bestVoice = pickBestVoice(voices);
    if (_bestVoice) {
        console.log("English Quest TTS: " + _bestVoice.name + " (" + _bestVoice.lang + ")");
    }
}

// Chrome 异步加载语音的预热机制：先触发 getVoices() 让浏览器开始加载，
// 再通过 onvoiceschanged 事件 + 500ms 兜底确保语音列表就绪
if (window.speechSynthesis) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = initVoices;
}
setTimeout(initVoices, 500);

function speak(text, rate = 0.85) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();

    if (!_voicesLoaded) initVoices();

    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = rate;
    u.pitch = 1;
    u.volume = 1;

    if (_bestVoice) {
        u.voice = _bestVoice;
    } else {
        const fallback = pickBestVoice(window.speechSynthesis.getVoices());
        if (fallback) u.voice = fallback;
    }

    window.speechSynthesis.speak(u);
    return u;
}

const API = {
    async post(url, body = {}) {
        const fd = new FormData();
        for (const [k, v] of Object.entries(body)) fd.append(k, v);
        const r = await fetch(url, { method: "POST", body: fd });
        if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.detail || r.statusText); }
        return r.json();
    },
    async get(url) {
        const r = await fetch(url);
        if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.detail || r.statusText); }
        return r.json();
    }
};

// ── 全局常量 ──────────────────────────────────────────
const LEVELS = [
    { name: "",             short: "",        cefr: "",    color: "#ccc" },
    { name: "L1 · 初识社交", short: "初识社交",  cefr: "A1",  color: "#FF6B00" },
    { name: "L2 · 日常生活", short: "日常生活",  cefr: "A2",  color: "#FF6B00" },
    { name: "L3 · 社交进阶", short: "社交进阶",  cefr: "B1",  color: "#FF6B00" },
    { name: "L4 · 职场初级", short: "职场初级",  cefr: "B1+", color: "#FF6B00" },
    { name: "L5 · 自如交流", short: "自如交流",  cefr: "B2",  color: "#FF6B00" },
];

const MASTERY = {
    1: { label: "🔴 遗忘",   color: "#d00" },
    2: { label: "🟡 需复习", color: "#FF6B00" },
    3: { label: "🟢 熟练",   color: "#00a000" },
};

function statCard(value, label) {
    return `<div class="card" style="flex:1;padding:16px;text-align:center">
        <div style="font-family:'Space Grotesk',sans-serif;font-weight:900;font-size:32px">${value}</div>
        <div style="font-size:10px;color:#666">${label}</div>
    </div>`;
}

// ── 状态 ──────────────────────────────────────────────
const S = {
    user: null,
    stats: null,
    scenarios: [],
    currentScenario: null,
    currentStep: 0,
    studyChunks: [],
    aiMessages: [],
};

// ── 页面切换 ──────────────────────────────────────────
function showPage(name, data) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    const el = document.getElementById(name);
    if (el) el.classList.add("active");
    document.getElementById("tabBar").style.display = (name === "loginPage") ? "none" : "flex";
    document.querySelectorAll(".tab-item").forEach(t => {
        t.classList.toggle("active", t.dataset.page === name);
    });
    window.scrollTo(0, 0);

    if (name === "homePage") renderHome(data);
    if (name === "chunksPage") renderChunks();
    if (name === "profilePage") renderProfile();
    if (name === "studyPage" && data) renderStudy();
}

// ── 初始化 ────────────────────────────────────────────
async function init() {
    try {
        const me = await API.get("/api/me");
        if (me.user) {
            S.user = me.user;
            S.stats = me.stats;
            showPage("homePage");
            await loadScenarios();
        } else {
            renderLogin();
        }
    } catch (e) {
        renderLogin();
    }
}

// ════════════════════════════════════════════════════════
//  登录页
// ════════════════════════════════════════════════════════
function renderLogin() {
    const el = document.getElementById("loginPage");
    el.innerHTML = `
        <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px">
            <h1 style="font-size:48px;line-height:1;margin-bottom:8px">ENGLISH<br>QUEST</h1>
            <p style="font-size:14px;color:#666;margin-bottom:32px">英语闯关 · 陪你练对话</p>
            <div class="card" style="padding:24px;width:100%">
                <h2 id="authTitle" style="font-size:24px;margin-bottom:20px">登录</h2>
                <input id="loginUser" class="input-field" placeholder="用户名" autocomplete="username" style="margin-bottom:12px">
                <input id="loginPass" class="input-field" type="password" placeholder="密码" autocomplete="current-password" style="margin-bottom:20px">
                <button id="authBtn" class="btn-primary" style="width:100%">登录</button>
                <p style="text-align:center;margin-top:16px;font-size:14px">
                    <span id="toggleAuth" style="color:#FF6B00;cursor:pointer;font-weight:700">创建新账号</span>
                </p>
            </div>
            <div id="authMsg" style="margin-top:16px;font-size:14px;color:#d00;text-align:center"></div>
        </div>`;

    let mode = "login";
    document.getElementById("toggleAuth").onclick = () => {
        mode = (mode === "login") ? "register" : "login";
        document.getElementById("authTitle").textContent = (mode === "login") ? "登录" : "注册";
        document.getElementById("authBtn").textContent = (mode === "login") ? "登录" : "注册";
        document.getElementById("toggleAuth").textContent = (mode === "login") ? "创建新账号" : "已有账号？登录";
        document.getElementById("authMsg").textContent = "";
    };

    document.getElementById("authBtn").onclick = async () => {
        const u = document.getElementById("loginUser").value.trim();
        const p = document.getElementById("loginPass").value.trim();
        if (!u || !p) { document.getElementById("authMsg").textContent = "请填写用户名和密码"; return; }
        try {
            const url = (mode === "login") ? "/api/login" : "/api/register";
            const r = await API.post(url, { username: u, password: p });
            S.user = r.user;
            const me = await API.get("/api/me");
            S.stats = me.stats;
            showPage("homePage");
            await loadScenarios();
        } catch (e) {
            document.getElementById("authMsg").textContent = e.message;
        }
    };

    document.getElementById("loginPass").onkeydown = (e) => {
        if (e.key === "Enter") document.getElementById("authBtn").click();
    };
}

// ════════════════════════════════════════════════════════
//  首页
// ════════════════════════════════════════════════════════
async function loadScenarios() {
    try {
        const data = await API.get("/api/scenarios");
        S.scenarios = data.scenarios;
        renderHome();
    } catch (e) {
        console.error(e);
        const el = document.getElementById("homePage");
        el.innerHTML += '<p style="text-align:center;color:#d00;margin-top:16px">加载场景失败，请检查网络后刷新页面</p>';
    }
}

function renderHome() {
    const el = document.getElementById("homePage");
    const level = S.user?.level || 1;
    const completed = S.stats?.completed_scenarios || 0;
    const total = S.stats?.total_scenarios || 50;

    let scenarioCards = "";
    const levelScenarios = S.scenarios.filter(s => s.level === level);
    for (const s of levelScenarios) {
        const doneStyle = completed >= s.order ? "border-color:#00a000;background:#f0fff0" : "";
        const check = completed >= s.order ? '<span style="color:#00a000;font-size:20px">✓</span>' : "";
        scenarioCards += `
            <div class="card scenario-card" data-id="${s.id}" style="padding:16px;margin-bottom:12px;cursor:pointer;transition:transform 0.15s;${doneStyle}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span style="font-family:'Space Grotesk',sans-serif;font-weight:900;font-size:20px;color:#ccc;margin-right:8px">${String(s.order).padStart(2,"0")}</span>
                        <span style="font-weight:700">${s.title_cn}</span>
                    </div>
                    ${check}
                </div>
                <p style="font-size:12px;color:#666;margin-top:4px">${s.title}</p>
            </div>`;
    }

    const lv = LEVELS[level] || { name: "L"+level, cefr: "A1" };
    el.innerHTML = `
        <h1 style="font-size:36px;line-height:1.1;margin-bottom:8px">ENGLISH<br>QUEST</h1>
        <div style="display:flex;gap:12px;margin-bottom:24px">
            ${statCard(level, "当前等级")}
            ${statCard(`${completed}/${total}`, "完成场景")}
            ${statCard(S.user?.streak_days||0, "连续天数")}
        </div>
        <h2 style="font-size:20px;margin-bottom:4px">${lv.name}</h2>
        <p style="font-size:12px;color:#666;margin-bottom:16px">CEFR ${lv.cefr}</p>
        ${scenarioCards}
        <p style="text-align:center;margin-top:16px">
            <button class="btn-primary" onclick="logout()">退出登录</button>
        </p>`;

    // 场景卡片点击 → 进入学习页
    document.querySelectorAll(".scenario-card").forEach(card => {
        card.onclick = () => openScenario(parseInt(card.dataset.id));
        card.onmouseenter = () => card.style.transform = "translateY(-2px)";
        card.onmouseleave = () => card.style.transform = "";
    });
}

async function openScenario(scenarioId) {
    try {
        const data = await API.get(`/api/scenarios/${scenarioId}`);
        S.currentScenario = data;
        S.currentStep = 0;
        S.studyChunks = [];
        S.aiMessages = [];
        showPage("studyPage", true);
    } catch (e) {
        alert("加载场景失败: " + e.message);
    }
}

async function logout() {
    await API.post("/api/logout");
    S.user = null;
    S.stats = null;
    S.scenarios = [];
    showPage("loginPage");
    renderLogin();
}

// ════════════════════════════════════════════════════════
//  学习页（六步闭环）
// ════════════════════════════════════════════════════════
function renderStudy() {
    const sc = S.currentScenario?.scenario;
    const prog = S.currentScenario?.progress;
    if (!sc) { showPage("homePage"); return; }

    const steps = [
        { name: "① 语块预览", icon: "fa-eye" },
        { name: "② 对话跟读", icon: "fa-volume-up" },
        { name: "③ AI 角色扮演", icon: "fa-comments" },
        { name: "④ 语块收藏", icon: "fa-bookmark" },
        { name: "⑤ 限时反应", icon: "fa-bolt" },
        { name: "⑥ 句型聚焦", icon: "fa-puzzle-piece" },
    ];

    let stepTabs = "";
    for (let i = 0; i < steps.length; i++) {
        const active = (i === S.currentStep) ? "active" : "";
        const done = (prog && prog[`step${i+1}_done`]) ? 'color:#00a000' : '';
        stepTabs += `<span class="step-tab ${active}" data-step="${i}" style="cursor:pointer;font-size:11px;font-weight:700;padding:4px 6px;${active?'border-bottom:3px solid #FF6B00;':''}${done}">${steps[i].name}</span>`;
    }

    const el = document.getElementById("studyPage");
    el.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
            <button style="background:none;border:3px solid #000;padding:4px 12px;cursor:pointer;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:16px" onclick="showPage('homePage')">←</button>
            <div>
                <h2 style="font-size:20px;line-height:1.2">${sc.title_cn}</h2>
                <p style="font-size:11px;color:#666">L${sc.level} · ${sc.title}</p>
            </div>
        </div>
        <div style="display:flex;gap:2px;overflow-x:auto;padding-bottom:8px;margin-bottom:16px;border-bottom:3px solid #000">
            ${stepTabs}
        </div>
        <div id="stepContent" class="card" style="padding:20px;min-height:300px"></div>
        <div id="stepNav" style="display:flex;justify-content:space-between;margin-top:16px"></div>`;

    // 步骤 tab 点击
    document.querySelectorAll(".step-tab").forEach(tab => {
        tab.onclick = () => {
            S.currentStep = parseInt(tab.dataset.step);
            renderStudy();
        };
    });

    renderStep();
}

function renderStep() {
    const sc = S.currentScenario.scenario;
    const step = S.currentStep;
    const container = document.getElementById("stepContent");
    const nav = document.getElementById("stepNav");

    switch (step) {
        case 0: renderStep1(container, sc); break;
        case 1: renderStep2(container, sc); break;
        case 2: renderStep3(container, sc); break;
        case 3: renderStep4(container, sc); break;
        case 4: renderStep5(container, sc); break;
        case 5: renderStep6(container, sc); break;
        default: container.innerHTML = '<p style="text-align:center;color:#d00;padding:40px">步骤加载失败，请返回重试</p>';
    }

    // 导航按钮
    nav.innerHTML = "";
    if (step > 0) {
        const prev = document.createElement("button");
        prev.className = "btn-primary";
        prev.textContent = "← 上一步";
        prev.onclick = () => { S.currentStep--; renderStudy(); };
        nav.appendChild(prev);
    }
    nav.appendChild(document.createElement("span")); // spacer

    if (step < 5) {
        const next = document.createElement("button");
        next.className = "btn-primary";
        next.textContent = "下一步 →";
        next.style.marginLeft = "auto";
        next.onclick = async () => {
            next.disabled = true;
            const ok = await markStepDone(step + 1);
            if (ok) {
                S.currentStep++;
                renderStudy();
            } else {
                next.disabled = false;
            }
        };
        nav.appendChild(next);
    } else {
        const done = document.createElement("button");
        done.className = "btn-primary";
        done.textContent = "完成场景 ✅";
        done.style.marginLeft = "auto";
        done.onclick = async () => {
            done.disabled = true;
            const ok = await markStepDone(6);
            if (ok) {
                S.currentScenario.progress = {
                    step1_done:1,step2_done:1,step3_done:1,
                    step4_done:1,step5_done:1,step6_done:1,
                    completed:true
                };
                renderStudy();
                showCanDo();
            } else {
                done.disabled = false;
            }
        };
        nav.appendChild(done);
    }
}

async function markStepDone(stepNum) {
    try {
        await API.post(`/api/progress/${S.currentScenario.scenario.id}`, { step: stepNum });
        if (!S.currentScenario.progress) S.currentScenario.progress = {};
        S.currentScenario.progress[`step${stepNum}_done`] = 1;
        const me = await API.get("/api/me");
        S.stats = me.stats;
        return true;
    } catch (e) {
        console.error("markStepDone failed:", e);
        return false;
    }
}

// ── 步骤 1：语块预览 ──────────────────────────────────
function renderStep1(el, sc) {
    const chunks = sc.chunks || [];
    let html = '<h3 style="font-size:18px;margin-bottom:12px">本场景可复用语块</h3>';
    html += '<p style="font-size:12px;color:#666;margin-bottom:16px">这些都是预制好的口语"积木"，不需要自己造句</p>';

    for (const c of chunks) {
        const idx = chunks.indexOf(c);
        const audioUrl = (sc.audio_chunks && sc.audio_chunks[idx]) ? sc.audio_chunks[idx] : "";
        html += `
            <div style="border:3px solid #000;padding:16px;margin-bottom:12px;background:#fff">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <strong style="font-size:18px;color:#FF6B00">${escHtml(c.chunk)}</strong>
                    <button class="btn-play" data-audio="${escAttr(audioUrl)}" data-text="${escAttr(c.chunk)}" data-rate="0.75" style="background:none;border:2px solid #000;width:36px;height:36px;cursor:pointer;font-size:16px">▶</button>
                </div>
                <p style="font-size:14px;color:#666;margin-top:4px">${escHtml(c.translation)}</p>
                ${c.replaceable ? `<p style="font-size:11px;color:#999;margin-top:4px">🔄 ${escHtml(c.replaceable)}</p>` : ""}
            </div>`;
    }
    el.innerHTML = html;
    bindAudioButtons(el);
}

// ── 步骤 2：对话 + 影子跟读 ───────────────────────────
function renderStep2(el, sc) {
    const lines = sc.dialogue_script || [];
    let html = '<h3 style="font-size:18px;margin-bottom:8px">场景对话</h3>';
    html += '<p style="font-size:12px;color:#666;margin-bottom:16px">先听完整对话，再逐句影子跟读（慢速→常速）</p>';

    const fullDialogue = lines.map(l => l.text_en).join(". ");
    const fullAudioUrl = sc.audio_dialogue || "";
    html += `<button class="btn-primary btn-play" data-audio="${escAttr(fullAudioUrl)}" data-text="${escAttr(fullDialogue)}" data-rate="0.8" style="margin-bottom:16px;width:100%">▶ 播放完整对话</button>`;

    html += '<div style="max-height:400px;overflow-y:auto">';
    for (const line of lines) {
        const isB = line.speaker.includes("You");
        const lineAudio = line.audio_url || "";
        html += `
            <div style="border-left:3px solid ${isB ? '#FF6B00' : '#000'};padding:8px 12px;margin-bottom:8px;background:${isB?'#fff8f0':'#fff'};display:flex;justify-content:space-between;align-items:center">
                <div style="flex:1">
                    <div style="font-size:10px;color:#999">${escHtml(line.speaker)}</div>
                    <div style="font-weight:700">${escHtml(line.text_en)}</div>
                    <div style="font-size:12px;color:#666">${escHtml(line.text_cn)}</div>
                </div>
                <button class="btn-play" data-audio="${escAttr(lineAudio)}" data-text="${escAttr(line.text_en)}" data-rate="0.75" style="background:none;border:2px solid #000;width:32px;height:32px;cursor:pointer;font-size:14px;flex-shrink:0;margin-left:8px">▶</button>
            </div>`;
    }
    html += '</div>';

    const el2 = document.createElement("p");
    el2.style.cssText = "font-size:12px;color:#666;margin-top:16px";
    el2.textContent = "💡 影子跟读：听一句 → 暂停 → 跟着念，模仿语调和节奏。先在慢速（0.75x）下完成，再用常速。";
    html += el2.outerHTML;

    el.innerHTML = html;
    bindAudioButtons(el);
}

// ── 步骤 3：AI 角色扮演 ────────────────────────────────
function renderStep3(el, sc) {
    let msgs = "";
    for (const m of S.aiMessages) {
        const isUser = m.role === "user";
        msgs += `
            <div style="display:flex;justify-content:${isUser?'flex-end':'flex-start'};margin-bottom:12px">
                <div style="max-width:80%;padding:12px 16px;border:3px solid #000;background:${isUser?'#FFFDF0':'#fff'};box-shadow:4px 4px 0px ${isUser?'#FF6B00':'#000'}">
                    <p style="font-size:14px">${escHtml(m.content)}</p>
                    ${m.tip ? `<p style="font-size:11px;color:#FF6B00;margin-top:6px;border-top:2px solid #000;padding-top:6px">💡 ${escHtml(m.tip)}</p>` : ""}
                </div>
            </div>`;
    }

    el.innerHTML = `
        <h3 style="font-size:18px;margin-bottom:8px">AI 角色扮演</h3>
        <p style="font-size:12px;color:#666;margin-bottom:16px">在「${sc.title_cn}」场景中和 AI 完成英文对话</p>
        <div id="chatMessages" style="min-height:250px;max-height:400px;overflow-y:auto;margin-bottom:16px">${msgs || '<p style="color:#999;text-align:center;padding-top:100px">开始你的第一次对话吧 👇</p>'}</div>
        <div style="display:flex;gap:8px">
            <input id="chatInput" class="input-field" placeholder="输入英文回复..." style="flex:1">
            <button id="chatBtn" class="btn-primary" style="flex-shrink:0">发送</button>
        </div>
        <button id="voiceBtn" style="width:100%;margin-top:8px;background:#000;color:#FFFDF0;border:3px solid #000;padding:10px;cursor:pointer;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px">🎤 语音输入</button>
        <p id="chatStatus" style="font-size:11px;color:#666;margin-top:8px;text-align:center"></p>`;

    const sendMsg = async () => {
        const input = document.getElementById("chatInput");
        const msg = input.value.trim();
        if (!msg) return;
        input.value = "";
        input.disabled = true;
        document.getElementById("chatBtn").disabled = true;
        document.getElementById("chatStatus").textContent = "AI 正在回复...";

        S.aiMessages.push({ role: "user", content: msg });
        renderStep3(el, sc);
        document.getElementById("chatMessages").scrollTop = document.getElementById("chatMessages").scrollHeight;

        try {
            const r = await API.post("/api/chat", { message: msg, scenario_id: sc.id });
            S.aiMessages.push({ role: "assistant", content: r.reply, tip: r.tip });
            renderStep3(el, sc);
            document.getElementById("chatMessages").scrollTop = document.getElementById("chatMessages").scrollHeight;
            document.getElementById("chatStatus").textContent = "";
        } catch (e) {
            document.getElementById("chatStatus").textContent = "发送失败: " + e.message;
        }
        input.disabled = false;
        document.getElementById("chatBtn").disabled = false;
        input.focus();
    };

    document.getElementById("chatBtn").onclick = sendMsg;
    document.getElementById("chatInput").onkeydown = (e) => { if (e.key === "Enter") sendMsg(); };

    document.getElementById("voiceBtn").onclick = () => {
        if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
            document.getElementById("chatStatus").textContent = "你的浏览器不支持语音输入，请使用 Chrome";
            return;
        }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new SR();
        rec.lang = "en-US";
        rec.interimResults = false;
        document.getElementById("chatStatus").textContent = "正在聆听...";
        rec.start();
        rec.onresult = (e) => {
            const text = e.results[0][0].transcript;
            document.getElementById("chatInput").value = text;
            document.getElementById("chatStatus").textContent = "识别完成，点击发送 →";
        };
        rec.onerror = (e) => {
            document.getElementById("chatStatus").textContent = "语音识别失败: " + e.error;
        };
    };
}

// ── 步骤 4：语块收藏 ──────────────────────────────────
function renderStep4(el, sc) {
    const chunks = sc.chunks || [];
    let html = '<h3 style="font-size:18px;margin-bottom:8px">语块收藏</h3>';
    html += '<p style="font-size:12px;color:#666;margin-bottom:16px">对话中学到的新表达，一键收藏到语块本</p>';
    html += '<p style="font-size:11px;color:#999;margin-bottom:16px">提示：如果 AI 角色扮演中遇到了新的地道表达，可以手动输入收藏</p>';

    // 自定义收藏表单
    html += `
        <div style="border:3px solid #000;padding:16px;margin-bottom:20px;background:#fff8f0">
            <p style="font-weight:700;margin-bottom:8px">✚ 手动添加语块</p>
            <input id="newChunkText" class="input-field" placeholder="英文语块，如: How have you been?" style="margin-bottom:8px">
            <input id="newChunkTrans" class="input-field" placeholder="中文翻译，如: 最近怎么样？" style="margin-bottom:8px">
            <button id="addChunkBtn" class="btn-primary" style="width:100%">收藏到语块本</button>
        </div>`;

    // 场景预置语块
    html += '<p style="font-weight:700;margin-bottom:8px">📋 本场景预置语块</p>';
    for (const c of chunks) {
        html += `
            <div style="border:3px solid #000;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
                <div>
                    <strong>${escHtml(c.chunk)}</strong>
                    <p style="font-size:12px;color:#666">${escHtml(c.translation)}</p>
                </div>
                <button class="collect-btn btn-primary" data-chunk="${escAttr(c.chunk)}" data-trans="${escAttr(c.translation)}" style="font-size:12px;padding:8px 12px;flex-shrink:0">收藏</button>
            </div>`;
    }

    el.innerHTML = html;

    // 收藏按钮事件
    el.querySelectorAll(".collect-btn").forEach(btn => {
        btn.onclick = async () => {
            try {
                await API.post("/api/chunks", {
                    chunk_text: btn.dataset.chunk,
                    translation: btn.dataset.trans,
                    scenario_id: sc.id,
                });
                btn.textContent = "✓ 已收藏";
                btn.disabled = true;
                btn.style.background = "#00a000";
                btn.style.color = "#fff";
            } catch (e) {
                alert("收藏失败: " + e.message);
            }
        };
    });

    // 手动添加
    document.getElementById("addChunkBtn").onclick = async () => {
        const text = document.getElementById("newChunkText").value.trim();
        const trans = document.getElementById("newChunkTrans").value.trim();
        if (!text || !trans) return;
        try {
            await API.post("/api/chunks", {
                chunk_text: text,
                translation: trans,
                scenario_id: sc.id,
            });
            document.getElementById("newChunkText").value = "";
            document.getElementById("newChunkTrans").value = "";
            document.getElementById("addChunkBtn").textContent = "✓ 已收藏";
            setTimeout(() => { document.getElementById("addChunkBtn").textContent = "收藏到语块本"; }, 1500);
        } catch (e) {
            alert("收藏失败: " + e.message);
        }
    };
}

// ── 步骤 5：限时反应 ──────────────────────────────────
function renderStep5(el, sc) {
    const questions = sc.reaction_questions || [];
    let html = '<h3 style="font-size:18px;margin-bottom:8px">限时反应</h3>';
    html += '<p style="font-size:12px;color:#666;margin-bottom:4px">30 秒内用学到的话快速回答 5 个问题</p>';
    html += '<p style="font-size:11px;color:#999;margin-bottom:16px">目标是脱口而出，不是完美语法</p>';

    html += '<div id="reactionArea">';
    html += '<button id="startReaction" class="btn-primary" style="width:100%">开始挑战 ⚡</button>';
    html += '</div>';

    el.innerHTML = html;

    document.getElementById("startReaction").onclick = () => {
        let qIdx = 0;
        let correctCount = 0;
        const area = document.getElementById("reactionArea");

        const showQuestion = () => {
            if (qIdx >= questions.length) {
                area.innerHTML = `
                    <div class="card" style="padding:24px;text-align:center">
                        <div style="font-family:'Space Grotesk',sans-serif;font-weight:900;font-size:48px;color:#FF6B00">${correctCount}/${questions.length}</div>
                        <p style="font-size:14px;margin-top:8px">流利度挑战完成</p>
                        <p style="font-size:11px;color:#666;margin-top:4px">不会的没关系，下次再练</p>
                    </div>`;
                return;
            }

            const q = questions[qIdx];
            area.innerHTML = `
                <div class="card" style="padding:24px;text-align:center">
                    <div style="font-size:11px;color:#999;margin-bottom:4px">${qIdx + 1} / ${questions.length}</div>
                    <p style="font-size:18px;font-weight:700;margin-bottom:16px">${escHtml(q.question)}</p>
                    <input id="reactionInput" class="input-field" placeholder="输入你的回答..." style="text-align:center;margin-bottom:12px">
                    <div style="display:flex;gap:8px;justify-content:center">
                        <button id="submitReaction" class="btn-primary">提交</button>
                        <button id="skipReaction" style="background:#fff;border:3px solid #000;padding:12px 24px;cursor:pointer;font-family:'Space Grotesk',sans-serif;font-weight:700">跳过 →</button>
                    </div>
                    <p id="reactionFeedback" style="font-size:12px;margin-top:12px"></p>
                </div>`;

            document.getElementById("submitReaction").onclick = () => {
                const answer = document.getElementById("reactionInput").value.trim();
                const expected = q.expected_answer.toLowerCase();
                const fb = document.getElementById("reactionFeedback");
                if (!answer) { fb.textContent = "试着回答一下！"; fb.style.color = "#d00"; return; }
                if (answer.toLowerCase().includes(expected) || expected.includes(answer.toLowerCase())) {
                    fb.textContent = "👍 很棒！参考: " + q.expected_answer;
                    fb.style.color = "#00a000";
                    correctCount++;
                } else {
                    fb.textContent = "💡 参考回答: " + q.expected_answer;
                    fb.style.color = "#FF6B00";
                }
                qIdx++;
                setTimeout(showQuestion, 1200);
            };

            document.getElementById("skipReaction").onclick = () => {
                document.getElementById("reactionFeedback").textContent = "💡 参考: " + q.expected_answer;
                document.getElementById("reactionFeedback").style.color = "#FF6B00";
                qIdx++;
                setTimeout(showQuestion, 1200);
            };

            document.getElementById("reactionInput").onkeydown = (e) => {
                if (e.key === "Enter") document.getElementById("submitReaction").click();
            };
        };

        showQuestion();
    };
}

// ── 步骤 6：句型聚焦 ──────────────────────────────────
function renderStep6(el, sc) {
    const pattern = sc.pattern_focus || "";
    let html = '<h3 style="font-size:18px;margin-bottom:12px">句型聚焦</h3>';
    html += '<p style="font-size:12px;color:#666;margin-bottom:16px">拆解本场景 1 个地道句型，掌握后可灵活替换</p>';

    // 简易 Markdown 渲染
    const rendered = pattern
        .replace(/### (.*)/g, '<h4 style="font-size:16px;margin-top:16px;margin-bottom:8px">$1</h4>')
        .replace(/## (.*)/g, '<h3 style="font-size:18px;margin-top:20px;margin-bottom:10px">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#000">$1</strong>')
        .replace(/^- (.*)/gm, '<div style="padding-left:16px;font-size:14px;margin:4px 0">• $1</div>')
        .replace(/^> (.*)/gm, '<div style="border-left:3px solid #FF6B00;padding:8px 16px;margin:12px 0;background:#fff8f0;font-size:16px;font-weight:700">$1</div>')
        .replace(/\n/g, '<br>');

    html += `<div style="font-size:14px;line-height:1.8">${rendered}</div>`;

    // 句型造句练习
    html += `
        <div style="border-top:3px solid #000;margin-top:20px;padding-top:16px">
            <p style="font-weight:700;margin-bottom:8px">✏️ 造句练习</p>
            <p style="font-size:11px;color:#666;margin-bottom:8px">模仿上面的句型，造一个你自己的句子</p>
            <input id="sentenceInput" class="input-field" placeholder="输入你造的句子..." style="margin-bottom:8px">
            <button id="saveSentence" class="btn-primary" style="width:100%">保存到语块本</button>
            <p id="sentenceMsg" style="font-size:11px;color:#00a000;margin-top:8px;text-align:center"></p>
        </div>`;

    el.innerHTML = html;

    document.getElementById("saveSentence").onclick = async () => {
        const sentence = document.getElementById("sentenceInput").value.trim();
        if (!sentence) return;
        try {
            await API.post("/api/chunks", {
                chunk_text: sentence,
                translation: "句型练习造句",
                scene_sentence: sentence,
                scenario_id: sc.id,
            });
            document.getElementById("sentenceMsg").textContent = "已保存到语块本 ✓";
            document.getElementById("sentenceInput").value = "";
        } catch (e) {
            document.getElementById("sentenceMsg").textContent = "保存失败: " + e.message;
            document.getElementById("sentenceMsg").style.color = "#d00";
        }
    };
}

// ── Can-Do 完成弹窗 ───────────────────────────────────
function showCanDo() {
    const sc = S.currentScenario?.scenario;
    const overlay = document.createElement("div");
    overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:200;display:flex;align-items:center;justify-content:center";
    overlay.innerHTML = `
        <div class="card" style="padding:24px;margin:20px;text-align:center;max-width:360px;background:#FFFDF0">
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:900;font-size:48px;margin-bottom:8px">🎉</div>
            <h2 style="font-size:24px;margin-bottom:4px">场景完成！</h2>
            <p style="font-size:14px;color:#FF6B00;font-weight:700;margin-bottom:16px">${escHtml(sc.title_cn)}</p>
            <div style="border:3px solid #000;padding:16px;margin-bottom:16px;text-align:left">
                <p style="font-size:10px;color:#999;margin-bottom:4px">CEFR Can-Do</p>
                <p style="font-size:14px;font-weight:700">${escHtml(sc.can_do || '完成本场景学习')}</p>
            </div>
            <button class="btn-primary" style="width:100%" onclick="document.body.removeChild(this.parentElement.parentElement);showPage('homePage');">返回首页</button>
        </div>`;
    document.body.appendChild(overlay);
    overlay.onclick = (e) => { if (e.target === overlay) { document.body.removeChild(overlay); showPage("homePage"); } };
}

// ════════════════════════════════════════════════════════
//  语块本页
// ════════════════════════════════════════════════════════
async function renderChunks() {
    const el = document.getElementById("chunksPage");
    el.innerHTML = '<h1 style="font-size:36px;line-height:1.1;margin-bottom:24px">语块本</h1><p style="text-align:center;color:#999">加载中...</p>';

    try {
        const [data, due] = await Promise.all([
            API.get("/api/chunks"),
            API.get("/api/chunks/due"),
        ]);
        const chunks = data.chunks;
        const dueIds = new Set(due.chunks.map(c => c.id));

        let html = '<h1 style="font-size:36px;line-height:1.1;margin-bottom:8px">语块本</h1>';

        if (due.chunks.length > 0) {
            html += `<div style="border:3px solid #FF6B00;padding:12px;margin-bottom:20px;background:#fff8f0">
                <p style="font-weight:700;font-size:14px">🔔 待复习: ${due.chunks.length} 个语块</p>
                <p style="font-size:11px;color:#666">点击复习，标记掌握程度</p>
            </div>`;
        }

        if (chunks.length === 0) {
            html += '<p style="text-align:center;color:#999;padding:60px 0">还没有收藏语块<br>在场景学习中点击收藏按钮</p>';
        } else {
            for (const c of chunks) {
                const isDue = dueIds.has(c.id);
                html += `
                    <div class="card" style="padding:16px;margin-bottom:12px;${isDue?'border-color:#FF6B00;':''}">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div style="flex:1">
                                <strong style="font-size:18px;color:#FF6B00">${escHtml(c.chunk_text)}</strong>
                                <p style="font-size:13px;color:#666;margin-top:2px">${escHtml(c.translation)}</p>
                                ${c.scene_sentence ? `<p style="font-size:11px;color:#999;margin-top:2px">📝 ${escHtml(c.scene_sentence)}</p>` : ""}
                            </div>
                            <span style="font-size:11px;font-weight:700;color:${(MASTERY[c.mastery]||{}).color||'#000'};white-space:nowrap">${(MASTERY[c.mastery]||{}).label||''}</span>
                        </div>
                        <div style="display:flex;gap:8px;margin-top:8px">
                            <button class="mastery-btn" data-id="${c.id}" data-level="1" style="background:#fff;border:2px solid #d00;color:#d00;padding:4px 8px;cursor:pointer;font-size:11px;font-weight:700">遗忘</button>
                            <button class="mastery-btn" data-id="${c.id}" data-level="2" style="background:#fff;border:2px solid #FF6B00;color:#FF6B00;padding:4px 8px;cursor:pointer;font-size:11px;font-weight:700">需复习</button>
                            <button class="mastery-btn" data-id="${c.id}" data-level="3" style="background:#fff;border:2px solid #00a000;color:#00a000;padding:4px 8px;cursor:pointer;font-size:11px;font-weight:700">熟练</button>
                        </div>
                    </div>`;
            }
        }

        el.innerHTML = html;

        el.querySelectorAll(".mastery-btn").forEach(btn => {
            btn.onclick = async () => {
                const id = btn.dataset.id;
                const level = parseInt(btn.dataset.level);
                try {
                    await API.post(`/api/chunks/${id}/mastery`, { mastery: level });
                    renderChunks();
                } catch (e) { alert("更新失败"); }
            };
        });
    } catch (e) {
        el.innerHTML = '<h1 style="font-size:36px;line-height:1.1;margin-bottom:24px">语块本</h1><p style="text-align:center;color:#d00">加载失败: ' + e.message + '</p>';
    }
}

// ════════════════════════════════════════════════════════
//  个人中心页
// ════════════════════════════════════════════════════════
function renderProfile() {
    const el = document.getElementById("profilePage");
    const level = S.user?.level || 1;
    const completed = S.stats?.completed_scenarios || 0;
    const totalChunks = S.stats?.total_chunks || 0;
    const streakDays = S.user?.streak_days || 0;

    const lv = LEVELS[level] || { name: "", cefr: "" };
    const levelProgress = Math.min(100, Math.round((completed / 10) * 100));

    el.innerHTML = `
        <h1 style="font-size:36px;line-height:1.1;margin-bottom:24px">我的</h1>

        <div class="card" style="padding:20px;margin-bottom:16px;text-align:center">
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:900;font-size:28px">${escHtml(S.user?.username||'')}</div>
            <p style="font-size:11px;color:#666">连续学习 <strong>${streakDays}</strong> 天</p>
        </div>

        <div class="card" style="padding:20px;margin-bottom:16px">
            <p style="font-weight:700;margin-bottom:8px">等级进度 · ${lv.short} (CEFR ${lv.cefr})</p>
            <div style="border:3px solid #000;height:28px;position:relative">
                <div style="background:#FF6B00;height:100%;width:${levelProgress}%;transition:width 0.5s"></div>
            </div>
            <p style="font-size:11px;color:#666;margin-top:4px">本等级已完成 ${completed} / 10 场景</p>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
            ${statCard(completed, "完成场景")}
            ${statCard(totalChunks, "收藏语块")}
            ${statCard(level, "当前等级")}
            ${statCard(streakDays, "连续天数")}
        </div>

        <button class="btn-primary" style="width:100%" onclick="logout()">退出登录</button>
    `;
}

// ════════════════════════════════════════════════════════
//  工具函数
// ════════════════════════════════════════════════════════
function escHtml(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
}

function escAttr(s) {
    if (!s) return "";
    return s.replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// ── 全局音频管理 ────────────────────────────────────
let _currentAudio = null;

function stopAudio() {
    if (_currentAudio) {
        _currentAudio.pause();
        _currentAudio = null;
    }
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

function playTTS(btn, text, rate) {
    if (!text) { btn.textContent = "▶"; return; }
    const u = speak(text, rate);
    if (u) {
        btn.textContent = "⏸";
        u.onend = () => { btn.textContent = "▶"; };
        u.onerror = () => { btn.textContent = "▶"; };
    }
}

function bindAudioButtons(el) {
    el.querySelectorAll(".btn-play").forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const text = btn.dataset.text;
            const rate = parseFloat(btn.dataset.rate || "0.85");
            if (!text) return;

            stopAudio();
            btn.textContent = "⏳";

            // 优先使用豆包 TTS API（服务器缓存，首次慢后续秒出）
            const ttsUrl = `/api/tts?text=${encodeURIComponent(text)}`;
            const audio = new Audio(ttsUrl);
            audio.playbackRate = rate;
            _currentAudio = audio;

            let resolved = false;
            const finish = () => {
                if (resolved) return;
                resolved = true;
                if (_currentAudio === audio) _currentAudio = null;
                btn.textContent = "▶";
            };

            const fallback = () => {
                if (resolved) return;
                resolved = true;
                if (_currentAudio === audio) _currentAudio = null;
                btn.textContent = "⏸";
                playTTS(btn, text, rate);
            };

            audio.onended = () => finish();
            audio.onerror = fallback;
            audio.load();
            audio.play().then(() => {
                btn.textContent = "⏸";
            }).catch(fallback);
        };
    });
}

// ── Tab 导航 ──────────────────────────────────────────
document.querySelectorAll(".tab-item").forEach(tab => {
    tab.addEventListener("click", () => {
        const page = tab.dataset.page;
        if (page === "chunksPage") showPage("chunksPage");
        if (page === "profilePage") showPage("profilePage");
        if (page === "homePage") showPage("homePage");
    });
});

// ── 启动 ──────────────────────────────────────────────
init();

// 注册 Service Worker
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
}
