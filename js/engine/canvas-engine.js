/**
 * Masterpiece Garden · Canvas Core Rendering Engine
 * 双层画布像素对齐、Retina DPI 自适应、空间衰减网格系统与高性能按需渲染循环
 */

import { elements, contexts, appState, config, scratchConfig } from '../state.js';
import { updateScratchRatio } from './scratch-machine.js';

export const SCRATCH_MASK_THRESHOLD = 0.35;

/**
 * 标记画布需要重绘，并按需唤醒帧渲染循环 (静止时 0 开销)
 */
export function markDirty() {
    appState.isDirty = true;
    if (!appState.isRenderingActive) {
        appState.isRenderingActive = true;
        requestAnimationFrame(renderLoop);
    }
}

/**
 * 初始化或重新分配空间衰减网格
 */
export function initGrid() {
    const { viewportWidth, viewportHeight } = appState;
    const { maskSmallCanvas, maskSmallCtx } = contexts;

    appState.gridCols = Math.ceil(viewportWidth / config.cellSize);
    appState.gridRows = Math.ceil(viewportHeight / config.cellSize);
    appState.totalCells = appState.gridCols * appState.gridRows;

    appState.gridAlpha = new Float32Array(appState.totalCells);
    appState.gridLastTouch = new Float64Array(appState.totalCells);
    appState.gridLastStroke = new Int32Array(appState.totalCells);
    appState.scratchedCellsCount = 0;

    maskSmallCanvas.width = appState.gridCols;
    maskSmallCanvas.height = appState.gridRows;
    appState.maskSmallImageData = maskSmallCtx.createImageData(appState.gridCols, appState.gridRows);

    // 默认将小遮罩填充为纯白通道 (RGB=255)，仅动态调制 Alpha 通道
    const data = appState.maskSmallImageData.data;
    for (let i = 0; i < appState.totalCells; i++) {
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
export function computeImageBounds() {
    if (!appState.isImageLoaded) return;
    const { gardenImage, viewportWidth, viewportHeight, macroZoom, panOffset } = appState;
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
            // 2. 手机竖屏模式 (智能完整呈现，杜绝大幅裁剪主体)
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

    // 边界阻尼约束
    if (macroZoom <= 1.01) {
        panOffset.x = 0;
        panOffset.y = 0;
    } else {
        const maxPanX = Math.max(0, (finalW - viewportWidth) / 2 + viewportWidth * 0.25);
        const maxPanY = Math.max(0, (finalH - viewportHeight) / 2 + viewportHeight * 0.25);
        panOffset.x = Math.max(-maxPanX, Math.min(maxPanX, panOffset.x));
        panOffset.y = Math.max(-maxPanY, Math.min(maxPanY, panOffset.y));
    }

    const drawX = (viewportWidth - finalW) / 2 + panOffset.x;
    const drawY = (viewportHeight - finalH) / 2 + panOffset.y;

    appState.imageBounds = {
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
export function computeNextImageBounds() {
    if (!appState.isNextImageLoaded) return;
    const { nextGardenImage, viewportWidth, viewportHeight, macroZoom, panOffset } = appState;
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

    appState.nextImageBounds = {
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
 * 刷新视口布局与底图重绘
 */
export function refreshLayout() {
    computeImageBounds();
    computeNextImageBounds();

    if (appState.appMode === 'scratch') {
        renderScratchBackground();
    } else {
        renderGrayscaleBackground();
        if (appState.isFullColorLocked) {
            const { revealCtx } = contexts;
            revealCtx.clearRect(0, 0, appState.viewportWidth, appState.viewportHeight);
            revealCtx.save();
            revealCtx.globalAlpha = config.colorRatio;
            revealCtx.drawImage(
                appState.gardenImage,
                appState.imageBounds.x,
                appState.imageBounds.y,
                appState.imageBounds.w,
                appState.imageBounds.h
            );
            revealCtx.restore();
        }
    }
    markDirty();
}

/**
 * 渲染底层古典灰阶油画 (经典沉睡模式)
 */
export function renderGrayscaleBackground() {
    if (!appState.isImageLoaded) return;
    const { bgCtx } = contexts;
    const { viewportWidth, viewportHeight, gardenImage, imageBounds } = appState;
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
export function renderScratchBackground() {
    if (appState.appMode !== 'scratch') return;
    const { bgCtx } = contexts;
    const { viewportWidth, viewportHeight, isNextImageLoaded, nextGardenImage, nextImageBounds } = appState;
    bgCtx.save();
    bgCtx.clearRect(0, 0, viewportWidth, viewportHeight);
    bgCtx.fillStyle = '#0d0f12';
    bgCtx.fillRect(0, 0, viewportWidth, viewportHeight);
    bgCtx.filter = 'none';

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
 * 视口尺寸变化与高清 Retina DPI 适配 (兼顾移动端动态地址栏与旋转)
 */
export function handleResize() {
    if (window.visualViewport) {
        appState.viewportWidth = Math.round(window.visualViewport.width);
        appState.viewportHeight = Math.round(window.visualViewport.height);
    } else {
        appState.viewportWidth = window.innerWidth;
        appState.viewportHeight = window.innerHeight;
    }
    appState.dpr = Math.min(window.devicePixelRatio || 1, 2.5);

    const { bgCanvas, revealCanvas } = elements;
    const { bgCtx, revealCtx, maskCanvas, maskCtx } = contexts;
    const { viewportWidth, viewportHeight, dpr } = appState;

    if (bgCanvas) {
        bgCanvas.width = Math.round(viewportWidth * dpr);
        bgCanvas.height = Math.round(viewportHeight * dpr);
        bgCanvas.style.width = viewportWidth + 'px';
        bgCanvas.style.height = viewportHeight + 'px';
        bgCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    if (revealCanvas) {
        revealCanvas.width = Math.round(viewportWidth * dpr);
        revealCanvas.height = Math.round(viewportHeight * dpr);
        revealCanvas.style.width = viewportWidth + 'px';
        revealCanvas.style.height = viewportHeight + 'px';
        revealCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    maskCanvas.width = Math.round(viewportWidth * dpr);
    maskCanvas.height = Math.round(viewportHeight * dpr);
    maskCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

    initGrid();
    computeImageBounds();
    computeNextImageBounds();

    if (appState.appMode === 'scratch') {
        renderScratchBackground();
    } else {
        renderGrayscaleBackground();
    }
}

/**
 * 在单点周围施加笔刷涂抹
 */
export function applyDab(px, py, strokeId, gainBase, now) {
    if (appState.appMode === 'scratch') {
        if (scratchConfig.isLocked || scratchConfig.isTransitioning) return;

        const radius = config.brushRadius;
        const cellSize = config.cellSize;
        const { gridCols, gridRows, gridAlpha } = appState;

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

                    const oldVal = gridAlpha[idx];
                    const eraseAmount = 0.65 * weight;
                    const newVal = Math.max(0.0, oldVal - eraseAmount);
                    gridAlpha[idx] = newVal;

                    if (oldVal >= SCRATCH_MASK_THRESHOLD && newVal < SCRATCH_MASK_THRESHOLD) {
                        appState.scratchedCellsCount++;
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
    const { gridCols, gridRows, gridAlpha, gridLastTouch, gridLastStroke } = appState;

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
export function strokeLine(from, to, strokeId, now) {
    if (appState.appMode === 'scratch' && (scratchConfig.isLocked || scratchConfig.isTransitioning)) {
        return;
    }

    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const dist = Math.hypot(dx, dy);
    const step = Math.max(6, config.brushRadius * 0.25);

    if (dist <= 0) {
        applyDab(to.x, to.y, strokeId, config.singlePassGain, now);
        if (appState.appMode === 'scratch') {
            updateScratchRatio();
        }
        return;
    }

    const steps = Math.ceil(dist / step);
    for (let i = 1; i <= steps; i++) {
        const t = i / steps;
        applyDab(from.x + dx * t, from.y + dy * t, strokeId, config.singlePassGain, now);
    }

    if (appState.appMode === 'scratch') {
        updateScratchRatio();
    }
}

/**
 * 鼠标停驻充能 (沉睡模式专用)
 */
export function applyHoverCharge(px, py, now) {
    if (appState.appMode === 'scratch') return;

    const radius = config.brushRadius;
    const cellSize = config.cellSize;
    const { gridCols, gridRows, gridAlpha, gridLastTouch } = appState;

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
export function renderLoop(currentTime) {
    const { viewportWidth, viewportHeight, isImageLoaded, gardenImage, imageBounds } = appState;
    const { revealCtx, maskCanvas, maskCtx, maskSmallCanvas, maskSmallCtx } = contexts;

    if (appState.appMode === 'scratch') {
        // ================= 🎲 随机漫游擦画渲染管线 =================
        const needsRender = appState.isDirty || scratchConfig.isTransitioning;

        if (needsRender) {
            const data = appState.maskSmallImageData ? appState.maskSmallImageData.data : null;
            if (data && appState.totalCells > 0) {
                for (let i = 0; i < appState.totalCells; i++) {
                    data[i * 4 + 3] = (appState.gridAlpha[i] * 255 + 0.5) | 0;
                }
            }

            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

            if (isImageLoaded && data) {
                maskSmallCtx.putImageData(appState.maskSmallImageData, 0, 0);

                maskCtx.clearRect(0, 0, viewportWidth, viewportHeight);
                maskCtx.save();
                maskCtx.imageSmoothingEnabled = true;
                maskCtx.imageSmoothingQuality = 'high';
                maskCtx.drawImage(maskSmallCanvas, 0, 0, viewportWidth, viewportHeight);
                maskCtx.restore();

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

            appState.isDirty = false;
        }

        if (scratchConfig.isTransitioning) {
            requestAnimationFrame(renderLoop);
        } else {
            appState.isRenderingActive = false;
        }
        return;
    }

    // ================= 🌸 经典沉睡唤醒渲染管线 =================
    // 1. 停驻充能逻辑
    if (appState.isPointerActive && appState.currentPointerPos) {
        const timeSinceMove = currentTime - appState.lastMoveTime;
        if (timeSinceMove > 40 && currentTime - appState.lastHoverChargeTime > 45) {
            applyHoverCharge(appState.currentPointerPos.x, appState.currentPointerPos.y, currentTime);
            appState.lastHoverChargeTime = currentTime;
        }
    }

    // 2. 一键全彩模式或微距放大探索处理
    if (appState.isFullColorLocked || appState.macroZoom > 1.05) {
        if (appState.isDirty) {
            revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);
            if (isImageLoaded) {
                revealCtx.save();
                revealCtx.globalAlpha = appState.isFullColorLocked ? config.colorRatio : 1.0;
                revealCtx.drawImage(
                    gardenImage,
                    imageBounds.x,
                    imageBounds.y,
                    imageBounds.w,
                    imageBounds.h
                );
                revealCtx.restore();
            }
            appState.isDirty = false;
        }
        appState.isRenderingActive = false;
        return;
    }

    // 3. 衰减与留存计算
    const data = appState.maskSmallImageData ? appState.maskSmallImageData.data : null;
    let hasAnyActiveColor = false;
    let hasFadingColor = false;

    if (data && appState.totalCells > 0) {
        const solidMs = config.solidDurationMs;
        const fadeMs = config.fadeDurationMs;

        for (let i = 0; i < appState.totalCells; i++) {
            const rawAlpha = appState.gridAlpha[i];
            if (rawAlpha <= 0.001) {
                data[i * 4 + 3] = 0;
                continue;
            }
            const alpha = Math.min(config.colorRatio, rawAlpha);

            const elapsed = currentTime - appState.gridLastTouch[i];
            let currentAlpha = alpha;

            if (elapsed <= solidMs) {
                currentAlpha = alpha;
                hasAnyActiveColor = true;
                hasFadingColor = true;
            } else {
                const fadeProgress = (elapsed - solidMs) / fadeMs;
                if (fadeProgress >= 1.0) {
                    appState.gridAlpha[i] = 0;
                    currentAlpha = 0;
                } else {
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

    // 4. 将小尺寸网格遮罩投射到全屏遮罩
    revealCtx.clearRect(0, 0, viewportWidth, viewportHeight);

    if (isImageLoaded && hasAnyActiveColor) {
        maskSmallCtx.putImageData(appState.maskSmallImageData, 0, 0);

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

    // 5. 持续渲染或休眠
    if (hasFadingColor || (appState.isPointerActive && appState.currentPointerPos)) {
        requestAnimationFrame(renderLoop);
    } else {
        appState.isDirty = false;
        appState.isRenderingActive = false;
    }
}
