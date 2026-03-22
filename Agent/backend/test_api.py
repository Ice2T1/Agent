"""
测试后端 API
"""
import requests
import json

# 测试健康检查
print("1. 测试健康检查...")
response = requests.get("http://localhost:8000/health")
print(f"状态码：{response.status_code}")
print(f"响应：{response.json()}")
print()

# 测试发送消息
print("2. 测试发送消息...")
data = {
    "message": "你好，请介绍一下自己",
    "thread_id": "test-123"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/chat/message",
        json=data,
        timeout=60
    )
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"错误：{e}")
