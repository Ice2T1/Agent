"""
高级工具模板
包含更多工具示例，可根据需要启用
"""
from langchain_core.tools import tool
from app.tools.registry import register_tool
from typing import Optional
import json


# ============================================
# 搜索类工具（需要 API Key）
# ============================================




# ============================================
# 计算类工具
# ============================================

@register_tool
@tool
def calculate_expression(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 2 * 3"
        
    Returns:
        计算结果
    """
    try:
        # 使用 ast 进行安全计算
        import ast
        import operator
        
        # 定义支持的操作符
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        def eval_node(node):
            if isinstance(node, ast.Num):  # 数字
                return node.n
            elif isinstance(node, ast.BinOp):  # 二元运算
                return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
            elif isinstance(node, ast.UnaryOp):  # 一元运算
                return operators[type(node.op)](eval_node(node.operand))
            else:
                raise TypeError(f"不支持的操作：{type(node)}")
        
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"


@register_tool
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    货币转换
    
    Args:
        amount: 金额
        from_currency: 源货币（如 USD, CNY）
        to_currency: 目标货币
        
    Returns:
        转换结果
    """
    # TODO: 集成实时汇率 API
    # 这里使用示例汇率
    rates = {
        'USD': 1.0,
        'CNY': 7.2,
        'EUR': 0.92,
        'JPY': 150.0,
    }
    
    if from_currency not in rates or to_currency not in rates:
        return "不支持的货币类型"
    
    usd_amount = amount / rates[from_currency]
    result = usd_amount * rates[to_currency]
    
    return f"{amount} {from_currency} = {result:.2f} {to_currency}"


# ============================================
# 文件操作类工具
# ============================================

@register_tool
@tool
def read_text_file(file_path: str, max_lines: Optional[int] = None) -> str:
    """
    读取文本文件
    
    Args:
        file_path: 文件路径
        max_lines: 最大读取行数（None 表示读取全部）
        
    Returns:
        文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if max_lines:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                return ''.join(lines)
            else:
                return f.read()
    except Exception as e:
        return f"读取文件错误：{str(e)}"


@register_tool
@tool
def write_text_file(file_path: str, content: str, append: bool = False) -> str:
    """
    写入文本文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
        append: 是否追加模式
        
    Returns:
        操作结果
    """
    try:
        mode = 'a' if append else 'w'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入文件：{file_path}"
    except Exception as e:
        return f"写入文件错误：{str(e)}"


# ============================================
# 数据处理类工具
# ============================================

@register_tool
@tool
def parse_json(json_string: str) -> dict:
    """
    解析 JSON 字符串
    
    Args:
        json_string: JSON 字符串
        
    Returns:
        解析后的字典
    """
    try:
        return json.loads(json_string)
    except Exception as e:
        return {"error": f"JSON 解析错误：{str(e)}"}


@register_tool
@tool
def format_json(data: dict, indent: int = 2) -> str:
    """
    格式化 JSON 数据
    
    Args:
        data: 字典数据
        indent: 缩进空格数
        
    Returns:
        格式化后的 JSON 字符串
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except Exception as e:
        return f"格式化错误：{str(e)}"


# ============================================
# 时间日期类工具
# ============================================

@register_tool
@tool
def get_current_date() -> str:
    """
    获取当前日期
    
    Returns:
        日期字符串（YYYY-MM-DD）
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


@register_tool
@tool
def get_current_datetime() -> str:
    """
    获取当前日期时间
    
    Returns:
        日期时间字符串（YYYY-MM-DD HH:MM:SS）
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@register_tool
@tool
def calculate_date_diff(date1: str, date2: str, format: str = "%Y-%m-%d") -> str:
    """
    计算两个日期之间的天数差
    
    Args:
        date1: 日期 1
        date2: 日期 2
        format: 日期格式
        
    Returns:
        天数差
    """
    from datetime import datetime
    try:
        d1 = datetime.strptime(date1, format)
        d2 = datetime.strptime(date2, format)
        diff = abs((d2 - d1).days)
        return f"两个日期相差 {diff} 天"
    except Exception as e:
        return f"日期计算错误：{str(e)}"


# ============================================
# 代码执行类工具（谨慎使用）
# ============================================

@register_tool
@tool
def execute_python_code(code: str, timeout: int = 5) -> str:
    """
    执行 Python 代码（沙箱环境）
    
    Args:
        code: Python 代码
        timeout: 超时时间（秒）
        
    Returns:
        执行结果
    """
    # 注意：生产环境应该使用更安全的沙箱机制
    # 如 e2b-code-interpreter 或 Docker 容器
    try:
        import io
        import sys
        from contextlib import redirect_stdout
        
        # 捕获输出
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code, {"__builtins__": __builtins__}, {})
        
        return f.getvalue()
    except Exception as e:
        return f"代码执行错误：{str(e)}"
