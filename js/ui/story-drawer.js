/**
 * Masterpiece Garden · Fine Art Story Drawer
 * 传世名画背景故事、历史典故与艺术鉴赏密码抽屉组件
 */

import { elements, appState } from '../state.js';

let onSwitchMasterpiece = null;

export function registerStoryCallbacks({ onSwitchArt }) {
    onSwitchMasterpiece = onSwitchArt;
}

// 底部上拉卡片仅在窄屏启用；桌面仍走右侧抽屉
const MOBILE_SHEET_QUERY = '(max-width: 640px)';

function isSheetMode() {
    return !!(window.matchMedia && window.matchMedia(MOBILE_SHEET_QUERY).matches);
}

/**
 * 设置移动端卡片高度档位
 * @param {'half'|'full'} level half = 与画作同屏；full = 完全展开
 */
export function setSheetLevel(level) {
    const { storyDrawer } = elements;
    if (!storyDrawer) return;
    if (!isSheetMode()) {
        delete storyDrawer.dataset.sheet;
        return;
    }
    storyDrawer.dataset.sheet = (level === 'full') ? 'full' : 'half';
}

/**
 * 在半屏与全屏之间切换
 */
export function toggleSheetLevel() {
    const { storyDrawer } = elements;
    if (!storyDrawer || !isSheetMode()) return;
    storyDrawer.dataset.sheet = (storyDrawer.dataset.sheet === 'full') ? 'half' : 'full';
}

/**
 * 更新名画故事抽屉的内容
 */
export function updateStoryContent(art) {
    if (!art || !window.getArtworkStory) return;
    const story = window.getArtworkStory(art);
    if (!story) return;

    const {
        storyTitle, storyEntitle, storyArtist, storyPeriod, storyGenre,
        storyLocation, storyNarrative, storyContext, storyAppreciation,
        storyQuoteText, storyQuoteAuthor
    } = elements;

    if (storyTitle) storyTitle.textContent = story.title;
    if (storyEntitle) storyEntitle.textContent = story.enTitle || '';
    if (storyArtist) storyArtist.textContent = story.artist;
    if (storyPeriod) storyPeriod.textContent = story.period;
    if (storyGenre) storyGenre.textContent = story.genre;
    if (storyLocation) storyLocation.textContent = story.location;
    // 画中故事：讲画面里正在发生什么（与下方「创作背景」互补：一个讲画的内容，一个讲画的来历）
    if (storyNarrative) storyNarrative.textContent = story.narrative || '';
    if (storyContext) storyContext.textContent = story.context;
    if (storyAppreciation) storyAppreciation.textContent = story.appreciation;
    if (storyQuoteText) storyQuoteText.textContent = story.quote;
    if (storyQuoteAuthor) storyQuoteAuthor.textContent = story.quoteAuthor;
}

/**
 * 打开名画背景故事抽屉
 */
export function openStory() {
    const { storyDrawer, brushPopup, brushToggleBtn } = elements;
    if (!storyDrawer) return;

    // 若画笔弹窗展开，顺畅收起
    if (brushPopup && brushPopup.classList.contains('open')) {
        brushPopup.classList.remove('open');
        if (brushToggleBtn) brushToggleBtn.classList.remove('active');
    }

    const currentArt = appState.masterpieces[appState.currentMasterpieceIndex];
    if (currentArt) {
        updateStoryContent(currentArt);
    }

    // 先定档位再 open，避免出现「未定档 → 面板停在屏幕外」的空帧
    setSheetLevel('half');
    document.body.classList.add('story-open');
    storyDrawer.classList.add('open');
    storyDrawer.setAttribute('aria-hidden', 'false');
}

/**
 * 关闭名画背景故事抽屉
 */
export function closeStory() {
    const { storyDrawer } = elements;
    if (!storyDrawer) return;
    document.body.classList.remove('story-open');
    storyDrawer.classList.remove('open');
    storyDrawer.setAttribute('aria-hidden', 'true');
    delete storyDrawer.dataset.sheet;
    appState.isCursorActive = false;
}

/**
 * 切换名画背景故事抽屉展开/收起
 */
export function toggleStory() {
    const { storyDrawer } = elements;
    if (storyDrawer && storyDrawer.classList.contains('open')) {
        closeStory();
    } else {
        openStory();
    }
}

/**
 * 初始化故事交互事件监听
 */
export function setupStoryUI() {
    const { storyToggleBtn, brushStoryBtn, storyCloseBtn, storyBackdrop, storyPrevBtn, storyNextBtn, storyDrawer, storySheetHandle } = elements;

    if (storyToggleBtn) {
        storyToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleStory();
        });
    }

    if (brushStoryBtn) {
        brushStoryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const { brushPopup, brushToggleBtn } = elements;
            if (brushPopup && brushPopup.classList.contains('open')) {
                brushPopup.classList.remove('open');
                if (brushToggleBtn) brushToggleBtn.classList.remove('active');
            }
            openStory();
        });
    }

    if (storyCloseBtn) {
        storyCloseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeStory();
        });
    }

    if (storyBackdrop) {
        storyBackdrop.addEventListener('click', (e) => {
            e.stopPropagation();
            closeStory();
        });
    }

    if (storyPrevBtn) {
        storyPrevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const total = appState.masterpieces.length;
            const nextIdx = (appState.currentMasterpieceIndex - 1 + total) % total;
            if (onSwitchMasterpiece) onSwitchMasterpiece(nextIdx);
        });
    }

    if (storyNextBtn) {
        storyNextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const total = appState.masterpieces.length;
            const nextIdx = (appState.currentMasterpieceIndex + 1) % total;
            if (onSwitchMasterpiece) onSwitchMasterpiece(nextIdx);
        });
    }

    // 移动端上拉卡片：拖拽把手或点击标题栏在半屏 / 全屏之间切换
    if (storySheetHandle) {
        const toggle = (e) => {
            e.stopPropagation();
            toggleSheetLevel();
        };
        storySheetHandle.addEventListener('click', toggle);
        storySheetHandle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleSheetLevel();
            }
        });
    }

    if (storyDrawer) {
        const header = storyDrawer.querySelector('.story-header');
        if (header) {
            header.addEventListener('click', (e) => {
                // 关闭按钮等自身已有处理，不重复触发
                if (e.target.closest('button')) return;
                if (!isSheetMode()) return;
                toggleSheetLevel();
            });
        }

        // 视口变宽（切回桌面布局）时清掉档位，避免残留 data-sheet 影响右侧抽屉
        window.addEventListener('resize', () => {
            if (!isSheetMode()) delete storyDrawer.dataset.sheet;
        });
    }
}
