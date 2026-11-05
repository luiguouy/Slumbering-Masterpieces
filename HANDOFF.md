# Session Handoff: Masterpiece Garden · 传世名画博览馆

## 1. 任务背景与核心目标
- **目标描述**：打造兼具电脑端与移动端（手机竖屏与横屏）殿堂级体验的古典传世名画互动博览馆。用户可通过指尖/鼠标轻拂唤醒沉睡名画真彩或擦拭漫游探索，并支持 420 幅名画的高维检索、流派/题材筛选、深度艺术鉴赏故事，以及局部微距放大镜与画布级双指细节缩放。
- **项目主路径**：`d:\Antigravity_Workspaces\art-web`
- **版本控制状态**：
  - 分支：`main`
  - 最新功能：`feat: 名画库按世界知名度 re-rank，首屏即蒙娜丽莎 (v4.8.0)`

## 2. 关键架构决策与确认项
- **原生 ES Module (Zero-build Native ESM) 模块化架构**：
  - 将原 3186 行巨型单文件 `app.js` 彻底拆解为职责单一、高内聚低耦合的现代化原生 ESM 模块体系，无需 Webpack/Vite 等任何外部繁重构建工具；
  - `js/state.js`: 统管响应式全局配置 `config`、`scratchConfig`、`galleryFilterState`、空间网格、几何参数与运行态数据；
  - `js/utils/preload-pool.js`: 智能双向名画预加载队列（当前画作 Index $\pm 1$ 与随机漫游候选），LRU 内存淘汰，消除切画黑屏；
  - `js/engine/canvas-engine.js`: 视口 DPR 自适应、网格空间透明度衰减、离屏双线性采样、双层画布对齐与帧渲染主循环 `renderLoop`；
  - `js/engine/macro-loupe.js`: 双指缩放几何计算、抓手漫游平移、古典黄铜透镜高精原画切片渲染与滚轮/芯片倍率调焦；
  - `js/engine/scratch-machine.js`: 随机漫游擦画状态机（O(1) 擦除比例统计、平滑揭开动画、防重复队列）；
  - `js/ui/gallery-drawer.js`: 420 幅名画展厅搜索、多维题材药丸、大师去重选择器与列表虚拟分批加载；
  - `js/ui/story-drawer.js`: 名画创作背景、艺术密码、馆藏与名言抽屉控制器；
  - `js/ui/brush-panel.js`: 画笔调节面板、模式切换、滑块联动与透镜倍率选项盒；
  - `js/ui/help-modal.js`: 操作指南与快捷键弹窗控制器及 Toast 轻提示；
  - `js/events/input-controller.js`: 统一管理鼠标移动/抓手拖拽、滚轮缩放、触控手势（双指捏合与 350ms 冷却互锁）、双击分流与键盘快捷键矩阵；
  - `js/main.js`: 主入口装配中枢，自启动各子系统并挂载 `window.__gardenEngine`。
- **双层绝对对齐画布引擎**：底层 Classical Grayscale / Next Canvas（灰阶或背底名画），顶层 Dynamic Reveal Canvas（真彩唤醒/遮罩），通过物理像素级对齐实现零畸变涂抹。
- **微距细节探索系统 (Macro Exploration Engine)**：
  - **画布级双指 Pinch-to-zoom & 平移漫游 (Pan)**：
    - 移动端双指捏合支持 $1.0\times \sim 4.5\times$ 连续无级平滑缩放与焦点膨胀（Focal point zooming）；
    - 双指漫游平移带边缘弹性阻尼约束，杜绝名画被拖出视口消失；
    - 单指涂抹与双指缩放严密互锁，双指操作期间不触发误划伤；
    - 智能双击分流（Smart Double-Tap）：放大状态下双击平滑弹性复位至 $100\%$ 全景；$100\%$ 全景状态下双击切换一键全彩盛放/恢复沉睡；
    - 左右轻扫切画仅在非放大状态（$\le 1.05\times$）下触发，防止放大漫游时误切画作；
    - 桌面端支持滚轮以光标为中心平滑缩放、右键/中键拖拽平移漫游。
  - **古典黄铜透镜 · 艺术微距探秘放大镜 (Artisan Brass Loupe)**：
    - 独立轻量圆形透镜（双圈香槟金倒角阴影、月牙高光玻璃、微米级十字准星）；
    - 实时采集光标/指尖对应名画的高清原始像素切片，以 $100\%$ 原始真彩与 $2.0\times / 3.5\times / 5.0\times$ 超高倍率直出；
    - 即使外部全景处于黑白沉睡状态，透镜内部依然穿透呈现原画真实璀璨的色彩与厚重颜料笔触；
    - 支持快捷键 `M` / `Z` 盲操一键开启/关闭。
- **屏幕比例自适应模型 (Aspect Ratio Engine)**：
  - 宽屏电脑/平板横屏（$\text{Aspect} \ge 1.0$）：横幅画作铺满沉浸，方幅/竖幅画作保留雅致留白；
  - 手机竖屏（$\text{Aspect} < 1.0$）：智能自适应 contain 模式，横幅贴合 98% 屏宽最大化展现高度；
  - 手机旋转为横屏时自动无缝切换为影院级全景宽屏。
- **现代视口标准**：全面采用 `100dvh` 与 `window.visualViewport` 动态计算，配合 iOS/Android 刘海屏与底部横条安全区（`env(safe-area-inset-*)`）。
- **知名度驱动的全局排序 (Fame Ranking)**：
  - `data/masterpieces.js` 中每幅画带 `fame`（0-100 整数），数组本身按 `fame` 降序存放，因此展厅列表、上下幅切画、首屏默认画作三处共用同一“知名度序”，无需前端再排序；
  - 分档口径：100-96 人类级文化符号（蒙娜丽莎 100、星夜/呐喊 99）、95-88 教科书封面级、87-78 大师代表作、77-66 流派标志作、65-50 系列变体与次要名作、50 以下学术型佳作；
  - 分数由 `scripts/score_fame.py` 统一维护（逐幅显式评分 + 画家基准分兜底），调整知名度只改这一张表后重跑即可；
  - 展厅卡片序号 = 全库知名度排名，因此按画家/题材筛选后序号会跳号，属预期语义（排名不因过滤而重编）。

## 3. 模块实现与实测状态
- [x] **420 幅传世名画数据库** (`data/masterpieces.js`，全部通过高分辨率与元数据审计)
- [x] **深度鉴赏智库与故事档案** (`data/art_stories.js`，420 幅作品的创作背景、艺术看点与大师名言)
- [x] **原生 ESM 模块化拆分重构** (`js/` 11 大模块，通过 `node -c` 与 Chrome DevTools E2E 全链路回归测试)
- [x] **智能双向预加载池** (`js/utils/preload-pool.js`，Index $\pm 1$ 预载与 LRU 缓存，切画零黑屏)
- [x] **多维展厅分类与搜索系统** (`js/ui/gallery-drawer.js`，支持 6 大核心题材药丸、131 位大师下拉、时期画派与热门巨匠快捷筛选)
- [x] **画布级双指平移缩放 (Pinch-to-zoom & Pan)** (`js/engine/macro-loupe.js`，手势平滑顺畅)
- [x] **古典黄铜透镜 · 艺术微距探秘放大镜** (`js/engine/macro-loupe.js`，原画高精切片真彩直出，支持 2.0x / 3.5x / 5.0x 切换)
- [x] **微距缩放浮动指示胶囊与一键平滑复位** (`#macro-zoom-hud`，点击或双击弹性复位)
- [x] **手机端触控防下拉刷新与手势防误触互锁**（单指涂抹、双指缩放、双击复位、左右轻扫协同工作）
- [x] **操作指南手势与快捷键指引** (`js/ui/help-modal.js`)

## 4. 关键配置文件与资源位置
- **核心入口页面**：`index.html` (使用 `<script type="module" src="js/main.js?v=4.6.0"></script>`)
- **主模块目录**：`js/`
  - `js/state.js` (状态与配置)
  - `js/engine/` (渲染与微距透镜)
  - `js/ui/` (展厅、鉴赏故事、画笔调节面板、帮助弹窗)
  - `js/events/` (多模态输入总线)
  - `js/utils/` (智能预加载池)
  - `js/main.js` (装配中枢与调试入口)
- **单文件历史参考**：`app.js` (保留备份)
- **核心样式表**：`style.css` (动态视口高度、微距胶囊、黄铜透镜、安全区避让)
- **名画数据源**：`data/masterpieces.js`
- **名画故事源**：`data/art_stories.js`
- **本地高清画作资源库**：`assets/images/`（420 张）与 `assets/thumbs/`（420 张 400px WebP 缩略图）
- **藏品台账**：`docs/COLLECTED_ARTWORKS.md`（由 `scripts/generate_catalog_md.py` 从数据源自动生成，含 fame 知名度列，勿手改）
- **知名度评级**：`scripts/score_fame.py`（420 幅逐幅打分，写入 `fame` 字段并重排数组）
- **扩充流水线工具**：
  - `scripts/gap_candidates_*.json`：候选画作元数据（含检索式）
  - `scripts/harvest_gap_batch.py`：批量采集（含文件名真伪校验）
  - `scripts/repair_gap_batch.py` + `scripts/gap_repair_specs.json`：定点修补失败/错配作品
  - `scripts/merge_gap_batch.py`：合并入库、分类计数与版本戳
  - `scripts/build_thumbs.py`：生成 400px WebP 缩略图
  - `scripts/make_contact_sheet.py`：生成带标签联络表供人工视觉核对

## 5. 踩坑与避错记录 (What Didn't Work & Solutions)
1. **双指缩放与单指涂抹打架**：
   - 踩坑：若未做手势互锁，双指捏合时会被识别为单指画笔划动，在名画上划出杂乱透明线条。
   - 解决：在 `touchstart` 捕获 `touches.length === 2` 时立即激活 `isPinching = true` 并将 `isPointerActive = false`；在 `touchmove` 与 `touchend` 期间彻底屏蔽涂抹，抬手后方恢复单指涂抹。
2. **放大状态下双击冲突**：
   - 踩坑：原本双击是全彩切换，如果用户放大到局部想恢复全貌，无法直观重置。
   - 解决：智能分流双击事件——放大状态下（`macroZoom > 1.05`）双击执行弹性平滑复位至 100%；100% 全貌时双击切换全彩盛放。
3. **放大状态下轻扫切画误触**：
   - 踩坑：在放大局部探索漫游时，用户向左或向右拖动容易误触发上一幅/下一幅轻扫切换。
4. **全局 `cursor: none` 导致鼠标丢失**：
   - 踩坑：在 `html, body` 强行设为 `cursor: none`，依赖自定义光标；当光标移至非舞台区或面板、或被事件重置时，原生指针为 none，用户屏幕上的鼠标彻底消失。
   - 解决：恢复 `html, body` 为 `cursor: default`，自定义艺术光标仅作为轻量跟随光环；微距放大时呈现 `grab` / `grabbing` 抓手光标，所有交互面板强制原生系统指针，光标 100% 稳定永不消失。
5. **微距透镜与主画布涂抹冲突**：
   - 踩坑：开启微距放大镜后，鼠标移动时依然执行 `strokeLine` 与 `applyDab`，导致边看画边涂花底层名画；且透镜上的小徽章跟随光标移动，光标永远点不到徽章。
   - 解决：微距透镜激活时彻底解耦画布涂抹（移动时纯粹探视）；移除透镜上的跟随按钮，将倍率选择优雅整合至画笔面板与滚轮调焦。
6. **手机双指捏合松手瞬态竞争与跳画**：
   - 踩坑：双指松开时两指不可能绝对同时离屏，先离开一指时系统会误捕获为单指滑动或双击。
   - 解决：引入 `pinchCooldownUntil` 350ms 冷却保护期，双指松手期间严格屏蔽任何单指事件，彻底消灭手势抖动与跳画。
7. **Commons 检索“张冠李戴”（扩充期最大隐患）**：
   - 踩坑：以「画家 + 画名 + 馆藏」检索 Wikimedia Commons 时，搜索引擎会返回别家画家的相近作品。曾出现搜乌切洛得到利皮《三博士来朝》、搜提香《珀耳修斯》得到莱顿同名画、搜蒙克《生命之舞》得到《圣母》等错配。
   - 解决：`museum_harvester.harvest()` 新增 `verify` 回调，批处理按「文件名必须含目标画家姓氏，否则要求画名关键词命中率 ≥85%，且『艺术家 - 作品』命名格式但艺术家不符一律否决」过滤候选；再辅以 `scripts/make_contact_sheet.py` 的联络表人工复核（可一眼识别相框、展厅游客照、局部裁切、文物品明信片）。
8. **展厅相框/游客照/局部裁切混入库**：
   - 踩坑：部分 Commons 图片带金框、玻璃反光与游客、或只是局部细节裁切，违反《ART_SELECTION_SPEC》纯净度红线。
   - 解决：`scripts/repair_gap_batch.py` 按 id 指定强制匹配词（如 `bethsabee`、`il vecchio bertin`、`patizambo`）+ 黑名单（`detail`、`panoramio`、`framed`）重采，并逐张生成联络表目视确认。
9. **冷启动首帧视口为 0 导致初始化中断**：
   - 踩坑：首次访问时容器尚未布局，`visualViewport` 尺寸为 0，`Math.ceil(0 / cellSize)` 得到 0 列 0 行，`createImageData(0, 0)` 抛 `IndexSizeError`，整个画布初始化中断，页面永久停在「正在加载」。
   - 解决：`handleResize()` 检测到视口 < 1px 时用 `requestAnimationFrame` 延迟一帧重试（`appState.resizeRetryScheduled` 防重入）；`initGrid()` 对 0 行列直接放弃本次重建。

## 6. 新窗口快速唤醒 Prompt 与本地运行指令

**在新会话窗口直接粘贴：**
> 我正在进行 Masterpiece Garden（传世名画博览馆）的开发与维护，当前已完成 PC 端与手机端屏幕比例自适应、触控手势、鉴赏故事智库、局部微距探秘放大镜、双指细节缩放、原生 ESM 模块化架构（v4.8.0），名画库 420 幅并按知名度 fame 权重降序排列。请先阅读根目录下的 `HANDOFF.md` 了解当前状态与架构，然后继续执行。

**本地运行与验证指令：**
```powershell
# 在项目根目录下启动本地静态服务器进行多端预览与调试
python -m http.server 8090
# 浏览器访问：http://localhost:8090
```

> 注：本机 8000 端口会被系统保留（`WinError 10013`），故统一使用 8090。
> 切勿直接双击 `index.html`：`file://` 下浏览器会拦截 ES Module，页面会停在「请通过本地服务器打开本馆」提示页。
> 服务重启/换端口后，旧标签页的页面外壳仍在内存里（看起来还能用），但新发起的缩略图请求会全部 404，表现为「展厅缩略图全是裂图」——重开新地址或强制刷新即可。
