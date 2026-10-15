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
 */
export function toggleFullColor(forceState) {
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
}

/**
 * 设置体验模式 ('sleep' | 'scratch')
 */
export function setAppMode(mode) {
    if (mode !== 'sleep' && mode !== 'scratch') return;
    appState.appMode = mode;

    const {
        modeSleepBtn, modeScratchBtn, sleepModeControls, scratchModeControls,
        scratchHud, scratchHudPercent, scratchHudFill, scratchRatioDisplay,
        scratchMiniBarFill, fullColorBtnText, toggleFullColorBtn
    } = elements;
    const { revealCtx } = contexts;

    if (modeSleepBtn) modeSleepBtn.classList.toggle('active', mode === 'sleep');
    if (modeScratchBtn) modeScratchBtn.classList.toggle('active', mode === 'scratch');

    if (sleepModeControls) sleepModeControls.style.display = (mode === 'sleep') ? 'block' : 'none';
    if (scratchModeControls) scratchModeControls.style.display = (mode === 'scratch') ? 'block' : 'none';
    if (scratchHud) scratchHud.style.display = (mode === 'scratch') ? 'flex' : 'none';

    if (mode === 'scratch') {
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

/**
 * 绑定画笔控制面板事件
 */
export function setupBrushUI() {
    const {
        brushToggleBtn, brushPopup, modeSleepBtn, modeScratchBtn,
        scratchThresholdSlider, scratchThresholdDisplay, scratchHudTargetVal,
        scratchRevealNowBtn, brushSlider, brushDurationSlider, colorRatioSlider,
        toggleFullColorBtn, fitAutoBtn, fitContainBtn, fitCoverBtn,
        fitScaleSlider, toggleLoupeBtn, loupeOptionsBox, macroZoomResetBtn
    } = elements;

    if (!brushToggleBtn || !brushPopup) return;

    // 模式切换按钮
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
        const isOpen = brushPopup.classList.toggle('open');
        brushToggleBtn.classList.toggle('active', isOpen);
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
}
