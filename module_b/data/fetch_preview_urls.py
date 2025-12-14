"""
获取 Freepik 3D 模型预览图 URL
运行此脚本会访问每个 freepik_url 并提取预览图链接
"""

import json
import re
import time
import requests
from pathlib import Path

ASSETS_FILE = "./assets.json"
OUTPUT_FILE = "./assets_with_previews.json"


def get_preview_url(freepik_url):
    """从 Freepik 页面获取预览图 URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(freepik_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # 查找预览图 URL 模式
            # 3D 模型: https://img.freepik.com/3d-models/v2/.../xxx-poster-1.png
            pattern_3d = r'https://img\.freepik\.com/3d-models/v2/[^"\']+poster-1\.png'
            # 普通图片: https://img.freepik.com/free-photo/...
            pattern_photo = r'https://img\.freepik\.com/free-photo/[^"\']+\.jpg'
            
            match_3d = re.search(pattern_3d, response.text)
            if match_3d:
                # 清理 URL（移除查询参数）
                url = match_3d.group(0).split('?')[0]
                return url
            
            match_photo = re.search(pattern_photo, response.text)
            if match_photo:
                url = match_photo.group(0).split('?')[0]
                return url
                
        return None
    except Exception as e:
        print(f"    错误: {e}")
        return None


def main():
    # 加载素材
    print("加载 assets.json...")
    with open(ASSETS_FILE, 'r', encoding='utf-8') as f:
        assets = json.load(f)
    
    print(f"共 {len(assets)} 个素材\n")
    
    # 遍历获取预览图
    for i, asset in enumerate(assets, 1):
        name = asset.get("name", "Unknown")
        freepik_url = asset.get("freepik_url", "")
        current_preview = asset.get("preview_url", "")
        
        print(f"[{i}/{len(assets)}] {name}")
        
        # 如果已有预览图，跳过
        if current_preview:
            print(f"    ✓ 已有预览图")
            continue
        
        if not freepik_url:
            print(f"    ⚠ 无 freepik_url")
            continue
        
        # 获取预览图
        print(f"    → 获取预览图...")
        preview_url = get_preview_url(freepik_url)
        
        if preview_url:
            asset["preview_url"] = preview_url
            print(f"    ✓ {preview_url[:60]}...")
        else:
            print(f"    ⚠ 未找到预览图")
        
        # 延迟避免被封
        time.sleep(1)
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 已保存到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
