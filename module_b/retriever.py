"""
Asset Retriever for Sketch & Search
封装 Qdrant 搜索逻辑，供其他模块直接调用
"""
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class AssetRetriever:
    """
    3D 资产检索器
    
    Usage:
        from module_b import AssetRetriever
        
        retriever = AssetRetriever()
        results = retriever.search("metallic sphere on dark background")
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "assets"):
        """
        初始化检索器
        
        Args:
            host: Qdrant 服务地址
            port: Qdrant 服务端口
            collection_name: 向量集合名称
        """
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = collection_name
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        搜索匹配的 3D 资产
        
        Args:
            query: 镜头描述，如 "metallic sphere on dark background"
            top_k: 返回结果数量
        
        Returns:
            匹配的资产列表，按相关度排序
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
            asset = {
                "id": result.payload["id"],
                "name": result.payload["name"],
                "description": result.payload["description"],
                "category": result.payload["category"],
                "style": result.payload["style"],
                "freepik_url": result.payload["freepik_url"],
                "score": round(result.score, 4)
            }
            matched_assets.append(asset)
        
        return matched_assets
    
    def search_shot(self, shot_description: str, top_k: int = 3) -> dict:
        """
        为单个镜头搜索资产（供 Module A 调用）
        
        Args:
            shot_description: LLM 生成的镜头描述
            top_k: 每个镜头返回的资产数量
        
        Returns:
            包含镜头信息和匹配资产的字典
        """
        assets = self.search(shot_description, top_k)
        return {
            "shot_description": shot_description,
            "matched_assets": assets
        }
    
    def search_multiple_shots(self, shots: list[str], top_k: int = 3) -> list[dict]:
        """
        批量搜索多个镜头的资产
        
        Args:
            shots: 镜头描述列表
            top_k: 每个镜头返回的资产数量
        
        Returns:
            每个镜头的匹配结果列表
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
        "floating geometric shapes",
        "elegant ribbon flowing"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        results = retriever.search(query, top_k=3)
        for i, asset in enumerate(results, 1):
            print(f"  {i}. {asset['name']} (score: {asset['score']})")
            print(f"     {asset['description']}")
    
    print("\n" + "=" * 50)
    print("✅ Retriever ready!")
    print("=" * 50)
