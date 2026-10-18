/**
 * Masterpiece Garden · Help Modal & Notification Center
 * 操作指南弹窗、Toast 轻提示与入场新手引导管理
 */

import { elements, appState } from '../state.js';

let toastTimer = null;
let isHintDismissed = false;

/**
 * 显示轻量优雅的 Toast 提示 (自动淡出)
 * @param {string} msg 提示内容
 * @param {string} icon 提示图标
 */
export function showToast(msg, icon = '✨') {
    const { modeToast, toastIconEl, toastTextEl } = elements;
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
export function dismissInitialHint() {
    if (isHintDismissed) return;
    isHintDismissed = true;
    const { interactiveHint } = elements;
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
 * 当前设备是否为粗指针（触屏）
 *
 * 提示文案必须区分「鼠标」与「指尖」：触摸设备上出现「用鼠标轻拂」属于明显错位。
 * 该判定在每次调用时求值，避免设备旋转/外接鼠标后文案陈旧。
 */
function isCoarsePointer() {
    return !!(window.matchMedia && window.matchMedia('(pointer: coarse)').matches);
}

/**
 * 根据当前体验模式动态切换操作提示语
 * @param {'sleep' | 'scratch'} mode 体验模式
 */
export function updateHintText(mode) {
    const { hintTextEl } = elements;
    if (!hintTextEl) return;
    const touch = isCoarsePointer();
    if (mode === 'scratch') {
        hintTextEl.textContent = touch
            ? '用指尖擦拭画面 · 透出下一幅随机名画'
            : '用鼠标擦拭画面 · 透出下一幅随机名画';
    } else {
        hintTextEl.textContent = touch
            ? '轻触划动指尖唤醒色彩 · 长按可充能绽放'
            : '用鼠标轻拂屏幕唤醒色彩 · 悬停可充能绽放';
    }
}

/**
 * 打开操作与快捷键指南弹窗
 */
export function openHelp() {
    const { helpModal } = elements;
    if (!helpModal) return;
    document.body.classList.add('help-open');
    helpModal.classList.add('open');
    helpModal.setAttribute('aria-hidden', 'false');
}

/**
 * 关闭操作与快捷键指南弹窗
 */
export function closeHelp() {
    const { helpModal } = elements;
    if (!helpModal) return;
    document.body.classList.remove('help-open');
    helpModal.classList.remove('open');
    helpModal.setAttribute('aria-hidden', 'true');
    appState.isCursorActive = false;
}

/**
 * 切换操作与快捷键指南弹窗
 */
export function toggleHelp() {
    const { helpModal } = elements;
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
export function setupHelpUI() {
    const { helpToggleBtn, helpCloseBtn, helpGotItBtn, helpBackdrop } = elements;

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
