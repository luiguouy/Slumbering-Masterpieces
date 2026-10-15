/**
 * Masterpiece Garden · Fine Art Story Drawer
 * 传世名画背景故事、历史典故与艺术鉴赏密码抽屉组件
 */

import { elements, appState } from '../state.js';

let onSwitchMasterpiece = null;

export function registerStoryCallbacks({ onSwitchArt }) {
    onSwitchMasterpiece = onSwitchArt;
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
        storyLocation, storyContext, storyAppreciation, storyQuoteText, storyQuoteAuthor
    } = elements;

    if (storyTitle) storyTitle.textContent = story.title;
    if (storyEntitle) storyEntitle.textContent = story.enTitle || '';
    if (storyArtist) storyArtist.textContent = story.artist;
    if (storyPeriod) storyPeriod.textContent = story.period;
    if (storyGenre) storyGenre.textContent = story.genre;
    if (storyLocation) storyLocation.textContent = story.location;
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
    const { storyToggleBtn, brushStoryBtn, storyCloseBtn, storyBackdrop, storyPrevBtn, storyNextBtn } = elements;

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
}
