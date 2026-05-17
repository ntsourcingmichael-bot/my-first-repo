"""
展会参展顾问智能体
帮助国内科技企业、品牌及外贸工厂评估海外展会参展可行性。
通过实时搜索展会主办方官网、社交媒体、参展企业新闻稿等信源，提供精准匹配与可行性评估。
"""

import anthropic
import json
import os
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
# 工具实现（客户端执行）
# ──────────────────────────────────────────────

def generate_assessment_report(
    company_name: str,
    # 9个必填用户画像字段
    products: str,
    industry: str,
    application_scenarios: str,
    company_size: str,
    business_model: str,
    profit_model: str,
    channel_type: str,
    manufacturing_capability: str,
    brand_capability: str,
    # 参展需求
    exhibition_goals: list[str],
    budget_range: str,
    historical_experience: str,
    # 推荐结果
    recommended_exhibitions: list[dict],
    overall_verdict: str,
    key_risks: str,
    action_items: list[str],
    match_reasoning: str,
    consultant_notes: str = "",
) -> dict:
    """生成结构化的参展可行性评估报告，并保存为文件。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = company_name.replace(" ", "_").replace("/", "-")[:30]

    lines = [
        "=" * 60,
        "       展会参展可行性评估报告",
        "=" * 60,
        f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
        "",
        "【企业用户画像】",
        f"  公司名称：{company_name}",
        f"  主要产品：{products}",
        f"  所属行业：{industry}",
        f"  应用场景：{application_scenarios}",
        f"  企业规模：{company_size}",
        f"  商业模式：{business_model}",
        f"  盈利模式：{profit_model}",
        f"  渠道类型：{channel_type}",
        f"  加工能力：{manufacturing_capability}",
        f"  品牌能力：{brand_capability}",
        "",
        "【参展需求】",
        f"  核心目标：{'；'.join(exhibition_goals)}",
        f"  预算区间：{budget_range}",
        f"  历史经验：{historical_experience}",
        "",
        "【推荐展会】",
    ]

    for i, ex in enumerate(recommended_exhibitions, 1):
        score = ex.get("match_score", 0)
        stars = "★" * score + "☆" * (5 - score)
        lines += [
            f"  {i}. {ex.get('name', '未知')}",
            f"     时间/地点：{ex.get('date_location', '待确认')}",
            f"     费用估算：{ex.get('estimated_cost', '待询价')}",
            f"     匹配度：{stars} ({score}/5)",
            f"     数据来源：{ex.get('data_sources', '官网/社交媒体')}",
            f"     推荐理由：{ex.get('reasons', '')}",
            "",
        ]

    verdict_map = {
        "建议参展":   "✅ 建议参展",
        "谨慎参展":   "⚠️  谨慎参展",
        "暂不建议":   "❌ 暂不建议参展",
    }
    verdict_display = verdict_map.get(overall_verdict, overall_verdict)

    lines += [
        "【匹配度分析】",
        f"  {match_reasoning}",
        "",
        "【可行性评估结论】",
        f"  综合建议：{verdict_display}",
        "",
        "【主要风险提示】",
    ]
    for risk_line in key_risks.split("；"):
        if risk_line.strip():
            lines.append(f"  • {risk_line.strip()}")

    lines += ["", "【下一步行动建议】"]
    for idx, item in enumerate(action_items, 1):
        lines.append(f"  {idx}. {item}")

    if consultant_notes:
        lines += ["", "【顾问备注】", f"  {consultant_notes}"]

    lines += ["", "=" * 60]
    report_text = "\n".join(lines)

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    file_path = reports_dir / f"{safe_name}_{timestamp}.txt"
    file_path.write_text(report_text, encoding="utf-8")

    return {
        "success": True,
        "report_text": report_text,
        "file_path": str(file_path),
        "verdict": overall_verdict,
    }


# ──────────────────────────────────────────────
# 工具定义
# ──────────────────────────────────────────────

BUILTIN_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
]

CUSTOM_TOOLS = [
    {
        "name": "generate_assessment_report",
        "description": (
            "在收集完所有9项用户画像信息、参展需求，并通过实时搜索确认推荐展会详情后，"
            "生成结构化的展会参展可行性评估报告。"
            "必须在已掌握全部必填字段后才可调用。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "公司名称（可匿名填『某科技公司』）",
                },
                # 9个用户画像字段
                "products": {
                    "type": "string",
                    "description": "主要产品描述，如：TWS耳机、激光切割机",
                },
                "industry": {
                    "type": "string",
                    "description": "所属行业，如：消费电子、工业设备、家居家电",
                },
                "application_scenarios": {
                    "type": "string",
                    "description": "产品的主要应用场景，如：家庭娱乐、工厂自动化、智慧零售",
                },
                "company_size": {
                    "type": "string",
                    "description": "企业规模，如：初创(<50人)、中小企业(50-500人)、大型企业(>500人)",
                },
                "business_model": {
                    "type": "string",
                    "description": "商业模式，如：B2B、B2C、B2B2C、ODM、OEM",
                },
                "profit_model": {
                    "type": "string",
                    "description": "盈利模式，如：产品销售、订阅服务、解决方案集成、代加工费",
                },
                "channel_type": {
                    "type": "string",
                    "description": "渠道类型，如：直销、经销商/代理商、电商平台、跨境电商",
                },
                "manufacturing_capability": {
                    "type": "string",
                    "description": "加工能力描述，如：自有工厂/年产能XXX万件、纯贸易/委外代工、具备定制化能力",
                },
                "brand_capability": {
                    "type": "string",
                    "description": "品牌能力描述，如：自有品牌出海、OEM贴牌为主、正在建立品牌、已有海外注册商标",
                },
                # 参展需求
                "exhibition_goals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "参展核心目标列表，如：[\"开发新客户\",\"品牌曝光\",\"市场调研\"]",
                },
                "budget_range": {
                    "type": "string",
                    "description": "参展总预算区间，如：5-10万元、10-30万元",
                },
                "historical_experience": {
                    "type": "string",
                    "description": "历史参展经验简述",
                },
                # 推荐结果
                "recommended_exhibitions": {
                    "type": "array",
                    "description": "推荐展会列表（基于实时搜索结果，按匹配度降序排列）",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name":            {"type": "string"},
                            "date_location":   {"type": "string"},
                            "estimated_cost":  {"type": "string"},
                            "match_score":     {"type": "integer", "minimum": 1, "maximum": 5},
                            "data_sources":    {"type": "string", "description": "信息来源（官网/社交媒体/新闻稿）"},
                            "reasons":         {"type": "string"},
                        },
                        "required": ["name", "match_score", "reasons"],
                    },
                },
                "overall_verdict": {
                    "type": "string",
                    "enum": ["建议参展", "谨慎参展", "暂不建议"],
                    "description": "综合可行性结论",
                },
                "key_risks": {
                    "type": "string",
                    "description": "主要风险，用中文分号分隔",
                },
                "action_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "建议的后续行动步骤",
                },
                "match_reasoning": {
                    "type": "string",
                    "description": (
                        "基于用户9项画像对推荐展会匹配度的综合推理说明，"
                        "解释为何这些展会最适合该企业的产品、目标市场、商业模式和品牌能力"
                    ),
                },
                "consultant_notes": {
                    "type": "string",
                    "description": "顾问额外备注（可选）",
                },
            },
            "required": [
                "company_name",
                "products", "industry", "application_scenarios",
                "company_size", "business_model", "profit_model",
                "channel_type", "manufacturing_capability", "brand_capability",
                "exhibition_goals", "budget_range", "historical_experience",
                "recommended_exhibitions", "overall_verdict",
                "key_risks", "action_items", "match_reasoning",
            ],
        },
    },
]

ALL_TOOLS = BUILTIN_TOOLS + CUSTOM_TOOLS

TOOL_HANDLERS = {
    "generate_assessment_report": generate_assessment_report,
}

# ──────────────────────────────────────────────
# 系统提示词
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """你是一位资深展会参展顾问，专门帮助中国科技企业（包括品牌商、OEM/ODM外贸工厂）评估海外展会的参展可行性。

## 核心差异化能力
与市场上其他展会查询平台不同，你的数据来源是**实时**的：
- 展会主办方官方网站（最新公告、展商名录、参展规格）
- 主办方社交媒体账号（LinkedIn、Twitter/X、Facebook、Instagram）
- 参展企业新闻稿和行业媒体报道
- 展会官方博客和邮件通讯摘要

你不依赖陈旧的静态数据库，每次推荐均基于当前可检索的最新信息。

## 第一阶段：收集用户画像（9项必填）

每轮对话只提问 1-2 项，保持自然节奏。**收集完全部9项后，才进入展会搜索阶段。**

### 收集方式：按字段类型区分

---

#### 对话式收集（开放描述，用户自由作答）

以下字段差异大、无法穷举，用问句引导用户描述：

**① 产品**
> "请问贵公司主要做什么产品？（品类、核心功能、有哪些型号都可以说说）"

**② 行业**
> 根据产品自动判断，必要时追问："您这个产品主要归属哪个行业细分？比如消费电子里的音频品类，还是工业设备里的激光加工？"

**③ 应用场景**
> "这个产品主要用在哪些场景？比如家庭娱乐、商用办公、工厂自动化、户外运动……"

**⑧ 加工能力**
> "生产这边是自有工厂还是委外代工？大概年产能是多少？支持客户定制吗？"

**⑨ 品牌能力**
> "贵公司有自己的品牌吗？品牌在目标市场的知名度大概是什么水平？有没有在海外注册商标？"

---

#### 选项式收集（分类明确，给用户编号选项）

以下字段有标准分类，直接列出选项，用户回复数字即可（可多选时说明）：

**④ 企业规模**
```
请问贵公司目前的规模？
  1. 初创期（50人以下）
  2. 中小企业（50–500人）
  3. 大型企业（500人以上）
```

**⑤ 商业模式**（可多选）
```
贵公司的商业模式是？（可选多项，回复数字）
  1. B2B — 直接对企业/经销商销售
  2. B2C — 对终端消费者销售
  3. ODM — 客户提供设计，你方生产
  4. OEM — 客户提供品牌，你方代工
  5. 其他（请补充说明）
```

**⑥ 盈利模式**（可多选）
```
主要收入来源是？（可选多项）
  1. 产品销售（买断式）
  2. 代加工费（按订单收费）
  3. 订阅 / SaaS 服务费
  4. 系统集成 / 整体解决方案
  5. 其他（请补充说明）
```

**⑦ 渠道类型**（可多选）
```
目前主要通过哪些渠道销售？（可选多项）
  1. 直销（直接对接品牌商 / 采购商）
  2. 经销商 / 代理商
  3. 跨境电商（亚马逊、独立站等）
  4. 国内外电商平台（阿里巴巴国际站、京东等）
  5. 其他（请补充说明）
```

---

#### 参展需求（与画像穿插收集）

**目标市场**（选项式）
```
主要希望开拓哪些海外市场？（可多选）
  1. 北美（美国、加拿大）
  2. 欧洲（西欧 / 东欧）
  3. 东南亚
  4. 中东 / 非洲
  5. 日韩 / 澳新
  6. 其他
```

**参展目标**（选项式，可多选）
```
这次参展最希望达成什么？（可多选）
  1. 开发新客户 / 经销商
  2. 品牌曝光与形象建立
  3. 维护现有客户关系
  4. 市场调研 / 竞品分析
  5. 寻找合作伙伴或代理商
  6. 其他
```

**预算**（对话式）
> "参展总预算大概是多少？包括展位费、布展、差旅和样品运输。"

**历史经验**（对话式）
> "之前有参加过海外展会吗？如果有，是哪个展、效果怎么样？"

---

**收集原则**：
- 每次只提 1–2 个问题，不要一次性列出所有字段
- 选项题后若用户选了"其他"，立即追问具体内容
- 对话题若答案模糊，用具体追问澄清（如"您说的直销是指直接飞去见客户，还是有驻外业务员？"）
- 9项画像 + 参展需求全部收齐后，告知用户"信息已收集完毕，正在为您搜索匹配展会"，再进入第二阶段

## 第二阶段：实时展会搜索与数据采集

收集完整用户画像后，执行多轮精准搜索，重点定向实时信源：

### 搜索策略

**第1轮：定位候选展会**
- 搜索词：`[行业关键词] trade show [目标市场] 2025 2026 site:linkedin.com OR site:twitter.com OR site:facebook.com`
- 搜索词：`[行业关键词] exhibition [目标市场] 2025 official announcement`
- 搜索词：`[产品类别] expo [目标市场] exhibitor news press release`

**第2轮：核实展会实时信息**
- 针对每个候选展会，搜索其官方网站获取：最新日期、地点、展位费、展商规模
- 搜索主办方社交媒体（LinkedIn公司主页、官方Twitter）获取最新动态
- 搜索格式：`"[展会名称]" 2025 2026 exhibitor booth fee registration official`

**第3轮：竞争格局与参展企业分析**
- 搜索同类中国企业在该展会的参展情况（验证行业匹配度）
- 搜索格式：`"[展会名称]" Chinese exhibitor [产品类别] 参展`

**第4轮：ROI参考数据（可选，预算充足时）**
- 搜索该展会往届参展商评价和效果反馈
- 搜索格式：`"[展会名称]" exhibitor review ROI leads generated`

### 数据质量要求
- 优先采用来自官方网站（`.org`、官方域名）和主办方社交媒体的信息
- 标注每条关键信息的来源（官网/LinkedIn/Twitter/新闻稿）
- 如果搜索结果中有日期，记录信息的发布时间，优先采用最新信息
- 对无法实时确认的信息，明确标注"待向主办方确认"

## 第三阶段：匹配度分析与报告生成

### 基于用户画像的匹配度评分（1-5星）

综合以下维度对每个展会评分：

| 维度 | 评分依据 |
|------|---------|
| 产品/行业匹配 | 展会主要行业与用户产品的重叠程度 |
| 应用场景匹配 | 展会买家需求与产品应用场景的契合度 |
| 商业模式匹配 | B2B/ODM展会 vs 消费者展会；OEM工厂适合采购展而非消费品展 |
| 渠道匹配 | 展会专业观众类型（批发商/零售商/系统集成商）与用户渠道策略 |
| 品牌能力适配 | 纯代工厂在品牌展会的回报率通常低于自有品牌企业 |
| 预算可行性 | 综合展位费+布展+差旅是否在预算范围内 |
| 目标市场精准度 | 展会地理位置与目标出海市场的匹配 |

**评分标准**：
- ⭐⭐⭐⭐⭐ (5星)：7项维度高度匹配，强烈推荐
- ⭐⭐⭐⭐ (4星)：5-6项匹配，有明显优势
- ⭐⭐⭐ (3星)：3-4项匹配，有一定风险需针对性解决
- ⭐⭐ (2星)：仅2项匹配，不推荐
- ⭐ (1星)：基本不匹配

### 整体结论
- **建议参展**：综合匹配度≥4星，预算可行，ROI预期良好
- **谨慎参展**：综合匹配度3星，或有某项明显短板需解决
- **暂不建议**：匹配度≤2星，或预算严重不足，或时机不成熟

完成分析后调用 `generate_assessment_report` 工具生成正式报告。

## 沟通原则
- 用简洁专业的中文，避免过度堆砌术语
- 对没有海外参展经验的企业，主动解释流程和注意事项
- 诚实告知风险，不过度推销参展
- 明确区分"已通过实时搜索确认"与"需进一步向主办方确认"的信息
- 9项画像未全部收集前，不提前给出展会推荐

## 开场白
用1-2句话介绍自己的独特价值（实时数据优势），然后问第一个问题（公司主要产品）。不要一次性列出所有需要填写的信息。"""


# ──────────────────────────────────────────────
# 智能体核心
# ──────────────────────────────────────────────

class ExhibitionAgent:
    def __init__(self, model: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = model
        self.messages: list[dict] = []
        self.last_report: dict | None = None  # 供 Streamlit 读取最新生成的报告

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
        try:
            result = handler(**tool_input)
            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def chat(self, user_message: str, on_token=None) -> str:
        """发送消息，处理工具调用循环，返回最终回复文本。

        on_token: 可选回调函数 (text: str) -> None，用于 Streamlit 流式展示。
                  为 None 时退回 CLI 模式（直接 print）。
        """
        self.messages.append({"role": "user", "content": user_message})

        system = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        while True:
            full_text = ""
            tool_use_blocks: list = []
            stop_reason = ""

            with self.client.messages.stream(
                model=self.model,
                max_tokens=8096,
                system=system,
                tools=ALL_TOOLS,
                messages=self.messages,
            ) as stream:
                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and event.delta.type == "text_delta"
                    ):
                        text = event.delta.text
                        full_text += text
                        if on_token:
                            on_token(text)
                        else:
                            print(text, end="", flush=True)

                final = stream.get_final_message()
                stop_reason = final.stop_reason

                for block in final.content:
                    if block.type == "tool_use":
                        tool_use_blocks.append(block)

            # 服务端工具（web_search）达到迭代上限，继续执行
            if stop_reason == "pause_turn":
                self.messages.append({"role": "assistant", "content": final.content})
                continue

            # 无客户端工具调用 → 对话结束
            if stop_reason != "tool_use" or not tool_use_blocks:
                if not on_token:
                    print()
                self.messages.append({"role": "assistant", "content": full_text or final.content})
                return full_text

            # 执行客户端工具
            if not on_token:
                print()
            self.messages.append({"role": "assistant", "content": final.content})

            tool_results = []
            for tb in tool_use_blocks:
                if not on_token:
                    print(f"\n[生成报告中...]")
                raw = self._execute_tool(tb.name, dict(tb.input))
                result_data = json.loads(raw)

                if tb.name == "generate_assessment_report" and result_data.get("success"):
                    self.last_report = result_data  # Streamlit 通过此字段读取报告
                    if not on_token:
                        print("\n" + result_data["report_text"])
                        print(f"\n[报告已保存至：{result_data['file_path']}]")

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tb.id,
                        "content": raw,
                    }
                )

            self.messages.append({"role": "user", "content": tool_results})

    def reset(self):
        self.messages.clear()
        self.last_report = None
        if True:  # always print in CLI context
            print("[对话已重置，开始新的咨询]")


# ──────────────────────────────────────────────
# 命令行交互入口
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  展会参展顾问 — 实时数据·智能匹配·可行性评估")
    print("  输入 /reset 重新开始 | /quit 退出")
    print("=" * 60)

    agent = ExhibitionAgent()

    print("\n顾问: ", end="", flush=True)
    agent.chat("你好，我想咨询参展的事情。")

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n感谢咨询，再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit", "退出", "再见"):
            print("感谢咨询，如有需要随时回来！再见！")
            break
        if user_input.lower() in ("/reset", "重置"):
            agent.reset()
            print("\n顾问: ", end="", flush=True)
            agent.chat("你好，我想咨询参展的事情。")
            continue

        print("\n顾问: ", end="", flush=True)
        try:
            agent.chat(user_input)
        except anthropic.AuthenticationError:
            print("\n[错误] API 密钥无效，请设置环境变量 ANTHROPIC_API_KEY")
            break
        except anthropic.RateLimitError:
            print("\n[错误] 请求频率过高，请稍后再试")
        except Exception as exc:
            print(f"\n[错误] {exc}")


if __name__ == "__main__":
    main()
