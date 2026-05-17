"""
智能体 (Intelligent Agent)
使用 Claude API 构建的通用对话助手，支持工具调用和提示词缓存。
"""

import anthropic
import json
import math
import os
from datetime import datetime
from typing import Any

# ──────────────────────────────────────────────
# 工具实现
# ──────────────────────────────────────────────

def get_weather(location: str, unit: str = "celsius") -> dict:
    """模拟天气查询（实际使用时替换为真实 API）。"""
    weather_db = {
        "北京":    {"temp": 25, "condition": "晴朗", "humidity": 40},
        "上海":    {"temp": 28, "condition": "多云", "humidity": 65},
        "广州":    {"temp": 32, "condition": "雷阵雨", "humidity": 80},
        "成都":    {"temp": 22, "condition": "阴天", "humidity": 70},
        "beijing": {"temp": 25, "condition": "Sunny", "humidity": 40},
        "shanghai":{"temp": 28, "condition": "Cloudy", "humidity": 65},
    }
    key = location.lower()
    data = weather_db.get(key) or weather_db.get(location)
    if not data:
        return {"error": f"未找到 {location} 的天气数据"}
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32, 1)
    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"],
    }


def calculate(expression: str) -> dict:
    """安全地计算数学表达式。"""
    allowed = set("0123456789+-*/()., %sqrtpilogabsce ")
    clean = expression.replace("^", "**")
    if not all(c in allowed for c in clean.lower()):
        return {"error": "表达式包含不允许的字符"}
    try:
        safe_names = {
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "log": math.log, "abs": abs, "sin": math.sin,
            "cos": math.cos, "tan": math.tan,
        }
        result = eval(clean, {"__builtins__": {}}, safe_names)  # noqa: S307
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"error": str(exc)}


def get_current_time(timezone: str = "Asia/Shanghai") -> dict:
    """获取当前时间。"""
    now = datetime.now()
    return {
        "timezone": timezone,
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y年%m月%d日"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()],
    }


# ──────────────────────────────────────────────
# 工具定义（发送给 Claude 的 JSON Schema）
# ──────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "get_weather",
        "description": "获取指定城市的当前天气信息，包括温度、天气状况和湿度。",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海、广州",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位，默认 celsius（摄氏度）",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "calculate",
        "description": "计算数学表达式，支持加减乘除、幂运算(^)、sqrt、sin、cos、tan、log、pi、e 等。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如：2^10、sqrt(144)、sin(pi/2)",
                },
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_current_time",
        "description": "获取当前日期和时间。",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区，例如：Asia/Shanghai（默认）",
                },
            },
            "required": [],
        },
    },
]

# 工具名称 → 函数的映射
TOOL_HANDLERS: dict[str, Any] = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
}

# ──────────────────────────────────────────────
# 系统提示词（会被缓存以节省成本）
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """你是一个智能助手，能够回答问题、进行多轮对话，并通过工具获取实时信息。

## 你的能力
- 回答各类知识性问题
- 进行自然、流畅的多轮对话，记住对话历史
- 通过工具查询天气、进行数学计算、获取当前时间
- 用中文或英文回复（跟随用户语言）

## 工具使用原则
- 只在真正需要时才调用工具（比如用户明确询问天气、时间、数学计算）
- 调用工具后，用友好的自然语言整合结果向用户说明
- 若工具返回错误，诚实告知用户并提供替代建议

## 回复风格
- 简洁清晰，避免冗余
- 友好自然，像朋友交谈
- 复杂问题分步骤解释"""


# ──────────────────────────────────────────────
# 智能体核心
# ──────────────────────────────────────────────

class Agent:
    def __init__(self, model: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = model
        self.messages: list[dict] = []

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
        result = handler(**tool_input)
        return json.dumps(result, ensure_ascii=False)

    def chat(self, user_message: str) -> str:
        """发送消息并获取回复（带流式输出和工具调用循环）。"""
        self.messages.append({"role": "user", "content": user_message})

        while True:
            # 系统提示词缓存：将稳定的 system prompt 标记为可缓存
            system = [
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

            print("\n助手: ", end="", flush=True)
            full_text = ""
            tool_use_blocks: list[dict] = []
            stop_reason = ""

            # 流式调用 API
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system,
                tools=TOOLS,
                messages=self.messages,
            ) as stream:
                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and event.delta.type == "text_delta"
                    ):
                        print(event.delta.text, end="", flush=True)
                        full_text += event.delta.text

                final = stream.get_final_message()
                stop_reason = final.stop_reason

                # 收集 tool_use 块
                for block in final.content:
                    if block.type == "tool_use":
                        tool_use_blocks.append(block)

            print()  # 换行

            # 无工具调用 → 对话结束
            if stop_reason != "tool_use":
                self.messages.append({"role": "assistant", "content": full_text})
                return full_text

            # 有工具调用：执行工具并将结果反馈给模型
            # 先将助手回复（含 tool_use 块）追加到历史
            self.messages.append(
                {"role": "assistant", "content": final.content}
            )

            tool_results = []
            for tool_block in tool_use_blocks:
                print(f"\n[调用工具: {tool_block.name}({tool_block.input})]")
                result = self._execute_tool(tool_block.name, dict(tool_block.input))
                print(f"[工具结果: {result}]")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result,
                    }
                )

            # 将工具结果作为 user 消息追加，继续循环
            self.messages.append({"role": "user", "content": tool_results})

    def reset(self):
        """清空对话历史。"""
        self.messages.clear()
        print("[对话已重置]")


# ──────────────────────────────────────────────
# 命令行交互入口
# ──────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Claude 智能体  (输入 /reset 重置, /quit 退出)")
    print("=" * 50)

    agent = Agent()

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit", "退出"):
            print("再见！")
            break
        if user_input.lower() in ("/reset", "重置"):
            agent.reset()
            continue

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
