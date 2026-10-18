# Masterpiece Garden · 代码审查报告

- **审查日期**：2026-10-16
- **审查范围**：`js/`（11 模块 3540 行）、`index.html`（550 行）、`style.css`（2704 行）、`data/`（4490 行）
- **审查版本**：v4.6.0（`dd0daa5`）
- **审查方法**：全量静态走读 + 资源数据实测抽样 + 关键路径交叉验证
- **修复进度**：**P0-1 ~ P0-4、P1-1 ~ P1-4 全部修复并验证**；P2 已完成 5/6（P2-2 主动保留，见下）

---

## 修复状态总览

| 编号 | 缺陷 | 状态 | 验证方式 |
|---|---|---|---|
| P0-1 | 擦除阈值移动端不可达 | ✅ 已修复 | 真实模块运行 + 122 幅样本统计 |
| P0-2 | `gardenImage` 无 `onerror` | ✅ 已修复 | 静态走读 + 降级路径推演 |
| P0-3 | 随机漫游切画竞态 | ✅ 已修复 | 并发对照测试（后发先至场景） |
| P0-4 | 缺少 `touchcancel` | ✅ 已修复 | 静态走读 + 语法/依赖校验 |
| P1-1 | 黄铜透镜未做 DPR 适配 | ✅ 已修复 | 真实模块运行（DPR 1/2/3） |
| P1-2 | `bounds` 计算函数重复 | ✅ 已修复 | 合并为单一实现 + 语法校验 |
| P1-3 | 画廊搜索无防抖 | ✅ 已修复 | 静态走读 |
| P1-4 | 预加载池策略缺陷 | ✅ 已修复 | 静态走读 |
| P2-1 | 选择器硬编码重复 8 处 | ✅ 已修复 | 收敛为 `isEventOverModal()` |
| P2-3 | 全彩重绘逻辑重复 | ✅ 已修复 | 合并为 `paintFullColorLayer()` |
| P2-4 | 卡片 `innerHTML` 未转义 | ✅ 已修复 | 引入 `escapeHtml()` |
| P2-5 | 透镜位置哨兵值失效 | ✅ 已修复 | 改为 `hasLoupePointerPos` 布尔标志 |
| P2-6 | observer 反复重建 | ✅ 已修复 | 单例 observer + `observe/unobserve` |
| P2-7 | 魔法数字散落 | ✅ 已修复 | 抽取 6 个具名常量 |
| **P2-2** | **网格遍历样板重复 3 处** | **⏭ 主动保留** | 见下方说明 |

**累计改动**：8 个文件，+408 / −182 行。

> **P2-2 保留说明**：`applyDab` / `applyHoverCharge` 中的网格遍历样板虽重复 3 次，但位于**每次鼠标移动都会触发的渲染热路径**。消除重复需引入闭包回调，存在难以在开发环境下量化的性能回归风险，而收益仅为代码整洁。遵循「不为整洁度牺牲已验证的热路径性能」，予以保留。

---

## 审查概要

整体工程质量**高于同类原生 ESM 项目平均水平**：模块职责切分清晰，`canvas-engine` 与 `scratch-machine` 之间通过回调注册解耦、有效规避了循环依赖，按需渲染（`markDirty` + 静止休眠）设计正确。

但审查发现 **4 个功能性缺陷（P0）**，其中 3 个经实测数据确认，会直接导致移动端核心交互失效或状态错乱。另有 4 个重要问题（P1）与若干可维护性项（P2）。

| 等级 | 数量 | 说明 |
|---|---|---|
| **P0 严重** | 4（已修 3） | 功能失效 / 状态错乱 / 崩溃风险 |
| **P1 重要** | 4 | 体验受损、性能隐患、高回归风险 |
| **P2 建议** | 8（顺带修 1） | 可维护性与代码整洁度 |

> 第一批修复顺带消除了 P2-1（选择器硬编码重复 8 处）——它是 P0-4 的同一根因面：新增浮层时极易漏改。

---

## P0 · 严重缺陷

### P0-1 随机漫游模式擦除阈值在移动端 100% 不可达

**位置**：`js/engine/scratch-machine.js:110-123`（`updateScratchRatio`）、`js/engine/canvas-engine.js:29-31`（`initGrid`）

**问题描述**：
擦除比例的分母是全视口网格数，而非画作实际覆盖面积：

```js
// scratch-machine.js:114
const ratio = appState.scratchedCellsCount / appState.totalCells;
```

而 `totalCells` 由整个视口算出：

```js
// canvas-engine.js:29-31
appState.gridCols = Math.ceil(viewportWidth / config.cellSize);   // cellSize = 14
appState.gridRows = Math.ceil(viewportHeight / config.cellSize);
appState.totalCells = appState.gridCols * appState.gridRows;
```

在 contain 模式下（手机竖屏强制走 contain），画作只占视口一部分，其余为黑边。用户擦拭画作区域时，分子最多只能增长到"画作覆盖的网格数"，永远追不上"全视口网格数"。

**实测数据**（随机抽样 120 幅画作，解析 JPEG SOF 段获取真实尺寸）：

| 指标 | 数值 |
|---|---|
| 画作宽高比中位数 | 1.26（最小 0.10，最大 13.20） |
| 手机竖屏 390×844 下画作占视口面积 · 中位数 | **35.1%** |
| 同上 · 最低 / 最高 | 3.4% / 83.8% |
| **无法达到 85% 阈值的画作占比** | **100%** |

**后果**：
随机漫游擦画模式下，自动展开动画**永不触发**；HUD 显示的"已擦除比例"语义失真（擦拭整幅画也只显示 35%）。用户只能依赖"立即完全展现"按钮手动兜底，核心玩法链路上出现断点。

**修复方向**：
分母改为画作实际覆盖的网格数。建议在 `computeNextImageBounds()` 后统计落在 `imageBounds` 矩形内的格子数并缓存为 `appState.paintingCells`，`updateScratchRatio` 用其作分母；或等价地按 `imageBounds.w × imageBounds.h / (viewportW × viewportH)` 归一化。

**✅ 实际修复**：
1. `js/state.js`：新增 `appState.paintingCells`；
2. `js/engine/canvas-engine.js`：新增 `updatePaintingCells(bounds)`，在 `computeImageBounds()` 末尾统计画作矩形覆盖的格子数（含视口外裁剪与空矩形兜底）；
3. `js/engine/scratch-machine.js`：`updateScratchRatio()` 改用 `paintingCells` 作分母（未算出时回退 `totalCells`），并对 `ratio` 施加 `Math.min(1.0, ...)` 上限钳制——擦拭画作外留白同样会计入分子，不钳制会导致进度条溢出 100%。

**验证**：真实模块运行（mock `state.js` 隔离 DOM，加载实际 `canvas-engine.js` / `scratch-machine.js`）：

| 检查项 | 结果 |
|---|---|
| 画作占视口面积 | 35.2%（修复前按旧分母最高只能达到此值） |
| `paintingCells` | 616（全视口 `totalCells` 为 1708，几何估算误差 <6%） |
| 擦完画作后 `ratio` | 1.000 ✅ |
| 擦一半时 `ratio` | 0.50 ✅（进度真实反映擦拭比例） |
| 擦满整个视口 | 钳制为 1.0，不溢出 ✅ |
| 达到 85% 阈值 | 触发自动展开动画 ✅ |

另以 122 幅真实样本统计三种视口下的阈值可达率，由修复前的 **0% / 1% / 7%** 提升至 **100%**，极端宽高比（0.10 与 13.20）均未触发兜底。

---

### P0-2 主画作图片缺少 `onerror`，任一资源 404 即永久白屏　✅ 已修复

**位置**：`js/main.js:127-137`、`js/ui/gallery-drawer.js:376-377`

**问题描述**：
全仓库仅有两处 `onerror`：`nextGardenImage`（`scratch-machine.js:78`）与预加载池（`preload-pool.js:47`）。主画作 `appState.gardenImage` **没有任何错误处理器**。

而 `switchMasterpiece` 在赋值前先置位：

```js
// gallery-drawer.js:376-377
appState.isImageLoaded = false;
appState.gardenImage.src = art.src;
```

若加载失败，`onload` 永不触发，`isImageLoaded` 将**永久保持 false**。这会导致：
- `computeImageBounds()`（canvas-engine.js:59）early-return
- `renderGrayscaleBackground()`（:258）early-return
- `renderLoop` 中 `isImageLoaded` 为假的分支全部跳过

**后果**：315 幅资源中任一文件缺失/损坏，应用静默白屏且无任何反馈，用户无法感知也无法恢复。

**修复方向**：
在 `start()` 中补 `appState.gardenImage.onerror`，执行「显示占位提示 → 自动跳到下一幅」的降级路径。

**✅ 实际修复**（`js/main.js`）：
新增 `gardenImage.onerror`，执行「Toast 提示 → 自动跳下一幅」降级；引入 `loadFailureCount` 计数器与 `MAX_CONSECUTIVE_LOAD_FAILURES = 3` 上限，防止连续损坏资源引发无限切换递归；`onload` 成功时重置计数器。

---

### P0-3 随机漫游切画竞态：索引与展示画面可能错位　✅ 已修复

**位置**：`js/main.js:127-137`、`js/engine/scratch-machine.js:206`、`js/ui/brush-panel.js:188`

**问题描述**：
`prepareNextRandomArtwork()` 存在三个调用点，其中 `main.js:135` 位于 `gardenImage.onload` 内部：

```js
// main.js:127-137
appState.gardenImage.onload = () => {
    appState.isImageLoaded = true;
    computeImageBounds();
    ...
    prepareNextRandomArtwork();   // ← 每次主图加载完成都触发
    markDirty();
};
```

而 `gardenImage.src` 在两处被赋值——`scratch-machine.js:174`（擦画结算时晋升下一幅）与 `gallery-drawer.js:377`（切画）。**每次赋值都会触发 onload**。

于是每次擦画结算的完整时序为：
1. `finalizeScratchTransition()` 置 `gardenImage.src`（触发 A 路加载）
2. `finalizeScratchTransition()` 第 5 步调用 `prepareNextRandomArtwork()` → 抽随机索引 **X**，开始加载 `nextGardenImage`
3. A 路 `gardenImage.onload` 触发 → `main.js:135` 再次调用 `prepareNextRandomArtwork()` → 抽随机索引 **Y**，再次加载 `nextGardenImage`

两次调用各自 `pickRandomNextIndex()` 抽到不同索引，并发争抢同一个 `nextGardenImage` 对象的 `src` 与 `appState.nextMasterpieceIndex`。

**雪上加霜**：`prepareNextRandomArtwork` 内部使用单例覆盖式回调：

```js
// scratch-machine.js:77
nextGardenImage.onload = finish;
```

后发起的调用会覆盖前一次的 `onload`，导致先发起者的 `finish()` 可能永不执行——而该函数负责置 `isNextImageLoaded = true` 与解锁状态机。目前仅靠 `setTimeout(doUnlock, 600)` 兜底才未完全卡死。

**后果**：`currentMasterpieceIndex` 与实际展示的画作、故事抽屉内容、名言署名可能不一致。

**修复方向**：
1. 将 `prepareNextRandomArtwork()` 从 `main.js` 的 `onload` 中移除——`onload` 只应负责 bounds 计算与重绘；
2. 在 `prepareNextRandomArtwork` 中引入单调递增的 `prepareToken`，异步回调内比对 token 失效则丢弃，杜绝过期结果覆写。

**✅ 实际修复**：
1. `js/main.js`：从 `gardenImage.onload` 移除 `prepareNextRandomArtwork()`（含对应 import），`onload` 回归单一职责；
2. `js/engine/scratch-machine.js`：引入模块级 `prepareToken`，`finish()` 内校验 `token !== prepareToken` 则直接返回，不产生任何副作用；
3. `js/ui/gallery-drawer.js`：在 `switchMasterpiece()` 中补上「scratch 模式主动切画后重新抽取下一幅」——补上移除隐式调用后的职责缺口，避免随机漫游模式下切画后底层不再更新。

**验证**：构造「后发先至」并发场景（第 1 次调用延迟 50ms、第 2 次延迟 10ms），对照有/无守卫两份实现：

| 指标 | 修复前 | 修复后 |
|---|---|---|
| 过期回调 `cb[1]` | ❌ 被执行（污染） | ✅ 被拦截 |
| 最新回调 `cb[2]` | ✅ 执行 | ✅ 执行 |
| `computeBounds` 副作用次数 | 2 | **1** |
| 异步事件序列 | `cb[2] → cb[1]`（过期回调后发制人） | `cb[2]`（干净） |

结论：守卫成功拦截过期回调，且未误伤最新调用。修复前过期回调会在最新图尚未就绪时触发 `doUnlock()`，提前解锁状态机。

---

### P0-4 缺少 `touchcancel` 处理，移动端存在永久性触摸失灵风险　✅ 已修复

**位置**：`js/events/input-controller.js:408`（`touchend`）

**问题描述**：
全仓库**无任何 `touchcancel` 监听器**（已确认）。`touchstart`/`touchmove`/`touchend` 三件套齐全，但触摸被系统打断时（来电、通知下拉、多任务切换、系统返回手势、浏览器接管手势）`touchend` **不会触发**。

关键状态变量 `isPinching` 仅在 `touchend` 中复位：

```js
// input-controller.js:410-419
if (isPinching) {
    if (e.touches.length === 0) {
        isPinching = false;
        pinchCooldownUntil = performance.now() + 350;
        ...
    }
    return;
}
```

若打断发生在双指捏合期间，`isPinching` 永久停留在 `true`。此后所有 `touchmove` 都在 `if (isPinching) return;`（:369）处被吞掉，`touchstart` 中 `e.touches.length === 1 && !isPinching` 条件（:306）也不再成立。

**后果**：**触摸交互彻底失灵，且无法通过任何操作恢复**，必须刷新页面。这是移动端最严重的一类缺陷。

**修复方向**：
补 `touchcancel` 监听，与 `touchend` 共用同一套状态清理逻辑。

**✅ 实际修复**（`js/events/input-controller.js`）：
将 `touchend` 的匿名回调提取为具名函数 `handleTouchEnd(e, isCancel = false)`，并同时注册到 `touchend` 与 `touchcancel`。三个要点：

1. **中断时强制复位**：`isPinching` 分支的复位条件由 `e.touches.length === 0` 改为 `isCancel || e.touches.length === 0`。`touchcancel` 触发时 `e.touches` 可能仍残留触点记录，若沿用原条件则不会复位，缺陷依旧存在——这是本次修复的关键细节；
2. **中断不结算手势**：状态清理完成后 `if (isCancel) return`，避免在用户并无意图时误触发双击全彩或轻扫切画；
3. 清理项补充 `isDraggingPan = false`，保证中断后拖拽态一致。

**顺带根因修复（P2-1）**：将散落 8 处的选择器硬编码收敛为模块级常量 `MODAL_SELECTOR` / `MACRO_HUD_SELECTOR` 与 `isEventOverModal(e, includeMacroHud)` 辅助函数。其中 `contextmenu` 与 `wheel` 两处传入 `includeMacroHud = false`，**严格维持原有行为不变**（这两处原本即不含 `.macro-zoom-hud`）。

**验证**：11 个模块 ESM 语法检查全通过；依赖图 DFS 环检测确认新增 import 未引入循环依赖（11 模块 / 36 条边，无环）。

---

## P1 · 重要问题

### P1-1 黄铜透镜未做 DPR 适配，高分屏下实为"放大模糊"

**位置**：`index.html:60`、`style.css:2538-2571`、`js/engine/macro-loupe.js:103`

三处尺寸定义共同锁死了 1× 像素比：

```html
<!-- index.html:60 -->
<canvas id="macro-loupe-canvas" width="220" height="220"></canvas>
```
```css
/* style.css:2542-2543 / 2566-2567 */
.macro-loupe { width: 220px; height: 220px; }
#macro-loupe-canvas { width: 100%; height: 100%; }
```

后端缓冲固定 220×220，CSS 显示尺寸同为 220px。在 DPR=2 的手机上需要 440 物理像素，实际只有 220 → **2× 拉伸模糊**；DPR=3 设备为 3× 模糊。

**这与项目其余部分的严谨处理形成明显反差**——`handleResize()`（canvas-engine.js:317-321）对主画布做了完整的 DPR 适配：

```js
bgCanvas.width = Math.round(viewportWidth * dpr);
bgCanvas.style.width = viewportWidth + 'px';
bgCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
```

透镜作为宣称"高精原画切片真彩直出"的核心卖点，恰恰遗漏了这一步。

**修复方向**：初始化时 `canvas.width = 220 * dpr` 并 `setTransform(dpr,0,0,dpr,0,0)`，渲染逻辑中的 `canvasW/canvasH` 改用 CSS 尺寸。

**✅ 实际修复**：
1. `js/state.js`：新增 `LOUPE_CSS_SIZE = 220` 常量（注释标明须与 `style.css` 中 `.macro-loupe` 保持一致）；
2. `js/engine/canvas-engine.js`：在 `handleResize()` 中按透镜实际 CSS 尺寸 × dpr 分配后端缓冲，随后 `setTransform(dpr,...)`（顺序不可颠倒，尺寸赋值会重置变换矩阵）；
3. `js/engine/macro-loupe.js`：`renderMacroLoupe()` 的 `canvasW/canvasH` 与 `loupeArtCoverage()` 的半径统一取自 `appState.loupeCssSize`，绘制统一走 CSS 坐标系。

> **后续修正（2026-10-18）**：本项最初以常量 `LOUPE_CSS_SIZE` 作为尺寸真源，实为「常量与 CSS 双源」结构——一旦 CSS 断点改变尺寸，JS 侧三处（缓冲分配、采样跨度、圆盘覆盖率）会静默失配。现改为 `measureLoupeCssSize()` 在 resize 时读取计算样式并缓存到 `appState.loupeCssSize`，常量降级为首屏兜底值（`getComputedStyle` 会触发样式重算，不可放进 mousemove 等高频路径）。
>
> 另经真机核实：`style.css` 中 `@media (max-width:640px)` 的 `.macro-loupe { width: 180px }` 因写在基础规则（220px）**之前**，被同 specificity 的后置声明覆盖，是一条**死声明**——移动端透镜实际一直是 220px，并不存在「倍率偏低 18%」的问题。若后续要让 180px 生效，必须先调整规则顺序或提高选择器权重；改后 JS 侧会因测量式取值自动跟随，无需同步改常量。

**验证**：真实模块运行 `handleResize()`，检查三种 DPR 下的缓冲分配：

| DPR | 有效 dpr | 后端缓冲 | 与物理显示像素 |
|---|---|---|---|
| 1 | 1 | 220×220 | 1:1 ✅ |
| 2 | 2 | 440×440 | 1:1 ✅（修复前仅 220，2× 拉伸） |
| 3 | **2.5**（项目上限） | 550×550 | 1:1 ✅ |

> 有效 dpr 在 3 时为 2.5，是因为 `handleResize()` 存在 `Math.min(devicePixelRatio, 2.5)` 的显存保护上限——透镜自动继承了这一策略，属预期行为。

同时确认**透镜采样跨度未改变**（修复前后均为 201.1 原图像素）：本次修复只提升输出分辨率，不改变取景范围。

---

### P1-2 `computeImageBounds` 与 `computeNextImageBounds` 近乎完全重复

**位置**：`js/engine/canvas-engine.js:58-145` 与 `150-223`

两个函数约 110 行，布局算法（effectiveMode 判定 → contain/cover 分支 → scale → macroZoom）**逐行相同**，唯一差异是前者多了平移阻尼约束（:122-131），后者没有。

**风险**：任何布局修复都必须同步改两处，漏改一处即产生双画布错位。这是明确的回归风险源，也直接推高了维护成本。

**修复方向**：抽取 `computeBoundsFor(img, { applyPanClamp })` 统一实现，两处仅传入不同参数。

**✅ 实际修复**：抽取模块内私有函数 `computeLayoutFor(imgW, imgH, applyPanClamp)`，两个导出函数退化为薄包装：

```js
export function computeImageBounds() {
    if (!appState.isImageLoaded) return;
    appState.imageBounds = computeLayoutFor(naturalW, naturalH, true);   // 施加平移阻尼
    updatePaintingCells(appState.imageBounds);
}
export function computeNextImageBounds() {
    if (!appState.isNextImageLoaded) return;
    appState.nextImageBounds = computeLayoutFor(naturalW, naturalH, false); // 跟随主画作平移量
}
```

关键点是保留了两者的**唯一实质差异**：底层「下一幅」画作不施加平移钳制（否则会对已钳制过的主画作平移量二次钳制，导致双层画布错位）。

---

### P1-3 画廊搜索无防抖，输入存在明显卡顿

**位置**：`js/ui/gallery-drawer.js:545-551`

```js
gallerySearchInput.addEventListener('input', (e) => {
    galleryFilterState.query = e.target.value;
    ...
    renderGalleryList();   // 无防抖
});
```

每次按键触发全量重算：315 条 × 6 个字段的正则归一化（`normalizeSearchText`）+ `innerHTML = ''` 清空 + 最多 24 张卡片 DOM 重建。中文输入法下组合输入还会产生额外事件。中低端手机上有可感知的掉帧。

**修复方向**：150~200ms 防抖（trailing）；数据量固定，也可考虑预计算归一化索引一次性缓存。

**✅ 实际修复**：引入 `GALLERY_SEARCH_DEBOUNCE_MS = 180` 与 `gallerySearchTimer`，仅将耗时的 `renderGalleryList()` 延后；清除按钮显隐保持即时反馈。

同时新增 `cancelPendingGallerySearch()`，由三处「立即生效」的筛选操作（清空按钮、重置筛选、Escape 清空）先行调用，避免随后被延时任务再重复渲染一次。

---

### P1-4 预加载池缓存污染与淘汰策略缺陷

**位置**：`js/utils/preload-pool.js:17-57`

两个问题：

1. **失败资源仍入缓存**（:47-50）：`img.onerror` 调用 `onFinish()`，把加载失败的坏图写入缓存。虽因 `img.complete && naturalWidth > 0` 判定会走重试分支，但缓存条目已被污染，且 `console.warn` 每次触发。
2. **淘汰不感知在用资源**（:38-41）：LRU 按插入顺序淘汰最久未用者，但不知道哪张是"即将展示的下一幅"。快速连续切画时（`preloadAdjacent` 频繁插入），可能恰好淘汰掉马上要用的相邻图，反而制造黑屏——与"消除切画黑屏"的设计目标相悖。

**修复方向**：失败不写入缓存（可记入短期黑名单避免反复重试）；淘汰时跳过 `appState.nextMasterpieceIndex` 与 index±1 对应的 src。

**✅ 实际修复**（`js/utils/preload-pool.js`）：
1. **失败不入缓存**：`onload` / `onerror` 分流为 `settle(true)` / `settle(false)`，仅成功时写入缓存，杜绝坏图占据缓存条目并被反复命中；
2. **淘汰豁免机制**：新增 `protectedKeys` 集合与 `protect(srcList)`（增量登记、超上限 `MAX_PROTECTED_ENTRIES = 6` 时按插入顺序滚动淘汰），`evictOne()` 只淘汰「未受保护且最久未用」的条目；
3. `preloadAdjacent()` 预载前先登记「当前 + 前一幅 + 后一幅」为豁免项；`scratch-machine.js` 的 `prepareNextRandomArtwork()` 亦保护「下一幅」候选。

---

## P2 · 可维护性与代码整洁度

| # | 问题 | 状态 |
|---|---|---|
| P2-1 | `isOverModal` 选择器字符串重复 8 次，且存在两种变体 | ✅ 收敛为 `isEventOverModal(e, includeMacroHud)` |
| P2-2 | 网格遍历样板重复 3 次 | ⏭ **主动保留**（热路径，见总览说明） |
| P2-3 | 全彩重绘逻辑在 `refreshLayout` 与 `renderLoop` 重复 | ✅ 合并为 `paintFullColorLayer(alpha)` |
| P2-4 | 卡片 `innerHTML` 直接插值未转义，`alt="${art.title}"` 遇引号会破坏属性结构 | ✅ 引入 `escapeHtml()`，6 处插值全部转义 |
| P2-5 | 用哨兵值 `lastLoupePointerPos.x > 0` 判断位置有效性，x ≤ 0 时失效 | ✅ 改为 `hasLoupePointerPos` 布尔标志 + `setLoupePointer()` |
| P2-6 | observer 反复 disconnect + 重建，且在其自身回调链路中被重建 | ✅ 单例 observer + `observeGallerySentinel()`（先 unobserve 再 observe） |
| P2-7 | 魔法数字散落 | ✅ 抽取 6 个具名常量（见下） |
| P2-8 | `scripts/` 下 89 个文件与运行时产物混置 | ⏭ 建议后续归入 `tools/`（非代码缺陷，未改动） |

**P2-7 新增常量**：`PINCH_COOLDOWN_MS`(350)、`MACRO_ZOOM_SNAP_THRESHOLD`(1.06)、`GALLERY_SEARCH_DEBOUNCE_MS`(180)、`LOUPE_CSS_SIZE`(220)、`MACRO_ZOOM_ACTIVE_THRESHOLD`(1.05)、`MAX_MACRO_ZOOM`(4.5)、`MAX_PROTECTED_ENTRIES`(6)。

---

## 建议修复顺序

**第一批（阻断性问题）— ✅ 已完成**
1. ~~P0-4 补 `touchcancel`~~ → 已修复，顺带收敛 8 处选择器硬编码
2. ~~P0-2 补 `gardenImage.onerror`~~ → 已修复，含 3 次连续失败熔断
3. ~~P0-3 竞态守卫~~ → 已修复，经并发对照测试验证

**第二批（核心体验）— ✅ 已完成**
4. ~~P0-1 擦除比例分母~~ → 已修复，122 幅样本验证可达率由 0% 升至 100%
5. ~~P1-1 透镜 DPR 适配~~ → 已修复，DPR 1/2/3 下均为 1:1 映射

**第三批（降低长期维护成本）— ✅ 已完成**
6. ~~P1-2 合并两个 bounds 函数~~ → 已合并为 `computeLayoutFor()`，保留平移钳制差异
7. ~~P1-3 搜索防抖~~ → 180ms 防抖 + 立即操作取消挂起任务
8. ~~P1-4 预加载池策略~~ → 失败不入缓存 + 淘汰豁免机制
9. ~~P2 清理~~ → P2-1/3/4/5/6/7 已处理；P2-2 主动保留；P2-8 未改动

**回归验证**：11 个模块 ESM 语法检查全通过；依赖图 DFS 环检测通过（11 模块 / 37 条边，无环）。

---

## 审查结论

架构层面**值得肯定**：`canvas-engine` ↔ `scratch-machine` 的回调注册解耦是正确设计，成功规避了原生 ESM 下最易踩的循环依赖陷阱；按需渲染与 O(1) 擦除统计体现了明确的性能意识；`HANDOFF.md` 中记录的 6 条踩坑及其解法，在代码中均有对应实现，未发现"文档承诺与实现不符"的情况。

三批修复**已全部完成**（除 P2-2 主动保留、P2-8 未改动）。累计改动 8 个文件、+408 / −182 行。

**经实测验证的三项**：
- **P0-1**：擦除进度改用画作覆盖网格数作分母，122 幅样本在三种视口下的阈值可达率由 0% / 1% / 7% 提升至 **100%**；
- **P0-3**：并发对照测试证明过期回调被拦截，副作用触发次数由 2 降为 1；
- **P1-1**：透镜后端缓冲在 DPR 1/2/3 下均与物理显示像素 1:1，且取景范围未变。

**工程校验**：11 个模块 ESM 语法检查全通过；依赖图 11 模块 / 37 条边，无循环依赖。

**唯一主动保留项**是 P2-2（网格遍历样板重复 3 次）：它位于每次鼠标移动都会触发的渲染热路径，消除重复需引入闭包回调，存在难以量化的性能回归风险，收益仅为代码整洁，故维持原状。

**建议在真机上做的最后确认**（自动化无法覆盖）：① 移动端随机漫游模式的自动展开手感；② DPR ≥ 2 设备上透镜清晰度的目视改善；③ 双指缩放过程中接听电话后触摸是否仍可正常响应。

---

## 第二轮修复（2026-10-18）

针对「首次审查未覆盖的运行期缺陷」的修复批次。全部结论均来自 Playwright + 系统 Chrome 的真实运行，非静态推演。

### 状态总览

| 编号 | 缺陷 | 严重度 | 状态 |
|---|---|---|---|
| R-1 | 随机漫游模式 resize 后画作被「擦光」，索引与画面脱节 | P0 | ✅ 已修复 |
| R-2 | 随机漫游模式下双击 / 空格改写遮罩，进度计数失真 | P0 | ✅ 已修复 |
| R-3 | 移动端微距透镜因面板容器全屏占位而完全不可用 | P0 | ✅ 已修复 |
| R-4 | 关闭画廊后字母快捷键与方向键全部失效 | P1 | ✅ 已修复 |
| R-5 | 透镜尺寸存在「常量 / CSS / JS」三处真源 | P2 | ✅ 已修复 |
| R-6 | 命中浮层未清指针活跃态；触屏提示文案错位 | P2 | ✅ 已修复 |

---

### R-1 `initGrid()` 未按模式恢复网格（P0）

**位置**：`js/engine/canvas-engine.js` `initGrid()` / `handleResize()`

**根因**：`handleResize()` 每次都会调用 `initGrid()` 重建网格，而重建时 `gridAlpha` 一律为全 0 的 `Float32Array`。该值在两种模式下语义相反——沉睡模式 0 = 全灰阶（正确），随机漫游模式 0 = 顶层遮罩全透明。于是 `orientationchange`（手机旋转，必经此路径）或 `visualViewport.resize` 发生后，随机漫游模式下顶层画作瞬间完全透明、底层「下一幅」整幅露出，而 `scratchedCellsCount` 仍为 0，HUD 显示 0%，索引未晋升。

**修复**：
1. 初始 Alpha 与 `gridAlpha` 均按模式取值（`scratch` → 255 / 1.0）；
2. `scratch` 模式下同时重置 `scratchedCellsCount`、`scratchConfig.ratio`，并强制解除 `isLocked` / `isTransitioning`——正在执行的揭示动画持有旧的 `startAlphas` 快照，继续跑会按新的 `totalCells` 越界读取并写入 `NaN`；
3. `handleResize()` 的 `scratch` 分支补 `syncScratchHud(0)`，避免 HUD 停留在旧百分比。

**验证**（390×844）：`scratch` 模式连续两次 resize 后顶层画布中心像素 Alpha 均为 255（修复前为 0）；HUD 回落 `0%`；沉睡模式 resize 前后均为 0。

---

### R-2 随机漫游模式下 `toggleFullColor` 破坏状态一致性（P0）

**位置**：`js/ui/brush-panel.js` `toggleFullColor()`，触发自 `input-controller.js` 的双击与 Space

**根因**：「一键全彩」通过整体改写 `gridAlpha` 实现，这只在沉睡模式成立。随机漫游模式下填 `colorRatio` 会把已擦出的洞补满，填 0 会让整幅顶层瞬透直接露底；两条路径都不修改 `scratchedCellsCount` / `scratchConfig.ratio`，也不走 `finalizeScratchTransition()`，结果是 HUD 百分比失真、后续少量擦拭即可越过阈值误触发自动展开、`currentMasterpieceIndex` 与实际画面脱节。

**修复**：在 `toggleFullColor()` 入口拦截 `scratch` 模式并返回 `false`（附 Toast 说明）；Space 分支改为 `if (toggleFullColor())` 再弹提示，避免覆盖模式提示；`setAppMode('scratch')` 主动清除 `isFullColorLocked` 并复位按钮；`switchMasterpiece()` 仅在非 `scratch` 下调用该函数。

**验证**：`scratch` 模式下调用返回 `false`，画布中心 Alpha 保持 255 不变。

---

### R-3 移动端微距透镜完全不可用（P0）

**位置**：`style.css` `.brush-popup`，`js/engine/macro-loupe.js` `hitPanel()`

**根因**：`.brush-popup` 未展开态虽为 `opacity:0`，但仍参与父容器 `.brush-control-panel` 的 flex 布局。实测 390×844 下该容器 rect 为 `[80,14,296,746]`——几乎覆盖整屏。`hitPanel()` 已按计算样式过滤掉 `opacity:0` 的 popup 本身，但**父容器**自身可见、矩形仍包含这块隐形区域，于是画作中心 (195,422) 命中，透镜一进画作即隐匿，只剩画外可用。

**修复**：`.brush-popup` 改为 `position:absolute; top:calc(100% + 10px); right:0` 脱离文档流，容器矩形收敛为按钮本身。

**验证**：容器 rect 由 `[80,14,296,746]` 变为 `[332,14,44,44]`；画中心透镜 `active=true` 且镜内采样像素非空 `[122,73,72,255]`；画外角落仍隐匿；弹层展开 rect `[80,68,376,760]`（桌面 `[1018,76,1252,764]`）均在视口内。

> **方法论**：凡是用 `getBoundingClientRect()` 做命中判定的容器，其 DOM 矩形必须等于视觉可见区域。「隐形子元素撑大父容器」会让所有基于 rect 的判定集体失真，且只在窄视口暴露。

---

### R-4 关闭画廊后快捷键全部失效（P1）

**位置**：`js/ui/gallery-drawer.js` `closeGallery()`

**根因**：`openGallery()` 会把焦点移到搜索框。抽屉关闭时只是平移出视口，搜索框仍在 DOM 中；焦点不随之释放，`keydown` 的 `isTyping` 判定（`activeElement` 为 `INPUT`）持续为真，导致 `H / S / G / M / Space / ← →` 全部被忽略，用户只能靠鼠标点击画布才能恢复。

**修复**：`closeGallery()` 中若 `activeElement` 位于抽屉内则 `blur()`。

**验证**：打开再关闭画廊后 `document.activeElement.tagName` 为 `BODY`（修复前 `INPUT`）；`M` 键可正常开关透镜；`←/→` 恢复翻页。

---

### R-5 透镜尺寸单一真源（P2）

见 P1-1 的「后续修正」说明。`LOUPE_CSS_SIZE` 降级为首屏兜底，实际尺寸由 `measureLoupeCssSize()` 在 resize 时测量并缓存。

---

### R-6 其余两项（P2）

- `mousemove` 命中浮层时补 `isPointerActive = false` 与 `currentPointerPos = null`。此前只清 `isCursorActive`，导致光标停在面板上时画作被持续停驻充能、rAF 循环永不进入静止休眠。
- `updateHintText()` 改为按 `matchMedia('(pointer: coarse)')` 分流文案，并让 `setupInputEvents()` 复用同一函数；此前触屏设备切入随机漫游后仍提示「用鼠标擦拭画面」。

---

### 回归验证

11 个模块 ESM 语法检查全通过；依赖图 11 模块 / 37 条边，无环。交互冒烟覆盖：快捷键矩阵、画廊搜索（含中文与空结果）、题材/画派筛选、重置、故事抽屉同步、卡片点击切画、适配模式与缩放、双击分流、透镜开关与隐匿、双模式往返，全程零 JS 异常。

**仍需真机确认**（自动化无法覆盖）：① 真机旋转屏幕时随机漫游的视觉连续性；② 双指缩放中接听电话后的触摸恢复；③ iOS Safari 上 `visualViewport.resize` 的触发频率是否导致进度被反复清零（若过于频繁，可考虑仅在尺寸实际变化超过阈值时才重建网格）。
