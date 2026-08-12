"""Unit tests for DotNetWebFormsStrategy."""

from src.domain.frameworks.dotnet_webforms import DotNetWebFormsStrategy


def test_supports_file_extensions() -> None:
    """Test supports_file for WebForms file extensions."""
    strategy = DotNetWebFormsStrategy()
    assert strategy.supports_file("Default.aspx") is True
    assert strategy.supports_file("UserControl.ascx") is True
    assert strategy.supports_file("Site.Master") is True
    assert strategy.supports_file("default.ASPX") is True
    assert strategy.supports_file("script.js") is False
    assert strategy.supports_file("index.html") is False


def test_supports_file_content_probe() -> None:
    """Test supports_file using content probe for non-standard file extensions."""
    strategy = DotNetWebFormsStrategy()
    assert (
        strategy.supports_file(
            "template.html", content_probe='<asp:TextBox runat="server">'
        )
        is True
    )
    assert (
        strategy.supports_file("view.tpl", content_probe="Hello <%: User.Name %>")
        is True
    )
    assert strategy.supports_file("view.tpl", content_probe="<h1>Title</h1>") is False


def test_analyze_semantics_server_controls_and_handlers() -> None:
    """Test analyzing ASP.NET WebForms server controls and event handlers."""
    strategy = DotNetWebFormsStrategy()
    content = (
        '<%@ Page Language="C#" CodeBehind="Default.aspx.cs" %>\n'
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<body>\n"
        '    <asp:TextBox ID="txtName" runat="server"'
        ' OnTextChanged="txtName_TextChanged" Text="Hello"></asp:TextBox>\n'
        '    <asp:Button ID="btnSubmit" runat="server"'
        ' OnClick="btnSubmit_Click" Text="Submit" />\n'
        "</body>\n"
        "</html>"
    )

    result = strategy.analyze_semantics("Default.aspx", content)

    assert result.framework_name == "dotnet_webforms"
    assert len(result.server_controls) == 2

    ctrl1 = result.server_controls[0]
    assert ctrl1.control_id == "txtName"
    assert ctrl1.control_type == "asp:TextBox"
    assert ctrl1.runat_server is True

    ctrl2 = result.server_controls[1]
    assert ctrl2.control_id == "btnSubmit"
    assert ctrl2.control_type == "asp:Button"

    assert len(result.event_handlers) == 2
    handler1 = result.event_handlers[0]
    assert handler1.control_id == "txtName"
    assert handler1.event_name == "OnTextChanged"
    assert handler1.handler_name == "txtName_TextChanged"

    handler2 = result.event_handlers[1]
    assert handler2.control_id == "btnSubmit"
    assert handler2.event_name == "OnClick"
    assert handler2.handler_name == "btnSubmit_Click"


def test_analyze_semantics_output_expressions() -> None:
    """Test analyzing <%: %> encoded vs <%= %> raw output expressions."""
    strategy = DotNetWebFormsStrategy()
    content = """<div>
    <p>Safe: <%: UserInput %></p>
    <p>Unsafe: <%= RawBio %></p>
    <p>Encoded Raw: <%= Server.HtmlEncode(RawBio) %></p>
</div>"""

    result = strategy.analyze_semantics("Profile.aspx", content)

    assert len(result.output_expressions) == 3

    expr1 = result.output_expressions[0]
    assert expr1.expression_type == "encoded"
    assert expr1.expression == "UserInput"
    assert expr1.is_sanitized is True

    expr2 = result.output_expressions[1]
    assert expr2.expression_type == "raw"
    assert expr2.expression == "RawBio"
    assert expr2.is_sanitized is False

    expr3 = result.output_expressions[2]
    assert expr3.expression_type == "raw"
    assert expr3.expression == "Server.HtmlEncode(RawBio)"
    assert expr3.is_sanitized is True

    assert len(result.sanitized_expressions) == 2
    assert "UserInput" in result.sanitized_expressions
    assert "Server.HtmlEncode(RawBio)" in result.sanitized_expressions


def test_is_sanitized_expression() -> None:
    """Test is_sanitized_expression for ASP.NET WebForms encoders."""
    strategy = DotNetWebFormsStrategy()

    assert strategy.is_sanitized_expression("<%: User.Name %>") is True
    assert strategy.is_sanitized_expression("Server.HtmlEncode(input)") is True
    assert strategy.is_sanitized_expression("HttpUtility.HtmlEncode(input)") is True
    assert strategy.is_sanitized_expression("AntiXss.HtmlEncode(input)") is True
    assert strategy.is_sanitized_expression("raw_user_input") is False
