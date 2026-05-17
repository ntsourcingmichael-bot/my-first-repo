"""不需要 API 密钥的本地单元测试。"""

import json
from agent import get_weather, calculate, get_current_time, TOOLS, TOOL_HANDLERS


def test_tools():
    # 天气
    result = get_weather("北京")
    assert result["temperature"] == 25
    assert result["condition"] == "晴朗"
    print("✓ get_weather (celsius)")

    result_f = get_weather("北京", unit="fahrenheit")
    assert result_f["unit"] == "fahrenheit"
    assert result_f["temperature"] == 77.0
    print("✓ get_weather (fahrenheit)")

    err = get_weather("不存在的城市")
    assert "error" in err
    print("✓ get_weather (missing city)")

    # 计算
    result = calculate("2 + 3 * 4")
    assert result["result"] == 14
    print("✓ calculate (basic)")

    result = calculate("sqrt(144)")
    assert result["result"] == 12.0
    print("✓ calculate (sqrt)")

    result = calculate("2^10")
    assert result["result"] == 1024
    print("✓ calculate (power)")

    err = calculate("__import__('os')")
    assert "error" in err
    print("✓ calculate (injection blocked)")

    # 时间
    result = get_current_time()
    assert "datetime" in result
    assert "weekday" in result
    print("✓ get_current_time")

    # 工具定义完整性
    tool_names = {t["name"] for t in TOOLS}
    handler_names = set(TOOL_HANDLERS.keys())
    assert tool_names == handler_names, f"工具定义与处理函数不匹配: {tool_names ^ handler_names}"
    print("✓ TOOLS / TOOL_HANDLERS 一致性")


if __name__ == "__main__":
    print("运行本地测试...\n")
    test_tools()
    print("\n所有测试通过 ✓")
