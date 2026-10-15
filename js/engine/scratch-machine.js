/**
 * Masterpiece Garden · Scratch Mode State Machine
 * 随机漫游擦画模式核心状态机 (O(1) 面积统计、平滑揭开动画、无缝切画与防重复队列)
 */

import { elements, scratchConfig, appState, config } from '../state.js';
import { preloadPool } from '../utils/preload-pool.js';

let onMarkDirty = null;
let onComputeBounds = null;
let onRenderScratchBg = null;
let onArtworkChanged = null;

export function registerScratchMachineCallbacks({ markDirty, computeBounds, renderScratchBg, onArtworkChange }) {
    onMarkDirty = markDirty;
    onComputeBounds = computeBounds;
    onRenderScratchBg = renderScratchBg;
    onArtworkChanged = onArtworkChange;
}

/**
 * 挑选下一幅不重复的随机名画索引
 */
export function pickRandomNextIndex() {
    const { masterpieces, currentMasterpieceIndex } = appState;
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
 * 预加载下一幅随机名画到后台底层 (结合 preloadPool 提升性能)
 */
export function prepareNextRandomArtwork(callback) {
    const { masterpieces, nextGardenImage } = appState;
    appState.nextMasterpieceIndex = pickRandomNextIndex();
    const nextArt = masterpieces[appState.nextMasterpieceIndex];
    appState.isNextImageLoaded = false;

    if (!nextArt) {
        if (callback) callback();
        return;
    }

    let handled = false;
    function finish() {
        if (handled) return;
        handled = true;
        appState.isNextImageLoaded = true;
        if (onComputeBounds) onComputeBounds();
        if (appState.appMode === 'scratch' && onRenderScratchBg) {
            onRenderScratchBg();
        }
        if (callback) callback();
    }

    // 通过智能预加载池提前加载图片
    preloadPool.preload(nextArt.src).then((cachedImg) => {
        if (cachedImg && cachedImg.naturalWidth > 0) {
            nextGardenImage.src = cachedImg.src;
            finish();
        } else {
            nextGardenImage.onload = finish;
            nextGardenImage.onerror = () => {
                console.error('[ScratchMachine] 载入下一幅随机名画失败:', nextArt.src);
                finish();
            };
            nextGardenImage.src = nextArt.src;
            if (nextGardenImage.complete && nextGardenImage.naturalWidth > 0) {
                finish();
            }
        }
    }).catch(() => {
        finish();
    });
}

/**
 * 节流更新 HUD 进度条与文字展示 (仅在数值变化时操作 DOM，避免高频回流)
 */
export function syncScratchHud(ratio) {
    const { scratchHudPercent, scratchHudFill, scratchRatioDisplay, scratchMiniBarFill } = elements;
    const pct = Math.min(100, Math.round(ratio * 100));
    if (pct === appState.lastRenderedHudPct) return;
    appState.lastRenderedHudPct = pct;

    if (scratchHudPercent) scratchHudPercent.textContent = `${pct}%`;
    if (scratchHudFill) scratchHudFill.style.width = `${pct}%`;
    if (scratchRatioDisplay) scratchRatioDisplay.textContent = `${pct}%`;
    if (scratchMiniBarFill) scratchMiniBarFill.style.width = `${pct}%`;
}

/**
 * 统计随机漫游模式下的已擦除露出面积比例 (O(1) 瞬时计算)
 */
export function updateScratchRatio() {
    if (appState.appMode !== 'scratch' || scratchConfig.isLocked || scratchConfig.isTransitioning) return;
    if (appState.totalCells <= 0) return;

    const ratio = appState.scratchedCellsCount / appState.totalCells;
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
export function triggerAutoScratchReveal() {
    if (scratchConfig.isLocked || scratchConfig.isTransitioning) return;
    scratchConfig.isLocked = true;
    scratchConfig.isTransitioning = true;

    const { scratchHud, scratchHudPercent } = elements;
    if (scratchHud) scratchHud.classList.add('locked');
    if (scratchHudPercent) scratchHudPercent.textContent = `${Math.round(scratchConfig.threshold * 100)}% ✨`;

    const startTime = performance.now();
    const duration = 480; // ms
    const startAlphas = new Float32Array(appState.gridAlpha);

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(1.0, elapsed / duration);
        const ease = 1 - Math.pow(1 - progress, 3);

        for (let i = 0; i < appState.totalCells; i++) {
            appState.gridAlpha[i] = startAlphas[i] * (1 - ease);
        }

        if (onMarkDirty) onMarkDirty();

        if (progress < 1.0) {
            requestAnimationFrame(step);
        } else {
            appState.gridAlpha.fill(0);
            appState.scratchedCellsCount = appState.totalCells;
            finalizeScratchTransition();
        }
    }

    if (onMarkDirty) onMarkDirty();
    requestAnimationFrame(step);
}

/**
 * 下一幅画已经 100% 完全展示完毕后执行的状态机结算
 * “注意，一幅画必须完全展示出来后，画笔涂抹才能擦去它。”
 */
export function finalizeScratchTransition() {
    // 1. 将刚刚完全展现的下一幅名画正式晋升为当前画
    appState.currentMasterpieceIndex = appState.nextMasterpieceIndex;
    const art = appState.masterpieces[appState.currentMasterpieceIndex];

    appState.gardenImage.src = appState.nextGardenImage.src;
    if (onComputeBounds) onComputeBounds();

    // 2. 联动更新全局画作状态与 UI
    if (onArtworkChanged) {
        onArtworkChanged(art, appState.currentMasterpieceIndex);
    }

    // 3. 重置顶层遮罩为 100% 不透明 (新画完好展现)
    appState.gridAlpha.fill(1.0);
    appState.scratchedCellsCount = 0;
    scratchConfig.ratio = 0;

    // 4. 重置 HUD 进度
    appState.lastRenderedHudPct = 0;
    const { scratchHudPercent, scratchHudFill, scratchRatioDisplay, scratchMiniBarFill, scratchHud } = elements;
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
        if (onMarkDirty) onMarkDirty();
    };

    // 5. 后台立即挑选并预加载下一幅全新的随机名画，渲染到底层 bgCanvas
    prepareNextRandomArtwork(() => {
        if (onComputeBounds) onComputeBounds();
        if (onRenderScratchBg) onRenderScratchBg();
        doUnlock();
    });

    // 6. 600ms 超时保底解锁，保证交互绝对流畅不卡顿
    setTimeout(doUnlock, 600);
    if (onMarkDirty) onMarkDirty();
}
