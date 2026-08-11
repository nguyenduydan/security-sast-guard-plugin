from src.mcp.schemas import TOOLS_SCHEMAS


def test_dataflow_path_tool_registered():
    names = [t["name"] for t in TOOLS_SCHEMAS]
    assert "sast_get_dataflow_path" in names


def test_taint_context_tool_registered():
    names = [t["name"] for t in TOOLS_SCHEMAS]
    assert "sast_get_taint_context" in names
