{
  "shots": [
    {
      "id": 1,
      "duration": 9000,
      "camera": {
        "movement": "slow-zoom-in",
        "angle": "slightly-top-down"
      },
      "elements": [
        {
          "id": "product",
          "type": "bottle",
          "motion": "yaw",
          "position": { "x": 50, "y": 52 },
          "presetPosition": "pos-bottle-center",
          "asset": null
        },
        {
          "id": "platform",
          "type": "bottle-platform",
          "parent": "product"
        },
        {
          "id": "fruitTop",
          "type": "pineapple",
          "parent": "platform",
          "motion": "float"
        },
        {
          "id": "canLoop",
          "type": "can-on-track",
          "motion": "loop-track"
        },
        {
          "id": "wheelRight",
          "type": "ferris-wheel",
          "motion": "rotate-wheel",
          "presetPosition": "pos-wheel-right"
        },
        {
          "id": "sign1",
          "type": "sign",
          "motion": "spin-slow",
          "presetPosition": "pos-sign-1"
        },
        {
          "id": "sign2",
          "type": "sign",
          "motion": "spin-slow",
          "presetPosition": "pos-sign-2"
        },
        {
          "id": "soloCan",
          "type": "solo-can",
          "motion": "rise-spin",
          "presetPosition": "pos-solo-can-left"
        },
        {
          "id": "tree1",
          "type": "tree",
          "presetPosition": "pos-tree-1"
        },
        {
          "id": "person1",
          "type": "person",
          "motion": "sway",
          "presetPosition": "pos-person-1"
        }
      ]
    }
  ]
}


# Team Pipeline

## 🎯 项目目标

输入：品牌 + 主推产品 + 风格描述  
输出：一个 6–10 秒、高质量、轻动效的 3D 短视频广告。

广告风格特征：
- 主推产品永远在画面中心，绝对主角  
- 场景为“乐园 / 小世界”风格（透明管道、水果、小球、人、树、摩天轮等元素）  
- 大部分元素静止，只有少量柔和小动（旋转、上下浮动、缓慢移动）  
- 画面干净、梦幻、具未来感  
- 当前版本不加入文字和 logo（后续可扩展）

---

## 🧩 三个模块（A / B / C）

### **A – Scene Generator（Gemini / Nano）**
根据用户输入生成**场景描述 JSON（shot plan）**，包含镜头布局、元素种类、动效建议等。

### **B – Asset Selector（Qdrant + Freepik）**
从素材库中根据 A 的描述选择最匹配的素材，并返回素材链接 / ID。

### **C – Scene Player（前端可视化播放器）**
将 A/B 的输出组合成可播放的广告动画。

---

## 🌈 当前进度（C 模块 Demo）

文件位置：`index.html`  
打开方式：**直接用浏览器打开即可**

内容说明：
- 一个 9 秒单镜头广告原型  
- 中央有饮料瓶，周围有管道、罐头、摩天轮、树、小人等元素  
- 包含轻微旋转、上下浮动、缓慢移动等动效  
- 目前元素写死在代码中，仅用于展示视觉方向  
- 下一个阶段将改成读取 `adJson` 结构，支持自动生成场景

---

## 🔜 下一阶段（C 模块 TODO）

- 将 demo 改造成“读取 JSON 自动生成 DOM 的广告播放器”  
- 定义统一的元素类型列表（bottle / pipe / fruit / wheel / can / tree ...）  
- 定义通用动效名称（rotate / float / drift / spin / loop ...）  
- 输出一个简单的 `/preview` 接口用于调试 A/B 的 JSON

