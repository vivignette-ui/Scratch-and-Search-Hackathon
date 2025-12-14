"""
下载 Freepik 3D 模型预览图
预览图是公开的，不需要 API Key
"""

import os
import json
import requests
from pathlib import Path

ASSETS_FILE = "./assets.json"
DOWNLOAD_DIR = "./assets/previews"


def download_preview(url, filepath):
    """下载预览图"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"    ⚠ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"    ⚠ 错误: {e}")
        return False


def main():
    # 创建下载目录
    download_path = Path(DOWNLOAD_DIR)
    download_path.mkdir(parents=True, exist_ok=True)
    
    # 加载素材列表
    print("正在加载 assets.json...")
    try:
        with open(ASSETS_FILE, 'r', encoding='utf-8') as f:
            assets = json.load(f)
        print(f"✓ 共 {len(assets)} 个素材\n")
    except FileNotFoundError:
        print(f"❌ 找不到 {ASSETS_FILE}")
        return
    
    success = 0
    failed = 0
    skipped = 0
    
    for i, asset in enumerate(assets, 1):
        asset_id = asset.get("id", f"unknown_{i}")
        name = asset.get("name", "Unknown")
        preview_url = asset.get("preview_url")
        
        print(f"[{i}/{len(assets)}] {name}")
        
        if not preview_url:
            print("    ⚠ 无 preview_url，跳过")
            skipped += 1
            continue
        
        # 确定文件名
        filename = f"{asset_id}_{name.lower().replace(' ', '_')}.png"
        filepath = download_path / filename
        
        # 检查是否已存在
        if filepath.exists():
            print(f"    ✓ 已存在: {filename}")
            skipped += 1
            continue
        
        # 下载
        print(f"    → 下载中...")
        if download_preview(preview_url, filepath):
            print(f"    ✓ 已保存: {filename}")
            success += 1
        else:
            failed += 1
    
    # 汇总
    print("\n" + "=" * 50)
    print("下载完成!")
    print(f"  ✓ 成功: {success}")
    print(f"  ⚠ 跳过: {skipped}")
    print(f"  ❌ 失败: {failed}")
    print(f"  📁 保存目录: {download_path.absolute()}")


if __name__ == "__main__":
    main()
