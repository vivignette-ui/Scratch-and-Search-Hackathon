"""
将 assets 数据导入 Qdrant
包含 preview_url 字段
"""
import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# 配置
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "assets"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 的向量维度

ASSETS_FILE = "./data/assets.json"
EMBEDDINGS_FILE = "./data/assets_embeddings.json"


def main():
    # 连接 Qdrant
    print("连接 Qdrant...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 加载数据
    print("加载数据...")
    with open(ASSETS_FILE, 'r', encoding='utf-8') as f:
        assets = json.load(f)
    
    with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
        embeddings_data = json.load(f)
    
    # 创建 embedding 字典 (id -> embedding)
    embeddings_dict = {item['id']: item['embedding'] for item in embeddings_data}
    
    # 重新创建 collection
    print(f"创建 collection: {COLLECTION_NAME}")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    
    # 准备数据点
    points = []
    for i, asset in enumerate(assets):
        asset_id = asset['id']
        embedding = embeddings_dict.get(asset_id)
        
        if not embedding:
            print(f"  ⚠ 跳过 {asset_id}: 无 embedding")
            continue
        
        # payload 包含所有字段，包括 preview_url
        payload = {
            "id": asset.get("id"),
            "name": asset.get("name"),
            "description": asset.get("description"),
            "tags": asset.get("tags", []),
            "category": asset.get("category"),
            "style": asset.get("style"),
            "freepik_id": asset.get("freepik_id"),
            "freepik_url": asset.get("freepik_url"),
            "preview_url": asset.get("preview_url", "")  # 新增
        }
        
        point = PointStruct(
            id=i,
            vector=embedding,
            payload=payload
        )
        points.append(point)
    
    # 写入 Qdrant
    print(f"写入 {len(points)} 条数据...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    print(f"\n✅ 完成！共导入 {len(points)} 个素材")
    print(f"   Collection: {COLLECTION_NAME}")
    
    # 验证
    info = client.get_collection(COLLECTION_NAME)
    print(f"   Points count: {info.points_count}")


if __name__ == "__main__":
    main()