"""
测试普通接口
"""
import requests
import json

url = "http://localhost:8000/api/v1/chat/message"
data = {
    "message": "你好，请介绍一下自己",
}

print(f"发送请求到：{url}")
print(f"请求数据：{json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=120)
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"错误：{e}")
