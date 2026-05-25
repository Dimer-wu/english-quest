"""导入 L1 全部 10 个场景的初始数据。重复运行安全（跳过已存在的场景）。"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import init_db, SessionLocal, Scenario

L1_SCENARIOS = [
    {
        "level": 1,
        "order": 1,
        "title": "Greetings & Self-Introduction",
        "title_cn": "打招呼与自我介绍",
        "category": "社交",
        "can_do": "能用英文打招呼、说出自己的名字和职业、简单介绍自己（CEFR A1 — 自我介绍）",
        "audio_dialogue": "/static/audio/l1_s1_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s1_chunk_1.mp3",
            "/static/audio/l1_s1_chunk_2.mp3",
            "/static/audio/l1_s1_chunk_3.mp3",
            "/static/audio/l1_s1_chunk_4.mp3",
            "/static/audio/l1_s1_chunk_5.mp3",
        ],
        "dialogue_script": [
            {"speaker": "👤 A (Tom)", "text_en": "Hi there! I don't think we've met. I'm Tom.", "text_cn": "嗨！我们好像没见过。我是 Tom。"},
            {"speaker": "👤 B (You)", "text_en": "Hi Tom, nice to meet you. I'm [Name].", "text_cn": "嗨 Tom，很高兴认识你。我是 [名字]。"},
            {"speaker": "👤 A (Tom)", "text_en": "Nice to meet you too. So, what do you do?", "text_cn": "我也很高兴认识你。那，你是做什么的？"},
            {"speaker": "👤 B (You)", "text_en": "I work in sales. How about you?", "text_cn": "我做销售。你呢？"},
            {"speaker": "👤 A (Tom)", "text_en": "Oh cool! I'm in marketing. Do you like your job?", "text_cn": "哦酷！我做市场营销。你喜欢你的工作吗？"},
            {"speaker": "👤 B (You)", "text_en": "Yeah, it's pretty interesting. I get to meet a lot of people.", "text_cn": "挺有意思的，能认识很多人。"},
            {"speaker": "👤 A (Tom)", "text_en": "That's awesome. Well, it was great chatting with you!", "text_cn": "太棒了。很高兴和你聊天！"},
            {"speaker": "👤 B (You)", "text_en": "You too! See you around.", "text_cn": "我也是！回头见。"},
        ],
        "chunks": [
            {"chunk": "Nice to meet you.", "translation": "很高兴认识你", "replaceable": ["Nice", "→ Good / Great / Lovely"]},
            {"chunk": "What do you do?", "translation": "你是做什么的？（问工作）", "replaceable": ["do you do", "→ do you do for a living"]},
            {"chunk": "I work in ___ .", "translation": "我在 ___ 行业工作", "replaceable": ["work in", "→ am in / do"]},
            {"chunk": "How about you?", "translation": "你呢？（反问对方）", "replaceable": ["How about", "→ What about / And"]},
            {"chunk": "See you around.", "translation": "回头见（随意地道别）", "replaceable": ["around", "→ later / soon"]},
        ],
        "pattern_focus": """## 本场景核心句型：What do you do?

**地道用法**：英语里问对方工作，几乎从不说 "What is your job?"——太生硬了。最自然的说法是：

> **"What do you do?"**

这句话字面意思是"你做什么"，但母语者都知道是在问工作。

**替换词练习**：
- What do you do **for a living**?（更明确问工作）
- What **kind of** work do you do?（问工作类型）
- What **line of** work are you in?（更正式一点）

**回答模板**：
- I work in **sales** / **marketing** / **IT** / **education** / **finance**
- I'm a **teacher** / **engineer** / **designer** / **manager**
""",
        "reaction_questions": [
            {"question": "How do you say hello to someone you just met?", "expected_answer": "Hi, nice to meet you."},
            {"question": "Ask someone what their job is.", "expected_answer": "What do you do?"},
            {"question": "Tell someone you work in sales.", "expected_answer": "I work in sales."},
            {"question": "Ask someone 'and you?' in a casual way.", "expected_answer": "How about you?"},
            {"question": "Say goodbye to a new friend.", "expected_answer": "See you around."},
        ],
    },
    {
        "level": 1,
        "order": 2,
        "title": "Small Talk — Weather",
        "title_cn": "聊天气",
        "category": "社交",
        "can_do": "能用英文聊天气、表达对天气的感受、做简单的寒暄（CEFR A1 — 日常寒暄）",
        "audio_dialogue": "/static/audio/l1_s2_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s2_chunk_1.mp3",
            "/static/audio/l1_s2_chunk_2.mp3",
            "/static/audio/l1_s2_chunk_3.mp3",
            "/static/audio/l1_s2_chunk_4.mp3",
            "/static/audio/l1_s2_chunk_5.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Nice day, isn't it?", "text_cn": "天气不错，对吧？"},
            {"speaker": "👤 B (You)", "text_en": "Yeah, it's beautiful. Not too hot.", "text_cn": "是啊，挺好的。不算太热。"},
            {"speaker": "👤 A", "text_en": "I know, right? Much better than last week.", "text_cn": "对吧？比上周好多了。"},
            {"speaker": "👤 B (You)", "text_en": "Yeah, last week was awful. So much rain.", "text_cn": "是啊，上周太糟了。下那么多雨。"},
            {"speaker": "👤 A", "text_en": "Fingers crossed it stays like this!", "text_cn": "希望天气一直这样！"},
            {"speaker": "👤 B (You)", "text_en": "Hope so too! Anyway, I gotta run.", "text_cn": "我也希望！那，我先走了。"},
        ],
        "chunks": [
            {"chunk": "Nice day, isn't it?", "translation": "天气不错，对吧？", "replaceable": ["Nice", "→ Beautiful / Lovely / Great"]},
            {"chunk": "Not too hot.", "translation": "不算太热", "replaceable": ["hot", "→ cold / warm / bad"]},
            {"chunk": "Much better than ___ .", "translation": "比 ___ 好多了", "replaceable": ["better", "→ worse（更糟）"]},
            {"chunk": "Fingers crossed!", "translation": "希望如此！（字面：交叉手指，表祈祷）", "replaceable": ["Fingers crossed", "→ Hopefully / Let's hope so"]},
            {"chunk": "I gotta run.", "translation": "我得走了（口语化）", "replaceable": ["gotta run", "→ gotta go / should get going"]},
        ],
        "pattern_focus": """## 本场景核心句型：Nice day, isn't it?

**地道用法**：英语中，用一个肯定句 + 反义疑问句（tag question）可以让对方自然地接话。

> **"Nice day, isn't it?"**

这种结构叫 tag question，是社交对话的润滑剂。

**规则**：肯定句 → 否定 tag / 否定句 → 肯定 tag
- It's cold, **isn't it**?
- You work in sales, **don't you**?
- It's not too bad, **is it**?
""",
        "reaction_questions": [
            {"question": "Say the weather is nice today.", "expected_answer": "Nice day, isn't it?"},
            {"question": "Say the weather was bad last week.", "expected_answer": "Last week was awful."},
            {"question": "Say you hope the good weather continues.", "expected_answer": "Fingers crossed!"},
            {"question": "Say you need to leave now (casually).", "expected_answer": "I gotta run."},
            {"question": "Compare today to last week.", "expected_answer": "Much better than last week."},
        ],
    },
    {
        "level": 1,
        "order": 3,
        "title": "Talking About Hobbies",
        "title_cn": "聊爱好",
        "category": "社交",
        "can_do": "能用英文聊兴趣爱好、问对方的兴趣、表达喜欢和不喜欢（CEFR A1 — 兴趣爱好）",
        "audio_dialogue": "/static/audio/l1_s3_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s3_chunk_1.mp3",
            "/static/audio/l1_s3_chunk_2.mp3",
            "/static/audio/l1_s3_chunk_3.mp3",
            "/static/audio/l1_s3_chunk_4.mp3",
            "/static/audio/l1_s3_chunk_5.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "So, what do you like to do in your free time?", "text_cn": "那你空闲时间喜欢做什么？"},
            {"speaker": "👤 B (You)", "text_en": "I like watching movies. And I'm trying to learn English.", "text_cn": "我喜欢看电影。还有在学英语。"},
            {"speaker": "👤 A", "text_en": "Oh nice! What kind of movies do you like?", "text_cn": "不错！你喜欢什么类型的电影？"},
            {"speaker": "👤 B (You)", "text_en": "I'm into action movies. What about you?", "text_cn": "我喜欢动作片。你呢？"},
            {"speaker": "👤 A", "text_en": "I'm a big fan of comedies. They help me relax.", "text_cn": "我特别喜欢喜剧片，能让我放松。"},
        ],
        "chunks": [
            {"chunk": "What do you like to do in your free time?", "translation": "你空闲时间喜欢做什么？", "replaceable": ["free time", "→ spare time / weekends"]},
            {"chunk": "I'm into ___ .", "translation": "我特别喜欢 ___", "replaceable": ["into", "→ a big fan of / really into"]},
            {"chunk": "What kind of ___ do you like?", "translation": "你喜欢什么类型的 ___？", "replaceable": ["kind of", "→ sort of / type of"]},
            {"chunk": "I'm a big fan of ___ .", "translation": "我特别喜欢 ___（比 like 更有力）", "replaceable": ["big fan", "→ huge fan / massive fan"]},
            {"chunk": "They help me relax.", "translation": "能让我放松", "replaceable": ["relax", "→ unwind / chill out"]},
        ],
        "pattern_focus": """## 本场景核心句型：I'm into ___

**地道用法**："I like" 没问题，但母语者更常说：

> **"I'm into [something]"**

表达"热衷、喜欢"，比 like 更自然有活力。

**程度升级**：
- I like movies. → 一般喜欢
- I'm into movies. → 挺喜欢的
- I'm a big fan of movies. → 特别喜欢
- I'm obsessed with movies. → 迷上了（极端）
""",
        "reaction_questions": [
            {"question": "Ask someone what they do in their free time.", "expected_answer": "What do you like to do in your free time?"},
            {"question": "Say you really like action movies.", "expected_answer": "I'm into action movies."},
            {"question": "Ask what type of movies they like.", "expected_answer": "What kind of movies do you like?"},
            {"question": "Say you're a big fan of comedies.", "expected_answer": "I'm a big fan of comedies."},
            {"question": "Ask 'and you?' in a different way.", "expected_answer": "What about you?"},
        ],
    },
    {
        "level": 1,
        "order": 4,
        "title": "Talking About Work",
        "title_cn": "聊工作",
        "category": "社交",
        "can_do": "能用英文聊工作内容、公司、工作感受（CEFR A1 — 工作话题）",
        "audio_dialogue": "/static/audio/l1_s4_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s4_chunk_1.mp3",
            "/static/audio/l1_s4_chunk_2.mp3",
            "/static/audio/l1_s4_chunk_3.mp3",
            "/static/audio/l1_s4_chunk_4.mp3",
            "/static/audio/l1_s4_chunk_5.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "So where do you work?", "text_cn": "你在哪里工作？"},
            {"speaker": "👤 B (You)", "text_en": "I work at a trading company. It's in Shanghai.", "text_cn": "我在一家贸易公司，在上海。"},
            {"speaker": "👤 A", "text_en": "Oh interesting! How long have you been there?", "text_cn": "有意思！你在那工作多久了？"},
            {"speaker": "👤 B (You)", "text_en": "About three years now. Time flies!", "text_cn": "差不多三年了。时间过得真快！"},
            {"speaker": "👤 A", "text_en": "Do you enjoy it?", "text_cn": "你喜欢这份工作吗？"},
            {"speaker": "👤 B (You)", "text_en": "Most days, yeah. Some days are tough but that's work, right?", "text_cn": "大部分时候还行。偶尔很难，但工作就是这样嘛。"},
        ],
        "chunks": [
            {"chunk": "Where do you work?", "translation": "你在哪里工作？", "replaceable": ["work", "→ work at / based"]},
            {"chunk": "I work at a ___ company.", "translation": "我在一家 ___ 公司工作", "replaceable": ["company", "→ firm / business"]},
            {"chunk": "How long have you been there?", "translation": "你在那工作多久了？", "replaceable": ["there", "→ at X / doing that"]},
            {"chunk": "Time flies!", "translation": "时间过得真快！", "replaceable": ["flies", "→ goes by fast / really flies"]},
            {"chunk": "That's work, right?", "translation": "工作就是这样嘛", "replaceable": ["That's work", "→ That's life / Goes with the job"]},
        ],
        "pattern_focus": """## 本场景核心句型：How long have you been ___?

**地道用法**：问某人做某事多久，用现在完成进行时（present perfect continuous）：

> **"How long have you been working there?"**

由 have/has + been + doing 构成，强调从过去持续至今。

**替换练习**：
- How long have you been **learning English**?
- How long have you been **living here**?
- How long have you been **doing that**?
""",
        "reaction_questions": [
            {"question": "Ask someone where they work.", "expected_answer": "Where do you work?"},
            {"question": "Say you work at a trading company.", "expected_answer": "I work at a trading company."},
            {"question": "Ask how long they have been working there.", "expected_answer": "How long have you been there?"},
            {"question": "Say time passes quickly.", "expected_answer": "Time flies!"},
            {"question": "Say that work has ups and downs.", "expected_answer": "Some days are tough but that's work."},
        ],
    },
    {
        "level": 1,
        "order": 5,
        "title": "Inviting Someone",
        "title_cn": "邀请朋友",
        "category": "社交",
        "can_do": "能用英文发出邀请、接受/婉拒邀请、约定时间和地点（CEFR A1 — 发出邀请）",
        "audio_dialogue": "/static/audio/l1_s5_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s5_chunk_1.mp3",
            "/static/audio/l1_s5_chunk_2.mp3",
            "/static/audio/l1_s5_chunk_3.mp3",
            "/static/audio/l1_s5_chunk_4.mp3",
            "/static/audio/l1_s5_chunk_5.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Hey, a few of us are grabbing coffee later. Wanna come?", "text_cn": "嘿，我们几个人等下要去喝咖啡。想一起来吗？"},
            {"speaker": "👤 B (You)", "text_en": "Oh, that sounds nice! What time?", "text_cn": "听起来不错！几点？"},
            {"speaker": "👤 A", "text_en": "Around 3. The place is just down the street.", "text_cn": "大概三点。就在这条街上。"},
            {"speaker": "👤 B (You)", "text_en": "I'm in! I'll meet you guys there.", "text_cn": "算我一个！我到那找你们。"},
            {"speaker": "👤 A", "text_en": "Awesome! See you then.", "text_cn": "太好了，到时候见。"},
        ],
        "chunks": [
            {"chunk": "Wanna come?", "translation": "想来吗？（口语缩读）", "replaceable": ["come", "→ join us / tag along"]},
            {"chunk": "That sounds nice!", "translation": "听起来不错！（接受邀请前奏）", "replaceable": ["nice", "→ great / fun / good"]},
            {"chunk": "I'm in!", "translation": "算我一个！", "replaceable": ["I'm in", "→ Count me in / I'd love to"]},
            {"chunk": "I'll meet you guys there.", "translation": "我到那找你们", "replaceable": ["you guys", "→ you all / everyone"]},
            {"chunk": "It's just down the street.", "translation": "就在这条街上（很近）", "replaceable": ["down the street", "→ around the corner / nearby"]},
        ],
        "pattern_focus": """## 本场景核心句型：Wanna ___?

**地道用法**：口语中 "want to" 缩读成 "wanna"，比正式版自然得多。

> **"Wanna come?"** = "Do you want to come?"

同样规则：
- Wanna **grab a coffee**?（喝杯咖啡？）
- Wanna **join us**?（一起？）
- Wanna **go**?（走不走？）

注意："wanna" 只在非常轻松的口语场合使用，写作、正式场合不要用。
""",
        "reaction_questions": [
            {"question": "Casually invite someone for coffee.", "expected_answer": "Wanna grab a coffee?"},
            {"question": "Accept an invitation with enthusiasm.", "expected_answer": "I'm in!"},
            {"question": "Ask what time an event is.", "expected_answer": "What time?"},
            {"question": "Say something sounds good.", "expected_answer": "That sounds nice!"},
            {"question": "Say you'll meet them at the place.", "expected_answer": "I'll meet you guys there."},
        ],
    },
    {
        "level": 1,
        "order": 6,
        "title": "Saying Goodbye",
        "title_cn": "道别",
        "category": "社交",
        "can_do": "能用英文自然地道别、表达下次见面的期待（CEFR A1 — 告别）",
        "audio_dialogue": "/static/audio/l1_s6_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s6_chunk_1.mp3",
            "/static/audio/l1_s6_chunk_2.mp3",
            "/static/audio/l1_s6_chunk_3.mp3",
            "/static/audio/l1_s6_chunk_4.mp3",
            "/static/audio/l1_s6_chunk_5.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Well, I should probably get going. It's getting late.", "text_cn": "我该走了。有点晚了。"},
            {"speaker": "👤 B (You)", "text_en": "Yeah, me too. It was really nice meeting you!", "text_cn": "我也该走了。真的很高兴认识你！"},
            {"speaker": "👤 A", "text_en": "Likewise! Let's do this again sometime.", "text_cn": "同感！改天再约。"},
            {"speaker": "👤 B (You)", "text_en": "Definitely. Take care!", "text_cn": "当然。保重！"},
            {"speaker": "👤 A", "text_en": "You too. Bye for now!", "text_cn": "你也是。先拜拜啦！"},
        ],
        "chunks": [
            {"chunk": "I should probably get going.", "translation": "我该走了（委婉自然）", "replaceable": ["get going", "→ head out / take off / be off"]},
            {"chunk": "It's getting late.", "translation": "有点晚了", "replaceable": ["late", "→ dark / cold"]},
            {"chunk": "It was really nice meeting you!", "translation": "真的很高兴认识你", "replaceable": ["nice", "→ great / lovely / a pleasure"]},
            {"chunk": "Let's do this again sometime.", "translation": "改天再约", "replaceable": ["this again", "→ it again / coffee / lunch"]},
            {"chunk": "Take care!", "translation": "保重！", "replaceable": ["Take care", "→ Look after yourself / All the best"]},
        ],
        "pattern_focus": """## 本场景核心句型：I should probably ___

**地道用法**："I should go" 有点生硬。"I should probably..." 更委婉自然。

> **"I should probably get going."**

这是一种"软离开"策略——不是直接说"我要走了"，而是给一个温和的信号。

**更多离开的说法**（从直接到委婉）：
- I'm off! → 最直接
- I'd better be going. → 温和
- I should probably get going. → 更温和
- Well, it's getting late... → 最委婉（暗示）
""",
        "reaction_questions": [
            {"question": "Softly signal that you need to leave.", "expected_answer": "I should probably get going."},
            {"question": "Say it was nice meeting someone.", "expected_answer": "It was really nice meeting you."},
            {"question": "Suggest meeting again.", "expected_answer": "Let's do this again sometime."},
            {"question": "Say goodbye warmly.", "expected_answer": "Take care!"},
            {"question": "Say a casual quick goodbye.", "expected_answer": "Bye for now!"},
        ],
    },
    {
        "level": 1,
        "order": 7,
        "title": "Apologizing & Thanking",
        "title_cn": "道歉与感谢",
        "category": "社交",
        "can_do": "能用英文道歉、道谢、回应道歉和道谢（CEFR A1 — 礼貌用语）",
        "audio_dialogue": "/static/audio/l1_s7_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s7_chunk_1.mp3",
            "/static/audio/l1_s7_chunk_2.mp3",
            "/static/audio/l1_s7_chunk_3.mp3",
            "/static/audio/l1_s7_chunk_4.mp3",
            "/static/audio/l1_s7_chunk_5.mp3",
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Hey, sorry I'm late. Traffic was a nightmare.", "text_cn": "抱歉我迟到了。路上堵死了。"},
            {"speaker": "👤 B (You)", "text_en": "No worries! I just got here myself.", "text_cn": "没事！我也刚到。"},
            {"speaker": "👤 A", "text_en": "Thanks for understanding. Oh, I brought you a coffee, by the way.", "text_cn": "谢谢你理解。对了，我给你带了杯咖啡。"},
            {"speaker": "👤 B (You)", "text_en": "That's so kind of you! Thanks a lot.", "text_cn": "太贴心了！非常感谢。"},
        ],
        "chunks": [
            {"chunk": "Sorry I'm late.", "translation": "抱歉我迟到了", "replaceable": ["late", "→ running late / held up"]},
            {"chunk": "Traffic was a nightmare.", "translation": "路上堵死了", "replaceable": ["nightmare", "→ terrible / crazy / really bad"]},
            {"chunk": "No worries!", "translation": "没事！/别担心！", "replaceable": ["No worries", "→ No problem / That's okay / It's all good"]},
            {"chunk": "That's so kind of you!", "translation": "太贴心了！", "replaceable": ["kind", "→ sweet / thoughtful / nice"]},
            {"chunk": "Thanks for understanding.", "translation": "谢谢你理解", "replaceable": ["understanding", "→ being patient / waiting"]},
        ],
        "pattern_focus": """## 本场景核心句型：No worries!

**地道用法**：英语里回应"Sorry"最自然的方式不是"You're welcome"（那个是回应 Thank you 的！），而是：

> **"No worries!"** / **"No problem!"** / **"It's all good!"**

**回应 Thank you 的选项**：
- You're welcome! → 标准正式
- No worries! → 随和友好
- Anytime! → 乐于帮忙
- Glad to help! → 很高兴帮到你
""",
        "reaction_questions": [
            {"question": "Apologize for being late.", "expected_answer": "Sorry I'm late."},
            {"question": "Respond to an apology casually.", "expected_answer": "No worries!"},
            {"question": "Thank someone for a gift.", "expected_answer": "That's so kind of you!"},
            {"question": "Say the traffic was terrible.", "expected_answer": "Traffic was a nightmare."},
            {"question": "Thank someone for being patient.", "expected_answer": "Thanks for understanding."},
        ],
    },
    {
        "level": 1,
        "order": 8,
        "title": "Giving Compliments",
        "title_cn": "称赞他人",
        "category": "社交",
        "can_do": "能用英文真心称赞他人、接受赞美、回应夸奖（CEFR A1 — 赞美）",
        "audio_dialogue": "/static/audio/l1_s8_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s8_chunk_1.mp3",
            "/static/audio/l1_s8_chunk_2.mp3",
            "/static/audio/l1_s8_chunk_3.mp3",
            "/static/audio/l1_s8_chunk_4.mp3",
            "/static/audio/l1_s8_chunk_5.mp3",
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Hey, I love your jacket! Where did you get it?", "text_cn": "嘿，你的外套真好看！在哪买的？"},
            {"speaker": "👤 B (You)", "text_en": "Oh thanks! I got it online actually. Good eye!", "text_cn": "谢谢！其实是在网上买的。好眼力！"},
            {"speaker": "👤 A", "text_en": "Seriously, it really suits you.", "text_cn": "说真的，很适合你。"},
            {"speaker": "👤 B (You)", "text_en": "That's really nice of you to say. Made my day!", "text_cn": "你这么说真好。我今天开心了！"},
        ],
        "chunks": [
            {"chunk": "I love your ___ !", "translation": "你的 ___ 真好看/真棒！", "replaceable": ["love", "→ really like / am loving"]},
            {"chunk": "Where did you get it?", "translation": "在哪买的？（赞美的自然延伸）", "replaceable": ["get it", "→ find it / buy it"]},
            {"chunk": "It really suits you.", "translation": "很适合你", "replaceable": ["suits", "→ looks great on / fits"]},
            {"chunk": "That's really nice of you to say.", "translation": "你这么说真好（接受赞美）", "replaceable": ["nice", "→ kind / sweet"]},
            {"chunk": "Made my day!", "translation": "让我今天都开心了！", "replaceable": ["Made my day", "→ You made my day / That makes me so happy"]},
        ],
        "pattern_focus": """## 本场景核心句型：I love your ___ !

**地道用法**：称赞别人物品时，说 "I love your..." 比 "Your... is nice" 更热情自然。

> **"I love your jacket!"**

**怎样自然接受赞美**：
- ❌ "No, it's cheap."（中式谦虚不合适）
- ✅ "Oh thanks!" + 反夸回去或分享信息
- ✅ "That's so kind of you to say!"（更正式）

英语文化中，被赞美时接受+感谢即可，不必过分谦虚。
""",
        "reaction_questions": [
            {"question": "Compliment someone's jacket.", "expected_answer": "I love your jacket!"},
            {"question": "Ask where they bought something.", "expected_answer": "Where did you get it?"},
            {"question": "Say something looks good on someone.", "expected_answer": "It really suits you."},
            {"question": "Accept a compliment gracefully.", "expected_answer": "That's really nice of you to say."},
            {"question": "Say something made you very happy.", "expected_answer": "Made my day!"},
        ],
    },
    {
        "level": 1,
        "order": 9,
        "title": "Casual Chat — Small Talk",
        "title_cn": "闲聊寒暄",
        "category": "社交",
        "can_do": "能用英文进行 3-5 轮自然闲聊、开启和收尾日常对话（CEFR A1 — 日常交流）",
        "audio_dialogue": "/static/audio/l1_s9_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s9_chunk_1.mp3",
            "/static/audio/l1_s9_chunk_2.mp3",
            "/static/audio/l1_s9_chunk_3.mp3",
            "/static/audio/l1_s9_chunk_4.mp3",
            "/static/audio/l1_s9_chunk_5.mp3",
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Hey! Long time no see. How have you been?", "text_cn": "嘿！好久不见。最近怎么样？"},
            {"speaker": "👤 B (You)", "text_en": "Hey! I've been good. Pretty busy with work though.", "text_cn": "嘿！还不错。就是工作挺忙的。"},
            {"speaker": "👤 A", "text_en": "Tell me about it. Same here. Any fun plans for the weekend?", "text_cn": "我懂。我也一样。周末有什么好计划吗？"},
            {"speaker": "👤 B (You)", "text_en": "Nothing special. Probably just taking it easy.", "text_cn": "没什么特别的，大概就放松一下吧。"},
            {"speaker": "👤 A", "text_en": "Sounds perfect. Anyway, don't let me keep you. Catch up soon?", "text_cn": "听着就不错。好了，不耽误你了。改天再聊？"},
        ],
        "chunks": [
            {"chunk": "Long time no see.", "translation": "好久不见", "replaceable": ["Long time no see", "→ It's been a while / Haven't seen you in ages"]},
            {"chunk": "How have you been?", "translation": "最近怎么样？", "replaceable": ["How have you been", "→ How's it going / What've you been up to"]},
            {"chunk": "Tell me about it.", "translation": "我懂。/可不是嘛。（表同感）", "replaceable": ["Tell me about it", "→ I hear you / I know, right"]},
            {"chunk": "Taking it easy.", "translation": "放松、不安排太多事", "replaceable": ["Taking it easy", "→ Chilling / Relaxing / Laying low"]},
            {"chunk": "Don't let me keep you.", "translation": "不耽误你了（体面收尾）", "replaceable": ["keep you", "→ hold you up / take up your time"]},
        ],
        "pattern_focus": """## 本场景核心句型：How have you been?

**地道用法**：不是 "How are you?"——那个太初级了。对有一段时间没见的人，说：

> **"How have you been?"**

表示"从上次见面到现在，你过得怎么样？"

**不同场景的问候**：
- How are you? → 日常、刚见面
- How have you been? → 一段时间没见
- How's it going? → 最随意
- What've you been up to? → 问最近在忙什么
""",
        "reaction_questions": [
            {"question": "Greet someone you haven't seen in a while.", "expected_answer": "Long time no see. How have you been?"},
            {"question": "Agree with someone's complaint.", "expected_answer": "Tell me about it."},
            {"question": "Say you're just relaxing this weekend.", "expected_answer": "Just taking it easy."},
            {"question": "Politely end a conversation.", "expected_answer": "Don't let me keep you."},
            {"question": "Suggest catching up again later.", "expected_answer": "Catch up soon?"},
        ],
    },
    {
        "level": 1,
        "order": 10,
        "title": "Review: First Impressions",
        "title_cn": "复习：初次社交综合",
        "category": "复习",
        "can_do": "能综合运用前 9 个场景的语言，完成一次完整自然的初次社交对话（CEFR A1 — 综合复习）",
        "audio_dialogue": "/static/audio/l1_s10_dialogue.mp3",
        "audio_chunks": [
            "/static/audio/l1_s10_chunk_1.mp3",
            "/static/audio/l1_s10_chunk_2.mp3",
            "/static/audio/l1_s10_chunk_3.mp3"
        ],
        "dialogue_script": [
            {"speaker": "👤 A", "text_en": "Hi, I'm Sarah. I don't think we've met before.", "text_cn": "嗨，我是 Sarah。我们好像没见过。"},
            {"speaker": "👤 B (You)", "text_en": "Hi Sarah! Nice to meet you. I'm [Name].", "text_cn": "嗨 Sarah！很高兴认识你。我是 [名字]。"},
            {"speaker": "👤 A", "text_en": "So, how do you know everyone here?", "text_cn": "那，你是怎么认识这边的人的？"},
            {"speaker": "👤 B (You)", "text_en": "I work with Tom. He invited me. How about you?", "text_cn": "我和 Tom 是同事。他邀请我的。你呢？"},
            {"speaker": "👤 A", "text_en": "Same! We're in the same department. So what do you do?", "text_cn": "我也是！我们在同一个部门。你是做什么的？"},
            {"speaker": "👤 B (You)", "text_en": "I'm in sales. It keeps me busy but I enjoy it.", "text_cn": "我做销售。挺忙的但我很喜欢。"},
            {"speaker": "👤 A", "text_en": "That's great. Anyway, I should go say hi to a few people. It was really nice meeting you!", "text_cn": "不错。好了，我得去跟几个人打个招呼。很高兴认识你！"},
            {"speaker": "👤 B (You)", "text_en": "You too! See you around!", "text_cn": "我也是！回头见！"},
        ],
        "chunks": [
            {"chunk": "How do you know everyone here?", "translation": "你是怎么认识这边的人的？", "replaceable": ["everyone here", "→ the host / these guys"]},
            {"chunk": "He invited me.", "translation": "他邀请我的", "replaceable": ["invited", "→ brought / asked"]},
            {"chunk": "I should go say hi to a few people.", "translation": "我得去跟几个人打个招呼", "replaceable": ["say hi", "→ say hello / introduce myself"]},
        ],
        "pattern_focus": """## 综合复习：初次社交完整流程

一次成功的初次社交对话 = **4 个阶段**：

1. **破冰**: Hi / Nice to meet you / I'm [name]
2. **找共同点**: How do you know [person/event]? / What brings you here?
3. **展开话题**: What do you do? / Where are you from? / 聊爱好天气
4. **自然收尾**: Was nice meeting you / Let's [do something] sometime / See you around!

试试默写这 4 步，看看你能回忆多少语块。""",
        "reaction_questions": [
            {"question": "Ask how someone knows the people at an event.", "expected_answer": "How do you know everyone here?"},
            {"question": "Say you need to greet other people too.", "expected_answer": "I should go say hi to a few people."},
            {"question": "Complete a natural goodbye after meeting someone new.", "expected_answer": "It was really nice meeting you. See you around!"},
            {"question": "Introduce yourself to a stranger.", "expected_answer": "Hi, I'm [Name]. Nice to meet you."},
            {"question": "Say you enjoy your job despite it being busy.", "expected_answer": "It keeps me busy but I enjoy it."},
        ],
    },
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        for s in L1_SCENARIOS:
            existing = db.query(Scenario).filter_by(level=s["level"], order=s["order"]).first()
            if existing:
                print(f"  [跳过] L{s['level']}-S{s['order']} {s['title_cn']}（已存在）")
                continue
            db.add(Scenario(**s))
            print(f"  [导入] L{s['level']}-S{s['order']} {s['title_cn']}")
        db.commit()
        print(f"\n场景数据导入完成 ({len(L1_SCENARIOS)} 个场景)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
