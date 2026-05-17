"""不需要 API 密钥的本地单元测试。"""

import json
import os
import sys
from pathlib import Path
from agent import generate_assessment_report, ALL_TOOLS, CUSTOM_TOOLS, BUILTIN_TOOLS, TOOL_HANDLERS


def test_tool_schema_consistency():
    """验证工具定义与处理函数的一致性。"""
    custom_tool_names = {t["name"] for t in CUSTOM_TOOLS}
    handler_names = set(TOOL_HANDLERS.keys())
    assert custom_tool_names == handler_names, (
        f"自定义工具定义与处理函数不匹配: {custom_tool_names ^ handler_names}"
    )
    print("✓ CUSTOM_TOOLS / TOOL_HANDLERS 一致性")

    # 内置工具不应出现在 TOOL_HANDLERS 中
    builtin_names = {t["name"] for t in BUILTIN_TOOLS}
    overlap = builtin_names & handler_names
    assert not overlap, f"内置工具不应有客户端处理函数: {overlap}"
    print("✓ BUILTIN_TOOLS 无客户端处理函数")

    # ALL_TOOLS 包含所有工具
    all_tool_names = {t["name"] for t in ALL_TOOLS}
    assert "web_search" in all_tool_names, "ALL_TOOLS 缺少 web_search"
    assert "generate_assessment_report" in all_tool_names, "ALL_TOOLS 缺少 generate_assessment_report"
    print("✓ ALL_TOOLS 完整性")


def test_required_schema_fields():
    """验证 generate_assessment_report 工具包含所有9项画像字段。"""
    tool = next(t for t in CUSTOM_TOOLS if t["name"] == "generate_assessment_report")
    required = set(tool["input_schema"]["required"])
    profile_fields = {
        "products", "industry", "application_scenarios",
        "company_size", "business_model", "profit_model",
        "channel_type", "manufacturing_capability", "brand_capability",
    }
    missing = profile_fields - required
    assert not missing, f"工具 schema 缺少用户画像字段: {missing}"
    print("✓ 9项用户画像字段均在 required 列表中")

    assert "match_reasoning" in required, "工具 schema 缺少 match_reasoning 字段"
    print("✓ match_reasoning 字段存在")


def test_generate_assessment_report():
    """验证报告生成函数的基本功能（写入临时目录）。"""
    import tempfile
    import unittest.mock as mock

    sample_exhibitions = [
        {
            "name": "CES 2026",
            "date_location": "2026年1月7-10日，拉斯维加斯",
            "estimated_cost": "15-25万元（含展位+布展+差旅）",
            "match_score": 5,
            "data_sources": "CES官网 ces.tech + LinkedIn官方账号",
            "reasons": "消费电子行业顶级展会，北美市场精准覆盖，买家质量高",
        },
        {
            "name": "IFA 2025",
            "date_location": "2025年9月5-9日，柏林",
            "estimated_cost": "12-20万元",
            "match_score": 4,
            "data_sources": "IFA官网 + Twitter @IFA_Berlin",
            "reasons": "欧洲最大消费电子展，德国辐射整个欧盟市场",
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch("agent.Path") as mock_path_cls:
            mock_reports_dir = mock.MagicMock()
            mock_path_cls.return_value = mock_reports_dir
            mock_reports_dir.__truediv__ = lambda self, other: Path(tmpdir) / other
            mock_reports_dir.mkdir = mock.MagicMock()

            real_path = Path(tmpdir) / "test_report.txt"
            with mock.patch("agent.Path", side_effect=lambda x: Path(tmpdir) if x == "reports" else Path(x)):
                result = generate_assessment_report(
                    company_name="某消费电子科技公司",
                    products="TWS无线耳机、智能音箱",
                    industry="消费电子",
                    application_scenarios="家庭娱乐、运动健身、居家办公",
                    company_size="中小企业（150人）",
                    business_model="B2B+自有品牌B2C",
                    profit_model="产品销售+ODM代工费",
                    channel_type="海外经销商+亚马逊跨境电商",
                    manufacturing_capability="自有工厂，年产能200万件，支持定制",
                    brand_capability="自有品牌「SoundX」，已注册美国商标",
                    exhibition_goals=["开发北美经销商", "品牌曝光", "竞品调研"],
                    budget_range="15-25万元",
                    historical_experience="参加过广交会，无海外展会经验",
                    recommended_exhibitions=sample_exhibitions,
                    overall_verdict="建议参展",
                    key_risks="首次海外参展经验不足；展位设计需专业支持；旺季机票酒店需提前预订",
                    action_items=[
                        "联系CES主办方确认2026展位申请截止时间",
                        "委托专业展台设计公司提前3个月布展设计",
                        "准备英文产品手册和演示样机",
                    ],
                    match_reasoning=(
                        "SoundX品牌自有商标+北美经销商渠道目标与CES买家结构高度吻合；"
                        "TWS耳机是CES消费电子主力品类；预算覆盖标准展位需求。"
                    ),
                    consultant_notes="建议优先参加CES，IFA作为备选方案。",
                )

    assert result["success"] is True
    assert result["verdict"] == "建议参展"
    assert "SoundX" in result["report_text"] or "某消费电子科技公司" in result["report_text"]
    assert "TWS无线耳机" in result["report_text"]
    assert "match_reasoning" not in result["report_text"]  # 字段内容应以标题形式展示
    assert "匹配度分析" in result["report_text"]
    assert "CES 2026" in result["report_text"]
    assert "★★★★★" in result["report_text"]  # 5星展示
    print("✓ generate_assessment_report 基本功能正常")
    print(f"  报告包含 {len(result['report_text'])} 字符")


def test_builtin_tool_type():
    """验证内置工具使用正确的类型声明。"""
    web_search = next(t for t in BUILTIN_TOOLS if t["name"] == "web_search")
    assert web_search["type"] == "web_search_20260209", (
        f"web_search 工具类型应为 web_search_20260209，实际为 {web_search['type']}"
    )
    print("✓ web_search 内置工具类型正确")


if __name__ == "__main__":
    print("运行本地测试...\n")
    test_tool_schema_consistency()
    test_required_schema_fields()
    test_builtin_tool_type()
    test_generate_assessment_report()
    print("\n所有测试通过 ✓")
