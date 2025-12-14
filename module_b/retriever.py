"""
Asset Retriever for Sketch & Search
封装 Qdrant 搜索逻辑，供其他模块直接调用

返回结果包含：
- preview_url: 在线预览图 URL
- local_preview: 本地预览图路径
"""
import os
from pathlib import Path
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class AssetRetriever:
    """
    3D 资产检索器
    
    Usage:
        from module_b import AssetRetriever
        
        retriever = AssetRetriever()
        results = retriever.search("metallic sphere on dark background")
        
        for asset in results:
            print(asset['local_preview'])  # 本地图片路径
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 collection_name: str = "assets",
                 previews_dir: str = None):
        """
        初始化检索器
        
        Args:
            host: Qdrant 服务地址
            port: Qdrant 服务端口
            collection_name: 向量集合名称
            previews_dir: 预览图目录路径
        """
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = collection_name
        
        # 预览图目录（默认相对于当前文件）
        if previews_dir:
            self.previews_dir = Path(previews_dir)
        else:
            self.previews_dir = Path(__file__).parent / "data" / "assets" / "previews"
    
    def _get_local_preview(self, asset_id: str, asset_name: str) -> str:
        """获取本地预览图路径"""
        # 文件名格式: asset_001_sphere.png
        filename = f"{asset_id}_{asset_name.lower().replace(' ', '_')}.png"
        filepath = self.previews_dir / filename
        
        if filepath.exists():
            return str(filepath)
        return ""
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        搜索匹配的 3D 资产
        
        Args:
            query: 镜头描述，如 "metallic sphere on dark background"
            top_k: 返回结果数量
        
        Returns:
            匹配的资产列表，包含 local_preview 路径
        """
        # 将查询文本转换为向量
        query_vector = self.model.encode(query).tolist()
        
        # 在 Qdrant 中搜索
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        # 格式化输出
        matched_assets = []
        for result in results.points:
            asset_id = result.payload.get("id", "")
            asset_name = result.payload.get("name", "")
            
            asset = {
                "id": asset_id,
                "name": asset_name,
                "description": result.payload.get("description"),
                "category": result.payload.get("category"),
                "style": result.payload.get("style"),
                "freepik_id": result.payload.get("freepik_id"),
                "freepik_url": result.payload.get("freepik_url"),
                "preview_url": result.payload.get("preview_url", ""),
                "local_preview": self._get_local_preview(asset_id, asset_name),
                "score": round(result.score, 4)
            }
            matched_assets.append(asset)
        
        return matched_assets
    
    def search_shot(self, shot_description: str, top_k: int = 3) -> dict:
        """
        为单个镜头搜索资产（供 Module A 调用）
        """
        assets = self.search(shot_description, top_k)
        return {
            "shot_description": shot_description,
            "matched_assets": assets
        }
    
    def search_multiple_shots(self, shots: list[str], top_k: int = 3) -> list[dict]:
        """
        批量搜索多个镜头的资产
        """
        return [self.search_shot(shot, top_k) for shot in shots]


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("🔍 Asset Retriever Test")
    print("=" * 50)
    
    retriever = AssetRetriever()
    
    test_queries = [
        "shiny metallic sphere",
        "colorful gradient background",
        "glass transparent crystal",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        results = retriever.search(query, top_k=3)
        for i, asset in enumerate(results, 1):
            print(f"  {i}. {asset['name']} (score: {asset['score']})")
            if asset['local_preview']:
                print(f"     📷 本地: {asset['local_preview']}")
            else:
                print(f"     📷 在线: {asset['preview_url'][:50]}...")
    
    print("\n" + "=" * 50)
    print("✅ Retriever ready!")