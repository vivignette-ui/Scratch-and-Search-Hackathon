# Freepik API 素材下载指南

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 设置 API Key

```bash
# Linux/Mac
export FREEPIK_API_KEY="你的API密钥"

# Windows (PowerShell)
$env:FREEPIK_API_KEY="你的API密钥"

# Windows (CMD)
set FREEPIK_API_KEY=你的API密钥
```

### 3. 确保 assets.json 格式正确

你的 `assets.json` 需要包含真实的 `freepik_id`：

```json
[
  {
    "id": "asset_001",
    "name": "Sphere",
    "freepik_id": "12345678"  // ← 真实的 Freepik 资源 ID
  }
]
```

### 4. 运行下载

```bash
python download_freepik_assets.py
```

---

## 如何获取真实的 freepik_id？

1. 打开 Freepik 网站找到你想要的素材
2. 查看 URL，例如：
   - `https://www.freepik.com/3d-model/metallic-sphere_12345.htm`
   - `https://www.freepik.com/free-photo/gradient-background_16482584.htm`
3. URL 末尾的数字就是 `freepik_id`（如 `12345` 或 `16482584`）

---

## API 限制

- Freepik API 有频率限制（Rate Limit）
- 脚本默认每次下载间隔 1 秒
- 免费 API 账户可能有每日下载限制
- 查看你的 API 额度：https://www.freepik.com/developers/dashboard

---

## 文件结构

下载后的文件会保存在 `./assets/` 目录：

```
project/
├── assets.json
├── download_freepik_assets.py
└── assets/
    ├── asset_001_sphere.zip
    ├── asset_002_cube.zip
    └── ...
```

---

## 常见问题

### Q: 提示 401 Unauthorized？
A: API Key 无效或未设置，检查环境变量

### Q: 提示 404 Not Found？
A: `freepik_id` 不存在，检查是否是真实的资源 ID

### Q: 提示 429 Too Many Requests？
A: 频率限制，增加 `DELAY_BETWEEN_DOWNLOADS` 的值

### Q: 下载的是 .zip 文件？
A: Freepik 3D 素材通常打包为 zip（包含 GLTF/OBJ/FBX + 贴图）
