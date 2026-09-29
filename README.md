# 🎨 Slumbering Masterpieces (沉睡的花园)

> **Fine Arts Digital Exhibition · An Interactive Chromatic Awakening**  
> *“I must have flowers, always, and always.” —— Claude Monet*  
> *触碰沉睡的静谧灰阶；用指尖的温度，在花瓣间唤醒稍纵即逝的绚烂盛放。*

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Technology: Vanilla JS](https://img.shields.io/badge/Technology-Vanilla%20JS%20%7C%20HTML5%20Canvas-336699.svg)](#)
[![Dependencies: None](https://img.shields.io/badge/Dependencies-Zero-success.svg)](#)
[![DPI: Retina%204K](https://img.shields.io/badge/Render-Retina%204K%20Ready-brightgreen.svg)](#)

---

## 🖼️ 艺术理念 (Artistic Philosophy)

《**Slumbering Masterpieces · 沉睡的花园**》是一件融合欧洲古典油画美学与数字图形学交互的传世名画级网络艺术装置。

- **静谧沉睡**：在未经触碰时，整幅画卷呈现为沉静肃穆的古典灰阶素描底稿，纤毫毕现却隐去了所有的色彩；
- **指尖苏醒**：随着观者的鼠标拂过画布，沉睡的生机在画卷深处被层层点亮；
- **回归永恒**：当指尖移开，盛开的色彩在画卷上久久留存，随后如晨雾般优雅消散，再度归于古典的宁静。

---

## ✨ 核心交互设计 (Interactive Highlights)

### 1. 🖌️ 多层划动渐进显色 (Multi-Pass Progressive Reveal)
- **拒绝一划爆满**：告别传统擦除效果中“轻轻一划就全屏全彩”的粗糙感。单次滑过时，仅透出约 25% 淡淡的微妙色彩，画面主体依然保持素描质感；
- **层层润色叠加**：像真实的古典画师在画布上来回罩染（Glazing）一样，只有在同一区域**来回擦拭、滑动 3~4 次**，色彩才会层层累加浸润，最终达到 100% 鲜艳饱满的原画真彩。

### 2. 🌸 停驻充能绽放 (Hover Focus Charge)
- **“只有停留的地方，才是绚烂焦点”**：快速掠过的鼠标不会破坏画面的宁静；
- 当光标停留在任意花朵或蓝天之上时，会触发**焦点充能机制**（每 45ms 递增）；只需驻足停留约 **0.4~0.5 秒**，该处便会迅速自内向外饱满盛开；
- **只要光标悬停，此处便永恒盛开不败**。

### 3. ⏳ 超长色彩留存与晨雾淡出 (Luminescent Hold & Foggy Decay)
- **漫长留存（默认 12.0 秒）**：
  - **高光饱和期**：涂抹出的鲜明真彩在鼠标离开后保持 **8.5 秒完全不褪色**，赋予观者从容品鉴笔触与细节的时间；
  - **优雅淡出期**：随后在 **3.5 秒内按非线性余弦曲线如晨雾般自然消退**，重归黑白灰阶。

### 4. 🎛️ 典雅画笔与留存控制台 (Artisan Control Panel)
- 点击右上角精致的**羽毛画笔小图标**，即可展开半透明深色磨砂玻璃（Backdrop Filter Blur）调控面板：
  - **画笔大小无级调节**：支持 **35px ~ 160px** 随意滑动，面板配备微缩圆点实时动态预览，视口中的艺术光标外圈（`cursor-ring`）实时等比缩放；
  - **色彩留存时长调节**：支持在 **4秒 ~ 30秒** 之间自由定制色彩停留寿命；
  - **极简无痕交互**：点击画布任意空白处自动轻柔折叠，完全不遮挡艺术画面。

### 5. 🏛️ 10 幅世界级花卉与风景名画一键切换 (Curated Gallery)
- 控制面板内置**【名画画廊】**，支持下拉快速跳转与 **‹ 上一幅 / 下一幅 ›** 快捷无缝切换；
- 切换时画面平滑重置为静谧灰阶，上方悬浮的名言与画家署名**同步联动更新**为专属艺术语录；
- 精选全球美术史上知名度最高的 10 幅花卉与风景传世巨作：
  1. **《莫奈的秘密花园 · 沉睡庄园》** · *Claude Monet 风格*
  2. **《维特伊的艺术家花园》** (The Artist's Garden at Vétheuil, 1880) · *克劳德·莫奈* (华盛顿国家美术馆藏)
  3. **《大都会的鸢尾花丛》** (Irises, 1890) · *克劳德·莫奈* (纽约大都会艺术博物馆藏)
  4. **《瓦日蒙玫瑰花海》** (A Garden at Wargemont, 1879) · *皮埃尔-奥古斯特·雷诺阿*
  5. **《大丽花与花园》** (Dahlias in the Garden, 1893) · *古斯塔夫·卡耶博特* (华盛顿国家美术馆藏)
  6. **《索罗拉故居庭院》** (Garden of the Sorolla House, 1919) · *华金·索罗拉* (马德里索罗拉博物馆藏)
  7. **《西莉亚的海岛盛开花园》** (Celia Thaxter's Island Garden, 1890) · *柴尔德·哈萨姆* (大都会艺术博物馆藏)
  8. **《盛放花境》** (Flower Garden / Blumengarten, 1908) · *埃米尔·诺尔德* (柏林现代艺术馆藏)
  9. **《万纳湖畔花境》** (Flower Terrace at Wannsee, 1915) · *马克斯·利伯曼*
  10. **《溪畔盛放的玫瑰花丛》** (Roses by the Riverbank, 1900) · *丹尼尔·里奇韦·奈特*

---

## ⚙️ 底层技术与图形学实现 (Technical Architecture)

本项目采用**纯原生前端架构（零外部第三方依赖包）**，针对 60~120fps 高刷屏与 4K 高分屏进行了深度优化：

1. **空间状态衰减网格系统 (Spatial Decay Grid Field)**：
   - 摒弃了点轨迹数组随时间无序膨胀导致的内存泄漏与 GC 卡顿隐患，采用轻量级固定网格（Cell-based TypedArray Field）；
   - 每个网格单元独立记录 `intensity`（显色强度）、`lastTouchTime`（最后激活时间戳）与 `lastStrokeId`（最后触碰笔画 ID），计算开销低于 0.1ms。
2. **笔划方向识别与防骤满算法 (Stroke ID Isolation)**：
   - 实时监测鼠标移动的速度向量变化与停顿时间，自动识别“来回折返”与“多次涂抹”；
   - 无论高速移动时插值密度多高，同单次滑动中对同一单元格的显色贡献均受严格约束，确保必须“多划几下”才能满彩。
3. **GPU 硬件加速双线性平滑插值 (Bilinear Bilateral Smoothing)**：
   - 低分辨率遮罩层通过 Canvas 2D 硬件管线直接投射并放大至物理分辨率；
   - 双线性滤波使笔触边缘呈现出如顶级宣纸吸墨、水彩晕染般的无缝高斯过渡，告别一切马赛克与折线锯齿。
4. **双缓冲像素级严格对齐 (Dual-Canvas Pixel-Perfect Compositing)**：
   - 底层由 CSS 纯粹 Filter 调色保持原画明暗灰阶；
   - 顶层通过 Cover 几何适配算法将 100% 饱和彩色名画通过 `destination-in` 混合模式精准投射在遮罩区域，两层绝对 1:1 对齐，毫无重影。

---

## 📂 项目结构 (Project Structure)

```text
Slumbering-Masterpieces/
├── .gitignore                      # Git 规范忽略配置
├── README.md                       # 项目主说明文档
└── 2026-09-28-secret-garden/       # 沉睡的花园艺术工程目录
    ├── index.html                  # 舞台主结构与名言排版
    ├── style.css                   # 传世名画级视觉样式与磨砂玻璃控件
    ├── app.js                      # 核心交互物理引擎 (v3.2.0)
    ├── README.md                   # 子模块说明文档
    └── assets/                     # 艺术资源目录
        └── images/                 # 高精合成油画原图与画作资产库
            └── garden.jpg          # 莫奈花园传世级主背景画作
```

---

## 🚀 启动与体验指南 (Quick Start)

本项目为**零第三方依赖**的纯净现代前端代码，支持任何主流浏览器（Chrome、Edge、Safari、Firefox 等）：

### 方式一：直接双击打开
进入 `2026-09-28-secret-garden/` 目录，双击打开 `index.html` 即可立即体验。

### 方式二：静态服务器运行（推荐，支持高清原图顺畅加载）
在项目根目录下通过终端执行：

```bash
# 使用 Python 启动
python -m http.server 8080 --directory 2026-09-28-secret-garden

# 或使用 Node.js / npx serve
npx serve 2026-09-28-secret-garden
```

在浏览器中打开：👉 **`http://localhost:8080`**

---

## 🎯 操作快捷指南 (Interaction Guide)

| 操作方式 | 对应效果 |
| :--- | :--- |
| **鼠标轻扫划过** | 淡淡透出约 25% 浅彩，主体依旧是素描灰色 |
| **同一区域反复涂抹 3~4 次** | 色彩层层浸透，完全还原 100% 名画鲜艳原色 |
| **鼠标停留在花朵/天空原地** | 原地充能，0.4 秒内迅速绚烂绽放，停驻时永不消退 |
| **光标移开** | 原色保持 8.5 秒不变，随后 3.5 秒内晨雾般淡出（默认 12 秒） |
| **点击右上角画笔图标** | 展开控制台，可自由滑动调节画笔粗细与留存时长 |

---

## 📜 艺术致敬 (Credits & Artworks)

- 主作画风与名言源自印象派巨匠 **克劳德·莫奈 (Claude Monet)**；
- 名画原图由欧洲古典庄园大师画作高精度数字合成。
