"""
Freepik API 素材下载脚本
=========================
使用 Freepik API 批量下载 assets.json 中的 3D 素材

使用方法:
1. 设置环境变量: export FREEPIK_API_KEY="your_api_key"
2. 确保 assets.json 在同一目录
3. 运行: python download_freepik_assets.py

API 文档: https://docs.freepik.com/api-reference/resources/download-a-resource
"""

import os
import json
import time
import requests
from pathlib import Path

# ============ 配置 ============
API_KEY = os.environ.get("FREEPIK_API_KEY", "")
ASSETS_FILE = "./assets.json"
DOWNLOAD_DIR = "./assets"
DELAY_BETWEEN_DOWNLOADS = 1  # 秒，避免频率限制

# Freepik API endpoints
BASE_URL = "https://api.freepik.com/v1"


def load_assets(filepath):
    """加载 assets.json"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_resource_detail(resource_id, api_key):
    """获取资源详情"""
    url = f"{BASE_URL}/resources/{resource_id}"
    headers = {"x-freepik-api-key": api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ⚠ 获取详情失败: {response.status_code} - {response.text}")
        return None


def get_download_url(resource_id, api_key):
    """获取下载链接"""
    url = f"{BASE_URL}/resources/{resource_id}/download"
    headers = {"x-freepik-api-key": api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {})
    else:
        print(f"  ⚠ 获取下载链接失败: {response.status_code} - {response.text}")
        return None


def download_file(url, filepath):
    """下载文件到本地"""
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    else:
        print(f"  ⚠ 下载失败: {response.status_code}")
        return False


def main():
    # 检查 API Key
    if not API_KEY:
        print("❌ 错误: 未设置 FREEPIK_API_KEY 环境变量")
        print("   请运行: export FREEPIK_API_KEY='your_api_key'")
        return
    
    # 创建下载目录
    download_path = Path(DOWNLOAD_DIR)
    download_path.mkdir(parents=True, exist_ok=True)
    
    # 加载素材列表
    print("正在加载 assets.json...")
    try:
        assets = load_assets(ASSETS_FILE)
        print(f"✓ 共 {len(assets)} 个素材\n")
    except FileNotFoundError:
        print(f"❌ 找不到 {ASSETS_FILE}")
        return
    
    # 统计
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    # 遍历下载
    for i, asset in enumerate(assets, 1):
        asset_id = asset.get("id", f"unknown_{i}")
        name = asset.get("name", "Unknown")
        freepik_id = asset.get("freepik_id")
        
        print(f"[{i}/{len(assets)}] {name}")
        
        # 检查 freepik_id
        if not freepik_id:
            print("  ⚠ 无 freepik_id，跳过")
            skipped_count += 1
            continue
        
        # 检查是否已下载
        # 由于不知道文件扩展名，先获取下载信息
        
        try:
            # 1. 获取下载链接
            print(f"  → 获取下载链接 (ID: {freepik_id})...")
            download_info = get_download_url(freepik_id, API_KEY)
            
            if not download_info:
                fail_count += 1
                continue
            
            download_url = download_info.get("url")
            filename = download_info.get("filename", f"{asset_id}.zip")
            
            if not download_url:
                print("  ⚠ 无下载链接")
                fail_count += 1
                continue
            
            # 2. 构建本地文件路径
            local_filepath = download_path / f"{asset_id}_{filename}"
            
            # 检查是否已存在
            if local_filepath.exists():
                print(f"  ✓ 已存在: {local_filepath.name}")
                skipped_count += 1
                continue
            
            # 3. 下载文件
            print(f"  → 下载中: {filename}...")
            if download_file(download_url, local_filepath):
                print(f"  ✓ 已保存: {local_filepath.name}")
                success_count += 1
            else:
                fail_count += 1
            
            # 延迟，避免频率限制
            time.sleep(DELAY_BETWEEN_DOWNLOADS)
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            fail_count += 1
    
    # 汇总
    print("\n" + "=" * 50)
    print("下载完成!")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ⚠ 跳过: {skipped_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📁 保存目录: {download_path.absolute()}")


if __name__ == "__main__":
    main()
