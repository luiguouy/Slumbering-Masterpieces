/**
 * Masterpiece Garden · Brush & Mode Control Panel
 * 画笔大小、显色比例、留存时长、规格模式、模式切换与一键全彩盛放面板控制器
 */

import { elements, contexts, appState, config, scratchConfig } from '../state.js';
import { refreshLayout, markDirty, renderGrayscaleBackground, renderScratchBackground } from '../engine/canvas-engine.js';
import { resetMacroZoom, toggleLoupe, setLoupeZoom } from '../engine/macro-loupe.js';
import { prepareNextRandomArtwork, triggerAutoScratchReveal } from '../engine/scratch-machine.js';
import { showToast, updateHintText } from './help-modal.js';

/**
 * 更新画笔大小与所有关联 UI (包括预览圆与艺术光标)
 */
export function updateBrushSize(newRadius) {
    config.brushRadius = Math.max(config.minBrushRadius, Math.min(config.maxBrushRadius, newRadius));
    const { brushSlider, brushSizeDisplay, brushPreviewDot, cursorRing } = elements;

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
export function updateDuration(totalSeconds) {
    config.totalDurationSeconds = Math.max(4, Math.min(30, totalSeconds));
    config.solidDurationMs = Math.round(config.totalDurationSeconds * 0.7 * 1000);
    config.fadeDurationMs = Math.round(config.totalDurationSeconds * 0.3 * 1000);

    const { brushDurationSlider, brushDurationDisplay } = elements;
    if (brushDurationSlider) {
        brushDurationSlider.value = config.totalDurationSeconds;
    }
    if (brushDurationDisplay) {
        brushDurationDisplay.textContent = `${config.totalDurationSeconds}秒`;
    }
}

/**
 * 更新划过唤醒原画显色比例 (0.2 ~ 1.0)
 */
export function updateColorRatio(newRatio) {
    config.colorRatio = Math.max(0.2, Math.min(1.0, newRatio));
    const pct = Math.round(config.colorRatio * 100);

    const { colorRatioSlider, colorRatioDisplay } = elements;
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
export function setFitMode(mode) {
    if (!['auto', 'contain', 'cover'].includes(mode)) return;
    config.fitMode = mode;

    const { fitAutoBtn, fitContainBtn, fitCoverBtn, fitModeDisplay } = elements;
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
export function setScale(scaleVal) {
    config.scale = Math.max(0.6, Math.min(1.4, scaleVal));

    const { fitScaleSlider, fitScaleDisplay } = elements;
    if (fitScaleSlider) {
        fitScaleSlider.value = Math.round(config.scale * 100);
    }
    if (fitScaleDisplay) {
        fitScaleDisplay.textContent = `${Math.round(config.scale * 100)}%`;
    }

    refreshLayout();
}

/**
 * 切换一键全彩盛放状态 (还原为原始全彩 或 恢复沉睡黑白)
 *
 * 该操作只对沉睡唤醒模式有意义：它通过把 gridAlpha 整体写成 colorRatio / 0
 * 来切换「全彩常驻」与「全灰阶」两种静态态。
 * 随机漫游模式本就是原彩直出，且其 gridAlpha 语义为「顶层遮罩不透明度」（1=完整遮挡），
 * 一旦被整体改写就会与 scratchedCellsCount / scratchConfig.ratio 脱节：
 * 填 1 会把已擦出的洞补满，填 0 会让整幅顶层瞬透直接露底，
 * 两种结果都不会走 finalizeScratchTransition，索引与画面随即错位。
 * 因此在此入口统一拦截，避免双击 / 空格等所有调用路径逐个补守卫。
 */
export function toggleFullColor(forceState) {
    if (appState.appMode === 'scratch') {
        showToast('🎲 随机漫游已是原彩直出，请擦拭画面或点击「立即完全展开」', '🎲');
        return false;
    }

    const targetState = (forceState !== undefined) ? forceState : !appState.isFullColorLocked;
    appState.isFullColorLocked = targetState;

    const { fullColorBtnText, toggleFullColorBtn } = elements;
    const { revealCtx } = contexts;

    if (appState.isFullColorLocked) {
        if (appState.gridAlpha) appState.gridAlpha.fill(config.colorRatio);
        if (appState.gridLastTouch) appState.gridLastTouch.fill(performance.now());

        if (fullColorBtnText) fullColorBtnText.textContent = '恢复黑白沉睡';
        if (toggleFullColorBtn) {
            toggleFullColorBtn.classList.add('active');
            toggleFullColorBtn.title = '点击让画面重归静谧黑白素描';
        }
    } else {
        if (appState.gridAlpha) appState.gridAlpha.fill(0);
        if (appState.gridLastStroke) appState.gridLastStroke.fill(0);
        if (appState.maskSmallImageData) {
            const d = appState.maskSmallImageData.data;
            for (let i = 0; i < appState.totalCells; i++) {
                d[i * 4 + 3] = 0;
            }
        }
        revealCtx.clearRect(0, 0, appState.viewportWidth, appState.viewportHeight);

        if (fullColorBtnText) fullColorBtnText.textContent = '一键全彩盛放';
        if (toggleFullColorBtn) {
            toggleFullColorBtn.classList.remove('active');
            toggleFullColorBtn.title = '一键将整幅画还原为原始真彩';
        }
    }
    markDirty();
    return true;
}

/**
 * 设置体验模式 ('sleep' | 'scratch')
 */
export function setAppMode(mode) {
    if (mode !== 'sleep' && mode !== 'scratch') return;
    appState.appMode = mode;

    const {
        modeSleepBtn, modeScratchBtn, sleepModeControls, scratchModeControls,
        mswSleepBtn, mswScratchBtn,
        scratchHud, scratchHudPercent, scratchHudFill, scratchRatioDisplay,
        scratchMiniBarFill, fullColorBtnText, toggleFullColorBtn
    } = elements;
    const { revealCtx } = contexts;

    if (modeSleepBtn) modeSleepBtn.classList.toggle('active', mode === 'sleep');
    if (modeScratchBtn) modeScratchBtn.classList.toggle('active', mode === 'scratch');
    // 一级切换控件的激活态与模式严格同步（它是主入口，不能与弹层状态脱节）
    if (mswSleepBtn) mswSleepBtn.classList.toggle('active', mode === 'sleep');
    if (mswScratchBtn) mswScratchBtn.classList.toggle('active', mode === 'scratch');

    if (sleepModeControls) sleepModeControls.style.display = (mode === 'sleep') ? 'block' : 'none';
    if (scratchModeControls) scratchModeControls.style.display = (mode === 'scratch') ? 'block' : 'none';
    if (scratchHud) scratchHud.style.display = (mode === 'scratch') ? 'flex' : 'none';

    if (mode === 'scratch') {
        // 沉睡模式遗留的全彩锁定态对随机漫游无意义：该模式本就原彩直出，
        // 保留锁定态会让切回沉睡时按钮文案与实际画面不一致。
        appState.isFullColorLocked = false;
        if (fullColorBtnText) fullColorBtnText.textContent = '一键全彩盛放';
        if (toggleFullColorBtn) toggleFullColorBtn.classList.remove('active');

        scratchConfig.isLocked = false;
        scratchConfig.isTransitioning = false;
        scratchConfig.ratio = 0;
        appState.scratchedCellsCount = 0;
        appState.lastRenderedHudPct = 0;
        if (appState.gridAlpha) appState.gridAlpha.fill(1.0);
        if (scratchHudPercent) scratchHudPercent.textContent = '0%';
        if (scratchHudFill) scratchHudFill.style.width = '0%';
        if (scratchRatioDisplay) scratchRatioDisplay.textContent = '0%';
        if (scratchMiniBarFill) scratchMiniBarFill.style.width = '0%';
        if (scratchHud) scratchHud.classList.remove('locked');

        refreshLayout();

        prepareNextRandomArtwork(() => {
            refreshLayout();
            renderScratchBackground();
            markDirty();
        });
        updateHintText('scratch');
        showToast('已切换为 🎲 随机漫游擦画模式', '🎲');
        markDirty();
    } else {
        refreshLayout();
        if (appState.gridAlpha) appState.gridAlpha.fill(0);
        if (appState.gridLastStroke) appState.gridLastStroke.fill(0);
        appState.isFullColorLocked = false;
        if (fullColorBtnText) fullColorBtnText.textContent = '一键全彩盛放';
        if (toggleFullColorBtn) toggleFullColorBtn.classList.remove('active');
        renderGrayscaleBackground();
        revealCtx.clearRect(0, 0, appState.viewportWidth, appState.viewportHeight);
        updateHintText('sleep');
        showToast('已切换为 🌸 沉睡唤醒古典模式', '🌸');
        markDirty();
    }
}

/* ==========================================================================
 * 🖐️ 画笔按钮自由拖拽
 * 右上角的画笔按钮默认锚定右上角，但每位观者顺手的位置不同（左利手、平板握持、
 * 竖屏单手操作……）。这里允许把它拖到画布任意位置，并持久化相对位置。
 *
 * 三个不变量：
 *   1. 拖拽全程置 appState.isFloatingPanelDragging，屏蔽画布涂抹与透镜判定；
 *   2. 位置始终夹在视口内，且按「相对比例」记忆，换设备/转屏不会跑到屏幕外；
 *   3. 弹层跟随按钮翻转对齐，靠右下角时向上展开，靠左侧时左对齐，永不出界。
 * ========================================================================== */

const PANEL_POS_STORAGE_KEY = 'artweb.brushPanelPos.v1';
const PANEL_EDGE_MARGIN = 8;       // 与视口边缘的最小间距
const PANEL_DRAG_THRESHOLD = 4;    // 超过该位移才判定为拖拽（区分点击与拖拽）

let panelDragState = null;         // { pointerId, startX, startY, originX, originY, moved }
let suppressPanelClick = false;    // 拖拽结束后吞掉紧随其后的那次 click

function hasCustomPanelPosition() {
    const el = elements.brushControl;
    return Boolean(el && el.classList.contains('is-custom-position'));
}

function clampPanelXY(x, y) {
    const el = elements.brushControl;
    const w = (el && el.offsetWidth) || 42;
    const h = (el && el.offsetHeight) || 42;
    const maxX = Math.max(PANEL_EDGE_MARGIN, window.innerWidth - w - PANEL_EDGE_MARGIN);
    const maxY = Math.max(PANEL_EDGE_MARGIN, window.innerHeight - h - PANEL_EDGE_MARGIN);
    return {
        x: Math.min(Math.max(PANEL_EDGE_MARGIN, x), maxX),
        y: Math.min(Math.max(PANEL_EDGE_MARGIN, y), maxY)
    };
}

/**
 * 弹层跟随按钮定位：水平方向默认右对齐，左侧放不下时改左对齐；
 * 垂直方向默认向下展开，下方不够则翻到按钮上方。
 */
function positionBrushPopup() {
    const { brushControl, brushPopup } = elements;
    if (!brushControl || !brushPopup) return;

    const cRect = brushControl.getBoundingClientRect();
    const pw = brushPopup.offsetWidth || 234;
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // 水平：先试右对齐（弹层右缘 ≈ 按钮右缘），越界则左对齐，最后再夹一次
    let popupLeft = cRect.right - pw;
    if (popupLeft < PANEL_EDGE_MARGIN) popupLeft = cRect.left;
    popupLeft = Math.min(
        Math.max(PANEL_EDGE_MARGIN, popupLeft),
        Math.max(PANEL_EDGE_MARGIN, vw - pw - PANEL_EDGE_MARGIN)
    );
    brushPopup.style.left = `${Math.round(popupLeft - cRect.left)}px`;
    brushPopup.style.right = 'auto';

    // 垂直：用 scrollHeight 而非 offsetHeight 取「自然高度」——
    // offsetHeight 已被上一轮写入的 max-height 截断过，用它判断会形成反馈循环，
    // 导致拖到屏幕下半部时永远判为「放得下」而不翻转。
    const naturalH = brushPopup.scrollHeight || brushPopup.offsetHeight || 0;
    const spaceBelow = vh - cRect.bottom - 10 - PANEL_EDGE_MARGIN;
    const spaceAbove = cRect.top - 10 - PANEL_EDGE_MARGIN;

    // 下方放不完整、且上方余量更多 → 向上展开；否则向下，并把高度收到可用空间内滚动显示
    const goUp = naturalH > spaceBelow && spaceAbove > spaceBelow;
    const avail = Math.max(120, goUp ? spaceAbove : spaceBelow);

    brushPopup.style.maxHeight = naturalH > avail ? `${Math.round(avail)}px` : '';

    if (goUp) {
        brushPopup.style.top = 'auto';
        brushPopup.style.bottom = 'calc(100% + 10px)';
    } else {
        brushPopup.style.top = 'calc(100% + 10px)';
        brushPopup.style.bottom = 'auto';
    }
}

/**
 * 将按钮放到视口坐标 (x, y)。坐标以视口左上角为原点，内部换算成相对舞台的偏移。
 */
function applyPanelPosition(x, y, { persist = false } = {}) {
    const el = elements.brushControl;
    if (!el) return;

    const pos = clampPanelXY(x, y);
    const parent = el.offsetParent || el.parentElement;
    const parentRect = parent ? parent.getBoundingClientRect() : { left: 0, top: 0 };

    el.style.left = `${Math.round(pos.x - parentRect.left)}px`;
    el.style.top = `${Math.round(pos.y - parentRect.top)}px`;
    el.style.right = 'auto';
    el.classList.add('is-custom-position');

    if (persist) {
        const maxX = Math.max(1, window.innerWidth - (el.offsetWidth || 42));
        const maxY = Math.max(1, window.innerHeight - (el.offsetHeight || 42));
        try {
            localStorage.setItem(PANEL_POS_STORAGE_KEY, JSON.stringify({
                x: Number((pos.x / maxX).toFixed(4)),
                y: Number((pos.y / maxY).toFixed(4))
            }));
        } catch (err) {
            // 隐私模式 / 存储禁用时静默降级为「本次会话有效」
        }
    }

    positionBrushPopup();
}

/** 恢复上次拖拽位置（按比例换算，跨分辨率与转屏均安全） */
function restorePanelPosition() {
    const el = elements.brushControl;
    if (!el) return;

    let saved = null;
    try {
        saved = JSON.parse(localStorage.getItem(PANEL_POS_STORAGE_KEY) || 'null');
    } catch (err) {
        saved = null;
    }
    if (!saved || typeof saved.x !== 'number' || typeof saved.y !== 'number') return;

    const maxX = Math.max(1, window.innerWidth - (el.offsetWidth || 42));
    const maxY = Math.max(1, window.innerHeight - (el.offsetHeight || 42));
    applyPanelPosition(saved.x * maxX, saved.y * maxY);
}

/** 复位到右上角默认位置（双击按钮触发） */
function resetPanelPosition() {
    const el = elements.brushControl;
    if (!el) return;
    el.style.left = '';
    el.style.top = '';
    el.style.right = '';
    el.classList.remove('is-custom-position');
    try {
        localStorage.removeItem(PANEL_POS_STORAGE_KEY);
    } catch (err) { /* ignore */ }
    positionBrushPopup();
}

/**
 * 初始化按钮拖拽（Pointer Events，鼠标 / 触屏 / 触控笔统一）
 */
function initDraggableBrushButton(brushToggleBtn) {
    const el = elements.brushControl;
    if (!el || !brushToggleBtn) return;

    brushToggleBtn.addEventListener('pointerdown', (e) => {
        // 只响应主键与单指，允许右键菜单等原生行为
        if (e.button !== undefined && e.button !== 0) return;
        if (!e.isPrimary) return;

        suppressPanelClick = false;

        const rect = el.getBoundingClientRect();
        panelDragState = {
            pointerId: e.pointerId,
            startX: e.clientX,
            startY: e.clientY,
            originX: rect.left,
            originY: rect.top,
            moved: false
        };

        // 捕获指针：拖出按钮范围后仍持续收到 move 事件
        try {
            brushToggleBtn.setPointerCapture(e.pointerId);
        } catch (err) { /* 部分旧浏览器不支持，退化为普通事件流 */ }
    });

    brushToggleBtn.addEventListener('pointermove', (e) => {
        if (!panelDragState || e.pointerId !== panelDragState.pointerId) return;

        const dx = e.clientX - panelDragState.startX;
        const dy = e.clientY - panelDragState.startY;

        if (!panelDragState.moved) {
            if (Math.hypot(dx, dy) < PANEL_DRAG_THRESHOLD) return;
            panelDragState.moved = true;
            // 拖拽期间屏蔽画布涂抹 / 透镜判定，并复位悬停缩放避免抖动
            appState.isFloatingPanelDragging = true;
            document.body.classList.add('is-panel-dragging');
        }

        if (e.cancelable) e.preventDefault();
        applyPanelPosition(panelDragState.originX + dx, panelDragState.originY + dy);
    });

    const endDrag = (e) => {
        if (!panelDragState || (e.pointerId !== undefined && e.pointerId !== panelDragState.pointerId)) return;

        const moved = panelDragState.moved;
        const rect = el.getBoundingClientRect();

        panelDragState = null;
        appState.isFloatingPanelDragging = false;
        document.body.classList.remove('is-panel-dragging');

        try {
            if (brushToggleBtn.hasPointerCapture(e.pointerId)) {
                brushToggleBtn.releasePointerCapture(e.pointerId);
            }
        } catch (err) { /* ignore */ }

        if (moved) {
            suppressPanelClick = true;
            applyPanelPosition(rect.left, rect.top, { persist: true });
        }
    };

    brushToggleBtn.addEventListener('pointerup', endDrag);
    brushToggleBtn.addEventListener('pointercancel', endDrag);
    // 兜底：指针捕获在个别环境失败时，松手位置可能落在按钮之外，
    // 若不接住会让 isFloatingPanelDragging 卡在 true，后续整页都无法涂抹。
    window.addEventListener('pointerup', endDrag);
    window.addEventListener('pointercancel', endDrag);

    // 双击复位：拖到角落抓不回来时的逃生通道
    brushToggleBtn.addEventListener('dblclick', (e) => {
        e.preventDefault();
        e.stopPropagation();
        resetPanelPosition();
        showToast('🧭 画笔按钮已复位到右上角', '🧭');
    });

    // 视口变化：自定义位置重新夹紧，默认位置重新对齐弹层
    window.addEventListener('resize', () => {
        if (hasCustomPanelPosition()) {
            const rect = el.getBoundingClientRect();
            applyPanelPosition(rect.left, rect.top);
        } else {
            positionBrushPopup();
        }
    });
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', () => {
            if (hasCustomPanelPosition()) {
                const rect = el.getBoundingClientRect();
                applyPanelPosition(rect.left, rect.top);
            }
        });
    }
}

/**
 * 绑定画笔控制面板事件
 */
export function setupBrushUI() {
    const {
        brushToggleBtn, brushPopup, modeSleepBtn, modeScratchBtn,
        mswSleepBtn, mswScratchBtn,
        scratchThresholdSlider, scratchThresholdDisplay, scratchHudTargetVal,
        scratchRevealNowBtn, brushSlider, brushDurationSlider, colorRatioSlider,
        toggleFullColorBtn, fitAutoBtn, fitContainBtn, fitCoverBtn,
        fitScaleSlider, toggleLoupeBtn, loupeOptionsBox, macroZoomResetBtn
    } = elements;

    if (!brushToggleBtn || !brushPopup) return;

    // 用户一旦主动切换，立即收起首次引导气泡（不等 8 秒动画结束）
    const dismissSwitchHint = () => {
        const hint = document.getElementById('mode-switch-hint');
        if (hint) hint.style.display = 'none';
    };

    // 一级模式切换（画布常驻胶囊）
    if (mswSleepBtn) {
        mswSleepBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dismissSwitchHint();
            setAppMode('sleep');
        });
    }
    if (mswScratchBtn) {
        mswScratchBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dismissSwitchHint();
            setAppMode('scratch');
        });
    }

    // 模式切换按钮（旧弹层入口，弹层内已移除，保留绑定以兼容历史入口）
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

    // 随机擦画阈值滑块
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
        // 拖拽结束时浏览器仍会补发一次 click，这里吞掉，避免「拖完顺手弹出面板」
        if (suppressPanelClick) {
            suppressPanelClick = false;
            return;
        }
        const isOpen = brushPopup.classList.toggle('open');
        brushToggleBtn.classList.toggle('active', isOpen);
        if (isOpen) positionBrushPopup();
    });

    // 画笔大小滑块
    if (brushSlider) {
        brushSlider.addEventListener('input', (e) => {
            updateBrushSize(parseInt(e.target.value, 10));
        });
        brushSlider.addEventListener('click', (e) => e.stopPropagation());
    }

    // 色彩留存时长滑块
    if (brushDurationSlider) {
        brushDurationSlider.addEventListener('input', (e) => {
            updateDuration(parseInt(e.target.value, 10));
        });
        brushDurationSlider.addEventListener('click', (e) => e.stopPropagation());
    }

    // 显色比例滑块
    if (colorRatioSlider) {
        colorRatioSlider.addEventListener('input', (e) => {
            updateColorRatio(parseInt(e.target.value, 10) / 100);
        });
        colorRatioSlider.addEventListener('click', (e) => e.stopPropagation());
    }

    // 一键全彩盛放按钮
    if (toggleFullColorBtn) {
        toggleFullColorBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleFullColor();
        });
    }

    // 画面规格模式选项卡
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

    // 画面缩放滑块
    if (fitScaleSlider) {
        fitScaleSlider.addEventListener('input', (e) => {
            setScale(parseInt(e.target.value, 10) / 100);
        });
        fitScaleSlider.addEventListener('click', (e) => e.stopPropagation());
    }

    // 古典微距探秘放大镜开关按钮
    if (toggleLoupeBtn) {
        toggleLoupeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleLoupe();
        });
    }

    // 微距透镜倍率选择芯片
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

    // 微距缩放胶囊指示器一键复位按钮
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

    brushPopup.addEventListener('mousemove', (e) => e.stopPropagation());
    brushToggleBtn.addEventListener('mousemove', (e) => e.stopPropagation());

    // 初始化面板与参数
    updateBrushSize(config.brushRadius);
    updateColorRatio(config.colorRatio);
    updateDuration(config.totalDurationSeconds);
    setFitMode(config.fitMode);
    setScale(config.scale);
    setAppMode(appState.appMode);

    // 画笔按钮自由拖拽（须在 setAppMode 之后：弹层内容高度已确定，翻转判定才准确）
    initDraggableBrushButton(brushToggleBtn);
    restorePanelPosition();
    positionBrushPopup();
}
