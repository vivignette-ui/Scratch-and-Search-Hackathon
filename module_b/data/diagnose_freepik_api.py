"""
Freepik API 诊断脚本
检查下载失败的具体原因
"""

import os
import requests

API_KEY = os.environ.get("FREEPIK_API_KEY", "")
BASE_URL = "https://api.freepik.com/v1"

# 测试资源：一个 Premium 3D 模型 和 一个免费图片
TEST_RESOURCES = [
    {"id": "15766", "name": "Sphere (Premium 3D)", "type": "3d"},
    {"id": "16482584", "name": "Gradient Background (Free Photo)", "type": "photo"},
]


def check_api_status():
    """检查 API Key 是否有效"""
    print("=" * 50)
    print("1. 检查 API Key 状态")
    print("=" * 50)
    
    if not API_KEY:
        print("❌ 未设置 FREEPIK_API_KEY")
        return False
    
    print(f"✓ API Key 已设置: {API_KEY[:8]}...{API_KEY[-4:]}")
    return True


def get_resource_detail(resource_id):
    """获取资源详情"""
    url = f"{BASE_URL}/resources/{resource_id}"
    headers = {"x-freepik-api-key": API_KEY}
    return requests.get(url, headers=headers)


def get_download_url(resource_id):
    """获取下载链接"""
    url = f"{BASE_URL}/resources/{resource_id}/download"
    headers = {"x-freepik-api-key": API_KEY}
    return requests.get(url, headers=headers)


def diagnose_resource(resource_id, name, resource_type):
    """诊断单个资源"""
    print(f"\n📦 测试: {name} (ID: {resource_id})")
    print("-" * 40)
    
    # 1. 获取资源详情
    print("  [1] 获取资源详情...")
    detail_resp = get_resource_detail(resource_id)
    
    print(f"      状态码: {detail_resp.status_code}")
    
    if detail_resp.status_code == 200:
        data = detail_resp.json().get("data", {})
        is_premium = data.get("premium", False)
        print(f"      资源名: {data.get('name', 'N/A')}")
        print(f"      类型: {data.get('type', 'N/A')}")
        print(f"      Premium: {'是 💰' if is_premium else '否 ✓免费'}")
    else:
        print(f"      错误: {detail_resp.text}")
        return
    
    # 2. 尝试下载
    print("  [2] 尝试获取下载链接...")
    download_resp = get_download_url(resource_id)
    
    print(f"      状态码: {download_resp.status_code}")
    
    if download_resp.status_code == 200:
        download_data = download_resp.json().get("data", {})
        print(f"      ✅ 可以下载!")
        print(f"      文件名: {download_data.get('filename', 'N/A')}")
    else:
        print(f"      ❌ 下载失败")
        print(f"      响应: {download_resp.text}")
        
        # 解析错误原因
        try:
            error_data = download_resp.json()
            if "message" in error_data:
                msg = error_data["message"].lower()
                if "premium" in msg or "subscription" in msg:
                    print("      📌 原因: 需要 Premium 订阅")
                elif "not found" in msg:
                    print("      📌 原因: 资源不存在")
                elif "unauthorized" in msg or "401" in str(download_resp.status_code):
                    print("      📌 原因: API Key 无效或权限不足")
                elif "rate" in msg or "limit" in msg:
                    print("      📌 原因: 超出 API 频率限制")
                else:
                    print(f"      📌 原因: {error_data.get('message', '未知')}")
        except:
            pass


def main():
    print("\n" + "=" * 50)
    print("   Freepik API 诊断工具")
    print("=" * 50)
    
    if not check_api_status():
        print("\n请先设置 API Key:")
        print("  export FREEPIK_API_KEY='your_key'")
        return
    
    print("\n" + "=" * 50)
    print("2. 测试资源访问")
    print("=" * 50)
    
    for resource in TEST_RESOURCES:
        diagnose_resource(resource["id"], resource["name"], resource["type"])
    
    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)
    print("""
📋 常见错误解读:

| 状态码 | 含义 |
|--------|------|
| 200    | 成功 |
| 401    | API Key 无效 |
| 403    | 无权限（需要 Premium） |
| 404    | 资源不存在 |
| 429    | 频率限制 |

如果 Premium 资源返回 403/401，说明你的 API 没有下载付费资源的权限。
""")


if __name__ == "__main__":
    main()
