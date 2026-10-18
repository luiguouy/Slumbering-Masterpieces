/**
 * Masterpiece Garden · Artisan Brass Loupe & Macro Zoom Engine
 * 古典黄铜透镜微距探秘放大镜与画布级视口平移缩放引擎
 */

import { elements, contexts, appState, MODAL_SELECTOR, MACRO_HUD_SELECTOR } from '../state.js';

// 透镜隐匿滞后的两级阈值（透镜圆盘与画作的交集占比）：
// 显示中交集低于隐匿阈值即消失；已隐匿后需回到更高占比才重新显示。
// 两级阈值构成滞回区间，避免在画作边缘来回移动时透镜高频闪烁。
const LOUPE_HIDE_COVERAGE = 0.35;
const LOUPE_SHOW_COVERAGE = 0.55;

/**
 * 估算透镜圆盘与画作的交集占比（0 ~ 1）
 *
 * 以圆心 + 内外两圈各 16 方向共 33 个采样点近似圆-矩形交集。
 * 只检查光标一个点是不够的——透镜圆盘直径 220px，
 * 光标还压在画作边缘时，圆盘大半已经悬在画外了。
 */
function loupeArtCoverage(x, y) {
    const b = appState.imageBounds;
    if (!appState.isImageLoaded || !b || !b.w || !b.h) return 0;

    // 半径取运行时实测的 CSS 尺寸：移动端断点下透镜是 180px 而非 220px，
    // 沿用常量会让判定半径比真实圆盘大 22%，导致靠近画作边缘时透镜提前消失。
    const R = appState.loupeCssSize / 2;
    let inside = 0;
    let total = 0;
    for (let ring = 0; ring <= 2; ring++) {
        const r = ring === 0 ? 0 : R * (ring === 1 ? 0.6 : 1.0);
        const steps = ring === 0 ? 1 : 16;
        for (let i = 0; i < steps; i++) {
            const angle = (i / steps) * Math.PI * 2;
            const px = x + Math.cos(angle) * r;
            const py = y + Math.sin(angle) * r;
            if (px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h) inside++;
            total++;
        }
    }
    return inside / total;
}

/**
 * 光标是否位于任何「可见的」浮层面板之上
 *
 * 按坐标几何判定而非 e.target：触摸事件的 target 固定在落指时刻，
 * 手指从画布滑入面板时 closest() 会漏判；几何检测对鼠标与触控同时生效。
 *
 * 必须过滤不可见元素：部分面板关闭态并非 display:none——
 *   help-dialog  关闭态为 visibility:hidden，但布局矩形仍覆盖视口中部；
 *   brush-popup  未展开态为 opacity:0，布局原位不动。
 * 这些「隐形面板」的 getBoundingClientRect 照常返回真实几何，
 * 不过滤就会永久压在画作上，导致透镜在画心也隐匿、只在画的边缘幸存。
 */
function hitPanel(x, y) {
    const nodes = document.querySelectorAll(`${MODAL_SELECTOR}, ${MACRO_HUD_SELECTOR}`);
    for (const node of nodes) {
        const s = getComputedStyle(node);
        if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) {
            continue;
        }
        const r = node.getBoundingClientRect();
        if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return true;
    }
    return false;
}

/**
 * 透镜是否应当隐匿：圆盘大部分移出画作，或压住任何浮层面板
 */
function shouldHideLoupe(x, y) {
    const threshold = appState.isLoupeVisible ? LOUPE_HIDE_COVERAGE : LOUPE_SHOW_COVERAGE;
    return loupeArtCoverage(x, y) < threshold || hitPanel(x, y);
}
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
 * 记录古典透镜的光标位置
 *
 * 以独立的布尔标志标记「已记录过位置」，替代原先 lastLoupePointerPos.x > 0 的哨兵判断
 * ——后者在光标 x 坐标为 0 或负值时会被误判为「尚未记录」，导致透镜不渲染。
 */
export function setLoupePointer(x, y) {
    appState.lastLoupePointerPos = { x, y };
    appState.hasLoupePointerPos = true;
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
        if (appState.isLoupeEnabled && appState.hasLoupePointerPos) {
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

        if (appState.isLoupeEnabled && appState.hasLoupePointerPos) {
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
    if (!appState.isLoupeEnabled || !macroLoupe || !macroLoupeCanvas || !macroLoupeCtx) return;

    // 隐匿判定：移出画作或压在浮层上即消失。
    // 透镜是「看画」工具——离开画作便失去意义，且此时 UV 采样超出图像边界，
    // 镜内会渲染成纯黑圆片，反而遮挡下层侧边栏 UI。
    if (shouldHideLoupe(screenX, screenY)) {
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

    // 统一采用 CSS 像素坐标系绘制。
    // 后端缓冲已在 handleResize 中按 dpr 放大，并通过 setTransform 建立缩放关系；
    // 此处若仍取 canvas.width（物理像素），会造成采样跨度与绘制尺寸被重复放大。
    // 尺寸同样取自 appState.loupeCssSize（与缓冲分配、覆盖率判定同源），
    // 否则移动端 180px 圆盘里会按 220px 的跨度采样，实际放大倍率低于标注值。
    const canvasW = appState.loupeCssSize;
    const canvasH = appState.loupeCssSize;

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
    if (appState.isLoupeVisible && appState.hasLoupePointerPos) {
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
    if (appState.isLoupeEnabled && appState.hasLoupePointerPos) {
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
