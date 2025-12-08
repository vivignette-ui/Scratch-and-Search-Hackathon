"""
Setup Qdrant Database for Sketch & Search
初始化向量数据库，导入资产和 embeddings

Usage:
    python -m module_b.setup_db
"""
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import json

# 配置
COLLECTION_NAME = "assets"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 的向量维度
DATA_DIR = Path(__file__).parent / "data"


def setup_database(host: str = "localhost", port: int = 6333):
    """
    初始化 Qdrant 数据库并导入资产数据
    """
    print("🚀 Setting up Qdrant database...")
    
    # 检查数据文件
    assets_path = DATA_DIR / "assets.json"
    embeddings_path = DATA_DIR / "assets_embeddings.json"
    
    if not assets_path.exists():
        raise FileNotFoundError(f"❌ assets.json not found at {assets_path}")
    if not embeddings_path.exists():
        raise FileNotFoundError(f"❌ assets_embeddings.json not found at {embeddings_path}")
    
    # 连接 Qdrant
    try:
        client = QdrantClient(host=host, port=port)
        client.get_collections()  # 测试连接
        print(f"✅ Connected to Qdrant at {host}:{port}")
    except Exception as e:
        raise ConnectionError(
            f"❌ Cannot connect to Qdrant at {host}:{port}\n"
            f"   请确保 Qdrant 正在运行: docker run -p 6333:6333 qdrant/qdrant"
        ) from e
    
    # 加载数据
    with open(assets_path, "r", encoding="utf-8") as f:
        assets = json.load(f)
    print(f"📦 Loaded {len(assets)} assets")
    
    with open(embeddings_path, "r", encoding="utf-8") as f:
        embeddings_data = json.load(f)
    
    # 创建 embedding 查找字典
    embeddings_dict = {item["id"]: item["embedding"] for item in embeddings_data}
    print(f"🔢 Loaded {len(embeddings_dict)} embeddings")
    
    # 创建 collection
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"📁 Created collection '{COLLECTION_NAME}'")
    
    # 准备数据点
    points = []
    missing = []
    for i, asset in enumerate(assets):
        asset_id = asset["id"]
        if asset_id in embeddings_dict:
            point = PointStruct(
                id=i,
                vector=embeddings_dict[asset_id],
                payload=asset
            )
            points.append(point)
        else:
            missing.append(asset_id)
    
    if missing:
        print(f"⚠️  Warning: Missing embeddings for {len(missing)} assets: {missing}")
    
    # 批量导入
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    print(f"\n{'=' * 50}")
    print(f"✅ Successfully imported {len(points)} assets to Qdrant")
    print(f"📊 Collection: '{COLLECTION_NAME}'")
    print(f"🌐 Dashboard: http://{host}:{port}/dashboard")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    setup_database()
