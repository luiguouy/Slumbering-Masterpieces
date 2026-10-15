/**
 * Masterpiece Garden · Artisan Brass Loupe & Macro Zoom Engine
 * 古典黄铜透镜微距探秘放大镜与画布级视口平移缩放引擎
 */

import { elements, contexts, appState } from '../state.js';
import { showToast } from '../ui/help-modal.js';

// 用于解耦画布重新布局与标记脏帧的回调接口
let onLayoutRefreshCallback = null;
let onMarkDirtyCallback = null;

export function registerMacroEngineCallbacks({ refreshLayout, markDirty }) {
    onLayoutRefreshCallback = refreshLayout;
    onMarkDirtyCallback = markDirty;
}

function refreshLayout() {
    if (onLayoutRefreshCallback) onLayoutRefreshCallback();
}

function markDirty() {
    if (onMarkDirtyCallback) onMarkDirtyCallback();
}

/**
 * 更新微距缩放浮动指示器 (HUD)
 */
export function updateMacroZoomHud() {
    const { macroZoomHud, macroZoomPercent } = elements;
    if (!macroZoomHud || !macroZoomPercent) return;
    if (appState.macroZoom > 1.05 || Math.abs(appState.panOffset.x) > 5 || Math.abs(appState.panOffset.y) > 5) {
        macroZoomHud.style.display = 'block';
        macroZoomPercent.textContent = Math.round(appState.macroZoom * 100) + '%';
    } else {
        macroZoomHud.style.display = 'none';
    }
}

/**
 * 平滑弹性复位微距缩放与平移漫游回到 100% 全景
 * @param {boolean} instant 是否立即瞬时复位（切画时使用）
 */
export function resetMacroZoom(instant = false) {
    if (appState.zoomAnimRaf) {
        cancelAnimationFrame(appState.zoomAnimRaf);
        appState.zoomAnimRaf = null;
    }

    if (instant) {
        appState.macroZoom = 1.0;
        appState.panOffset.x = 0;
        appState.panOffset.y = 0;
        refreshLayout();
        updateMacroZoomHud();
        if (appState.isLoupeEnabled && appState.lastLoupePointerPos.x > 0) {
            renderMacroLoupe(appState.lastLoupePointerPos.x, appState.lastLoupePointerPos.y);
        }
        return;
    }

    const startZoom = appState.macroZoom;
    const startPanX = appState.panOffset.x;
    const startPanY = appState.panOffset.y;
    const startTime = performance.now();
    const duration = 280; // 280ms 优雅回弹

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(1.0, elapsed / duration);
        // 经典三次方缓动曲线 easeOutCubic
        const ease = 1 - Math.pow(1 - progress, 3);

        appState.macroZoom = startZoom + (1.0 - startZoom) * ease;
        appState.panOffset.x = startPanX + (0 - startPanX) * ease;
        appState.panOffset.y = startPanY + (0 - startPanY) * ease;

        refreshLayout();
        updateMacroZoomHud();

        if (appState.isLoupeEnabled && appState.lastLoupePointerPos.x > 0) {
            renderMacroLoupe(appState.lastLoupePointerPos.x, appState.lastLoupePointerPos.y);
        }

        if (progress < 1.0) {
            appState.zoomAnimRaf = requestAnimationFrame(step);
        } else {
            appState.macroZoom = 1.0;
            appState.panOffset.x = 0;
            appState.panOffset.y = 0;
            refreshLayout();
            updateMacroZoomHud();
            appState.zoomAnimRaf = null;
        }
    }
    appState.zoomAnimRaf = requestAnimationFrame(step);
}

/**
 * 古典黄铜透镜 · 艺术微距探秘放大镜渲染管线
 * 实时采集光标下方对应名画的高清原始像素切片，以 100% 真彩与超高放大倍率呈现
 */
export function renderMacroLoupe(screenX, screenY) {
    const { macroLoupe, macroLoupeCanvas } = elements;
    const { macroLoupeCtx } = contexts;
    if (!appState.isLoupeEnabled || !macroLoupe || !macroLoupeCanvas || !macroLoupeCtx || !appState.isImageLoaded) return;

    // 若光标超出视口，平滑隐匿
    if (screenX < 0 || screenX > appState.viewportWidth || screenY < 0 || screenY > appState.viewportHeight) {
        macroLoupe.classList.remove('active');
        appState.isLoupeVisible = false;
        return;
    }

    macroLoupe.style.left = screenX + 'px';
    macroLoupe.style.top = screenY + 'px';
    if (!appState.isLoupeVisible) {
        macroLoupe.classList.add('active');
        appState.isLoupeVisible = true;
    }

    // 计算准星对应在名画矩形中的归一化 UV 坐标
    const { imageBounds, gardenImage } = appState;
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
    const srcSpanW = (canvasW * screenPxToNatPx) / appState.loupeZoom;
    const srcSpanH = (canvasH * screenPxToNatPx) / appState.loupeZoom;

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
export function setLoupeZoom(z) {
    const { loupeOptionsBox } = elements;
    appState.loupeZoom = Math.max(1.5, Math.min(6.0, Math.round(z * 10) / 10));
    if (loupeOptionsBox) {
        const chips = loupeOptionsBox.querySelectorAll('.loupe-zoom-chip');
        chips.forEach(chip => {
            const chipZ = parseFloat(chip.dataset.zoom);
            chip.classList.toggle('active', Math.abs(chipZ - appState.loupeZoom) < 0.2);
        });
    }
    showToast(`🔍 透镜倍率: ${appState.loupeZoom.toFixed(1)}×`);
    if (appState.isLoupeVisible && appState.lastLoupePointerPos.x > 0) {
        renderMacroLoupe(appState.lastLoupePointerPos.x, appState.lastLoupePointerPos.y);
    }
}

/**
 * 开启 / 关闭古典微距探秘透镜
 */
export function toggleLoupe(forcedState) {
    const { toggleLoupeBtn, loupePillStatus, loupeOptionsBox, macroLoupe } = elements;
    appState.isLoupeEnabled = (forcedState !== undefined) ? forcedState : !appState.isLoupeEnabled;

    if (toggleLoupeBtn) {
        toggleLoupeBtn.classList.toggle('active', appState.isLoupeEnabled);
    }
    if (loupePillStatus) {
        loupePillStatus.textContent = appState.isLoupeEnabled ? '已开启' : '已关闭';
    }
    if (loupeOptionsBox) {
        loupeOptionsBox.style.display = appState.isLoupeEnabled ? 'block' : 'none';
    }
    if (macroLoupe) {
        macroLoupe.style.display = appState.isLoupeEnabled ? 'block' : 'none';
        if (!appState.isLoupeEnabled) {
            macroLoupe.classList.remove('active');
            appState.isLoupeVisible = false;
        }
    }
    showToast(appState.isLoupeEnabled ? '🔍 已开启古典真彩微距探秘透镜' : '🔍 已关闭微距透镜');
    if (appState.isLoupeEnabled && appState.lastLoupePointerPos.x > 0) {
        renderMacroLoupe(appState.lastLoupePointerPos.x, appState.lastLoupePointerPos.y);
    }
}

/**
 * 循环切换微距放大镜预设倍率 (2.0× -> 3.5× -> 5.0×)
 */
export function cycleLoupeZoom() {
    appState.loupeZoomIndex = (appState.loupeZoomIndex + 1) % appState.loupeZoomLevels.length;
    setLoupeZoom(appState.loupeZoomLevels[appState.loupeZoomIndex]);
}
