# Module B: Asset Retrieval

向量检索模块 - 根据镜头描述搜索匹配的 3D 资产

## 快速开始

### 1. 安装依赖

```bash
pip install qdrant-client sentence-transformers
```

### 2. 启动 Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. 初始化数据库（只需运行一次）

```bash
cd module_b
python setup_db.py
```

---

## 如何调用

### 基本用法

```python
from module_b import AssetRetriever

retriever = AssetRetriever()

# 搜索资产
results = retriever.search("metallic sphere on dark background")
```

### 返回格式

```python
[
    {
        "id": "asset_001",
        "name": "Metallic Sphere",
        "description": "A shiny metallic silver sphere with reflections",
        "category": "shape",
        "style": "modern",
        "freepik_url": "https://...",
        "score": 0.8234  # 相似度分数
    },
    ...
]
```

---

## API 参考

### `AssetRetriever`

```python
retriever = AssetRetriever(host="localhost", port=6333)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `host` | `"localhost"` | Qdrant 地址 |
| `port` | `6333` | Qdrant 端口 |

### `search(query, top_k=5)`

搜索单个查询

```python
results = retriever.search("golden metallic texture", top_k=3)
```

### `search_shot(shot_description, top_k=3)`

为单个镜头搜索资产，返回带描述的结构

```python
result = retriever.search_shot("A rotating glass cube with light refraction")
# 返回:
# {
#     "shot_description": "A rotating glass cube...",
#     "matched_assets": [...]
# }
```

### `search_multiple_shots(shots, top_k=3)`

批量搜索多个镜头（配合 Module A）

```python
shots = [
    "golden sphere floating in space",
    "blue gradient background",
    "glass crystal with rainbow refraction"
]
results = retriever.search_multiple_shots(shots)
```

---

## 与 Module A 对接示例

```python
from module_a import ShotPlanner
from module_b import AssetRetriever

# Module A: 生成镜头计划
planner = ShotPlanner()
shot_plan = planner.generate("Create a luxury tech brand ad")
# shot_plan = ["metallic sphere rotating", "gradient background fade in", ...]

# Module B: 为每个镜头找素材
retriever = AssetRetriever()
assets_per_shot = retriever.search_multiple_shots(shot_plan)

# 传给 Module C
```

---

## 文件结构

```
module_b/
├── __init__.py              # 包入口
├── retriever.py             # 核心搜索类
├── setup_db.py              # 数据库初始化
├── generate_embeddings.py   # Embedding 生成（开发用）
├── README.md
└── data/
    ├── assets.json          # 素材元数据
    └── assets_embeddings.json  # 向量数据
```

---

## 常见问题

### Qdrant 连接失败

确保 Docker 容器在运行：

```bash
docker ps  # 查看运行中的容器
docker run -p 6333:6333 qdrant/qdrant  # 重新启动
```

### 搜索结果不准确

检查 Qdrant Dashboard 确认数据已导入：

```
http://localhost:6333/dashboard
```

### 需要更新素材

1. 修改 `data/assets.json`
2. 运行 `python generate_embeddings.py`
3. 运行 `python setup_db.py`

---

## 联系

Module B 负责人：James
