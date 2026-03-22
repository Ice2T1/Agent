"""
测试流式接口
"""
import requests
import json

url = "http://localhost:8000/api/v1/chat/stream"
data = {
    "message": "你好，请介绍一下自己",
}

print(f"发送请求到：{url}")
print(f"请求数据：{json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=60, stream=True)
    print(f"状态码：{response.status_code}")
    print(f"响应头：{dict(response.headers)}")
    print("\n响应内容：")
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    print(f"错误：{e}")
