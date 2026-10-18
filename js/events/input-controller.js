/**
 * Masterpiece Garden · Unified Multi-modal Input Controller
 * 统一多模态输入总线控制器 (鼠标、触控手势、微距双指捏合与平移漫游、古典黄铜透镜互锁及全局快捷键矩阵)
 */

import { elements, appState, config, MODAL_SELECTOR, MACRO_HUD_SELECTOR } from '../state.js';
import { handleResize, refreshLayout, applyDab, strokeLine, MACRO_ZOOM_ACTIVE_THRESHOLD, MAX_MACRO_ZOOM } from '../engine/canvas-engine.js';
import { renderMacroLoupe, resetMacroZoom, setLoupeZoom, toggleLoupe, updateMacroZoomHud, setLoupePointer } from '../engine/macro-loupe.js';
import { toggleFullColor } from '../ui/brush-panel.js';
import { switchMasterpiece, openGallery, closeGallery } from '../ui/gallery-drawer.js';
import { openStory, closeStory, toggleStory } from '../ui/story-drawer.js';
import { openHelp, closeHelp, toggleHelp, showToast, dismissInitialHint, updateHintText } from '../ui/help-modal.js';

// 双指离屏后的单指事件冷却保护期 (ms)，用于消除两指抬手时间差引发的误触
const PINCH_COOLDOWN_MS = 350;

// 双指松手后若缩放已接近全景，则自动吸附复位至 100%
const MACRO_ZOOM_SNAP_THRESHOLD = 1.06;

/**
 * 判定事件是否命中浮层 / 弹窗区域
 * @param {Event} e 事件对象
 * @param {boolean} includeMacroHud 是否将微距缩放胶囊一并视为浮层
 */
function isEventOverModal(e, includeMacroHud = true) {
    if (!e.target || !e.target.closest) return false;
    const selector = includeMacroHud ? `${MODAL_SELECTOR}, ${MACRO_HUD_SELECTOR}` : MODAL_SELECTOR;
    return Boolean(e.target.closest(selector));
}

export function setupInputEvents() {
    window.addEventListener('resize', handleResize);

    // 鼠标拖拽平移漫游状态 (微距放大时支持自如拖拽漫游)
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

    const { artStage: artStageEl, cursor, macroLoupe, artQuote } = elements;

    // ================= 1. 鼠标移动事件监听 =================
    window.addEventListener('mousemove', (e) => {
        // 1. 处理微距放大状态下的鼠标拖拽平移漫游
        if (isDraggingPan) {
            appState.panOffset.x = dragStartPan.x + (e.clientX - dragStartMouse.x);
            appState.panOffset.y = dragStartPan.y + (e.clientY - dragStartMouse.y);
            refreshLayout();
            updateMacroZoomHud();
            if (appState.isLoupeEnabled) {
                renderMacroLoupe(e.clientX, e.clientY);
            }
            return;
        }

        // 2. 检查鼠标当前是否位于浮层或弹窗内部
        const isOverModal = isEventOverModal(e);

        if (isOverModal) {
            if (cursor) {
                cursor.style.opacity = '0';
                cursor.classList.remove('active');
            }
            if (artStageEl) {
                artStageEl.classList.remove('macro-panning', 'macro-panning-active');
            }
            if (appState.isLoupeEnabled && macroLoupe) {
                macroLoupe.classList.remove('active');
                appState.isLoupeVisible = false;
            }
            appState.isCursorActive = false;
            appState.lastPointerPos = null;
            // 必须同时停用指针活跃态：renderLoop 的沉睡分支依赖它决定是否继续
            // 执行停驻充能并保持 rAF 循环；否则光标停在面板上时画作会被持续充能，
            // 帧循环也永不进入静止休眠状态（持续耗电）。
            appState.isPointerActive = false;
            appState.currentPointerPos = null;
            return;
        }

        dismissInitialHint();
        const now = performance.now();
        const pos = { x: e.clientX, y: e.clientY };

        // 3. 古典黄铜透镜模式：专心渲染真彩超清透视，绝不涂抹底层名画
        if (appState.isLoupeEnabled) {
            setLoupePointer(pos.x, pos.y);
            renderMacroLoupe(pos.x, pos.y);
            if (cursor) {
                cursor.style.opacity = '0';
                cursor.classList.remove('active');
            }
            if (artStageEl) {
                artStageEl.classList.remove('macro-panning', 'macro-panning-active');
            }
            appState.lastPointerPos = null;
            return;
        }

        // 4. 微距放大状态：呈现抓手光标 (Grab)，允许按住拖动漫游
        if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD) {
            if (artStageEl) {
                artStageEl.classList.add('macro-panning');
                artStageEl.classList.remove('macro-panning-active');
            }
            if (cursor) {
                cursor.style.opacity = '0';
                cursor.classList.remove('active');
            }
            appState.lastPointerPos = null;
            return;
        } else {
            if (artStageEl) {
                artStageEl.classList.remove('macro-panning', 'macro-panning-active');
            }
        }

        // 5. 正常全景状态：极简艺术光标与轻拂涂抹唤醒
        appState.currentPointerPos = pos;
        appState.isPointerActive = true;
        appState.lastMoveTime = now;

        if (cursor) {
            cursor.style.transform = `translate3d(${pos.x}px, ${pos.y}px, 0)`;
            if (!appState.isCursorActive) {
                appState.isCursorActive = true;
                cursor.style.opacity = '1';
                cursor.classList.add('active');
            }
        }

        if (appState.lastPointerPos) {
            const moveDx = pos.x - appState.lastPointerPos.x;
            const moveDy = pos.y - appState.lastPointerPos.y;
            const moveDist = Math.hypot(moveDx, moveDy);

            if (moveDist > 1) {
                const dot = (moveDx * appState.lastMoveVector.x + moveDy * appState.lastMoveVector.y) /
                            (moveDist * Math.hypot(appState.lastMoveVector.x, appState.lastMoveVector.y) || 1);

                appState.strokeMoveDistance += moveDist;

                if (dot < 0.2 || appState.strokeMoveDistance > 160) {
                    appState.currentStrokeId++;
                    appState.strokeMoveDistance = 0;
                }

                appState.lastMoveVector = { x: moveDx, y: moveDy };
                strokeLine(appState.lastPointerPos, pos, appState.currentStrokeId, now);
            }
        } else {
            appState.currentStrokeId++;
            applyDab(pos.x, pos.y, appState.currentStrokeId, config.singlePassGain, now);
        }

        appState.lastPointerPos = pos;

        if (!appState.isQuoteSubtle && artQuote) {
            appState.isQuoteSubtle = true;
            artQuote.classList.add('subtle');
        }
    });

    // ================= 2. 鼠标按下与松开 =================
    window.addEventListener('mousedown', (e) => {
        const isOverModal = isEventOverModal(e);
        if (isOverModal) return;

        if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD && !appState.isLoupeEnabled) {
            isDraggingPan = true;
            dragStartMouse = { x: e.clientX, y: e.clientY };
            dragStartPan = { x: appState.panOffset.x, y: appState.panOffset.y };
            if (artStageEl) {
                artStageEl.classList.add('macro-panning-active');
            }
            if (e.button === 2) {
                e.preventDefault();
            }
        }
    });

    window.addEventListener('mouseup', () => {
        if (isDraggingPan) {
            isDraggingPan = false;
            if (artStageEl) {
                artStageEl.classList.remove('macro-panning-active');
                if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD) {
                    artStageEl.classList.add('macro-panning');
                }
            }
        }
    });

    // ================= 3. 桌面端双击分流 =================
    window.addEventListener('dblclick', (e) => {
        const isOverModal = isEventOverModal(e);
        if (isOverModal) return;

        if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD || Math.abs(appState.panOffset.x) > 6 || Math.abs(appState.panOffset.y) > 6) {
            resetMacroZoom();
            showToast('🔍 已平滑复位至全景');
        } else {
            toggleFullColor();
        }
    });

    // 屏蔽画布区域上下文菜单
    window.addEventListener('contextmenu', (e) => {
        const isOverModal = isEventOverModal(e, false);
        if (!isOverModal) {
            e.preventDefault();
        }
    });

    // ================= 4. 鼠标滚轮缩放与调焦 =================
    window.addEventListener('wheel', (e) => {
        const isOverModal = isEventOverModal(e, false);
        if (isOverModal) return;

        if (e.cancelable) e.preventDefault();

        if (appState.isLoupeEnabled) {
            const factor = e.deltaY < 0 ? 1.15 : 0.87;
            setLoupeZoom(appState.loupeZoom * factor);
            return;
        }

        const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
        const oldZoom = appState.macroZoom;
        const newZoom = Math.max(1.0, Math.min(MAX_MACRO_ZOOM, appState.macroZoom * zoomFactor));

        if (Math.abs(newZoom - oldZoom) > 0.004) {
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            const cx = appState.viewportWidth / 2 + appState.panOffset.x;
            const cy = appState.viewportHeight / 2 + appState.panOffset.y;
            const scaleChange = newZoom / oldZoom;
            appState.panOffset.x = mouseX - (mouseX - cx) * scaleChange - appState.viewportWidth / 2;
            appState.panOffset.y = mouseY - (mouseY - cy) * scaleChange - appState.viewportHeight / 2;
            appState.macroZoom = newZoom;

            if (appState.macroZoom < 1.03) {
                appState.macroZoom = 1.0;
                appState.panOffset.x = 0;
                appState.panOffset.y = 0;
            }

            refreshLayout();
            updateMacroZoomHud();
        }
    }, { passive: false });

    // 鼠标离开视口
    window.addEventListener('mouseleave', () => {
        appState.isPointerActive = false;
        isDraggingPan = false;
        appState.lastPointerPos = null;
        appState.currentPointerPos = null;
        appState.lastMoveVector = { x: 0, y: 0 };
        appState.currentStrokeId++;
        appState.isCursorActive = false;
        appState.isQuoteSubtle = false;

        if (cursor) {
            cursor.style.opacity = '0';
            cursor.classList.remove('active');
        }
        if (artStageEl) {
            artStageEl.classList.remove('macro-panning', 'macro-panning-active');
        }
        if (appState.isLoupeEnabled && macroLoupe) {
            macroLoupe.classList.remove('active');
            appState.isLoupeVisible = false;
        }
        if (artQuote) {
            artQuote.classList.remove('subtle');
        }
    });

    // ================= 5. 移动端专用触控手势 =================
    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;
    let lastTapTime = 0;
    let lastTapPos = { x: 0, y: 0 };

    window.addEventListener('touchstart', (e) => {
        const isOverModal = isEventOverModal(e);
        if (isOverModal) {
            appState.lastPointerPos = null;
            return;
        }

        dismissInitialHint();

        // 双指触控
        if (e.touches.length >= 2) {
            isPinching = true;
            appState.isPointerActive = false;
            appState.currentPointerPos = null;
            appState.lastPointerPos = null;

            const t1 = e.touches[0];
            const t2 = e.touches[1];
            pinchStartDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY) || 1;
            pinchStartZoom = appState.macroZoom;
            pinchStartPan = { x: appState.panOffset.x, y: appState.panOffset.y };
            pinchCenter = {
                x: (t1.clientX + t2.clientX) / 2,
                y: (t1.clientY + t2.clientY) / 2
            };
            if (e.cancelable) e.preventDefault();
            return;
        }

        if (performance.now() < pinchCooldownUntil) {
            return;
        }

        // 单指触控
        if (e.touches.length === 1 && !isPinching) {
            const now = performance.now();
            const t = e.touches[0];
            const pos = { x: t.clientX, y: t.clientY };

            touchStartX = pos.x;
            touchStartY = pos.y;
            touchStartTime = now;

            if (appState.isLoupeEnabled) {
                setLoupePointer(pos.x, pos.y);
                renderMacroLoupe(pos.x, pos.y);
                return;
            }

            appState.currentPointerPos = pos;
            appState.lastPointerPos = pos;
            appState.isPointerActive = true;
            appState.lastMoveTime = now;
            appState.currentStrokeId++;
            appState.strokeMoveDistance = 0;
            applyDab(pos.x, pos.y, appState.currentStrokeId, config.singlePassGain, now);
        }
    }, { passive: false });

    window.addEventListener('touchmove', (e) => {
        const isOverModal = isEventOverModal(e);
        if (isOverModal) {
            appState.lastPointerPos = null;
            return;
        }

        if (e.cancelable) {
            e.preventDefault();
        }

        // 双指捏合缩放与平移漫游
        if (e.touches.length >= 2) {
            isPinching = true;
            appState.isPointerActive = false;

            const t1 = e.touches[0];
            const t2 = e.touches[1];
            const currentDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
            const currentCenter = {
                x: (t1.clientX + t2.clientX) / 2,
                y: (t1.clientY + t2.clientY) / 2
            };

            const distRatio = currentDist / pinchStartDist;
            const newZoom = Math.max(1.0, Math.min(MAX_MACRO_ZOOM, pinchStartZoom * distRatio));

            const panDx = currentCenter.x - pinchCenter.x;
            const panDy = currentCenter.y - pinchCenter.y;
            appState.panOffset.x = pinchStartPan.x + panDx;
            appState.panOffset.y = pinchStartPan.y + panDy;
            appState.macroZoom = newZoom;

            refreshLayout();
            updateMacroZoomHud();
            return;
        }

        if (isPinching || performance.now() < pinchCooldownUntil) {
            return;
        }

        // 单指划动涂抹或透镜移动
        if (e.touches.length === 1 && !isPinching) {
            const now = performance.now();
            const t = e.touches[0];
            const pos = { x: t.clientX, y: t.clientY };

            if (appState.isLoupeEnabled) {
                setLoupePointer(pos.x, pos.y);
                renderMacroLoupe(pos.x, pos.y);
                return;
            }

            appState.currentPointerPos = pos;
            appState.isPointerActive = true;
            appState.lastMoveTime = now;

            if (appState.lastPointerPos) {
                const moveDx = pos.x - appState.lastPointerPos.x;
                const moveDy = pos.y - appState.lastPointerPos.y;
                const moveDist = Math.hypot(moveDx, moveDy);
                appState.strokeMoveDistance += moveDist;

                if (appState.strokeMoveDistance > 140) {
                    appState.currentStrokeId++;
                    appState.strokeMoveDistance = 0;
                }

                strokeLine(appState.lastPointerPos, pos, appState.currentStrokeId, now);
            } else {
                applyDab(pos.x, pos.y, appState.currentStrokeId, config.singlePassGain, now);
            }
            appState.lastPointerPos = pos;
        }
    }, { passive: false });

    /**
     * 统一抬手 / 中断结算：手势状态清理 + 意图识别
     * @param {TouchEvent} e 触摸事件
     * @param {boolean} isCancel 是否为 touchcancel 系统中断事件
     *        中断时必须无条件复位所有手势状态——否则 isPinching 会永久停留在 true，
     *        导致后续 touchmove 在 isPinching 分支被全部吞掉，移动端触摸交互彻底失灵且无法恢复
     */
    function handleTouchEnd(e, isCancel = false) {
        // 1. 双指捏合结束：启动冷却保护期
        //    中断场景下 e.touches 可能仍残留触点记录，故一律强制复位
        if (isPinching) {
            if (isCancel || e.touches.length === 0) {
                isPinching = false;
                pinchCooldownUntil = performance.now() + PINCH_COOLDOWN_MS;
                if (appState.macroZoom < MACRO_ZOOM_SNAP_THRESHOLD) {
                    resetMacroZoom();
                }
            }
            return;
        }

        if (performance.now() < pinchCooldownUntil) {
            return;
        }

        // 2. 通用指针与笔画状态清理
        appState.isPointerActive = false;
        isDraggingPan = false;
        appState.lastPointerPos = null;
        appState.currentPointerPos = null;
        appState.currentStrokeId++;

        if (appState.isLoupeEnabled && macroLoupe) {
            macroLoupe.classList.remove('active');
            appState.isLoupeVisible = false;
        }

        // 3. 系统中断事件到此为止：仅清理状态，绝不结算双击 / 轻扫等手势意图
        if (isCancel) return;

        const isOverModal = isEventOverModal(e);
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

            // 手机端双击屏幕智能分流
            if (touchDistance < 22 && touchDuration < 280) {
                const timeSinceLastTap = now - lastTapTime;
                const tapDistFromLast = Math.hypot(endX - lastTapPos.x, endY - lastTapPos.y);
                if (timeSinceLastTap < 320 && tapDistFromLast < 35) {
                    if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD || Math.abs(appState.panOffset.x) > 6 || Math.abs(appState.panOffset.y) > 6) {
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

            // 手机端水平轻扫切画 (仅在非放大状态且非透镜模式下触发)
            if (!appState.isLoupeEnabled && appState.macroZoom <= MACRO_ZOOM_ACTIVE_THRESHOLD && touchDuration < 420 && Math.abs(touchDx) > 68 && Math.abs(touchDx) > Math.abs(touchDy) * 1.6) {
                const total = appState.masterpieces.length;
                if (touchDx < 0) {
                    const nextIdx = (appState.currentMasterpieceIndex + 1) % total;
                    switchMasterpiece(nextIdx);
                } else {
                    const prevIdx = (appState.currentMasterpieceIndex - 1 + total) % total;
                    switchMasterpiece(prevIdx);
                }
            }
        }
    }

    window.addEventListener('touchend', handleTouchEnd);
    // 系统手势打断 / 来电 / 多任务切换等场景下 touchend 不会触发，
    // 必须监听 touchcancel 兜底清理，否则移动端触摸交互将永久失灵
    window.addEventListener('touchcancel', (e) => handleTouchEnd(e, true));

    window.addEventListener('orientationchange', () => {
        setTimeout(handleResize, 180);
    });
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', handleResize);
    }

    // ================= 6. 全局键盘快捷键矩阵 =================
    window.addEventListener('keydown', (e) => {
        const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement && document.activeElement.tagName);
        const { helpModal, storyDrawer, galleryDrawer, brushPopup, brushToggleBtn } = elements;

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
                // toggleFullColor 在随机漫游模式下会自行给出提示并返回 false；
                // 此处不可再覆盖 toast，否则会把「模式不适用」误报成「已重置画布色彩」。
                if (toggleFullColor()) {
                    showToast(appState.isFullColorLocked ? '已一键盛放全幅色彩' : '已重置画布色彩', appState.isFullColorLocked ? '🌸' : '🔄');
                }
            } else if (e.key === 'm' || e.key === 'M' || e.key === 'z' || e.key === 'Z') {
                e.preventDefault();
                toggleLoupe();
            } else if (e.key === '0' || e.key === 'r' || e.key === 'R') {
                e.preventDefault();
                if (appState.macroZoom > MACRO_ZOOM_ACTIVE_THRESHOLD || Math.abs(appState.panOffset.x) > 5 || Math.abs(appState.panOffset.y) > 5) {
                    resetMacroZoom();
                    showToast('🔍 已平滑复位至全景');
                }
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                const total = appState.masterpieces.length;
                const prevIdx = (appState.currentMasterpieceIndex - 1 + total) % total;
                switchMasterpiece(prevIdx);
                showToast(`《${appState.masterpieces[prevIdx].title}》`, '🖼️');
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                const total = appState.masterpieces.length;
                const nextIdx = (appState.currentMasterpieceIndex + 1) % total;
                switchMasterpiece(nextIdx);
                showToast(`《${appState.masterpieces[nextIdx].title}》`, '🖼️');
            }
        }
    });

    // 提示语统一由 updateHintText 生成（内部自行判定粗指针设备），
    // 避免此处与模式切换路径各自维护一份文案而产生措辞分叉。
    updateHintText(appState.appMode);
}
