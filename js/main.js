/**
 * Masterpiece Garden · Interactive Fine Art Engine (v4.6.0 Modular Architecture)
 * 传世名画博览馆 · 核心主入口装配中枢
 */

import { elements, appState, config, scratchConfig, initMasterpieces, toThumbSrc } from './state.js';
import { preloadPool } from './utils/preload-pool.js';
import {
    handleResize,
    refreshLayout,
    markDirty,
    renderGrayscaleBackground,
    renderScratchBackground,
    computeImageBounds,
    computeNextImageBounds,
    strokeLine
} from './engine/canvas-engine.js';
import {
    registerMacroEngineCallbacks,
    resetMacroZoom,
    setLoupeZoom,
    toggleLoupe,
    cycleLoupeZoom,
    updateMacroZoomHud
} from './engine/macro-loupe.js';
import {
    registerScratchMachineCallbacks,
    triggerAutoScratchReveal
} from './engine/scratch-machine.js';
import {
    setupBrushUI,
    updateBrushSize,
    updateDuration,
    updateColorRatio,
    setFitMode,
    setScale,
    setAppMode,
    toggleFullColor
} from './ui/brush-panel.js';
import {
    setupGalleryUI,
    switchMasterpiece,
    updateActiveCardHighlight,
    openGallery,
    closeGallery
} from './ui/gallery-drawer.js';
import {
    setupStoryUI,
    registerStoryCallbacks,
    updateStoryContent,
    openStory,
    closeStory,
    toggleStory
} from './ui/story-drawer.js';
import {
    setupHelpUI,
    openHelp,
    closeHelp,
    toggleHelp,
    showToast,
    dismissInitialHint
} from './ui/help-modal.js';
import { setupInputEvents } from './events/input-controller.js';

/**
 * 注册引擎子模块之间的解耦回调与联动通信
 */
function initEngineInterconnect() {
    registerMacroEngineCallbacks({
        refreshLayout,
        markDirty
    });

    registerScratchMachineCallbacks({
        markDirty,
        computeBounds: () => {
            computeImageBounds();
            computeNextImageBounds();
        },
        renderScratchBg: renderScratchBackground,
        onArtworkChange: (art, index) => {
            const { quoteTextEl, quoteAuthorEl, currentArtThumb, currentArtTitle, currentArtArtist, masterpieceIndexBadge } = elements;
            if (quoteTextEl) quoteTextEl.textContent = art.quote;
            if (quoteAuthorEl) quoteAuthorEl.textContent = art.quoteAuthor;

            if (currentArtThumb) {
                currentArtThumb.src = toThumbSrc(art.src);
                currentArtThumb.alt = art.title;
            }
            if (currentArtTitle) currentArtTitle.textContent = art.title;
            if (currentArtArtist) currentArtArtist.textContent = `${art.artist} · 🔍 检索画廊`;
            if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `${index + 1} / ${appState.masterpieces.length}`;

            updateActiveCardHighlight(index);
            updateStoryContent(art);

            preloadPool.preloadAdjacent(appState.masterpieces, index);
        }
    });

    registerStoryCallbacks({
        onSwitchArt: switchMasterpiece
    });
}

/**
 * 引擎启动与名画载入
 */
function start() {
    if (appState.isInitialized) return;
    appState.isInitialized = true;

    initMasterpieces();
    initEngineInterconnect();

    handleResize();
    setupBrushUI();
    setupGalleryUI();
    setupStoryUI();
    setupHelpUI();
    setupInputEvents();

    // 首次入场提示在 5 秒后如晨雾般优雅自动淡出
    setTimeout(dismissInitialHint, 5000);

    // 名画资源载入失败降级计数器 (防止连续损坏资源引发无限切换递归)
    let loadFailureCount = 0;
    const MAX_CONSECUTIVE_LOAD_FAILURES = 3;

    appState.gardenImage.onload = () => {
        appState.isImageLoaded = true;
        loadFailureCount = 0;
        computeImageBounds();
        if (appState.appMode === 'scratch') {
            renderScratchBackground();
        } else {
            renderGrayscaleBackground();
        }
        markDirty();
    };

    // 名画载入失败降级：跳过损坏资源并自动切至下一幅。
    // 315 幅资源中任一 404 若不处理，isImageLoaded 将永久停留在 false，导致静默白屏且无任何反馈。
    appState.gardenImage.onerror = () => {
        const failedArt = appState.masterpieces[appState.currentMasterpieceIndex];
        console.error('[GardenEngine] 载入名画资源失败:', failedArt && failedArt.src);

        const total = appState.masterpieces.length;
        if (loadFailureCount < MAX_CONSECUTIVE_LOAD_FAILURES && total > 1) {
            loadFailureCount++;
            showToast(`⚠️ 名画资源载入失败，已自动跳过 (${loadFailureCount}/${MAX_CONSECUTIVE_LOAD_FAILURES})`, '⚠️');
            switchMasterpiece((appState.currentMasterpieceIndex + 1) % total);
            return;
        }

        loadFailureCount = 0;
        showToast('⚠️ 名画资源载入失败，请检查 assets/images 目录完整性', '⚠️');
    };

    // 默认载入首幅传世名画
    switchMasterpiece(0);

    markDirty();
}

/**
 * 暴露 100% 兼容的诊断与调试测试接口
 */
window.__gardenEngine = {
    isLoaded: () => appState.isImageLoaded,
    getAppMode: () => appState.appMode,
    setAppMode: setAppMode,
    getBrushRadius: () => config.brushRadius,
    setBrushRadius: updateBrushSize,
    getDuration: () => config.totalDurationSeconds,
    setDuration: updateDuration,
    getColorRatio: () => config.colorRatio,
    setColorRatio: updateColorRatio,
    getMasterpieces: () => appState.masterpieces,
    getCurrentIndex: () => appState.currentMasterpieceIndex,
    setMasterpiece: switchMasterpiece,
    openStory: openStory,
    closeStory: closeStory,
    toggleStory: toggleStory,
    openGallery: openGallery,
    closeGallery: closeGallery,
    openHelp: openHelp,
    closeHelp: closeHelp,
    toggleHelp: toggleHelp,
    showToast: showToast,
    dismissHint: dismissInitialHint,
    getNextMasterpieceIndex: () => appState.nextMasterpieceIndex,
    getScratchRatio: () => scratchConfig.ratio,
    getScratchThreshold: () => scratchConfig.threshold,
    setScratchThreshold: (t) => {
        const val = Math.max(0.5, Math.min(0.95, t));
        scratchConfig.threshold = val;
        const { scratchThresholdSlider, scratchThresholdDisplay, scratchHudTargetVal } = elements;
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
    getBounds: () => appState.imageBounds,
    getNextBounds: () => appState.nextImageBounds,
    isNextLoaded: () => appState.isNextImageLoaded,
    getNextImgInfo: () => ({
        src: appState.nextGardenImage.src,
        complete: appState.nextGardenImage.complete,
        nw: appState.nextGardenImage.naturalWidth,
        nh: appState.nextGardenImage.naturalHeight
    }),
    toggleFullColor: toggleFullColor,
    isFullColor: () => appState.isFullColorLocked,
    getMacroZoom: () => appState.macroZoom,
    setMacroZoom: (z) => {
        appState.macroZoom = Math.max(1.0, Math.min(4.5, z));
        refreshLayout();
        updateMacroZoomHud();
    },
    getPanOffset: () => ({ ...appState.panOffset }),
    setPanOffset: (x, y) => {
        appState.panOffset.x = x;
        appState.panOffset.y = y;
        refreshLayout();
        updateMacroZoomHud();
    },
    resetMacroZoom: resetMacroZoom,
    isLoupeEnabled: () => appState.isLoupeEnabled,
    toggleLoupe: toggleLoupe,
    getLoupeZoom: () => appState.loupeZoom,
    cycleLoupeZoom: cycleLoupeZoom,
    stroke: (x1, y1, x2, y2) => {
        appState.currentStrokeId++;
        strokeLine({ x: x1, y: y1 }, { x: x2, y: y2 }, appState.currentStrokeId, performance.now());
    },
    preloadPool: preloadPool
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
} else {
    start();
}
