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
    const toggleFullColorBtn = document.getElementById('toggle-full-color-btn');
    const fullColorBtnText = document.getElementById('full-color-btn-text');

    // 画面规格与缩放控制 UI 元素
    const fitAutoBtn = document.getElementById('fit-auto-btn');
    const fitContainBtn = document.getElementById('fit-contain-btn');
    const fitCoverBtn = document.getElementById('fit-cover-btn');
    const fitModeDisplay = document.getElementById('fit-mode-display');
    const fitScaleSlider = document.getElementById('fit-scale-slider');
    const fitScaleDisplay = document.getElementById('fit-scale-display');

    // 名画画廊切换 UI 元素
    const masterpieceSelect = document.getElementById('masterpiece-select');
    const masterpieceIndexBadge = document.getElementById('masterpiece-index');
    const prevArtBtn = document.getElementById('prev-art-btn');
    const nextArtBtn = document.getElementById('next-art-btn');

    const bgCtx = bgCanvas.getContext('2d');
    const revealCtx = revealCanvas.getContext('2d');

    // 离屏遮罩画布 (全分辨率) 与低分辨率网格采样画布
    const maskCanvas = document.createElement('canvas');
    const maskCtx = maskCanvas.getContext('2d');

    const maskSmallCanvas = document.createElement('canvas');
    const maskSmallCtx = maskSmallCanvas.getContext('2d', { willReadFrequently: true });

    // 交互参数配置
    const config = {
        brushRadius: 75,             // 默认画笔半径 (px)
        minBrushRadius: 35,          // 最小画笔半径
        maxBrushRadius: 160,         // 最大画笔半径
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
    let gridAlpha = null;        // 当前累积显色度 (0.0 ~ 1.0)
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

    // 传世名画博览馆数据库 (由 data/masterpieces.js 注入全量名作，具备完整 10 大艺术史展厅分类)
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
    }

    /**
     * 计算名画在视口中的几何布局参数 (支持智能自适应/完整呈现/居中铺满与无级缩放)
     */
    function computeImageBounds() {
        if (!isImageLoaded) return;
        const imgW = gardenImage.naturalWidth || 2560;
        const imgH = gardenImage.naturalHeight || 1440;
        const imgAspect = imgW / imgH;
        const screenAspect = viewportWidth / viewportHeight;

        let effectiveMode = config.fitMode;
        if (effectiveMode === 'auto') {
            // 智能判定：横屏遇到竖幅或方幅名画 (如 1:1 的日本桥) 自动采用完整呈现 (Contain)，避免上下重要画面被剧烈裁剪！
            if (screenAspect > 1.2 && imgAspect < 1.22) {
                effectiveMode = 'contain';
            } else if (screenAspect < 0.88 && imgAspect > 1.1) {
                effectiveMode = 'contain';
            } else {
                effectiveMode = 'cover';
            }
        }

        let drawW, drawH;
        if (effectiveMode === 'contain') {
            // 完整呈现模式：整幅名画 100% 完整容纳于视口内，四周留有雅致古典画廊留白
            if (screenAspect > imgAspect) {
                drawH = viewportHeight * 0.94;
                drawW = drawH * imgAspect;
            } else {
                drawW = viewportWidth * 0.94;
                drawH = drawW / imgAspect;
            }
        } else {
            // 居中铺满模式：无黑边充满视口，且真正绝对居中锚定
            if (screenAspect > imgAspect) {
                drawW = viewportWidth;
                drawH = viewportWidth / imgAspect;
            } else {
                drawH = viewportHeight;
                drawW = viewportHeight * imgAspect;
            }
        }

        // 应用用户自定义缩放倍率
        drawW *= config.scale;
        drawH *= config.scale;

        // 视口绝对中心对称对齐
        const drawX = (viewportWidth - drawW) / 2;
        const drawY = (viewportHeight - drawH) / 2;

        imageBounds = { x: drawX, y: drawY, w: drawW, h: drawH, effectiveMode: effectiveMode };
    }

    /**
     * 刷新视口布局与底图重绘
     */
    function refreshLayout() {
        computeImageBounds();
        renderGrayscaleBackground();
        if (isFullColorLocked) {
            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
            revealCtx.drawImage(
                gardenImage,
                imageBounds.x,
                imageBounds.y,
                imageBounds.w,
                imageBounds.h
            );
        }
    }

    /**
     * 渲染底层古典灰阶油画 (保持 1:1 纯粹灰度质感)
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
     * 视口尺寸变化与高清 Retina DPI 适配
     */
    function handleResize() {
        viewportWidth = window.innerWidth;
        viewportHeight = window.innerHeight;
        dpr = window.devicePixelRatio || 1;

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
        renderGrayscaleBackground();
    }

    /**
     * 在单点周围施加笔刷涂抹 (多划几下渐进累加)
     * @param {number} px 屏幕X坐标
     * @param {number} py 屏幕Y坐标
     * @param {number} strokeId 当前划动的编号
     * @param {number} gainBase 显色增量基数
     * @param {number} now 时间戳
     */
    function applyDab(px, py, strokeId, gainBase, now) {
        const radius = config.brushRadius;
        const cellSize = config.cellSize;

        const minCol = Math.max(0, Math.floor((px - radius) / cellSize));
        const maxCol = Math.min(gridCols - 1, Math.floor((px + radius) / cellSize));
        const minRow = Math.max(0, Math.floor((py - radius) / cellSize));
        const maxRow = Math.min(gridRows - 1, Math.floor((py + radius) / cellSize));

        for (let r = minRow; r <= maxRow; r++) {
            const cellCenterY = (r + 0.5) * cellSize;
            const dy = cellCenterY - py;
            const dy2 = dy * dy;

            for (let c = minCol; c <= maxCol; c++) {
                const cellCenterX = (c + 0.5) * cellSize;
                const dx = cellCenterX - px;
                const dist2 = dx * dx + dy2;

                if (dist2 <= radius * radius) {
                    const dist = Math.sqrt(dist2);
                    const idx = r * gridCols + c;

                    // 同一次划过同一单元格仅生效一次，防止插值密集时单笔直接爆满
                    if (strokeId !== null && gridLastStroke[idx] === strokeId) {
                        continue;
                    }

                    if (strokeId !== null) {
                        gridLastStroke[idx] = strokeId;
                    }

                    // 径向平滑余弦羽化权重 (核心饱满，外圈柔润晕染)
                    const normalizedDist = dist / radius;
                    const weight = 0.5 * (1 + Math.cos(normalizedDist * Math.PI));

                    // 渐进增加透明度
                    const increment = gainBase * weight;
                    gridAlpha[idx] = Math.min(1.0, gridAlpha[idx] + increment);
                    gridLastTouch[idx] = now;
                }
            }
        }
    }

    /**
     * 笔触轨迹插值 (保证高速滑动时笔刷轨迹平滑无断点)
     */
    function strokeLine(from, to, strokeId, now) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dist = Math.hypot(dx, dy);
        const step = Math.max(6, config.brushRadius * 0.25);

        if (dist <= 0) {
            applyDab(to.x, to.y, strokeId, config.singlePassGain, now);
            return;
        }

        const steps = Math.ceil(dist / step);
        for (let i = 1; i <= steps; i++) {
            const t = i / steps;
            applyDab(from.x + dx * t, from.y + dy * t, strokeId, config.singlePassGain, now);
        }
    }

    /**
     * 鼠标停驻充能 (只有停留或反复摩擦之处才会迅速蓄满 100% 满彩)
     */
    function applyHoverCharge(px, py, now) {
        const radius = config.brushRadius;
        const cellSize = config.cellSize;

        const minCol = Math.max(0, Math.floor((px - radius) / cellSize));
        const maxCol = Math.min(gridCols - 1, Math.floor((px + radius) / cellSize));
        const minRow = Math.max(0, Math.floor((py - radius) / cellSize));
        const maxRow = Math.min(gridRows - 1, Math.floor((py + radius) / cellSize));

        for (let r = minRow; r <= maxRow; r++) {
            const cellCenterY = (r + 0.5) * cellSize;
            const dy = cellCenterY - py;
            const dy2 = dy * dy;

            for (let c = minCol; c <= maxCol; c++) {
                const cellCenterX = (c + 0.5) * cellSize;
                const dx = cellCenterX - px;
                const dist2 = dx * dx + dy2;

                if (dist2 <= radius * radius) {
                    const dist = Math.sqrt(dist2);
                    const idx = r * gridCols + c;

                    const normalizedDist = dist / radius;
                    const weight = 0.5 * (1 + Math.cos(normalizedDist * Math.PI));

                    // 停驻充能：层层滋润绽放
                    const increment = config.hoverChargeGain * weight;
                    gridAlpha[idx] = Math.min(1.0, gridAlpha[idx] + increment);
                    gridLastTouch[idx] = now; // 持续更新时间戳，停留处永久盛开
                }
            }
        }
    }

    /**
     * 核心渲染主循环 (双线性插值遮罩与独立生命周期衰减)
     */
    function renderLoop(currentTime) {
        // 1. 停驻充能逻辑：当鼠标处于激活状态且停留未剧烈移动时，持续充能
        if (isPointerActive && currentPointerPos) {
            const timeSinceMove = currentTime - lastMoveTime;
            // 只要停顿超过 40ms，即进入原地充能机制，每 45ms 充能一次
            if (timeSinceMove > 40 && currentTime - lastHoverChargeTime > 45) {
                applyHoverCharge(currentPointerPos.x, currentPointerPos.y, currentTime);
                lastHoverChargeTime = currentTime;
            }
        }

        // 2. 衰减与留存计算：在保留期内 100% 保持，过后平滑渐隐退回灰色
        const data = maskSmallImageData ? maskSmallImageData.data : null;
        let hasActiveColor = false;

        if (data && totalCells > 0) {
            if (isFullColorLocked) {
                // 一键全彩模式：所有网格单元强制展现 100% 原画真彩
                hasActiveColor = true;
                for (let i = 0; i < totalCells; i++) {
                    data[i * 4 + 3] = 255;
                }
            } else {
                const solidMs = config.solidDurationMs;
                const fadeMs = config.fadeDurationMs;

                for (let i = 0; i < totalCells; i++) {
                    const alpha = gridAlpha[i];
                    if (alpha <= 0.001) {
                        data[i * 4 + 3] = 0;
                        continue;
                    }

                const elapsed = currentTime - gridLastTouch[i];
                let currentAlpha = alpha;

                if (elapsed <= solidMs) {
                    // 保留期内：维持当前涂抹出的彩色强度不退色
                    currentAlpha = alpha;
                } else {
                    // 超过保留期后：在 2.0 秒内优雅余弦衰减
                    const fadeProgress = (elapsed - solidMs) / fadeMs;
                    if (fadeProgress >= 1.0) {
                        gridAlpha[i] = 0;
                        currentAlpha = 0;
                    } else {
                        const decayFactor = 0.5 * (1 + Math.cos(fadeProgress * Math.PI));
                        currentAlpha = alpha * decayFactor;
                    }
                }

                if (currentAlpha > 0.002) {
                    hasActiveColor = true;
                    data[i * 4 + 3] = Math.min(255, Math.round(currentAlpha * 255));
                } else {
                    data[i * 4 + 3] = 0;
                }
            }
        }
    }

        // 3. 将小尺寸网格遮罩通过 GPU 双线性平滑插值投射到全屏遮罩
        revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

        if (isImageLoaded && hasActiveColor) {
            maskSmallCtx.putImageData(maskSmallImageData, 0, 0);

            maskCtx.clearRect(0, 0, viewportWidth, viewportHeight);
            maskCtx.save();
            maskCtx.imageSmoothingEnabled = true;
            maskCtx.imageSmoothingQuality = 'high';
            maskCtx.drawImage(maskSmallCanvas, 0, 0, viewportWidth, viewportHeight);
            maskCtx.restore();

            // 绘制彩色原图并使用 destination-in 应用平滑羽化遮罩
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

        requestAnimationFrame(renderLoop);
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
     * 绑定画笔控制面板事件
     */
    function setupBrushUI() {
        if (!brushToggleBtn || !brushPopup) return;

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

        // 初始化画笔大小、留存时间、规格模式与缩放
        updateBrushSize(config.brushRadius);
        updateDuration(config.totalDurationSeconds);
        setFitMode(config.fitMode);
        setScale(config.scale);
    }

    /**
     * 切换一键全彩盛放状态 (还原为原始全彩 或 恢复沉睡黑白)
     * @param {boolean} [forceState] 可选的强制布尔状态
     */
    function toggleFullColor(forceState) {
        const targetState = (forceState !== undefined) ? forceState : !isFullColorLocked;
        isFullColorLocked = targetState;

        if (isFullColorLocked) {
            // 瞬间将全网格充满至 100% 满彩
            if (gridAlpha) gridAlpha.fill(1.0);
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
    }

    /**
     * 切换当前激活的名画
     * @param {number} index 画作索引 (0 ~ masterpieces.length - 1)
     */
    function switchMasterpiece(index) {
        if (index < 0 || index >= masterpieces.length) return;
        currentMasterpieceIndex = index;
        const art = masterpieces[index];

        // 切换名画时复位全彩模式
        if (isFullColorLocked) {
            toggleFullColor(false);
        }

        // 1. 重置显色状态网格与离屏采样遮罩
        if (gridAlpha) gridAlpha.fill(0);
        if (gridLastStroke) gridLastStroke.fill(0);
        if (maskSmallImageData) {
            const d = maskSmallImageData.data;
            for (let i = 0; i < totalCells; i++) {
                d[i * 4 + 3] = 0;
            }
        }

        // 2. 清理顶层彩色画布
        revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

        // 3. 更新诗意名言与作者署名
        if (quoteTextEl) quoteTextEl.textContent = art.quote;
        if (quoteAuthorEl) quoteAuthorEl.textContent = art.quoteAuthor;

        // 4. 更新控制面板下拉菜单与画作编号徽章
        if (masterpieceSelect) masterpieceSelect.value = index;
        if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `${index + 1} / ${masterpieces.length}`;

        // 5. 载入新名画原图并重新渲染古典灰阶底图
        isImageLoaded = false;
        gardenImage.src = art.src;
    }

    /**
     * 初始化名画画廊选择器 UI
     */
    function setupGalleryUI() {
        if (!masterpieceSelect) return;

        masterpieceSelect.innerHTML = '';

        if (window.ART_CATEGORIES && window.ART_CATEGORIES.length) {
            window.ART_CATEGORIES.forEach(cat => {
                const group = document.createElement('optgroup');
                group.label = cat.name;
                const items = masterpieces
                    .map((art, idx) => ({ art, idx }))
                    .filter(item => item.art.category === cat.id);

                items.forEach(({ art, idx }) => {
                    const opt = document.createElement('option');
                    opt.value = idx;
                    opt.textContent = `${idx + 1}. ${art.title} · ${art.artist}`;
                    group.appendChild(opt);
                });

                if (items.length > 0) {
                    masterpieceSelect.appendChild(group);
                }
            });
        } else {
            const defaultGroup = document.createElement('optgroup');
            defaultGroup.label = `🏛️ 传世名画博览馆 (${masterpieces.length}幅)`;
            masterpieces.forEach((art, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = `${idx + 1}. ${art.title} · ${art.artist}`;
                defaultGroup.appendChild(opt);
            });
            masterpieceSelect.appendChild(defaultGroup);
        }

        masterpieceSelect.addEventListener('change', (e) => {
            switchMasterpiece(parseInt(e.target.value, 10));
        });
        masterpieceSelect.addEventListener('click', (e) => e.stopPropagation());

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

        // 初始选中第 1 幅
        masterpieceSelect.value = 0;
        if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `1 / ${masterpieces.length}`;
    }

    /**
     * 鼠标、触控与交互事件监听
     */
    function setupEvents() {
        window.addEventListener('resize', handleResize);

        // 鼠标移动
        window.addEventListener('mousemove', (e) => {
            const now = performance.now();
            const pos = { x: e.clientX, y: e.clientY };
            currentPointerPos = pos;
            isPointerActive = true;
            lastMoveTime = now;

            // 更新极简艺术光标
            if (cursor) {
                cursor.style.transform = `translate(${pos.x}px, ${pos.y}px)`;
                cursor.style.opacity = '1';
                cursor.classList.add('active');
            }

            if (lastPointerPos) {
                const moveDx = pos.x - lastPointerPos.x;
                const moveDy = pos.y - lastPointerPos.y;
                const moveDist = Math.hypot(moveDx, moveDy);

                if (moveDist > 1) {
                    // 计算划动方向变化：来回折返划动或停顿后划动即判定为新的一划 (开启新的 Stroke ID)
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

            // 交互时莫奈名言自然微弱淡隐
            if (artQuote) {
                artQuote.classList.add('subtle');
            }
        });

        // 鼠标离开视口
        window.addEventListener('mouseleave', () => {
            isPointerActive = false;
            lastPointerPos = null;
            currentPointerPos = null;
            lastMoveVector = { x: 0, y: 0 };
            currentStrokeId++;

            if (cursor) {
                cursor.style.opacity = '0';
                cursor.classList.remove('active');
            }
            if (artQuote) {
                artQuote.classList.remove('subtle');
            }
        });

        // 移动端触控支持
        window.addEventListener('touchstart', (e) => {
            if (e.touches.length > 0) {
                const now = performance.now();
                const t = e.touches[0];
                const pos = { x: t.clientX, y: t.clientY };
                currentPointerPos = pos;
                lastPointerPos = pos;
                isPointerActive = true;
                lastMoveTime = now;
                currentStrokeId++;
                strokeMoveDistance = 0;
                applyDab(pos.x, pos.y, currentStrokeId, config.singlePassGain, now);
            }
        }, { passive: true });

        window.addEventListener('touchmove', (e) => {
            if (e.touches.length > 0) {
                const now = performance.now();
                const t = e.touches[0];
                const pos = { x: t.clientX, y: t.clientY };
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
        }, { passive: true });

        window.addEventListener('touchend', () => {
            isPointerActive = false;
            lastPointerPos = null;
            currentPointerPos = null;
            currentStrokeId++;
        });
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
        setupEvents();

        gardenImage.onload = () => {
            isImageLoaded = true;
            computeImageBounds();
            renderGrayscaleBackground();
        };

        // 默认载入首幅传世名画
        switchMasterpiece(0);

        requestAnimationFrame(renderLoop);
    }

    // 暴露诊断与调试接口
    window.__gardenEngine = {
        isLoaded: () => isImageLoaded,
        getBrushRadius: () => config.brushRadius,
        setBrushRadius: updateBrushSize,
        getDuration: () => config.totalDurationSeconds,
        setDuration: updateDuration,
        getMasterpieces: () => masterpieces,
        getCurrentIndex: () => currentMasterpieceIndex,
        setMasterpiece: switchMasterpiece,
        setFitMode: setFitMode,
        getFitMode: () => config.fitMode,
        setScale: setScale,
        getScale: () => config.scale,
        getBounds: () => imageBounds,
        toggleFullColor: toggleFullColor,
        isFullColor: () => isFullColorLocked,
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
