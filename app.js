/**
 * Masterpiece Garden · Interactive Fine Art Engine (v3.2.0)
 * 传世名画级交互引擎：多层划动渐进显色、停驻充能与画笔大小调节
 *
 * 核心交互机制：
 * 1. 默认底色为沉静古典灰阶（与原画 1:1 像素级精准契合）；
 * 2. 划动显色需多划几下：单次轻划只透出浅浅一层（约 25% 灰度透彩），来回划动 3~4 次才层层累加至 100% 鲜艳原色；
 * 3. 停驻充能机制：鼠标停留在某处不移动时持续充能，约 0.4 秒迅速绽放为 100% 满彩，悬停之处永远盛开；
 * 4. 独立留存衰减：停止涂抹后，该区域保持原有艳丽度 3.0 秒不掉色，随后 2.0 秒内如晨雾般优雅淡出退回灰色；
 * 5. 画笔大小动态调节：提供典雅的小图标与滑块面板，支持实时预览与光标尺寸联动。
 */

(function () {
    'use strict';

    // 核心画布与界面元素
    const bgCanvas = document.getElementById('bg-canvas');
    const revealCanvas = document.getElementById('reveal-canvas');
    const artQuote = document.getElementById('art-quote');
    const quoteTextEl = artQuote ? artQuote.querySelector('.quote-text') : null;
    const quoteAuthorEl = artQuote ? artQuote.querySelector('.quote-author') : null;
    const cursor = document.getElementById('custom-cursor');
    const cursorRing = cursor ? cursor.querySelector('.cursor-ring') : null;

    // 画笔控制 UI 元素
    const brushToggleBtn = document.getElementById('brush-toggle-btn');
    const brushPopup = document.getElementById('brush-popup');
    const brushSlider = document.getElementById('brush-size-slider');
    const brushSizeDisplay = document.getElementById('brush-size-display');
    const brushPreviewDot = document.getElementById('brush-preview-dot');
    const brushDurationSlider = document.getElementById('brush-duration-slider');
    const brushDurationDisplay = document.getElementById('brush-duration-display');
    const colorRatioSlider = document.getElementById('brush-color-ratio-slider');
    const colorRatioDisplay = document.getElementById('brush-color-ratio-display');
    const toggleFullColorBtn = document.getElementById('toggle-full-color-btn');
    const fullColorBtnText = document.getElementById('full-color-btn-text');

    // 模式切换与随机漫游控制 UI 元素
    const modeSleepBtn = document.getElementById('mode-sleep-btn');
    const modeScratchBtn = document.getElementById('mode-scratch-btn');
    const sleepModeControls = document.getElementById('sleep-mode-controls');
    const scratchModeControls = document.getElementById('scratch-mode-controls');
    const scratchThresholdSlider = document.getElementById('scratch-threshold-slider');
    const scratchThresholdDisplay = document.getElementById('scratch-threshold-display');
    const scratchRatioDisplay = document.getElementById('scratch-ratio-display');
    const scratchMiniBarFill = document.getElementById('scratch-mini-bar-fill');
    const scratchRevealNowBtn = document.getElementById('scratch-reveal-now-btn');
    const scratchHud = document.getElementById('scratch-hud');
    const scratchHudPercent = document.getElementById('scratch-hud-percent');
    const scratchHudTargetVal = document.getElementById('scratch-hud-target-val');
    const scratchHudFill = document.getElementById('scratch-hud-fill');

    // 画面规格与缩放控制 UI 元素
    const fitAutoBtn = document.getElementById('fit-auto-btn');
    const fitContainBtn = document.getElementById('fit-contain-btn');
    const fitCoverBtn = document.getElementById('fit-cover-btn');
    const fitModeDisplay = document.getElementById('fit-mode-display');
    const fitScaleSlider = document.getElementById('fit-scale-slider');
    const fitScaleDisplay = document.getElementById('fit-scale-display');

    // 微距细节探索与古典黄铜透镜 UI 元素
    const macroZoomHud = document.getElementById('macro-zoom-hud');
    const macroZoomPercent = document.getElementById('macro-zoom-percent');
    const macroZoomResetBtn = document.getElementById('macro-zoom-reset-btn');
    const macroLoupe = document.getElementById('macro-loupe');
    const macroLoupeCanvas = document.getElementById('macro-loupe-canvas');
    const macroLoupeCtx = macroLoupeCanvas ? macroLoupeCanvas.getContext('2d') : null;
    const toggleLoupeBtn = document.getElementById('toggle-loupe-btn');
    const loupePillStatus = document.getElementById('loupe-pill-status');
    const loupeOptionsBox = document.getElementById('loupe-options-box');

    // 名画画廊切换 UI 元素 (画笔面板卡片)
    const masterpieceIndexBadge = document.getElementById('masterpiece-index');
    const openGalleryModalBtn = document.getElementById('open-gallery-modal-btn');
    const currentArtThumb = document.getElementById('current-art-thumb');
    const currentArtTitle = document.getElementById('current-art-title');
    const currentArtArtist = document.getElementById('current-art-artist');
    const prevArtBtn = document.getElementById('prev-art-btn');
    const nextArtBtn = document.getElementById('next-art-btn');

    // 传世名画博览馆 · 典藏搜索与多维分类抽屉展厅 UI 元素
    const galleryOpenBtn = document.getElementById('gallery-open-btn');
    const galleryOpenBadge = document.getElementById('gallery-open-badge');
    const galleryDrawer = document.getElementById('gallery-drawer');
    const galleryBackdrop = document.getElementById('gallery-backdrop');
    const galleryCloseBtn = document.getElementById('gallery-close-btn');
    const gallerySearchInput = document.getElementById('gallery-search-input');
    const gallerySearchClear = document.getElementById('gallery-search-clear');
    const genrePillsContainer = document.getElementById('genre-pills-container');
    const artistFilterSelect = document.getElementById('artist-filter-select');
    const categoryFilterSelect = document.getElementById('category-filter-select');
    const quickArtistsContainer = document.getElementById('quick-artists-container');
    const galleryResultCount = document.getElementById('gallery-result-count');
    const galleryFilterDesc = document.getElementById('gallery-filter-desc');
    const galleryResetBtn = document.getElementById('gallery-reset-btn');
    const galleryListContainer = document.getElementById('gallery-list-container');

    // 名画背景故事与艺术鉴赏抽屉 UI 元素
    const storyToggleBtn = document.getElementById('story-toggle-btn');
    const brushStoryBtn = document.getElementById('brush-story-btn');
    const storyDrawer = document.getElementById('story-drawer');
    const storyBackdrop = document.getElementById('story-backdrop');
    const storyCloseBtn = document.getElementById('story-close-btn');
    const storyTitle = document.getElementById('story-title');
    const storyEntitle = document.getElementById('story-entitle');
    const storyArtist = document.getElementById('story-artist');
    const storyPeriod = document.getElementById('story-period');
    const storyGenre = document.getElementById('story-genre');
    const storyLocation = document.getElementById('story-location');
    const storyContext = document.getElementById('story-context');
    const storyAppreciation = document.getElementById('story-appreciation');
    const storyQuoteText = document.getElementById('story-quote-text');
    const storyQuoteAuthor = document.getElementById('story-quote-author');
    const storyPrevBtn = document.getElementById('story-prev-btn');
    const storyNextBtn = document.getElementById('story-next-btn');

    // 操作引导与快捷键指南 UI 元素
    const interactiveHint = document.getElementById('interactive-hint');
    const hintTextEl = document.getElementById('hint-text');
    const modeToast = document.getElementById('mode-toast');
    const toastIconEl = document.getElementById('toast-icon');
    const toastTextEl = document.getElementById('toast-text');
    const helpToggleBtn = document.getElementById('help-toggle-btn');
    const helpModal = document.getElementById('help-modal');
    const helpBackdrop = document.getElementById('help-backdrop');
    const helpCloseBtn = document.getElementById('help-close-btn');
    const helpGotItBtn = document.getElementById('help-got-it-btn');

    let isHintDismissed = false;
    let toastTimer = null;

    const bgCtx = bgCanvas.getContext('2d');
    const revealCtx = revealCanvas.getContext('2d');

    // 离屏遮罩画布 (全分辨率) 与低分辨率网格采样画布
    const maskCanvas = document.createElement('canvas');
    const maskCtx = maskCanvas.getContext('2d');

    const maskSmallCanvas = document.createElement('canvas');
    const maskSmallCtx = maskSmallCanvas.getContext('2d', { willReadFrequently: true });

    // 模式状态：'sleep' (沉睡唤醒) | 'scratch' (随机漫游擦画)
    let appMode = 'sleep';

    // 随机漫游擦画模式核心状态机
    const scratchConfig = {
        threshold: 0.85,             // 默认 85% 触发自动完全展开 (0.50 ~ 0.95)
        isLocked: false,             // 关键状态机锁：一幅画未完全展示出来前，严禁擦除！
        isTransitioning: false,      // 正在进行平滑揭晓过渡
        ratio: 0.0,                  // 当前已擦除露出面积比例 (0.0 ~ 1.0)
        historyQueue: [],            // 历史防重复队列
        maxHistoryLen: 30            // 记忆最近 30 幅画作防重复
    };

    // 下一幅名画原图与几何参数 (用于随机模式底层透出)
    const nextGardenImage = new Image();
    let isNextImageLoaded = false;
    let nextMasterpieceIndex = -1;
    let nextImageBounds = { x: 0, y: 0, w: 0, h: 0 };

    // 交互参数配置
    const config = {
        brushRadius: 75,             // 默认画笔半径 (px)
        minBrushRadius: 35,          // 最小画笔半径
        maxBrushRadius: 160,         // 最大画笔半径
        colorRatio: 1.0,             // 划过唤醒显色比例 (0.2 ~ 1.0, 默认 1.0 即 100%)
        singlePassGain: 0.26,        // 单次划过最大显色增量 (需多划 3~4 次才满彩)
        hoverChargeGain: 0.12,       // 悬停充能增量 (每 45ms 递增)
        totalDurationSeconds: 12,    // 默认色彩留存总时长 (12 秒)
        solidDurationMs: 8500,       // 涂抹后 100% 彩色高光保持不褪色时长 (8.5 秒)
        fadeDurationMs: 3500,        // 保持期过后优雅平滑渐隐淡出时长 (3.5 秒)
        cellSize: 14,                // 空间衰减网格分辨率 (px)
        fitMode: 'auto',             // 画面规格模式: 'auto' (智能) | 'contain' (完整) | 'cover' (铺满)
        scale: 1.0,                  // 用户自定义缩放倍率 (0.6 ~ 1.4)
    };

    let viewportWidth = window.innerWidth;
    let viewportHeight = window.innerHeight;
    let dpr = window.devicePixelRatio || 1;

    // 空间状态网格系统 (记录每个网格的透明度、最后触碰时间和笔划ID)
    let gridCols = 0;
    let gridRows = 0;
    let totalCells = 0;
    let gridAlpha = null;        // 当前累积显色度/不透明度 (0.0 ~ 1.0)
    let gridLastTouch = null;    // 最后被划过或充能的时间戳 (ms)
    let gridLastStroke = null;   // 最后一次修改该单元格的笔画 ID
    let maskSmallImageData = null;

    // 鼠标与笔划跟踪状态
    let isPointerActive = false;
    let currentPointerPos = null;
    let lastPointerPos = null;
    let lastMoveTime = 0;
    let lastHoverChargeTime = 0;
    let currentStrokeId = 1;
    let strokeMoveDistance = 0;
    let lastMoveVector = { x: 0, y: 0 };
    let isInitialized = false;
    let isFullColorLocked = false;

    // 高性能按需渲染控制与增量统计
    let isDirty = true;
    let isRenderingActive = false;
    let scratchedCellsCount = 0;             // O(1) 维护漫游模式已擦除单元格总数
    const SCRATCH_MASK_THRESHOLD = 0.35;     // 判定为透出底层新画的遮罩阈值
    let lastRenderedHudPct = -1;             // 缓存已渲染 HUD 百分比，杜绝高频 DOM 重排
    // 微距细节探索与画布平移漫游核心状态 (Pinch-to-zoom & Canvas Pan)
    let macroZoom = 1.0;                     // 微距缩放倍率 (1.0 ~ 4.5)
    let panOffset = { x: 0, y: 0 };          // 画布平移偏移量 (px)
    let zoomAnimRaf = null;                  // 复位动画 RAF 句柄

    // 古典黄铜透镜 · 艺术微距探秘放大镜核心状态 (Artisan Brass Loupe)
    let isLoupeEnabled = false;              // 透镜是否开启
    let loupeZoom = 3.5;                     // 当前透镜倍率 (2.0 / 3.5 / 5.0)
    const loupeZoomLevels = [2.0, 3.5, 5.0];
    let loupeZoomIndex = 1;
    let lastLoupePointerPos = { x: -9999, y: -9999 };
    let isLoupeVisible = false;

    /**
     * 标记画布需要重绘，并按需唤醒帧渲染循环 (静止时 0 开销)
     */
    function markDirty() {
        isDirty = true;
        if (!isRenderingActive) {
            isRenderingActive = true;
            requestAnimationFrame(renderLoop);
        }
    }

    // 传世名画博览馆数据库 (由 data/masterpieces.js 注入全量名作)
    const masterpieces = (window.MASTERPIECES && window.MASTERPIECES.length) ? window.MASTERPIECES : [];

    let currentMasterpieceIndex = 0;

    // 名画原图加载与几何参数
    const gardenImage = new Image();
    let isImageLoaded = false;
    let imageBounds = { x: 0, y: 0, w: 0, h: 0 };

    /**
     * 初始化或重新分配空间衰减网格
     */
    function initGrid() {
        gridCols = Math.ceil(viewportWidth / config.cellSize);
        gridRows = Math.ceil(viewportHeight / config.cellSize);
        totalCells = gridCols * gridRows;

        gridAlpha = new Float32Array(totalCells);
        gridLastTouch = new Float64Array(totalCells);
        gridLastStroke = new Int32Array(totalCells);
        scratchedCellsCount = 0;

        maskSmallCanvas.width = gridCols;
        maskSmallCanvas.height = gridRows;
        maskSmallImageData = maskSmallCtx.createImageData(gridCols, gridRows);

        // 默认将小遮罩填充为纯白通道 (RGB=255)，仅动态调制 Alpha 通道
        const data = maskSmallImageData.data;
        for (let i = 0; i < totalCells; i++) {
            const p = i * 4;
            data[p] = 255;
            data[p + 1] = 255;
            data[p + 2] = 255;
            data[p + 3] = 0;
        }

        markDirty();
    }

    /**
     * 计算名画在视口中的几何布局参数 (深度优化：手机竖屏/横屏/电脑宽屏智能自适应)
     */
    function computeImageBounds() {
        if (!isImageLoaded) return;
        const imgW = gardenImage.naturalWidth || 2560;
        const imgH = gardenImage.naturalHeight || 1440;
        const imgAspect = imgW / imgH;
        const screenAspect = viewportWidth / viewportHeight;

        let effectiveMode = config.fitMode;
        if (effectiveMode === 'auto') {
            if (screenAspect >= 1.0) {
                // 1. 桌面端 / 平板横屏 / 手机横屏 (宽屏视野)
                if (screenAspect > 1.2 && imgAspect < 1.22) {
                    effectiveMode = 'contain';
                } else {
                    effectiveMode = 'cover';
                }
            } else {
                // 2. 手机竖屏模式 (screenAspect 通常在 0.45 ~ 0.65 之间，屏幕极窄极高)
                // 竖幅肖像、方幅与横幅画作在手机竖屏下均采用智能完整呈现，杜绝大幅裁剪主体
                effectiveMode = 'contain';
            }
        }

        let drawW, drawH;
        if (effectiveMode === 'contain') {
            // 完整呈现模式：
            // 手机竖屏时采用 0.98 贴合留白，桌面宽屏采用 0.94 雅致画廊留白
            const containRatio = (screenAspect < 1.0) ? 0.98 : 0.94;
            if (screenAspect > imgAspect) {
                drawH = viewportHeight * containRatio;
                drawW = drawH * imgAspect;
            } else {
                drawW = viewportWidth * containRatio;
                drawH = drawW / imgAspect;
            }
        } else {
            // 居中铺满模式 (Cover)：
            if (screenAspect >= 1.0) {
                if (screenAspect > imgAspect) {
                    drawW = viewportWidth;
                    drawH = viewportWidth / imgAspect;
                } else {
                    drawH = viewportHeight;
                    drawW = viewportHeight * imgAspect;
                }
            } else {
                // 手机竖屏下的铺满优化：
                // 如果是横幅画作，避免直接按视口高度完全拉伸导致左右裁剪超过 75%
                if (imgAspect > 1.15) {
                    // 横幅画在手机竖屏下的铺满：兼顾沉浸感与构图主体
                    drawH = Math.max(viewportHeight * 0.72, viewportWidth);
                    drawW = drawH * imgAspect;
                } else {
                    // 方幅与竖幅名画自然铺满
                    if (screenAspect > imgAspect) {
                        drawW = viewportWidth;
                        drawH = viewportWidth / imgAspect;
                    } else {
                        drawH = viewportHeight;
                        drawW = viewportHeight * imgAspect;
                    }
                }
            }
        }

        // 应用用户自定义缩放倍率
        drawW *= config.scale;
        drawH *= config.scale;

        // 应用微距探索缩放倍率 (macroZoom: 1.0 ~ 4.5)
        const finalW = drawW * macroZoom;
        const finalH = drawH * macroZoom;

        // 边界阻尼约束：微距放大时限制平移范围，防止画作被拖出视口消失
        if (macroZoom <= 1.01) {
            panOffset.x = 0;
            panOffset.y = 0;
        } else {
            const maxPanX = Math.max(0, (finalW - viewportWidth) / 2 + viewportWidth * 0.25);
            const maxPanY = Math.max(0, (finalH - viewportHeight) / 2 + viewportHeight * 0.25);
            panOffset.x = Math.max(-maxPanX, Math.min(maxPanX, panOffset.x));
            panOffset.y = Math.max(-maxPanY, Math.min(maxPanY, panOffset.y));
        }

        // 视口绝对中心对称对齐加上平移偏移量
        const drawX = (viewportWidth - finalW) / 2 + panOffset.x;
        const drawY = (viewportHeight - finalH) / 2 + panOffset.y;

        imageBounds = {
            x: drawX,
            y: drawY,
            w: finalW,
            h: finalH,
            baseW: drawW,
            baseH: drawH,
            effectiveMode: effectiveMode
        };
    }

    /**
     * 计算下一幅名画在视口中的几何布局参数 (用于随机漫游模式底层全景透出)
     */
    function computeNextImageBounds() {
        if (!isNextImageLoaded) return;
        const imgW = nextGardenImage.naturalWidth || 2560;
        const imgH = nextGardenImage.naturalHeight || 1440;
        const imgAspect = imgW / imgH;
        const screenAspect = viewportWidth / viewportHeight;

        let effectiveMode = config.fitMode;
        if (effectiveMode === 'auto') {
            if (screenAspect >= 1.0) {
                if (screenAspect > 1.2 && imgAspect < 1.22) {
                    effectiveMode = 'contain';
                } else {
                    effectiveMode = 'cover';
                }
            } else {
                effectiveMode = 'contain';
            }
        }

        let drawW, drawH;
        if (effectiveMode === 'contain') {
            const containRatio = (screenAspect < 1.0) ? 0.98 : 0.94;
            if (screenAspect > imgAspect) {
                drawH = viewportHeight * containRatio;
                drawW = drawH * imgAspect;
            } else {
                drawW = viewportWidth * containRatio;
                drawH = drawW / imgAspect;
            }
        } else {
            if (screenAspect >= 1.0) {
                if (screenAspect > imgAspect) {
                    drawW = viewportWidth;
                    drawH = viewportWidth / imgAspect;
                } else {
                    drawH = viewportHeight;
                    drawW = viewportHeight * imgAspect;
                }
            } else {
                if (imgAspect > 1.15) {
                    drawH = Math.max(viewportHeight * 0.72, viewportWidth);
                    drawW = drawH * imgAspect;
                } else {
                    if (screenAspect > imgAspect) {
                        drawW = viewportWidth;
                        drawH = viewportWidth / imgAspect;
                    } else {
                        drawH = viewportHeight;
                        drawW = viewportHeight * imgAspect;
                    }
                }
            }
        }

        drawW *= config.scale;
        drawH *= config.scale;

        const finalW = drawW * macroZoom;
        const finalH = drawH * macroZoom;
        const drawX = (viewportWidth - finalW) / 2 + panOffset.x;
        const drawY = (viewportHeight - finalH) / 2 + panOffset.y;

        nextImageBounds = {
            x: drawX,
            y: drawY,
            w: finalW,
            h: finalH,
            baseW: drawW,
            baseH: drawH,
            effectiveMode: effectiveMode
        };
    }

    /**
     * 更新微距缩放浮动指示器 (HUD)
     */
    function updateMacroZoomHud() {
        if (!macroZoomHud || !macroZoomPercent) return;
        if (macroZoom > 1.05 || Math.abs(panOffset.x) > 5 || Math.abs(panOffset.y) > 5) {
            macroZoomHud.style.display = 'block';
            macroZoomPercent.textContent = Math.round(macroZoom * 100) + '%';
        } else {
            macroZoomHud.style.display = 'none';
        }
    }

    /**
     * 平滑弹性复位微距缩放与平移漫游回到 100% 全景
     * @param {boolean} instant 是否立即瞬时复位（切画时使用）
     */
    function resetMacroZoom(instant = false) {
        if (zoomAnimRaf) {
            cancelAnimationFrame(zoomAnimRaf);
            zoomAnimRaf = null;
        }

        if (instant) {
            macroZoom = 1.0;
            panOffset.x = 0;
            panOffset.y = 0;
            refreshLayout();
            updateMacroZoomHud();
            if (isLoupeEnabled && lastLoupePointerPos.x > 0) {
                renderMacroLoupe(lastLoupePointerPos.x, lastLoupePointerPos.y);
            }
            return;
        }

        const startZoom = macroZoom;
        const startPanX = panOffset.x;
        const startPanY = panOffset.y;
        const startTime = performance.now();
        const duration = 280; // 280ms 优雅回弹

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(1.0, elapsed / duration);
            // 经典三次方缓动曲线 easeOutCubic
            const ease = 1 - Math.pow(1 - progress, 3);

            macroZoom = startZoom + (1.0 - startZoom) * ease;
            panOffset.x = startPanX + (0 - startPanX) * ease;
            panOffset.y = startPanY + (0 - startPanY) * ease;

            refreshLayout();
            updateMacroZoomHud();

            if (isLoupeEnabled && lastLoupePointerPos.x > 0) {
                renderMacroLoupe(lastLoupePointerPos.x, lastLoupePointerPos.y);
            }

            if (progress < 1.0) {
                zoomAnimRaf = requestAnimationFrame(step);
            } else {
                macroZoom = 1.0;
                panOffset.x = 0;
                panOffset.y = 0;
                refreshLayout();
                updateMacroZoomHud();
                zoomAnimRaf = null;
            }
        }
        zoomAnimRaf = requestAnimationFrame(step);
    }

    /**
     * 古典黄铜透镜 · 艺术微距探秘放大镜渲染管线
     * 实时采集光标下方对应名画的高清原始像素切片，以 100% 真彩与超高放大倍率呈现
     */
    function renderMacroLoupe(screenX, screenY) {
        if (!isLoupeEnabled || !macroLoupe || !macroLoupeCanvas || !macroLoupeCtx || !isImageLoaded) return;

        // 若光标超出视口，平滑隐匿
        if (screenX < 0 || screenX > viewportWidth || screenY < 0 || screenY > viewportHeight) {
            macroLoupe.classList.remove('active');
            isLoupeVisible = false;
            return;
        }

        macroLoupe.style.left = screenX + 'px';
        macroLoupe.style.top = screenY + 'px';
        if (!isLoupeVisible) {
            macroLoupe.classList.add('active');
            isLoupeVisible = true;
        }

        // 计算准星对应在名画矩形中的归一化 UV 坐标
        const relU = (screenX - imageBounds.x) / imageBounds.w;
        const relV = (screenY - imageBounds.y) / imageBounds.h;

        const natW = gardenImage.naturalWidth || 2560;
        const natH = gardenImage.naturalHeight || 1440;

        const centerNatX = relU * natW;
        const centerNatY = relV * natH;

        const canvasW = macroLoupeCanvas.width;
        const canvasH = macroLoupeCanvas.height;

        // 依据透镜放大倍率计算在原画高精底图上的采样矩形跨度
        const screenPxToNatPx = natW / imageBounds.w;
        const srcSpanW = (canvasW * screenPxToNatPx) / loupeZoom;
        const srcSpanH = (canvasH * screenPxToNatPx) / loupeZoom;

        const srcX = centerNatX - srcSpanW / 2;
        const srcY = centerNatY - srcSpanH / 2;

        macroLoupeCtx.clearRect(0, 0, canvasW, canvasH);
        macroLoupeCtx.save();
        // 垫一层典雅古典暗色底，防止画幅边缘透明穿帮
        macroLoupeCtx.fillStyle = '#0d0f12';
        macroLoupeCtx.fillRect(0, 0, canvasW, canvasH);

        macroLoupeCtx.imageSmoothingEnabled = true;
        macroLoupeCtx.imageSmoothingQuality = 'high';
        macroLoupeCtx.drawImage(
            gardenImage,
            srcX,
            srcY,
            srcSpanW,
            srcSpanH,
            0,
            0,
            canvasW,
            canvasH
        );
        macroLoupeCtx.restore();
    }

    /**
     * 设置古典微距透镜放大倍率 (支持滚轮无级微调与预设档位)
     */
    function setLoupeZoom(z) {
        loupeZoom = Math.max(1.5, Math.min(6.0, Math.round(z * 10) / 10));
        if (loupeOptionsBox) {
            const chips = loupeOptionsBox.querySelectorAll('.loupe-zoom-chip');
            chips.forEach(chip => {
                const chipZ = parseFloat(chip.dataset.zoom);
                chip.classList.toggle('active', Math.abs(chipZ - loupeZoom) < 0.2);
            });
        }
        showToast(`🔍 透镜倍率: ${loupeZoom.toFixed(1)}×`);
        if (isLoupeVisible && lastLoupePointerPos.x > 0) {
            renderMacroLoupe(lastLoupePointerPos.x, lastLoupePointerPos.y);
        }
    }

    /**
     * 开启 / 关闭古典微距探秘透镜
     */
    function toggleLoupe(forcedState) {
        isLoupeEnabled = (forcedState !== undefined) ? forcedState : !isLoupeEnabled;
        if (toggleLoupeBtn) {
            toggleLoupeBtn.classList.toggle('active', isLoupeEnabled);
        }
        if (loupePillStatus) {
            loupePillStatus.textContent = isLoupeEnabled ? '已开启' : '已关闭';
        }
        if (loupeOptionsBox) {
            loupeOptionsBox.style.display = isLoupeEnabled ? 'block' : 'none';
        }
        if (macroLoupe) {
            macroLoupe.style.display = isLoupeEnabled ? 'block' : 'none';
            if (!isLoupeEnabled) {
                macroLoupe.classList.remove('active');
                isLoupeVisible = false;
            }
        }
        showToast(isLoupeEnabled ? '🔍 已开启古典真彩微距探秘透镜' : '🔍 已关闭微距透镜');
        if (isLoupeEnabled && lastLoupePointerPos.x > 0) {
            renderMacroLoupe(lastLoupePointerPos.x, lastLoupePointerPos.y);
        }
    }

    /**
     * 循环切换微距放大镜预设倍率 (2.0× -> 3.5× -> 5.0×)
     */
    function cycleLoupeZoom() {
        loupeZoomIndex = (loupeZoomIndex + 1) % loupeZoomLevels.length;
        setLoupeZoom(loupeZoomLevels[loupeZoomIndex]);
    }

    /**
     * 刷新视口布局与底图重绘
     */
    function refreshLayout() {
        computeImageBounds();
        computeNextImageBounds();

        if (appMode === 'scratch') {
            renderScratchBackground();
        } else {
            renderGrayscaleBackground();
            if (isFullColorLocked) {
                revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
                revealCtx.save();
                revealCtx.globalAlpha = config.colorRatio;
                revealCtx.drawImage(
                    gardenImage,
                    imageBounds.x,
                    imageBounds.y,
                    imageBounds.w,
                    imageBounds.h
                );
                revealCtx.restore();
            }
        }
        markDirty();
    }

    /**
     * 渲染底层古典灰阶油画 (经典沉睡模式)
     */
    function renderGrayscaleBackground() {
        if (!isImageLoaded) return;
        bgCtx.save();
        bgCtx.clearRect(0, 0, viewportWidth, viewportHeight);
        bgCtx.filter = 'grayscale(100%)';
        bgCtx.drawImage(
            gardenImage,
            imageBounds.x,
            imageBounds.y,
            imageBounds.w,
            imageBounds.h
        );
        bgCtx.restore();
    }

    /**
     * 渲染底层下一幅名画 (随机漫游模式：无需变灰，直接展示原画真彩)
     */
    function renderScratchBackground() {
        if (appMode !== 'scratch') return;
        bgCtx.save();
        bgCtx.clearRect(0, 0, viewportWidth, viewportHeight);
        bgCtx.fillStyle = '#0d0f12';
        bgCtx.fillRect(0, 0, viewportWidth, viewportHeight);
        bgCtx.filter = 'none'; // 原画色彩，不作任何灰度处理

        if (isNextImageLoaded) {
            bgCtx.drawImage(
                nextGardenImage,
                nextImageBounds.x,
                nextImageBounds.y,
                nextImageBounds.w,
                nextImageBounds.h
            );
        }
        bgCtx.restore();
    }

    /**
     * 挑选下一幅不重复的随机名画索引
     */
    function pickRandomNextIndex() {
        if (masterpieces.length <= 1) return 0;
        const recentSet = new Set(scratchConfig.historyQueue);
        let candidates = [];
        for (let i = 0; i < masterpieces.length; i++) {
            if (i !== currentMasterpieceIndex && !recentSet.has(i)) {
                candidates.push(i);
            }
        }
        if (candidates.length === 0) {
            candidates = masterpieces.map((_, i) => i).filter(i => i !== currentMasterpieceIndex);
        }
        const picked = candidates[Math.floor(Math.random() * candidates.length)];
        scratchConfig.historyQueue.push(picked);
        if (scratchConfig.historyQueue.length > scratchConfig.maxHistoryLen) {
            scratchConfig.historyQueue.shift();
        }
        return picked;
    }

    /**
     * 预加载下一幅随机名画到后台底层
     */
    function prepareNextRandomArtwork(callback) {
        nextMasterpieceIndex = pickRandomNextIndex();
        const nextArt = masterpieces[nextMasterpieceIndex];
        isNextImageLoaded = false;

        let handled = false;
        function finish() {
            if (handled) return;
            handled = true;
            isNextImageLoaded = true;
            computeNextImageBounds();
            if (appMode === 'scratch') {
                renderScratchBackground();
            }
            if (callback) callback();
        }

        nextGardenImage.onload = finish;
        nextGardenImage.onerror = () => {
            console.error('Failed to load next random artwork:', nextArt.src);
            finish();
        };
        nextGardenImage.src = nextArt.src;
        if (nextGardenImage.complete && nextGardenImage.naturalWidth > 0) {
            finish();
        }
    }

    /**
     * 视口尺寸变化与高清 Retina DPI 适配 (兼顾移动端动态地址栏与旋转)
     */
    function handleResize() {
        if (window.visualViewport) {
            viewportWidth = Math.round(window.visualViewport.width);
            viewportHeight = Math.round(window.visualViewport.height);
        } else {
            viewportWidth = window.innerWidth;
            viewportHeight = window.innerHeight;
        }
        // 限制移动端极端高分屏 (3x/4x) DPR，避免显存爆仓与掉帧
        dpr = Math.min(window.devicePixelRatio || 1, 2.5);

        // 设置高清物理画布像素
        bgCanvas.width = Math.round(viewportWidth * dpr);
        bgCanvas.height = Math.round(viewportHeight * dpr);
        bgCanvas.style.width = viewportWidth + 'px';
        bgCanvas.style.height = viewportHeight + 'px';
        bgCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

        revealCanvas.width = Math.round(viewportWidth * dpr);
        revealCanvas.height = Math.round(viewportHeight * dpr);
        revealCanvas.style.width = viewportWidth + 'px';
        revealCanvas.style.height = viewportHeight + 'px';
        revealCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

        maskCanvas.width = Math.round(viewportWidth * dpr);
        maskCanvas.height = Math.round(viewportHeight * dpr);
        maskCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

        initGrid();
        computeImageBounds();
        computeNextImageBounds();

        if (appMode === 'scratch') {
            renderScratchBackground();
        } else {
            renderGrayscaleBackground();
        }
    }

    /**
     * 在单点周围施加笔刷涂抹 (多划几下渐进累加)
     * @param {number} px 屏幕X坐标
     * @param {number} py 屏幕Y坐标
     * @param {number} strokeId 当前划动的编号
     * @param {number} gainBase 显色增量基数
     * @param {number} now 时间戳
     */
    /**
     * 在单点周围施加笔刷涂抹
     * - 沉睡模式：渐进增加显色度
     * - 随机模式：擦除当前画遮罩，透出底层背后的下一幅随机名画
     */
    function applyDab(px, py, strokeId, gainBase, now) {
        if (appMode === 'scratch') {
            // 核心红线约束：一幅画必须完全展示出来后，画笔涂抹才能擦去它！
            if (scratchConfig.isLocked || scratchConfig.isTransitioning) return;

            const radius = config.brushRadius;
            const cellSize = config.cellSize;

            const minCol = Math.max(0, Math.floor((px - radius) / cellSize));
            const maxCol = Math.min(gridCols - 1, Math.floor((px + radius) / cellSize));
            const minRow = Math.max(0, Math.floor((py - radius) / cellSize));
            const maxRow = Math.min(gridRows - 1, Math.floor((py + radius) / cellSize));
            const radius2 = radius * radius;

            let modified = false;

            for (let r = minRow; r <= maxRow; r++) {
                const cellCenterY = (r + 0.5) * cellSize;
                const dy = cellCenterY - py;
                const dy2 = dy * dy;

                for (let c = minCol; c <= maxCol; c++) {
                    const cellCenterX = (c + 0.5) * cellSize;
                    const dx = cellCenterX - px;
                    const dist2 = dx * dx + dy2;

                    if (dist2 <= radius2) {
                        const dist = Math.sqrt(dist2);
                        const idx = r * gridCols + c;
                        const t = dist / radius;
                        // 经典 Smoothstep 曲线: 代替昂贵的 Math.cos，过渡极其平滑自然
                        const weight = 1 - t * t * (3 - 2 * t);

                        const oldVal = gridAlpha[idx];
                        const eraseAmount = 0.65 * weight;
                        const newVal = Math.max(0.0, oldVal - eraseAmount);
                        gridAlpha[idx] = newVal;

                        // O(1) 增量维护已擦除单元格计数器
                        if (oldVal >= SCRATCH_MASK_THRESHOLD && newVal < SCRATCH_MASK_THRESHOLD) {
                            scratchedCellsCount++;
                        }
                        modified = true;
                    }
                }
            }

            if (modified) {
                markDirty();
            }
            return;
        }

        // 经典沉睡模式逻辑
        const radius = config.brushRadius;
        const cellSize = config.cellSize;

        const minCol = Math.max(0, Math.floor((px - radius) / cellSize));
        const maxCol = Math.min(gridCols - 1, Math.floor((px + radius) / cellSize));
        const minRow = Math.max(0, Math.floor((py - radius) / cellSize));
        const maxRow = Math.min(gridRows - 1, Math.floor((py + radius) / cellSize));
        const radius2 = radius * radius;

        let modified = false;

        for (let r = minRow; r <= maxRow; r++) {
            const cellCenterY = (r + 0.5) * cellSize;
            const dy = cellCenterY - py;
            const dy2 = dy * dy;

            for (let c = minCol; c <= maxCol; c++) {
                const cellCenterX = (c + 0.5) * cellSize;
                const dx = cellCenterX - px;
                const dist2 = dx * dx + dy2;

                if (dist2 <= radius2) {
                    const idx = r * gridCols + c;

                    if (strokeId !== null && gridLastStroke[idx] === strokeId) {
                        continue;
                    }

                    if (strokeId !== null) {
                        gridLastStroke[idx] = strokeId;
                    }

                    const dist = Math.sqrt(dist2);
                    const t = dist / radius;
                    const weight = 1 - t * t * (3 - 2 * t);

                    const increment = gainBase * weight;
                    gridAlpha[idx] = Math.min(config.colorRatio, gridAlpha[idx] + increment);
                    gridLastTouch[idx] = now;
                    modified = true;
                }
            }
        }

        if (modified) {
            markDirty();
        }
    }

    /**
     * 笔触轨迹插值 (保证高速滑动时笔刷轨迹平滑无断点)
     */
    function strokeLine(from, to, strokeId, now) {
        if (appMode === 'scratch' && (scratchConfig.isLocked || scratchConfig.isTransitioning)) {
            return;
        }

        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dist = Math.hypot(dx, dy);
        const step = Math.max(6, config.brushRadius * 0.25);

        if (dist <= 0) {
            applyDab(to.x, to.y, strokeId, config.singlePassGain, now);
            if (appMode === 'scratch') {
                updateScratchRatio();
            }
            return;
        }

        const steps = Math.ceil(dist / step);
        for (let i = 1; i <= steps; i++) {
            const t = i / steps;
            applyDab(from.x + dx * t, from.y + dy * t, strokeId, config.singlePassGain, now);
        }

        if (appMode === 'scratch') {
            updateScratchRatio();
        }
    }

    /**
     * 节流更新 HUD 进度条与文字展示 (仅在数值变化时操作 DOM，避免高频回流)
     */
    function syncScratchHud(ratio) {
        const pct = Math.min(100, Math.round(ratio * 100));
        if (pct === lastRenderedHudPct) return;
        lastRenderedHudPct = pct;

        if (scratchHudPercent) scratchHudPercent.textContent = `${pct}%`;
        if (scratchHudFill) scratchHudFill.style.width = `${pct}%`;
        if (scratchRatioDisplay) scratchRatioDisplay.textContent = `${pct}%`;
        if (scratchMiniBarFill) scratchMiniBarFill.style.width = `${pct}%`;
    }

    /**
     * 统计随机漫游模式下的已擦除露出面积比例 (O(1) 瞬时计算)
     */
    function updateScratchRatio() {
        if (appMode !== 'scratch' || scratchConfig.isLocked || scratchConfig.isTransitioning) return;
        if (totalCells <= 0) return;

        const ratio = scratchedCellsCount / totalCells;
        scratchConfig.ratio = ratio;

        syncScratchHud(ratio);

        // 达到设定阈值 (默认 85%)，立即锁定并触发完全展示
        if (ratio >= scratchConfig.threshold) {
            triggerAutoScratchReveal();
        }
    }

    /**
     * 达到阈值触发自动完全展开平滑过渡动画
     */
    function triggerAutoScratchReveal() {
        if (scratchConfig.isLocked || scratchConfig.isTransitioning) return;
        scratchConfig.isLocked = true;
        scratchConfig.isTransitioning = true;

        if (scratchHud) scratchHud.classList.add('locked');
        if (scratchHudPercent) scratchHudPercent.textContent = `${Math.round(scratchConfig.threshold * 100)}% ✨`;

        const startTime = performance.now();
        const duration = 480; // ms
        const startAlphas = new Float32Array(gridAlpha);

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(1.0, elapsed / duration);
            const ease = 1 - Math.pow(1 - progress, 3);

            for (let i = 0; i < totalCells; i++) {
                gridAlpha[i] = startAlphas[i] * (1 - ease);
            }

            markDirty();

            if (progress < 1.0) {
                requestAnimationFrame(step);
            } else {
                gridAlpha.fill(0);
                scratchedCellsCount = totalCells;
                finalizeScratchTransition();
            }
        }

        markDirty();
        requestAnimationFrame(step);
    }

    /**
     * 下一幅画已经 100% 完全展示完毕后执行的状态机结算
     * “注意，一幅画必须完全展示出来后，画笔涂抹才能擦去它。”
     */
    function finalizeScratchTransition() {
        // 1. 将刚刚完全展现的下一幅名画正式晋升为当前画
        currentMasterpieceIndex = nextMasterpieceIndex;
        const art = masterpieces[currentMasterpieceIndex];

        gardenImage.src = nextGardenImage.src;
        computeImageBounds();

        // 2. 联动更新名言与作者
        if (quoteTextEl) quoteTextEl.textContent = art.quote;
        if (quoteAuthorEl) quoteAuthorEl.textContent = art.quoteAuthor;

        // 3. 联动更新画笔面板当前名画卡片
        if (currentArtThumb) {
            currentArtThumb.src = art.src;
            currentArtThumb.alt = art.title;
        }
        if (currentArtTitle) currentArtTitle.textContent = art.title;
        if (currentArtArtist) currentArtArtist.textContent = `${art.artist} · 🔍 检索画廊`;
        if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `${currentMasterpieceIndex + 1} / ${masterpieces.length}`;
        updateActiveCardHighlight(currentMasterpieceIndex);
        updateStoryContent(art);

        // 4. 重置顶层遮罩为 100% 不透明 (新画完好展现)
        gridAlpha.fill(1.0);
        scratchedCellsCount = 0;
        scratchConfig.ratio = 0;

        // 5. 重置 HUD 进度
        lastRenderedHudPct = 0;
        if (scratchHudPercent) scratchHudPercent.textContent = '0%';
        if (scratchHudFill) scratchHudFill.style.width = '0%';
        if (scratchRatioDisplay) scratchRatioDisplay.textContent = '0%';
        if (scratchMiniBarFill) scratchMiniBarFill.style.width = '0%';
        if (scratchHud) scratchHud.classList.remove('locked');

        let hasUnlocked = false;
        const doUnlock = () => {
            if (hasUnlocked) return;
            hasUnlocked = true;
            scratchConfig.isLocked = false;
            scratchConfig.isTransitioning = false;
            markDirty();
        };

        // 6. 后台立即挑选并预加载下一幅全新的随机名画，渲染到底层 bgCanvas
        prepareNextRandomArtwork(() => {
            computeNextImageBounds();
            renderScratchBackground();
            doUnlock();
        });

        // 7. 600ms 超时保底解锁，保证交互绝对流畅不卡顿
        setTimeout(doUnlock, 600);
        markDirty();
    }

    /**
     * 鼠标停驻充能 (沉睡模式专用)
     */
    function applyHoverCharge(px, py, now) {
        if (appMode === 'scratch') return;

        const radius = config.brushRadius;
        const cellSize = config.cellSize;

        const minCol = Math.max(0, Math.floor((px - radius) / cellSize));
        const maxCol = Math.min(gridCols - 1, Math.floor((px + radius) / cellSize));
        const minRow = Math.max(0, Math.floor((py - radius) / cellSize));
        const maxRow = Math.min(gridRows - 1, Math.floor((py + radius) / cellSize));
        const radius2 = radius * radius;

        let modified = false;

        for (let r = minRow; r <= maxRow; r++) {
            const cellCenterY = (r + 0.5) * cellSize;
            const dy = cellCenterY - py;
            const dy2 = dy * dy;

            for (let c = minCol; c <= maxCol; c++) {
                const cellCenterX = (c + 0.5) * cellSize;
                const dx = cellCenterX - px;
                const dist2 = dx * dx + dy2;

                if (dist2 <= radius2) {
                    const dist = Math.sqrt(dist2);
                    const idx = r * gridCols + c;
                    const t = dist / radius;
                    const weight = 1 - t * t * (3 - 2 * t);

                    const increment = config.hoverChargeGain * weight;
                    gridAlpha[idx] = Math.min(config.colorRatio, gridAlpha[idx] + increment);
                    gridLastTouch[idx] = now;
                    modified = true;
                }
            }
        }

        if (modified) {
            markDirty();
        }
    }

    /**
     * 核心渲染主循环 (按需渲染 + 静止休眠)
     */
    function renderLoop(currentTime) {
        if (appMode === 'scratch') {
            // ================= 🎲 随机漫游擦画渲染管线 =================
            const needsRender = isDirty || scratchConfig.isTransitioning;

            if (needsRender) {
                const data = maskSmallImageData ? maskSmallImageData.data : null;
                if (data && totalCells > 0) {
                    for (let i = 0; i < totalCells; i++) {
                        data[i * 4 + 3] = (gridAlpha[i] * 255 + 0.5) | 0;
                    }
                }

                revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

                if (isImageLoaded && data) {
                    maskSmallCtx.putImageData(maskSmallImageData, 0, 0);

                    maskCtx.clearRect(0, 0, viewportWidth, viewportHeight);
                    maskCtx.save();
                    maskCtx.imageSmoothingEnabled = true;
                    maskCtx.imageSmoothingQuality = 'high';
                    maskCtx.drawImage(maskSmallCanvas, 0, 0, viewportWidth, viewportHeight);
                    maskCtx.restore();

                    // 顶层绘制当前画作 (原画真实色彩，无需灰度)，通过 destination-in 抠出擦除洞，透出底层
                    revealCtx.save();
                    revealCtx.fillStyle = '#0d0f12';
                    revealCtx.fillRect(0, 0, viewportWidth, viewportHeight);

                    revealCtx.drawImage(
                        gardenImage,
                        imageBounds.x,
                        imageBounds.y,
                        imageBounds.w,
                        imageBounds.h
                    );
                    revealCtx.globalCompositeOperation = 'destination-in';
                    revealCtx.drawImage(maskCanvas, 0, 0, viewportWidth, viewportHeight);
                    revealCtx.restore();
                }

                isDirty = false;
            }

            // 如果正在进行完全展开动画过渡，继续下一帧；否则完全静止休眠，消耗归零
            if (scratchConfig.isTransitioning) {
                requestAnimationFrame(renderLoop);
            } else {
                isRenderingActive = false;
            }
            return;
        }

        // ================= 🌸 经典沉睡唤醒渲染管线 =================
        // 1. 停驻充能逻辑
        if (isPointerActive && currentPointerPos) {
            const timeSinceMove = currentTime - lastMoveTime;
            if (timeSinceMove > 40 && currentTime - lastHoverChargeTime > 45) {
                applyHoverCharge(currentPointerPos.x, currentPointerPos.y, currentTime);
                lastHoverChargeTime = currentTime;
            }
        }

        // 2. 一键全彩模式或微距放大探索处理 (微距放大探索时直接以 100% 鲜艳真彩展现笔触与细节)
        if (isFullColorLocked || macroZoom > 1.05) {
            if (isDirty) {
                revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
                if (isImageLoaded) {
                    revealCtx.save();
                    revealCtx.globalAlpha = isFullColorLocked ? config.colorRatio : 1.0;
                    revealCtx.drawImage(
                        gardenImage,
                        imageBounds.x,
                        imageBounds.y,
                        imageBounds.w,
                        imageBounds.h
                    );
                    revealCtx.restore();
                }
                isDirty = false;
            }
            isRenderingActive = false;
            return;
        }

        // 3. 衰减与留存计算
        const data = maskSmallImageData ? maskSmallImageData.data : null;
        let hasAnyActiveColor = false;
        let hasFadingColor = false;

        if (data && totalCells > 0) {
            const solidMs = config.solidDurationMs;
            const fadeMs = config.fadeDurationMs;

            for (let i = 0; i < totalCells; i++) {
                const rawAlpha = gridAlpha[i];
                if (rawAlpha <= 0.001) {
                    data[i * 4 + 3] = 0;
                    continue;
                }
                const alpha = Math.min(config.colorRatio, rawAlpha);

                const elapsed = currentTime - gridLastTouch[i];
                let currentAlpha = alpha;

                if (elapsed <= solidMs) {
                    currentAlpha = alpha;
                    hasAnyActiveColor = true;
                    hasFadingColor = true;
                } else {
                    const fadeProgress = (elapsed - solidMs) / fadeMs;
                    if (fadeProgress >= 1.0) {
                        gridAlpha[i] = 0;
                        currentAlpha = 0;
                    } else {
                        // Smoothstep 衰减曲线
                        const p = fadeProgress;
                        const decayFactor = 1 - p * p * (3 - 2 * p);
                        currentAlpha = alpha * decayFactor;
                        hasFadingColor = true;
                    }
                }

                if (currentAlpha > 0.002) {
                    hasAnyActiveColor = true;
                    data[i * 4 + 3] = (currentAlpha * 255 + 0.5) | 0;
                } else {
                    data[i * 4 + 3] = 0;
                }
            }
        }

        // 4. 将小尺寸网格遮罩通过 GPU 双线性平滑插值投射到全屏遮罩
        revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

        if (isImageLoaded && hasAnyActiveColor) {
            maskSmallCtx.putImageData(maskSmallImageData, 0, 0);

            maskCtx.clearRect(0, 0, viewportWidth, viewportHeight);
            maskCtx.save();
            maskCtx.imageSmoothingEnabled = true;
            maskCtx.imageSmoothingQuality = 'high';
            maskCtx.drawImage(maskSmallCanvas, 0, 0, viewportWidth, viewportHeight);
            maskCtx.restore();

            revealCtx.save();
            revealCtx.drawImage(
                gardenImage,
                imageBounds.x,
                imageBounds.y,
                imageBounds.w,
                imageBounds.h
            );
            revealCtx.globalCompositeOperation = 'destination-in';
            revealCtx.drawImage(maskCanvas, 0, 0, viewportWidth, viewportHeight);
            revealCtx.restore();
        }

        // 5. 判断是否需要继续下一帧：若有颜色正在衰减或光标保持活动，持续渲染；若完全归于沉睡，则自动休眠
        if (hasFadingColor || (isPointerActive && currentPointerPos)) {
            requestAnimationFrame(renderLoop);
        } else {
            isDirty = false;
            isRenderingActive = false;
        }
    }

    /**
     * 更新画笔大小与所有关联 UI (包括预览圆与艺术光标)
     */
    function updateBrushSize(newRadius) {
        config.brushRadius = Math.max(config.minBrushRadius, Math.min(config.maxBrushRadius, newRadius));

        if (brushSlider) {
            brushSlider.value = config.brushRadius;
        }
        if (brushSizeDisplay) {
            brushSizeDisplay.textContent = `${config.brushRadius}px`;
        }

        // 更新弹窗中的预览圆圈
        if (brushPreviewDot) {
            const previewDiameter = Math.min(46, Math.max(10, Math.round(config.brushRadius * 0.3)));
            brushPreviewDot.style.width = `${previewDiameter}px`;
            brushPreviewDot.style.height = `${previewDiameter}px`;
        }

        // 同步更新页面上的艺术光标外圈大小
        if (cursorRing) {
            const ringSize = Math.max(28, Math.round(config.brushRadius * 0.48));
            cursorRing.style.width = `${ringSize}px`;
            cursorRing.style.height = `${ringSize}px`;
        }
    }

    /**
     * 更新色彩留存时长 (秒)
     */
    function updateDuration(totalSeconds) {
        config.totalDurationSeconds = Math.max(4, Math.min(30, totalSeconds));
        // 70% 时间用于高光完全保留不褪色，30% 时间用于舒缓柔和淡出
        config.solidDurationMs = Math.round(config.totalDurationSeconds * 0.7 * 1000);
        config.fadeDurationMs = Math.round(config.totalDurationSeconds * 0.3 * 1000);

        if (brushDurationSlider) {
            brushDurationSlider.value = config.totalDurationSeconds;
        }
        if (brushDurationDisplay) {
            brushDurationDisplay.textContent = `${config.totalDurationSeconds}秒`;
        }
    }

    /**
     * 更新划过唤醒原画显色比例 (0.2 ~ 1.0)
     * @param {number} newRatio 
     */
    function updateColorRatio(newRatio) {
        config.colorRatio = Math.max(0.2, Math.min(1.0, newRatio));
        const pct = Math.round(config.colorRatio * 100);

        if (colorRatioSlider) {
            colorRatioSlider.value = pct;
        }
        if (colorRatioDisplay) {
            colorRatioDisplay.textContent = `${pct}%`;
        }

        markDirty();
    }

    /**
     * 设置画面规格模式 ('auto' | 'contain' | 'cover')
     */
    function setFitMode(mode) {
        if (!['auto', 'contain', 'cover'].includes(mode)) return;
        config.fitMode = mode;

        // 更新 UI 标签与选项卡高亮
        if (fitAutoBtn) fitAutoBtn.classList.toggle('active', mode === 'auto');
        if (fitContainBtn) fitContainBtn.classList.toggle('active', mode === 'contain');
        if (fitCoverBtn) fitCoverBtn.classList.toggle('active', mode === 'cover');

        if (fitModeDisplay) {
            const labels = { auto: '智能', contain: '完整', cover: '铺满' };
            fitModeDisplay.textContent = labels[mode] || mode;
        }

        refreshLayout();
    }

    /**
     * 设置画面手动缩放倍率 (0.6 ~ 1.4)
     */
    function setScale(scaleVal) {
        config.scale = Math.max(0.6, Math.min(1.4, scaleVal));

        if (fitScaleSlider) {
            fitScaleSlider.value = Math.round(config.scale * 100);
        }
        if (fitScaleDisplay) {
            fitScaleDisplay.textContent = `${Math.round(config.scale * 100)}%`;
        }

        refreshLayout();
    }

    /**
     * 设置体验模式 ('sleep' | 'scratch')
     * @param {'sleep' | 'scratch'} mode 
     */
    function setAppMode(mode) {
        if (mode !== 'sleep' && mode !== 'scratch') return;
        appMode = mode;

        if (modeSleepBtn) modeSleepBtn.classList.toggle('active', mode === 'sleep');
        if (modeScratchBtn) modeScratchBtn.classList.toggle('active', mode === 'scratch');

        if (sleepModeControls) sleepModeControls.style.display = (mode === 'sleep') ? 'block' : 'none';
        if (scratchModeControls) scratchModeControls.style.display = (mode === 'scratch') ? 'block' : 'none';
        if (scratchHud) scratchHud.style.display = (mode === 'scratch') ? 'flex' : 'none';

        if (mode === 'scratch') {
            // 切换到随机漫游擦画模式
            scratchConfig.isLocked = false;
            scratchConfig.isTransitioning = false;
            scratchConfig.ratio = 0;
            scratchedCellsCount = 0;
            lastRenderedHudPct = 0;
            if (gridAlpha) gridAlpha.fill(1.0); // 顶层全遮挡不透明
            if (scratchHudPercent) scratchHudPercent.textContent = '0%';
            if (scratchHudFill) scratchHudFill.style.width = '0%';
            if (scratchRatioDisplay) scratchRatioDisplay.textContent = '0%';
            if (scratchMiniBarFill) scratchMiniBarFill.style.width = '0%';
            if (scratchHud) scratchHud.classList.remove('locked');

            computeImageBounds();
            computeNextImageBounds();

            // 预加载下一幅并绘制底层全彩背景
            prepareNextRandomArtwork(() => {
                computeNextImageBounds();
                renderScratchBackground();
                markDirty();
            });
            updateHintText('scratch');
            showToast('已切换为 🎲 随机漫游擦画模式', '🎲');
            markDirty();
        } else {
            // 切换回经典沉睡唤醒模式
            computeImageBounds();
            if (gridAlpha) gridAlpha.fill(0);
            if (gridLastStroke) gridLastStroke.fill(0);
            isFullColorLocked = false;
            if (fullColorBtnText) fullColorBtnText.textContent = '一键全彩盛放';
            if (toggleFullColorBtn) toggleFullColorBtn.classList.remove('active');
            renderGrayscaleBackground();
            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
            updateHintText('sleep');
            showToast('已切换为 🌸 沉睡唤醒古典模式', '🌸');
            markDirty();
        }
    }

    /**
     * 绑定画笔控制面板事件
     */
    function setupBrushUI() {
        if (!brushToggleBtn || !brushPopup) return;

        // 模式切换按钮 (沉睡唤醒 vs 随机漫游)
        if (modeSleepBtn) {
            modeSleepBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                setAppMode('sleep');
            });
        }
        if (modeScratchBtn) {
            modeScratchBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                setAppMode('scratch');
            });
        }

        // 随机擦画阈值滑块 (50% ~ 95%)
        if (scratchThresholdSlider) {
            scratchThresholdSlider.addEventListener('input', (e) => {
                const val = parseInt(e.target.value, 10);
                scratchConfig.threshold = val / 100;
                if (scratchThresholdDisplay) scratchThresholdDisplay.textContent = `${val}%`;
                if (scratchHudTargetVal) scratchHudTargetVal.textContent = `${val}%`;
            });
            scratchThresholdSlider.addEventListener('click', (e) => e.stopPropagation());
        }

        // 立即完全展现按钮
        if (scratchRevealNowBtn) {
            scratchRevealNowBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                triggerAutoScratchReveal();
            });
        }

        // 点击切换调节面板展开/收起
        brushToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = brushPopup.classList.toggle('open');
            brushToggleBtn.classList.toggle('active', isOpen);
        });

        // 画笔大小滑块拖动实时调节
        if (brushSlider) {
            brushSlider.addEventListener('input', (e) => {
                updateBrushSize(parseInt(e.target.value, 10));
            });
            brushSlider.addEventListener('click', (e) => e.stopPropagation());
        }

        // 色彩留存时长滑块拖动实时调节
        if (brushDurationSlider) {
            brushDurationSlider.addEventListener('input', (e) => {
                updateDuration(parseInt(e.target.value, 10));
            });
            brushDurationSlider.addEventListener('click', (e) => e.stopPropagation());
        }

        // 显色比例滑块拖动实时调节
        if (colorRatioSlider) {
            colorRatioSlider.addEventListener('input', (e) => {
                updateColorRatio(parseInt(e.target.value, 10) / 100);
            });
            colorRatioSlider.addEventListener('click', (e) => e.stopPropagation());
        }

        // 绑定一键全彩盛放按钮
        if (toggleFullColorBtn) {
            toggleFullColorBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleFullColor();
            });
        }

        // 绑定画面规格模式选项卡
        if (fitAutoBtn) {
            fitAutoBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                setFitMode('auto');
            });
        }
        if (fitContainBtn) {
            fitContainBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                setFitMode('contain');
            });
        }
        if (fitCoverBtn) {
            fitCoverBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                setFitMode('cover');
            });
        }

        // 绑定画面缩放滑块
        if (fitScaleSlider) {
            fitScaleSlider.addEventListener('input', (e) => {
                setScale(parseInt(e.target.value, 10) / 100);
            });
            fitScaleSlider.addEventListener('click', (e) => e.stopPropagation());
        }

        // 绑定古典微距探秘放大镜开关按钮
        if (toggleLoupeBtn) {
            toggleLoupeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleLoupe();
            });
        }

        // 绑定微距透镜倍率选择芯片
        if (loupeOptionsBox) {
            const chips = loupeOptionsBox.querySelectorAll('.loupe-zoom-chip');
            chips.forEach(chip => {
                chip.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const targetZ = parseFloat(chip.dataset.zoom) || 3.5;
                    setLoupeZoom(targetZ);
                });
            });
        }

        // 绑定微距缩放胶囊指示器一键复位按钮
        if (macroZoomResetBtn) {
            macroZoomResetBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                resetMacroZoom();
                showToast('🔍 已平滑复位至全景');
            });
        }

        // 点击外部空白区域自动收起调节弹窗
        window.addEventListener('click', (e) => {
            if (!brushPopup.contains(e.target) && !brushToggleBtn.contains(e.target)) {
                brushPopup.classList.remove('open');
                brushToggleBtn.classList.remove('active');
            }
        });

        // 阻止弹窗内部鼠标移动冒泡触发画布笔刷
        brushPopup.addEventListener('mousemove', (e) => e.stopPropagation());
        brushToggleBtn.addEventListener('mousemove', (e) => e.stopPropagation());

        // 初始化画笔大小、显色比例、留存时间、规格模式与缩放
        updateBrushSize(config.brushRadius);
        updateColorRatio(config.colorRatio);
        updateDuration(config.totalDurationSeconds);
        setFitMode(config.fitMode);
        setScale(config.scale);
        setAppMode(appMode);
    }

    /**
     * 切换一键全彩盛放状态 (还原为原始全彩 或 恢复沉睡黑白)
     * @param {boolean} [forceState] 可选的强制布尔状态
     */
    function toggleFullColor(forceState) {
        const targetState = (forceState !== undefined) ? forceState : !isFullColorLocked;
        isFullColorLocked = targetState;

        if (isFullColorLocked) {
            // 瞬间将全网格充满至当前设定的显色比例
            if (gridAlpha) gridAlpha.fill(config.colorRatio);
            if (gridLastTouch) gridLastTouch.fill(performance.now());

            if (fullColorBtnText) fullColorBtnText.textContent = '恢复黑白沉睡';
            if (toggleFullColorBtn) {
                toggleFullColorBtn.classList.add('active');
                toggleFullColorBtn.title = '点击让画面重归静谧黑白素描';
            }
        } else {
            // 清空全彩，重归沉睡灰阶
            if (gridAlpha) gridAlpha.fill(0);
            if (gridLastStroke) gridLastStroke.fill(0);
            if (maskSmallImageData) {
                const d = maskSmallImageData.data;
                for (let i = 0; i < totalCells; i++) {
                    d[i * 4 + 3] = 0;
                }
            }
            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

            if (fullColorBtnText) fullColorBtnText.textContent = '一键全彩盛放';
            if (toggleFullColorBtn) {
                toggleFullColorBtn.classList.remove('active');
                toggleFullColorBtn.title = '一键将整幅画还原为原始真彩';
            }
        }
        markDirty();
    }

    /**
     * 题材分类定义与匹配器 (符合西方艺术史 6 大正统题材体系)
     */
    const GENRE_DEFINITIONS = [
        { id: 'all', label: '全部题材', icon: '🎨', test: () => true },
        { id: 'life', label: '风俗生活', icon: '👥', test: (art) => art.genre && (art.genre.includes('风俗') || art.genre.includes('生活')) },
        { id: 'landscape', label: '自然风景', icon: '🌿', test: (art) => art.genre && (art.genre.includes('风景') || art.genre.includes('风光')) },
        { id: 'portrait', label: '人物肖像', icon: '👤', test: (art) => art.genre && art.genre.includes('人物') },
        { id: 'mythology', label: '神话宗教', icon: '🏛️', test: (art) => art.genre && (art.genre.includes('神话') || art.genre.includes('宗教')) },
        { id: 'history', label: '历史故事', icon: '⚔️', test: (art) => art.genre && (art.genre.includes('历史') || art.genre.includes('故事') || art.genre.includes('叙事')) },
        { id: 'still_life', label: '静物花卉', icon: '💐', test: (art) => art.genre && (art.genre.includes('静物') || art.genre.includes('花卉')) }
    ];

    // 全局名画多维筛选与搜索状态
    const galleryFilterState = {
        query: '',
        genre: 'all',
        artist: 'all',
        category: 'all'
    };

    /**
     * 切换当前激活的名画
     * @param {number} index 画作索引 (0 ~ masterpieces.length - 1)
     */
    function switchMasterpiece(index) {
        if (index < 0 || index >= masterpieces.length) return;
        currentMasterpieceIndex = index;
        const art = masterpieces[index];

        // 切换名画时复位全彩模式与微距缩放
        if (isFullColorLocked) {
            toggleFullColor(false);
        }
        resetMacroZoom(true);

        // 1. 重置显色状态网格与离屏采样遮罩
        if (appMode === 'scratch') {
            if (gridAlpha) gridAlpha.fill(1.0); // 随机漫游模式：顶层保持 100% 遮罩遮挡新画
            scratchedCellsCount = 0;
            scratchConfig.ratio = 0;
            scratchConfig.isLocked = false;
            scratchConfig.isTransitioning = false;
            lastRenderedHudPct = 0;
            if (scratchHudPercent) scratchHudPercent.textContent = '0%';
            if (scratchHudFill) scratchHudFill.style.width = '0%';
            if (scratchRatioDisplay) scratchRatioDisplay.textContent = '0%';
            if (scratchMiniBarFill) scratchMiniBarFill.style.width = '0%';
            if (scratchHud) scratchHud.classList.remove('locked');
        } else {
            if (gridAlpha) gridAlpha.fill(0); // 经典沉睡模式：清空显色
            if (gridLastStroke) gridLastStroke.fill(0);
            if (maskSmallImageData) {
                const d = maskSmallImageData.data;
                for (let i = 0; i < totalCells; i++) {
                    d[i * 4 + 3] = 0;
                }
            }
            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
        }

        // 3. 更新诗意名言与作者署名
        if (quoteTextEl) quoteTextEl.textContent = art.quote;
        if (quoteAuthorEl) quoteAuthorEl.textContent = art.quoteAuthor;

        // 4. 更新画笔面板当前名画卡片展示与徽章
        if (currentArtThumb) {
            currentArtThumb.src = art.src;
            currentArtThumb.alt = art.title;
        }
        if (currentArtTitle) currentArtTitle.textContent = art.title;
        if (currentArtArtist) currentArtArtist.textContent = `${art.artist} · 🔍 检索画廊`;
        if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `${index + 1} / ${masterpieces.length}`;

        // 5. 同步更新画廊展厅卡片激活高亮状态
        updateActiveCardHighlight(index);
        updateStoryContent(art);

        // 6. 载入新名画原图并重新渲染古典灰阶底图
        isImageLoaded = false;
        gardenImage.src = art.src;
        markDirty();
    }

    /**
     * 更新画廊抽屉列表中的激活高亮项
     */
    function updateActiveCardHighlight(activeIndex) {
        if (!galleryListContainer) return;
        const cards = galleryListContainer.querySelectorAll('.gallery-card');
        cards.forEach(card => {
            const idx = parseInt(card.getAttribute('data-index'), 10);
            const isTarget = idx === activeIndex;
            card.classList.toggle('is-active', isTarget);
            let badge = card.querySelector('.card-badge-viewing');
            if (isTarget) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'card-badge-viewing';
                    badge.textContent = '👑 观赏中';
                    const header = card.querySelector('.card-header-row');
                    if (header) header.appendChild(badge);
                }
            } else if (badge) {
                badge.remove();
            }
        });
    }

    /**
     * 规范化检索文本 (忽略空格、间隔号·、英文标点等，支持“达芬奇”匹配“达·芬奇”)
     */
    function normalizeSearchText(str) {
        if (!str) return '';
        return String(str).toLowerCase().replace(/[\s·\-\._・/()（）,"'‘’“”]/g, '');
    }

    /**
     * 执行名画多维过滤与关键词检索
     */
    function getFilteredMasterpieces() {
        const q = galleryFilterState.query.trim();
        const qNorm = normalizeSearchText(q);
        const activeGenre = GENRE_DEFINITIONS.find(g => g.id === galleryFilterState.genre) || GENRE_DEFINITIONS[0];

        return masterpieces
            .map((art, index) => ({ art, index }))
            .filter(({ art }) => {
                // 1. 题材筛选
                if (!activeGenre.test(art)) return false;

                // 2. 画家筛选
                if (galleryFilterState.artist !== 'all' && art.artist !== galleryFilterState.artist) {
                    return false;
                }

                // 3. 画派时期筛选
                if (galleryFilterState.category !== 'all' && art.category !== galleryFilterState.category) {
                    return false;
                }

                // 4. 关键词智能模糊搜索 (画名、外文名、画家、名言、题材、时期)
                if (qNorm) {
                    const matchTitle = normalizeSearchText(art.title).includes(qNorm);
                    const matchEnTitle = normalizeSearchText(art.enTitle).includes(qNorm);
                    const matchArtist = normalizeSearchText(art.artist).includes(qNorm);
                    const matchGenre = normalizeSearchText(art.genre).includes(qNorm);
                    const matchQuote = normalizeSearchText(art.quote).includes(qNorm);
                    const matchCategory = normalizeSearchText(art.category).includes(qNorm);
                    if (!matchTitle && !matchEnTitle && !matchArtist && !matchGenre && !matchQuote && !matchCategory) {
                        return false;
                    }
                }

                return true;
            });
    }

    /**
     * 重新渲染画廊抽屉列表
     */
    // 展厅超高性能增量分批渲染引擎
    let galleryFilteredItems = [];
    let galleryRenderedCount = 0;
    const GALLERY_BATCH_SIZE = 24; // 每次追加 24 项 (约 1.5~2 屏)
    let gallerySentinelEl = null;
    let galleryObserver = null;

    /**
     * 创建单个名画卡片 DOM 节点 (高度复用与异步解码属性优化)
     */
    function createGalleryCard({ art, index }) {
        const isCurrent = index === currentMasterpieceIndex;
        const card = document.createElement('div');
        card.className = `gallery-card ${isCurrent ? 'is-active' : ''}`;
        card.setAttribute('data-index', index);
        card.setAttribute('role', 'listitem');
        card.title = `点击切换欣赏：《${art.title}》· ${art.artist}`;

        let catLabel = '';
        if (window.ART_CATEGORIES) {
            const catObj = window.ART_CATEGORIES.find(c => c.id === art.category);
            if (catObj) catLabel = catObj.name.split('(')[0].trim();
        }

        card.innerHTML = `
            <div class="card-thumb-box">
                <img class="card-thumb-img" src="${art.src}" alt="${art.title}" loading="lazy" decoding="async" fetchpriority="low" width="54" height="54">
            </div>
            <div class="card-details">
                <div class="card-header-row">
                    <div class="card-title">${index + 1}. ${art.title}</div>
                    ${isCurrent ? '<span class="card-badge-viewing">👑 观赏中</span>' : ''}
                </div>
                ${art.enTitle ? `<div class="card-entitle">${art.enTitle}</div>` : ''}
                <div class="card-artist">${art.artist}</div>
                <div class="card-tags-row">
                    ${art.genre ? `<span class="card-tag card-tag-genre">${art.genre}</span>` : ''}
                    ${catLabel ? `<span class="card-tag card-tag-cat">${catLabel}</span>` : ''}
                </div>
            </div>
        `;

        card.addEventListener('click', () => {
            switchMasterpiece(index);
            if (window.innerWidth <= 640) {
                closeGallery();
            }
        });

        return card;
    }

    /**
     * 追加渲染下一批画作卡片
     */
    function appendGalleryBatch() {
        if (!galleryListContainer || galleryRenderedCount >= galleryFilteredItems.length) {
            if (gallerySentinelEl && gallerySentinelEl.parentNode) {
                gallerySentinelEl.style.display = 'none';
            }
            return;
        }

        const nextCount = Math.min(galleryFilteredItems.length, galleryRenderedCount + GALLERY_BATCH_SIZE);
        const frag = document.createDocumentFragment();

        for (let i = galleryRenderedCount; i < nextCount; i++) {
            frag.appendChild(createGalleryCard(galleryFilteredItems[i]));
        }

        galleryRenderedCount = nextCount;

        if (gallerySentinelEl && gallerySentinelEl.parentNode === galleryListContainer) {
            galleryListContainer.insertBefore(frag, gallerySentinelEl);
            gallerySentinelEl.style.display = (galleryRenderedCount < galleryFilteredItems.length) ? 'block' : 'none';
        } else {
            galleryListContainer.appendChild(frag);
            if (galleryRenderedCount < galleryFilteredItems.length) {
                ensureGallerySentinel();
            }
        }
    }

    function ensureGallerySentinel() {
        if (!gallerySentinelEl) {
            gallerySentinelEl = document.createElement('div');
            gallerySentinelEl.className = 'gallery-scroll-sentinel';
            gallerySentinelEl.style.height = '40px';
            gallerySentinelEl.style.width = '100%';
            gallerySentinelEl.style.pointerEvents = 'none';
        }
        gallerySentinelEl.style.display = 'block';
        galleryListContainer.appendChild(gallerySentinelEl);
        initGalleryObserver();
    }

    function initGalleryObserver() {
        if (galleryObserver) {
            galleryObserver.disconnect();
        }
        if (!gallerySentinelEl || !('IntersectionObserver' in window)) return;

        galleryObserver = new IntersectionObserver((entries) => {
            if (entries[0] && entries[0].isIntersecting) {
                appendGalleryBatch();
            }
        }, {
            root: galleryListContainer,
            rootMargin: '300px 0px',
            threshold: 0.01
        });

        galleryObserver.observe(gallerySentinelEl);
    }

    /**
     * 重新渲染画廊抽屉列表 (高性能分批增量渲染)
     */
    function renderGalleryList() {
        if (!galleryListContainer) return;

        galleryFilteredItems = getFilteredMasterpieces();
        const hasActiveFilter = galleryFilterState.query.trim() !== '' ||
            galleryFilterState.genre !== 'all' ||
            galleryFilterState.artist !== 'all' ||
            galleryFilterState.category !== 'all';

        // 更新结果统计与重置按钮
        if (galleryResultCount) galleryResultCount.textContent = galleryFilteredItems.length;
        if (galleryResetBtn) {
            galleryResetBtn.style.display = hasActiveFilter ? 'inline-block' : 'none';
        }

        // 更新筛选描述提示
        if (galleryFilterDesc) {
            const parts = [];
            if (galleryFilterState.genre !== 'all') {
                const g = GENRE_DEFINITIONS.find(item => item.id === galleryFilterState.genre);
                if (g) parts.push(g.label);
            }
            if (galleryFilterState.artist !== 'all') parts.push(galleryFilterState.artist.split('(')[0].trim());
            if (galleryFilterState.category !== 'all' && window.ART_CATEGORIES) {
                const c = window.ART_CATEGORIES.find(item => item.id === galleryFilterState.category);
                if (c) parts.push(c.name.split('(')[0].replace(/[^\u4e00-\u9fa5]/g, ''));
            }
            galleryFilterDesc.textContent = parts.length > 0 ? `(${parts.join(' · ')})` : '';
        }

        if (galleryObserver) {
            galleryObserver.disconnect();
        }

        galleryListContainer.innerHTML = '';
        galleryRenderedCount = 0;

        if (galleryFilteredItems.length === 0) {
            // 空状态展示
            const emptyEl = document.createElement('div');
            emptyEl.className = 'gallery-empty-state';
            emptyEl.innerHTML = `
                <div class="empty-icon">🎨</div>
                <div class="empty-title">未寻得匹配的名画作品</div>
                <p class="empty-desc">换个搜索词试试，或者重置当前题材与画家分类筛选。</p>
                <button class="empty-reset-btn" type="button">重置所有筛选</button>
            `;
            const emptyResetBtn = emptyEl.querySelector('.empty-reset-btn');
            if (emptyResetBtn) {
                emptyResetBtn.addEventListener('click', resetAllFilters);
            }
            galleryListContainer.appendChild(emptyEl);
            return;
        }

        // 智能计算初次渲染批次：
        // 若当前名画在列表更后位置（如第 70 幅），则初次渲染恰好覆盖到该画作，确保自动居中滚入时无缝可用；
        // 否则仅渲染首批 24 幅，极速秒开！
        let initialLimit = GALLERY_BATCH_SIZE;
        const currentArtIndexInList = galleryFilteredItems.findIndex(item => item.index === currentMasterpieceIndex);
        if (currentArtIndexInList >= 0 && currentArtIndexInList >= GALLERY_BATCH_SIZE) {
            initialLimit = Math.min(galleryFilteredItems.length, Math.ceil((currentArtIndexInList + 8) / GALLERY_BATCH_SIZE) * GALLERY_BATCH_SIZE);
        }

        const frag = document.createDocumentFragment();
        const limit = Math.min(galleryFilteredItems.length, initialLimit);
        for (let i = 0; i < limit; i++) {
            frag.appendChild(createGalleryCard(galleryFilteredItems[i]));
        }
        galleryRenderedCount = limit;
        galleryListContainer.appendChild(frag);

        if (galleryRenderedCount < galleryFilteredItems.length) {
            ensureGallerySentinel();
        }
    }

    /**
     * 重置所有筛选与搜索
     */
    function resetAllFilters() {
        galleryFilterState.query = '';
        galleryFilterState.genre = 'all';
        galleryFilterState.artist = 'all';
        galleryFilterState.category = 'all';

        if (gallerySearchInput) gallerySearchInput.value = '';
        if (gallerySearchClear) gallerySearchClear.style.display = 'none';

        // 复位题材药丸高亮
        if (genrePillsContainer) {
            const pills = genrePillsContainer.querySelectorAll('.genre-pill');
            pills.forEach(p => p.classList.toggle('active', p.getAttribute('data-genre') === 'all'));
        }

        // 复位下拉
        if (artistFilterSelect) artistFilterSelect.value = 'all';
        if (categoryFilterSelect) categoryFilterSelect.value = 'all';

        // 复位热门大师高亮
        if (quickArtistsContainer) {
            const qp = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
            qp.forEach(p => p.classList.remove('active'));
        }

        renderGalleryList();
    }

    /**
     * 打开名画抽屉展厅
     */
    function openGallery() {
        if (!galleryDrawer) return;

        // 打开大展厅时，顺畅收起右上角画笔控制弹窗
        if (brushPopup && brushPopup.classList.contains('open')) {
            brushPopup.classList.remove('open');
            if (brushToggleBtn) brushToggleBtn.classList.remove('active');
        }

        document.body.classList.add('gallery-open');
        galleryDrawer.classList.add('open');
        galleryDrawer.setAttribute('aria-hidden', 'false');

        // 自动聚焦搜索框
        setTimeout(() => {
            if (gallerySearchInput) gallerySearchInput.focus();
        }, 150);

        // 自动滚入视窗：让当前观赏的画作卡片居中可见
        setTimeout(() => {
            if (galleryListContainer) {
                const activeCard = galleryListContainer.querySelector('.gallery-card.is-active');
                if (activeCard) {
                    activeCard.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                }
            }
        }, 220);
    }

    /**
     * 关闭名画抽屉展厅
     */
    function closeGallery() {
        if (!galleryDrawer) return;
        document.body.classList.remove('gallery-open');
        galleryDrawer.classList.remove('open');
        galleryDrawer.setAttribute('aria-hidden', 'true');
        isCursorActive = false;
    }

    /**
     * 初始化名画画廊与多维分类检索 UI
     */
    function setupGalleryUI() {
        // 1. 初始化题材药丸按钮 (包含数量统计)
        if (genrePillsContainer) {
            genrePillsContainer.innerHTML = '';
            GENRE_DEFINITIONS.forEach(def => {
                const count = def.id === 'all'
                    ? masterpieces.length
                    : masterpieces.filter(def.test).length;

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `genre-pill ${def.id === 'all' ? 'active' : ''}`;
                btn.setAttribute('data-genre', def.id);
                btn.innerHTML = `<span>${def.icon} ${def.label}</span><span class="genre-pill-count">(${count})</span>`;

                btn.addEventListener('click', () => {
                    galleryFilterState.genre = def.id;
                    const allPills = genrePillsContainer.querySelectorAll('.genre-pill');
                    allPills.forEach(p => p.classList.toggle('active', p === btn));
                    renderGalleryList();
                });

                genrePillsContainer.appendChild(btn);
            });
        }

        const gallerySubInfo = document.querySelector('.gallery-sub-info');
        if (gallerySubInfo) {
            gallerySubInfo.textContent = `World Masterpieces · ${masterpieces.length} 幅传世杰作`;
        }

        // 2. 统计所有画家作品数并按作品量降序填充下拉菜单
        const artistCounts = {};
        masterpieces.forEach(art => {
            const a = art.artist || '未知艺术家';
            artistCounts[a] = (artistCounts[a] || 0) + 1;
        });
        const sortedArtists = Object.keys(artistCounts).sort((a, b) => artistCounts[b] - artistCounts[a]);

        if (artistFilterSelect) {
            artistFilterSelect.innerHTML = `<option value="all">🎨 全部画家 (${sortedArtists.length}位大师)</option>`;
            sortedArtists.forEach(artist => {
                const opt = document.createElement('option');
                opt.value = artist;
                opt.textContent = `${artist} (${artistCounts[artist]}幅)`;
                artistFilterSelect.appendChild(opt);
            });

            artistFilterSelect.addEventListener('change', (e) => {
                galleryFilterState.artist = e.target.value;
                // 同步热门大师高亮
                if (quickArtistsContainer) {
                    const qp = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
                    qp.forEach(p => p.classList.toggle('active', p.getAttribute('data-artist') === e.target.value));
                }
                renderGalleryList();
            });
        }

        // 3. 填充时期画派流派下拉
        if (categoryFilterSelect && window.ART_CATEGORIES) {
            categoryFilterSelect.innerHTML = `<option value="all">🏛️ 全部画派时期 (${window.ART_CATEGORIES.length}大流派)</option>`;
            window.ART_CATEGORIES.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.id;
                opt.textContent = `${cat.name} (${cat.count || 0}幅)`;
                categoryFilterSelect.appendChild(opt);
            });

            categoryFilterSelect.addEventListener('change', (e) => {
                galleryFilterState.category = e.target.value;
                renderGalleryList();
            });
        }

        // 4. 填充热门艺术大师快捷直选胶囊
        if (quickArtistsContainer) {
            quickArtistsContainer.innerHTML = '';
            // 挑选前 7 位大师作品量最大的或最具代表性的
            const topArtists = sortedArtists.slice(0, 8);
            topArtists.forEach(artist => {
                // 提取短名，如 "Claude Monet (莫奈)" -> "莫奈"
                const shortMatch = artist.match(/\((.*?)\)/);
                const shortName = shortMatch ? shortMatch[1] : artist.split(' ')[0];
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'quick-artist-pill';
                btn.setAttribute('data-artist', artist);
                btn.textContent = `${shortName} (${artistCounts[artist]})`;

                btn.addEventListener('click', () => {
                    if (galleryFilterState.artist === artist) {
                        // 再次点击取消选择
                        galleryFilterState.artist = 'all';
                        btn.classList.remove('active');
                        if (artistFilterSelect) artistFilterSelect.value = 'all';
                    } else {
                        galleryFilterState.artist = artist;
                        const allPills = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
                        allPills.forEach(p => p.classList.toggle('active', p === btn));
                        if (artistFilterSelect) artistFilterSelect.value = artist;
                    }
                    renderGalleryList();
                });

                quickArtistsContainer.appendChild(btn);
            });
        }

        // 5. 搜索栏输入与实时清除事件
        if (gallerySearchInput) {
            gallerySearchInput.addEventListener('input', (e) => {
                galleryFilterState.query = e.target.value;
                if (gallerySearchClear) {
                    gallerySearchClear.style.display = e.target.value ? 'flex' : 'none';
                }
                renderGalleryList();
            });

            gallerySearchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    if (gallerySearchInput.value) {
                        gallerySearchInput.value = '';
                        galleryFilterState.query = '';
                        if (gallerySearchClear) gallerySearchClear.style.display = 'none';
                        renderGalleryList();
                    } else {
                        closeGallery();
                    }
                    e.stopPropagation();
                }
            });
        }

        if (gallerySearchClear) {
            gallerySearchClear.addEventListener('click', () => {
                if (gallerySearchInput) gallerySearchInput.value = '';
                galleryFilterState.query = '';
                gallerySearchClear.style.display = 'none';
                if (gallerySearchInput) gallerySearchInput.focus();
                renderGalleryList();
            });
        }

        // 6. 重置所有筛选按钮
        if (galleryResetBtn) {
            galleryResetBtn.addEventListener('click', resetAllFilters);
        }

        // 7. 展厅打开/关闭触发器
        if (galleryOpenBtn) {
            galleryOpenBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openGallery();
            });
        }

        if (openGalleryModalBtn) {
            openGalleryModalBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openGallery();
            });
        }

        if (galleryCloseBtn) {
            galleryCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeGallery();
            });
        }

        if (galleryBackdrop) {
            galleryBackdrop.addEventListener('click', (e) => {
                e.stopPropagation();
                closeGallery();
            });
        }

        // 8. 上一幅 / 下一幅快捷切换
        if (prevArtBtn) {
            prevArtBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const nextIdx = (currentMasterpieceIndex - 1 + masterpieces.length) % masterpieces.length;
                switchMasterpiece(nextIdx);
            });
        }

        if (nextArtBtn) {
            nextArtBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const nextIdx = (currentMasterpieceIndex + 1) % masterpieces.length;
                switchMasterpiece(nextIdx);
            });
        }

        // 9. 全局键盘快捷键: 支持盲操、背景故事、画作切换、展厅与帮助指南
        window.addEventListener('keydown', (e) => {
            const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement && document.activeElement.tagName);
            if (e.key === 'Escape') {
                if (helpModal && helpModal.classList.contains('open')) {
                    closeHelp();
                } else if (storyDrawer && storyDrawer.classList.contains('open')) {
                    closeStory();
                } else if (galleryDrawer && galleryDrawer.classList.contains('open')) {
                    closeGallery();
                } else if (brushPopup && brushPopup.classList.contains('open')) {
                    brushPopup.classList.remove('open');
                    if (brushToggleBtn) brushToggleBtn.classList.remove('active');
                }
            } else if (!isTyping) {
                if (e.key === '?' || e.key === 'h' || e.key === 'H') {
                    e.preventDefault();
                    toggleHelp();
                } else if (e.key === 's' || e.key === 'S' || e.key === 'i' || e.key === 'I') {
                    e.preventDefault();
                    toggleStory();
                } else if (e.key === 'g' || e.key === 'G' || e.key === '/') {
                    e.preventDefault();
                    openGallery();
                } else if (e.code === 'Space') {
                    e.preventDefault();
                    toggleFullColor();
                    showToast(isFullColorLocked ? '已一键盛放全幅色彩' : '已重置画布色彩', isFullColorLocked ? '🌸' : '🔄');
                } else if (e.key === 'm' || e.key === 'M' || e.key === 'z' || e.key === 'Z') {
                    e.preventDefault();
                    toggleLoupe();
                } else if (e.key === '0' || e.key === 'r' || e.key === 'R') {
                    e.preventDefault();
                    if (macroZoom > 1.05 || Math.abs(panOffset.x) > 5 || Math.abs(panOffset.y) > 5) {
                        resetMacroZoom();
                        showToast('🔍 已平滑复位至全景');
                    }
                } else if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevIdx = (currentMasterpieceIndex - 1 + masterpieces.length) % masterpieces.length;
                    switchMasterpiece(prevIdx);
                    showToast(`《${masterpieces[prevIdx].title}》`, '🖼️');
                } else if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    const nextIdx = (currentMasterpieceIndex + 1) % masterpieces.length;
                    switchMasterpiece(nextIdx);
                    showToast(`《${masterpieces[nextIdx].title}》`, '🖼️');
                }
            }
        });

        // 滚动时无感追加下一批画作 (兼顾滚动高性能与无白屏体验)
        if (galleryListContainer) {
            galleryListContainer.addEventListener('scroll', () => {
                if (galleryRenderedCount < galleryFilteredItems.length) {
                    const remaining = galleryListContainer.scrollHeight - (galleryListContainer.scrollTop + galleryListContainer.clientHeight);
                    if (remaining < 450) {
                        appendGalleryBatch();
                    }
                }
            }, { passive: true });
        }

        // 初始渲染卡片列表
        renderGalleryList();
    }

    /**
     * 更新名画故事抽屉的内容
     */
    function updateStoryContent(art) {
        if (!art || !window.getArtworkStory) return;
        const story = window.getArtworkStory(art);
        if (!story) return;

        if (storyTitle) storyTitle.textContent = story.title;
        if (storyEntitle) storyEntitle.textContent = story.enTitle || '';
        if (storyArtist) storyArtist.textContent = story.artist;
        if (storyPeriod) storyPeriod.textContent = story.period;
        if (storyGenre) storyGenre.textContent = story.genre;
        if (storyLocation) storyLocation.textContent = story.location;
        if (storyContext) storyContext.textContent = story.context;
        if (storyAppreciation) storyAppreciation.textContent = story.appreciation;
        if (storyQuoteText) storyQuoteText.textContent = story.quote;
        if (storyQuoteAuthor) storyQuoteAuthor.textContent = story.quoteAuthor;
    }

    /**
     * 打开名画背景故事抽屉
     */
    function openStory() {
        if (!storyDrawer) return;

        // 若画笔弹窗展开，顺畅收起
        if (brushPopup && brushPopup.classList.contains('open')) {
            brushPopup.classList.remove('open');
            if (brushToggleBtn) brushToggleBtn.classList.remove('active');
        }

        const currentArt = masterpieces[currentMasterpieceIndex];
        if (currentArt) {
            updateStoryContent(currentArt);
        }

        document.body.classList.add('story-open');
        storyDrawer.classList.add('open');
        storyDrawer.setAttribute('aria-hidden', 'false');
    }

    /**
     * 关闭名画背景故事抽屉
     */
    function closeStory() {
        if (!storyDrawer) return;
        document.body.classList.remove('story-open');
        storyDrawer.classList.remove('open');
        storyDrawer.setAttribute('aria-hidden', 'true');
        isCursorActive = false;
    }

    /**
     * 切换名画背景故事抽屉展开/收起
     */
    function toggleStory() {
        if (storyDrawer && storyDrawer.classList.contains('open')) {
            closeStory();
        } else {
            openStory();
        }
    }

    /**
     * 初始化故事交互事件监听
     */
    function setupStoryUI() {
        if (storyToggleBtn) {
            storyToggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleStory();
            });
        }

        if (brushStoryBtn) {
            brushStoryBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // 打开鉴赏故事抽屉时，收起画笔面板以保持开阔的鉴赏阅读视野
                if (brushPopup && brushPopup.classList.contains('open')) {
                    brushPopup.classList.remove('open');
                    if (brushToggleBtn) brushToggleBtn.classList.remove('active');
                }
                openStory();
            });
        }

        if (storyCloseBtn) {
            storyCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeStory();
            });
        }

        if (storyBackdrop) {
            storyBackdrop.addEventListener('click', (e) => {
                e.stopPropagation();
                closeStory();
            });
        }

        if (storyPrevBtn) {
            storyPrevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const nextIdx = (currentMasterpieceIndex - 1 + masterpieces.length) % masterpieces.length;
                switchMasterpiece(nextIdx);
                updateStoryContent(masterpieces[nextIdx]);
            });
        }

        if (storyNextBtn) {
            storyNextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const nextIdx = (currentMasterpieceIndex + 1) % masterpieces.length;
                switchMasterpiece(nextIdx);
                updateStoryContent(masterpieces[nextIdx]);
            });
        }
    }

    /**
     * 显示轻量优雅的 Toast 提示 (自动淡出)
     * @param {string} msg 
     * @param {string} icon 
     */
    function showToast(msg, icon = '✨') {
        if (!modeToast) return;
        if (toastTimer) {
            clearTimeout(toastTimer);
            toastTimer = null;
        }
        if (toastIconEl) toastIconEl.textContent = icon;
        if (toastTextEl) toastTextEl.textContent = msg;
        modeToast.classList.add('visible', 'show');
        toastTimer = setTimeout(() => {
            modeToast.classList.remove('visible', 'show');
            toastTimer = null;
        }, 2500);
    }

    /**
     * 消除首次入场操作提示 (自然淡出过渡)
     */
    function dismissInitialHint() {
        if (isHintDismissed) return;
        isHintDismissed = true;
        if (interactiveHint) {
            interactiveHint.classList.add('dismissed');
            setTimeout(() => {
                if (interactiveHint && interactiveHint.parentNode) {
                    interactiveHint.style.display = 'none';
                }
            }, 800);
        }
    }

    /**
     * 根据当前体验模式动态切换操作提示语
     * @param {'sleep' | 'scratch'} mode 
     */
    function updateHintText(mode) {
        if (!hintTextEl) return;
        if (mode === 'scratch') {
            hintTextEl.textContent = '用鼠标擦拭画面 · 透出下一幅随机名画';
        } else {
            hintTextEl.textContent = '用鼠标轻拂屏幕唤醒色彩 · 悬停可充能绽放';
        }
    }

    /**
     * 打开操作与快捷键指南弹窗
     */
    function openHelp() {
        if (!helpModal) return;
        document.body.classList.add('help-open');
        helpModal.classList.add('open');
        helpModal.setAttribute('aria-hidden', 'false');
    }

    /**
     * 关闭操作与快捷键指南弹窗
     */
    function closeHelp() {
        if (!helpModal) return;
        document.body.classList.remove('help-open');
        helpModal.classList.remove('open');
        helpModal.setAttribute('aria-hidden', 'true');
        isCursorActive = false;
    }

    /**
     * 切换操作与快捷键指南弹窗
     */
    function toggleHelp() {
        if (!helpModal) return;
        if (helpModal.classList.contains('open')) {
            closeHelp();
        } else {
            openHelp();
        }
    }

    /**
     * 绑定操作指南弹窗事件
     */
    function setupHelpUI() {
        if (helpToggleBtn) {
            helpToggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleHelp();
            });
        }
        if (helpCloseBtn) {
            helpCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeHelp();
            });
        }
        if (helpGotItBtn) {
            helpGotItBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeHelp();
            });
        }
        if (helpBackdrop) {
            helpBackdrop.addEventListener('click', (e) => {
                e.stopPropagation();
                closeHelp();
            });
        }
    }

    /**
     * 鼠标、触控与交互事件监听
     */
    function setupEvents() {
        window.addEventListener('resize', handleResize);

        // 鼠标拖拽平移漫游状态 (微距放大时支持左键/右键/中键自如拖拽漫游)
        let isDraggingPan = false;
        let dragStartMouse = { x: 0, y: 0 };
        let dragStartPan = { x: 0, y: 0 };

        // 移动端多指操作冷却机制 (防止松开两指时毫秒级时间差误触发单指乱划或误切画作)
        let pinchCooldownUntil = 0;
        let isPinching = false;
        let pinchStartDist = 0;
        let pinchStartZoom = 1.0;
        let pinchStartPan = { x: 0, y: 0 };
        let pinchCenter = { x: 0, y: 0 };

        const artStageEl = document.getElementById('art-stage');

        // 鼠标移动事件监听
        window.addEventListener('mousemove', (e) => {
            // 1. 处理微距放大状态下的鼠标拖拽平移漫游
            if (isDraggingPan) {
                panOffset.x = dragStartPan.x + (e.clientX - dragStartMouse.x);
                panOffset.y = dragStartPan.y + (e.clientY - dragStartMouse.y);
                refreshLayout();
                updateMacroZoomHud();
                if (isLoupeEnabled) {
                    renderMacroLoupe(e.clientX, e.clientY);
                }
                return;
            }

            // 2. 检查鼠标当前是否位于展厅、背景故事抽屉、操作指南弹窗或画笔设置面板内部
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));

            if (isOverModal) {
                // 悬停在交互面板上：隐藏自定义圆环，显示原生系统清晰高亮指针
                if (cursor) {
                    cursor.style.opacity = '0';
                    cursor.classList.remove('active');
                }
                if (artStageEl) {
                    artStageEl.classList.remove('macro-panning', 'macro-panning-active');
                }
                if (isLoupeEnabled && macroLoupe) {
                    macroLoupe.classList.remove('active');
                    isLoupeVisible = false;
                }
                isCursorActive = false;
                lastPointerPos = null;
                return;
            }

            dismissInitialHint();
            const now = performance.now();
            const pos = { x: e.clientX, y: e.clientY };

            // 3. 古典黄铜透镜模式：专心渲染真彩超清透视，绝不污染或涂抹底层名画
            if (isLoupeEnabled) {
                lastLoupePointerPos = pos;
                renderMacroLoupe(pos.x, pos.y);
                if (cursor) {
                    cursor.style.opacity = '0';
                    cursor.classList.remove('active');
                }
                if (artStageEl) {
                    artStageEl.classList.remove('macro-panning', 'macro-panning-active');
                }
                lastPointerPos = null;
                return;
            }

            // 4. 微距放大状态：呈现抓手光标 (Grab)，允许按住拖动漫游
            if (macroZoom > 1.05) {
                if (artStageEl) {
                    artStageEl.classList.add('macro-panning');
                    artStageEl.classList.remove('macro-panning-active');
                }
                if (cursor) {
                    cursor.style.opacity = '0';
                    cursor.classList.remove('active');
                }
                lastPointerPos = null;
                return;
            } else {
                if (artStageEl) {
                    artStageEl.classList.remove('macro-panning', 'macro-panning-active');
                }
            }

            // 5. 正常全景状态：极简艺术光标与轻拂涂抹唤醒
            currentPointerPos = pos;
            isPointerActive = true;
            lastMoveTime = now;

            if (cursor) {
                cursor.style.transform = `translate3d(${pos.x}px, ${pos.y}px, 0)`;
                if (!isCursorActive) {
                    isCursorActive = true;
                    cursor.style.opacity = '1';
                    cursor.classList.add('active');
                }
            }

            if (lastPointerPos) {
                const moveDx = pos.x - lastPointerPos.x;
                const moveDy = pos.y - lastPointerPos.y;
                const moveDist = Math.hypot(moveDx, moveDy);

                if (moveDist > 1) {
                    const dot = (moveDx * lastMoveVector.x + moveDy * lastMoveVector.y) /
                                (moveDist * Math.hypot(lastMoveVector.x, lastMoveVector.y) || 1);

                    strokeMoveDistance += moveDist;

                    if (dot < 0.2 || strokeMoveDistance > 160) {
                        currentStrokeId++;
                        strokeMoveDistance = 0;
                    }

                    lastMoveVector = { x: moveDx, y: moveDy };
                    strokeLine(lastPointerPos, pos, currentStrokeId, now);
                }
            } else {
                currentStrokeId++;
                applyDab(pos.x, pos.y, currentStrokeId, config.singlePassGain, now);
            }

            lastPointerPos = pos;

            if (!isQuoteSubtle && artQuote) {
                isQuoteSubtle = true;
                artQuote.classList.add('subtle');
            }
        });

        // 鼠标按下：在微距放大状态下按住左键/右键/中键均可拖动画布漫游
        window.addEventListener('mousedown', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));
            if (isOverModal) return;

            if (macroZoom > 1.05 && !isLoupeEnabled) {
                isDraggingPan = true;
                dragStartMouse = { x: e.clientX, y: e.clientY };
                dragStartPan = { x: panOffset.x, y: panOffset.y };
                if (artStageEl) {
                    artStageEl.classList.add('macro-panning-active');
                }
                if (e.button === 2) {
                    e.preventDefault();
                }
            }
        });

        // 鼠标松开：结束拖拽漫游
        window.addEventListener('mouseup', () => {
            if (isDraggingPan) {
                isDraggingPan = false;
                if (artStageEl) {
                    artStageEl.classList.remove('macro-panning-active');
                    if (macroZoom > 1.05) {
                        artStageEl.classList.add('macro-panning');
                    }
                }
            }
        });

        // 桌面端双击屏幕智能分流：放大状态下双击平滑弹性复位至全景；全景状态下双击切换全彩盛放
        window.addEventListener('dblclick', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));
            if (isOverModal) return;

            if (macroZoom > 1.05 || Math.abs(panOffset.x) > 6 || Math.abs(panOffset.y) > 6) {
                resetMacroZoom();
                showToast('🔍 已平滑复位至全景');
            } else {
                toggleFullColor();
            }
        });

        // 屏蔽画布区域的右键上下文菜单，防止打断操作
        window.addEventListener('contextmenu', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup'));
            if (!isOverModal) {
                e.preventDefault();
            }
        });

        // 桌面端鼠标滚轮：透镜开启时无级调节透镜倍率，未开启时平滑缩放名画
        window.addEventListener('wheel', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup'));
            if (isOverModal) return;

            if (e.cancelable) e.preventDefault();

            // 若微距透镜开启，滚轮无级调焦微距透镜
            if (isLoupeEnabled) {
                const factor = e.deltaY < 0 ? 1.15 : 0.87;
                setLoupeZoom(loupeZoom * factor);
                return;
            }

            // 否则滚轮平滑缩放整幅画作
            const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
            const oldZoom = macroZoom;
            const newZoom = Math.max(1.0, Math.min(4.5, macroZoom * zoomFactor));

            if (Math.abs(newZoom - oldZoom) > 0.004) {
                const mouseX = e.clientX;
                const mouseY = e.clientY;
                const cx = viewportWidth / 2 + panOffset.x;
                const cy = viewportHeight / 2 + panOffset.y;
                const scaleChange = newZoom / oldZoom;
                panOffset.x = mouseX - (mouseX - cx) * scaleChange - viewportWidth / 2;
                panOffset.y = mouseY - (mouseY - cy) * scaleChange - viewportHeight / 2;
                macroZoom = newZoom;

                if (macroZoom < 1.03) {
                    macroZoom = 1.0;
                    panOffset.x = 0;
                    panOffset.y = 0;
                }

                refreshLayout();
                updateMacroZoomHud();
            }
        }, { passive: false });

        // 鼠标离开视口
        window.addEventListener('mouseleave', () => {
            isPointerActive = false;
            isDraggingPan = false;
            lastPointerPos = null;
            currentPointerPos = null;
            lastMoveVector = { x: 0, y: 0 };
            currentStrokeId++;
            isCursorActive = false;
            isQuoteSubtle = false;

            if (cursor) {
                cursor.style.opacity = '0';
                cursor.classList.remove('active');
            }
            if (artStageEl) {
                artStageEl.classList.remove('macro-panning', 'macro-panning-active');
            }
            if (isLoupeEnabled && macroLoupe) {
                macroLoupe.classList.remove('active');
                isLoupeVisible = false;
            }
            if (artQuote) {
                artQuote.classList.remove('subtle');
            }
        });

        // 移动端专用触控手势与状态追踪 (双指 Pinch-to-zoom、Canvas Pan 与冷却互锁)
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;
        let lastTapTime = 0;
        let lastTapPos = { x: 0, y: 0 };

        // 移动端 touchstart
        window.addEventListener('touchstart', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));
            if (isOverModal) {
                lastPointerPos = null;
                return;
            }

            dismissInitialHint();

            // 1. 双指触控：进入微距捏合缩放与平移漫游模式
            if (e.touches.length >= 2) {
                isPinching = true;
                isPointerActive = false;
                currentPointerPos = null;
                lastPointerPos = null;

                const t1 = e.touches[0];
                const t2 = e.touches[1];
                pinchStartDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY) || 1;
                pinchStartZoom = macroZoom;
                pinchStartPan = { x: panOffset.x, y: panOffset.y };
                pinchCenter = {
                    x: (t1.clientX + t2.clientX) / 2,
                    y: (t1.clientY + t2.clientY) / 2
                };
                if (e.cancelable) e.preventDefault();
                return;
            }

            // 检查多指冷却期：刚捏合完毕时严密拦截单指误划
            if (performance.now() < pinchCooldownUntil) {
                return;
            }

            // 2. 单指触控：名画唤醒涂抹 / 透镜移动
            if (e.touches.length === 1 && !isPinching) {
                const now = performance.now();
                const t = e.touches[0];
                const pos = { x: t.clientX, y: t.clientY };
                
                touchStartX = pos.x;
                touchStartY = pos.y;
                touchStartTime = now;

                if (isLoupeEnabled) {
                    lastLoupePointerPos = pos;
                    renderMacroLoupe(pos.x, pos.y);
                    return;
                }

                currentPointerPos = pos;
                lastPointerPos = pos;
                isPointerActive = true;
                lastMoveTime = now;
                currentStrokeId++;
                strokeMoveDistance = 0;
                applyDab(pos.x, pos.y, currentStrokeId, config.singlePassGain, now);
            }
        }, { passive: false });

        // 移动端 touchmove
        window.addEventListener('touchmove', (e) => {
            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));
            if (isOverModal) {
                lastPointerPos = null;
                return;
            }

            if (e.cancelable) {
                e.preventDefault();
            }

            // 1. 双指捏合缩放与平移漫游
            if (e.touches.length >= 2) {
                isPinching = true;
                isPointerActive = false;

                const t1 = e.touches[0];
                const t2 = e.touches[1];
                const currentDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
                const currentCenter = {
                    x: (t1.clientX + t2.clientX) / 2,
                    y: (t1.clientY + t2.clientY) / 2
                };

                const distRatio = currentDist / pinchStartDist;
                const newZoom = Math.max(1.0, Math.min(4.5, pinchStartZoom * distRatio));

                const panDx = currentCenter.x - pinchCenter.x;
                const panDy = currentCenter.y - pinchCenter.y;
                panOffset.x = pinchStartPan.x + panDx;
                panOffset.y = pinchStartPan.y + panDy;
                macroZoom = newZoom;

                refreshLayout();
                updateMacroZoomHud();
                return;
            }

            // 冷却期防护
            if (isPinching || performance.now() < pinchCooldownUntil) {
                return;
            }

            // 2. 单指划动涂抹或透镜移动
            if (e.touches.length === 1 && !isPinching) {
                const now = performance.now();
                const t = e.touches[0];
                const pos = { x: t.clientX, y: t.clientY };

                if (isLoupeEnabled) {
                    lastLoupePointerPos = pos;
                    renderMacroLoupe(pos.x, pos.y);
                    return;
                }

                currentPointerPos = pos;
                isPointerActive = true;
                lastMoveTime = now;

                if (lastPointerPos) {
                    const moveDx = pos.x - lastPointerPos.x;
                    const moveDy = pos.y - lastPointerPos.y;
                    const moveDist = Math.hypot(moveDx, moveDy);
                    strokeMoveDistance += moveDist;

                    if (strokeMoveDistance > 140) {
                        currentStrokeId++;
                        strokeMoveDistance = 0;
                    }

                    strokeLine(lastPointerPos, pos, currentStrokeId, now);
                } else {
                    applyDab(pos.x, pos.y, currentStrokeId, config.singlePassGain, now);
                }
                lastPointerPos = pos;
            }
        }, { passive: false });

        // 移动端 touchend
        window.addEventListener('touchend', (e) => {
            // 双指捏合结束：启动 350ms 冷却保护期，杜绝松开手指时的手势竞争
            if (isPinching) {
                if (e.touches.length === 0) {
                    isPinching = false;
                    pinchCooldownUntil = performance.now() + 350;
                    if (macroZoom < 1.06) {
                        resetMacroZoom();
                    }
                }
                return;
            }

            if (performance.now() < pinchCooldownUntil) {
                return;
            }

            isPointerActive = false;
            lastPointerPos = null;
            currentPointerPos = null;
            currentStrokeId++;

            if (isLoupeEnabled && macroLoupe) {
                macroLoupe.classList.remove('active');
                isLoupeVisible = false;
            }

            const isOverModal = Boolean(e.target && e.target.closest && e.target.closest('.gallery-panel, .story-panel, .help-dialog, .brush-popup, .macro-zoom-hud'));
            if (isOverModal) return;

            const now = performance.now();
            const changedTouch = e.changedTouches && e.changedTouches[0];
            if (changedTouch) {
                const endX = changedTouch.clientX;
                const endY = changedTouch.clientY;
                const touchDx = endX - touchStartX;
                const touchDy = endY - touchStartY;
                const touchDuration = now - touchStartTime;
                const touchDistance = Math.hypot(touchDx, touchDy);

                // 1. 手机端双击屏幕智能分流：
                // 放大状态下双击平滑弹性复位至 100% 全景；100% 全貌时双击一键全彩盛放/恢复沉睡
                if (touchDistance < 22 && touchDuration < 280) {
                    const timeSinceLastTap = now - lastTapTime;
                    const tapDistFromLast = Math.hypot(endX - lastTapPos.x, endY - lastTapPos.y);
                    if (timeSinceLastTap < 320 && tapDistFromLast < 35) {
                        if (macroZoom > 1.05 || Math.abs(panOffset.x) > 6 || Math.abs(panOffset.y) > 6) {
                            resetMacroZoom();
                            showToast('🔍 已平滑复位至全景');
                        } else {
                            toggleFullColor();
                        }
                        lastTapTime = 0;
                        return;
                    }
                    lastTapTime = now;
                    lastTapPos = { x: endX, y: endY };
                }

                // 2. 手机端水平快速轻扫切画：严格仅在非放大状态（<= 1.05）且非透镜模式下触发，杜绝放大漫游时意外误切画作
                if (!isLoupeEnabled && macroZoom <= 1.05 && touchDuration < 420 && Math.abs(touchDx) > 68 && Math.abs(touchDx) > Math.abs(touchDy) * 1.6) {
                    if (touchDx < 0) {
                        const nextIdx = (currentMasterpieceIndex + 1) % masterpieces.length;
                        switchMasterpiece(nextIdx);
                    } else {
                        const prevIdx = (currentMasterpieceIndex - 1 + masterpieces.length) % masterpieces.length;
                        switchMasterpiece(prevIdx);
                    }
                }
            }
        });

        // 监听移动端屏幕旋转与虚拟视口尺寸变动
        window.addEventListener('orientationchange', () => {
            setTimeout(handleResize, 180);
        });
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', handleResize);
        }

        // 触控设备专属文案自适应
        const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (window.matchMedia && window.matchMedia('(pointer: coarse)').matches);
        if (isTouchDevice) {
            const hintTextEl = document.getElementById('hint-text');
            if (hintTextEl) {
                hintTextEl.textContent = '轻触划动指尖唤醒色彩 · 长按可充能绽放';
            }
        }
    }

    /**
     * 引擎启动与名画载入
     */
    function start() {
        if (isInitialized) return;
        isInitialized = true;

        handleResize();
        setupBrushUI();
        setupGalleryUI();
        setupStoryUI();
        setupHelpUI();
        setupEvents();

        // 首次入场提示在 5 秒后如晨雾般优雅自动淡出
        setTimeout(dismissInitialHint, 5000);

        gardenImage.onload = () => {
            isImageLoaded = true;
            computeImageBounds();
            if (appMode === 'scratch') {
                renderScratchBackground();
            } else {
                renderGrayscaleBackground();
            }
            // 预加载下一幅候选名画，让漫游擦画即刻就绪
            prepareNextRandomArtwork();
            markDirty();
        };

        // 默认载入首幅传世名画
        switchMasterpiece(0);

        markDirty();
    }

    // 暴露诊断与调试接口
    window.__gardenEngine = {
        isLoaded: () => isImageLoaded,
        getAppMode: () => appMode,
        setAppMode: setAppMode,
        getBrushRadius: () => config.brushRadius,
        setBrushRadius: updateBrushSize,
        getDuration: () => config.totalDurationSeconds,
        setDuration: updateDuration,
        getColorRatio: () => config.colorRatio,
        setColorRatio: updateColorRatio,
        getMasterpieces: () => masterpieces,
        getCurrentIndex: () => currentMasterpieceIndex,
        setMasterpiece: switchMasterpiece,
        openStory: openStory,
        closeStory: closeStory,
        toggleStory: toggleStory,
        openHelp: openHelp,
        closeHelp: closeHelp,
        toggleHelp: toggleHelp,
        showToast: showToast,
        dismissHint: dismissInitialHint,
        getNextMasterpieceIndex: () => nextMasterpieceIndex,
        getScratchRatio: () => scratchConfig.ratio,
        getScratchThreshold: () => scratchConfig.threshold,
        setScratchThreshold: (t) => {
            const val = Math.max(0.5, Math.min(0.95, t));
            scratchConfig.threshold = val;
            if (scratchThresholdSlider) scratchThresholdSlider.value = Math.round(val * 100);
            if (scratchThresholdDisplay) scratchThresholdDisplay.textContent = `${Math.round(val * 100)}%`;
            if (scratchHudTargetVal) scratchHudTargetVal.textContent = `${Math.round(val * 100)}%`;
        },
        triggerScratchReveal: triggerAutoScratchReveal,
        isScratchLocked: () => scratchConfig.isLocked,
        setFitMode: setFitMode,
        getFitMode: () => config.fitMode,
        setScale: setScale,
        getScale: () => config.scale,
        getBounds: () => imageBounds,
        getNextBounds: () => nextImageBounds,
        isNextLoaded: () => isNextImageLoaded,
        getNextImgInfo: () => ({ src: nextGardenImage.src, complete: nextGardenImage.complete, nw: nextGardenImage.naturalWidth, nh: nextGardenImage.naturalHeight }),
        toggleFullColor: toggleFullColor,
        isFullColor: () => isFullColorLocked,
        getMacroZoom: () => macroZoom,
        setMacroZoom: (z) => {
            macroZoom = Math.max(1.0, Math.min(4.5, z));
            refreshLayout();
            updateMacroZoomHud();
        },
        getPanOffset: () => ({ ...panOffset }),
        setPanOffset: (x, y) => {
            panOffset.x = x;
            panOffset.y = y;
            refreshLayout();
            updateMacroZoomHud();
        },
        resetMacroZoom: resetMacroZoom,
        isLoupeEnabled: () => isLoupeEnabled,
        toggleLoupe: toggleLoupe,
        getLoupeZoom: () => loupeZoom,
        cycleLoupeZoom: cycleLoupeZoom,
        stroke: (x1, y1, x2, y2) => {
            currentStrokeId++;
            strokeLine({ x: x1, y: y1 }, { x: x2, y: y2 }, currentStrokeId, performance.now());
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
