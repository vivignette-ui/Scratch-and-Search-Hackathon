# Module B: Asset Retriever

3D 素材向量检索模块 - 根据镜头描述搜索匹配的 3D 资产

## 功能

- 基于语义搜索匹配 3D 素材
- 返回预览图（本地路径 + 在线 URL）
- 支持单个/批量镜头搜索

## 目录结构

```
module_b/
├── __init__.py
├── retriever.py          # 核心检索类
├── setup_db.py           # 导入数据到 Qdrant
├── generate_embeddings.py
├── data/
│   ├── assets.json       # 素材元数据
│   ├── assets_embeddings.json
│   └── assets/
│       └── previews/     # 预览图
│           ├── asset_001_sphere.png
│           └── ...
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install qdrant-client sentence-transformers
```

### 2. 启动 Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. 导入数据

```bash
python setup_db.py
```

### 4. 使用

```python
from module_b import AssetRetriever

retriever = AssetRetriever()
results = retriever.search("metallic sphere", top_k=3)

for asset in results:
    print(asset['name'])
    print(asset['local_preview'])  # 本地图片路径
    print(asset['preview_url'])    # 在线图片 URL
```

## API

### `AssetRetriever`

```python
retriever = AssetRetriever(
    host="localhost",      # Qdrant 地址
    port=6333,             # Qdrant 端口
    collection_name="assets"
)
```

### `search(query, top_k=5)`

搜索匹配的素材

```python
results = retriever.search("colorful gradient background", top_k=3)
```

**返回示例：**

```python
[
    {
        "id": "asset_001",
        "name": "Sphere",
        "description": "3D yoga ball sphere shape",
        "category": "shape",
        "style": "minimal",
        "freepik_id": "4491",
        "freepik_url": "https://www.freepik.com/3d-model/yoga-ball_4491.htm",
        "preview_url": "https://img.freepik.com/3d-models/v2/.../yoga-ball-poster-1.png",
        "local_preview": "/path/to/module_b/data/assets/previews/asset_001_sphere.png",
        "score": 0.7823
    }
]
```

### `search_shot(shot_description, top_k=3)`

为单个镜头搜索素材（供 Module A 调用）

```python
result = retriever.search_shot("product reveal with shiny sphere")
```

### `search_multiple_shots(shots, top_k=3)`

批量搜索多个镜头

```python
shots = [
    "product reveal with metallic sphere",
    "luxury showcase on dark background",
    "final shot with gradient"
]
results = retriever.search_multiple_shots(shots)
```

## 素材列表

共 21 个 3D 素材：

| ID | 名称 | 类别 | 风格 |
|----|------|------|------|
| asset_001 | Sphere | shape | minimal |
| asset_002 | Cube | shape | minimal |
| asset_003 | Torus | shape | elegant |
| asset_004 | Cone | shape | abstract |
| asset_005 | Gradient Background | background | vibrant |
| asset_006 | Pyramid | shape | classic |
| asset_007 | Cylinder | shape | decorative |
| asset_008 | Octahedron | shape | geometric |
| asset_009 | Dodecahedron | shape | geometric |
| asset_010 | Capsule | shape | product |
| asset_011 | Twisted Torus | shape | abstract |
| asset_012 | Helix | shape | playful |
| asset_013 | Wave Surface | shape | organic |
| asset_014 | Liquid Drop | shape | organic |
| asset_015 | Shattered Fragments | shape | dramatic |
| asset_016 | Pedestal | shape | product |
| asset_017 | Ring Frame | shape | minimal |
| asset_018 | Floating Cubes | shape | playful |
| asset_019 | Glass Panel | shape | modern |
| asset_020 | Abstract Ribbon | shape | elegant |
| asset_021 | Crystal | shape | luxury |

## 与其他模块集成

### Module A → Module B

```python
# Module A 生成 shot plan 后调用
from module_b import AssetRetriever

retriever = AssetRetriever()
shot_descriptions = ["metallic sphere on dark background", ...]
results = retriever.search_multiple_shots(shot_descriptions)
```

### Module B → Module C

```python
# 返回给 Module C 的数据
{
    "shot_description": "metallic sphere on dark background",
    "matched_assets": [
        {
            "id": "asset_001",
            "name": "Sphere",
            "local_preview": "/path/to/previews/asset_001_sphere.png",
            "score": 0.78
        }
    ]
}
```

## 注意事项

- 需要先启动 Qdrant 再运行 `setup_db.py`
- 预览图来自 Freepik，仅用于演示
- `local_preview` 为空时可用 `preview_url` 作为备选