"""
生成 assets embeddings 脚本
运行前先安装依赖: pip install sentence-transformers

使用方法:
1. 把 assets.json 放在同一目录下
2. 运行: python generate_embeddings.py
3. 生成 assets_embeddings.json
"""

import json
from sentence_transformers import SentenceTransformer

def load_assets(filepath):
    """读取 assets.json"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """保存 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_embedding_text(asset):
    """把素材信息组合成文字，用于生成 embedding"""
    parts = [
        asset.get('name', ''),
        asset.get('description', ''),
        ' '.join(asset.get('tags', [])),
        asset.get('category', ''),
        asset.get('style', '')
    ]
    return ' '.join(filter(None, parts))

def main():
    # 1. 加载模型
    print("正在加载 Embedding 模型...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ 模型加载完成")
    
    # 2. 读取素材
    print("\n正在读取 assets.json...")
    assets = load_assets('./assets.json')
    print(f"✓ 读取到 {len(assets)} 个素材")
    
    # 3. 生成 embedding
    print("\n正在生成 embeddings...")
    embeddings_data = []
    
    for asset in assets:
        # 组合文字
        text = generate_embedding_text(asset)
        
        # 生成 embedding
        embedding = model.encode(text)
        
        # 保存结果
        embeddings_data.append({
            "id": asset['id'],
            "name": asset['name'],
            "category": asset['category'],
            "text": text,  # 保留原文，方便调试
            "embedding": embedding.tolist()
        })
        
        print(f"  ✓ {asset['id']}: {asset['name']}")
    
    # 4. 保存结果
    output_file = './assets_embeddings.json'
    save_json(embeddings_data, output_file)
    print(f"\n✓ 已保存到 {output_file}")
    print(f"  向量维度: {len(embeddings_data[0]['embedding'])}")

if __name__ == "__main__":
    main()
