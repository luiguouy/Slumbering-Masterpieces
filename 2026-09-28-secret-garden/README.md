# The Slumbering Masterpieces (沉睡的名画)

> **Fine Arts Digital Exhibition · An Interactive Chromatic Awakening & Random Wander (v4.3.0)**  
> *“I must have flowers, always, and always.” —— Claude Monet*  
> *"Touch the dormant monochrome; or wander through timeless canvases with a brush stroke."*

---

## 🎨 艺术理念与双重交互模式 (Dual Interactive Modes)

《**Slumbering Masterpieces · 沉睡的名画**》融合西方经典油画美学与数字图形学交互。现已支持两大模式：

1. **🌸 沉睡唤醒 (Dormant Awakening)**：
   - 未触碰时整幅画呈现为沉静古典的黑白灰阶素描；
   - 鼠标划过时多层累积显色（需来回 3~4 次完全复原真彩）；
   - 鼠标停驻之地在 0.4 秒内迅速绚烂绽放，悬停永不退隐；
   - 指尖离去后，色彩在 8.5 秒内保持高光饱和，随后优雅如晨雾般退去（4~30 秒自由定制）。
2. **🎲 随机漫游 (Random Wander & Scratch Mode)**：
   - 原画真彩直出，无需灰阶；
   - 画笔滑动擦除顶层画作，直接露出底层背后的下一幅随机名画；
   - 达到用户设定阈值（默认 85%）自动平滑完全展开；
   - 严格状态机锁定：一幅画必须完全展现出来后，画笔涂抹才能擦去它；
   - 深色画廊防漏底合成体系：无论画作是智能、完整（Contain）还是缩放，四周留白绝不提前穿帮露底。

---

## 🎛️ 画面控制台与自由构图 (Artisan Controls)

- **清爽模式分段切换**：面板顶部直观分段按钮，当前模式金色微光高亮；
- **画笔大小无级调节**：35px ~ 160px，带微缩预览与视口艺术光标等比缩放；
- **画面规格自适应**：【智能 (Auto)】、【完整 (Contain)】、【铺满 (Cover)】与 **60% ~ 140% 缩放**无论在沉睡还是漫游模式下均实时生效；
- **传世名画博览馆**：收录 315 幅世界殿堂级油画杰作，覆盖 8 大时代展厅、6 大西方正统题材与多维关键词检索。

---

## 🚀 启动与体验 (Quick Start)

```bash
# 静态服务器启动 (推荐)
python -m http.server 8080
# 浏览器访问
http://localhost:8080
```
