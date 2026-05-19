"""
Streamlit Web UI — 展会参展顾问
留资门槛 → 智能对话 → 报告生成 → 微信转化
"""

import csv
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from agent import ExhibitionAgent

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="展会参展顾问 · 免费评估",
    page_icon="🌐",
    layout="centered",
)

# 简单样式：隐藏 Streamlit 默认菜单和 footer
st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; max-width: 760px;}
    .stChatMessage {border-radius: 12px;}
    .lead-box {
        background: #f0f7ff;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        border: 1px solid #c9e0ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CONSULTANT_WECHAT = os.environ.get("CONSULTANT_WECHAT", "请联系顾问")

# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def save_lead(data: dict) -> None:
    leads_dir = Path("leads")
    leads_dir.mkdir(exist_ok=True)
    leads_file = leads_dir / "leads.csv"
    fieldnames = ["timestamp", "company_name", "name", "contact", "target_markets", "products"]
    file_exists = leads_file.exists()
    with open(leads_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **data,
        })


def stream_response(agent: ExhibitionAgent, user_message: str) -> str:
    """在 Streamlit chat_message 上下文内调用，流式渲染 agent 回复。"""
    placeholder = st.empty()
    placeholder.markdown("*正在思考…*")
    tokens: list[str] = []

    def on_token(text: str) -> None:
        tokens.append(text)
        placeholder.markdown("".join(tokens) + "▌")

    response = agent.chat(user_message, on_token=on_token)
    placeholder.markdown(response or "（顾问正在整理信息，请稍候）")
    return response or ""


# ──────────────────────────────────────────────
# 页面：留资表单
# ──────────────────────────────────────────────

def show_form() -> None:
    st.markdown("## 🌐 展会参展顾问")
    st.markdown("**实时数据 · 智能匹配 · 免费评估**")
    st.caption("我们通过展会主办方官网、社交媒体和新闻稿实时获取展会信息，比传统平台更准确。")
    st.divider()

    with st.form("lead_form", border=False):
        st.markdown('<div class="lead-box">', unsafe_allow_html=True)
        st.markdown("#### 填写基本信息，开始免费评估")

        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("公司名称 *", placeholder="例：深圳某科技有限公司")
        with col2:
            name = st.text_input("您的姓名 *", placeholder="例：张总")

        contact = st.text_input(
            "微信号 / 手机号 *",
            placeholder="用于接收完整评估报告",
        )

        target_markets = st.multiselect(
            "目标出海市场 *（可多选）",
            ["北美（美国、加拿大）", "欧洲", "东南亚", "中东 / 非洲", "日韩 / 澳新", "其他"],
        )

        products = st.text_input(
            "主要产品 *",
            placeholder="例：TWS耳机、激光切割机、智能门锁",
        )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        submitted = st.form_submit_button(
            "🚀 开始免费评估",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        errors = []
        if not company_name.strip():
            errors.append("公司名称")
        if not name.strip():
            errors.append("姓名")
        if not contact.strip():
            errors.append("微信号/手机号")
        if not target_markets:
            errors.append("目标市场")
        if not products.strip():
            errors.append("主要产品")

        if errors:
            st.error(f"请填写：{'、'.join(errors)}")
            return

        lead = {
            "company_name": company_name.strip(),
            "name": name.strip(),
            "contact": contact.strip(),
            "target_markets": "、".join(target_markets),
            "products": products.strip(),
        }
        save_lead(lead)
        st.session_state.lead = lead
        st.session_state.page = "chat"
        st.rerun()


# ──────────────────────────────────────────────
# 页面：对话
# ──────────────────────────────────────────────

def show_chat() -> None:
    lead = st.session_state.lead

    # 顶部信息栏
    col_title, col_reset = st.columns([5, 1])
    with col_title:
        st.markdown("## 🌐 展会参展顾问")
        st.caption(f"👤 {lead['name']} · {lead['company_name']}")
    with col_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("重新开始", use_container_width=True):
            for key in ["agent", "messages", "report", "agent_initialized"]:
                st.session_state.pop(key, None)
            st.session_state.page = "form"
            st.rerun()

    st.divider()

    # ── 初始化 agent（仅第一次） ──
    if "agent_initialized" not in st.session_state:
        st.session_state.agent = ExhibitionAgent()
        st.session_state.messages = []
        st.session_state.report = None
        st.session_state.agent_initialized = True

        # 发送预填信息，触发顾问开场白（此消息不显示给用户）
        initial_msg = (
            f"你好，我想咨询参展服务。我的基本信息如下——"
            f"公司名称：{lead['company_name']}；姓名：{lead['name']}；"
            f"主要产品：{lead['products']}；目标出海市场：{lead['target_markets']}。"
            f"请在已知信息基础上，继续收集其他必要信息，为我提供参展评估。"
        )

        with st.chat_message("assistant", avatar="🧑‍💼"):
            response = stream_response(st.session_state.agent, initial_msg)

        st.session_state.messages.append({"role": "assistant", "content": response})

    else:
        # ── 展示历史消息 ──
        for msg in st.session_state.messages:
            avatar = "🧑‍💼" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # ── 报告展示 + 转化 CTA ──
    if st.session_state.get("report"):
        show_report_cta(st.session_state.report)

    # ── 输入框 ──
    if prompt := st.chat_input("输入您的回复…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🧑‍💼"):
            response = stream_response(st.session_state.agent, prompt)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # 检查是否生成了报告
        if st.session_state.agent.last_report:
            st.session_state.report = st.session_state.agent.last_report
            st.session_state.agent.last_report = None
            st.rerun()


# ──────────────────────────────────────────────
# 报告展示 + 微信转化钩子
# ──────────────────────────────────────────────

def show_report_cta(report_data: dict) -> None:
    st.divider()
    verdict = report_data.get("verdict", "")
    verdict_emoji = {"建议参展": "✅", "谨慎参展": "⚠️", "暂不建议": "❌"}.get(verdict, "📋")
    st.success(f"{verdict_emoji} 评估报告已生成 — **{verdict}**")

    with st.expander("📄 查看完整评估报告", expanded=True):
        st.text(report_data["report_text"])

    st.divider()
    st.markdown("#### 📱 获取专业顾问支持")
    st.markdown(
        "添加顾问微信，获取：**完整 PDF 报告** · **展位申请协助** · **参展全程跟进**"
    )

    col1, col2 = st.columns(2)
    with col1:
        wechat_val = CONSULTANT_WECHAT
        if st.button(f"📋 复制微信号：{wechat_val}", use_container_width=True, type="primary"):
            st.toast(f"微信号已复制：{wechat_val}", icon="✅")

    with col2:
        st.download_button(
            label="⬇️ 下载报告文本",
            data=report_data["report_text"],
            file_name=f"展会评估报告_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.caption(f"报告已自动保存至服务器：{report_data.get('file_path', '')}")


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

def main() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "form"

    if st.session_state.page == "form":
        show_form()
    else:
        show_chat()


main()
