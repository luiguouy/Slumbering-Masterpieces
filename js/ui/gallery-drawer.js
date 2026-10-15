/**
 * Masterpiece Garden · Fine Art Collection Drawer & Search Engine
 * 传世名画博览馆 · 典藏搜索、多维流派题材分类、分批虚拟滚动与卡片交互抽屉
 */

import { elements, contexts, appState, config, scratchConfig, GENRE_DEFINITIONS, galleryFilterState } from '../state.js';
import { refreshLayout, markDirty, renderGrayscaleBackground } from '../engine/canvas-engine.js';
import { resetMacroZoom } from '../engine/macro-loupe.js';
import { toggleFullColor } from './brush-panel.js';
import { updateStoryContent } from './story-drawer.js';
import { preloadPool } from '../utils/preload-pool.js';

let galleryFilteredItems = [];
let galleryRenderedCount = 0;
const GALLERY_BATCH_SIZE = 24;
let gallerySentinelEl = null;
let galleryObserver = null;

/**
 * 规范化检索文本 (忽略空格、间隔号·、英文标点等，支持“达芬奇”匹配“达·芬奇”)
 */
export function normalizeSearchText(str) {
    if (!str) return '';
    return String(str).toLowerCase().replace(/[\s·\-\._・/()（）,"'‘’“”]/g, '');
}

/**
 * 执行名画多维过滤与关键词检索
 */
export function getFilteredMasterpieces() {
    const q = galleryFilterState.query.trim();
    const qNorm = normalizeSearchText(q);
    const activeGenre = GENRE_DEFINITIONS.find(g => g.id === galleryFilterState.genre) || GENRE_DEFINITIONS[0];

    return appState.masterpieces
        .map((art, index) => ({ art, index }))
        .filter(({ art }) => {
            // 1. 题材筛选
            if (!activeGenre.test(art)) return false;

            // 2. 画家筛选
            if (galleryFilterState.artist !== 'all' && art.artist !== galleryFilterState.artist) {
                return false;
            }

            // 3. 画派时期筛选
            if (galleryFilterState.category !== 'all' && art.category !== galleryFilterState.category) {
                return false;
            }

            // 4. 关键词智能模糊搜索
            if (qNorm) {
                const matchTitle = normalizeSearchText(art.title).includes(qNorm);
                const matchEnTitle = normalizeSearchText(art.enTitle).includes(qNorm);
                const matchArtist = normalizeSearchText(art.artist).includes(qNorm);
                const matchGenre = normalizeSearchText(art.genre).includes(qNorm);
                const matchQuote = normalizeSearchText(art.quote).includes(qNorm);
                const matchCategory = normalizeSearchText(art.category).includes(qNorm);
                if (!matchTitle && !matchEnTitle && !matchArtist && !matchGenre && !matchQuote && !matchCategory) {
                    return false;
                }
            }

            return true;
        });
}

/**
 * 创建单个名画卡片 DOM 节点
 */
export function createGalleryCard({ art, index }) {
    const isCurrent = index === appState.currentMasterpieceIndex;
    const card = document.createElement('div');
    card.className = `gallery-card ${isCurrent ? 'is-active' : ''}`;
    card.setAttribute('data-index', index);
    card.setAttribute('role', 'listitem');
    card.title = `点击切换欣赏：《${art.title}》· ${art.artist}`;

    let catLabel = '';
    if (window.ART_CATEGORIES) {
        const catObj = window.ART_CATEGORIES.find(c => c.id === art.category);
        if (catObj) catLabel = catObj.name.split('(')[0].trim();
    }

    card.innerHTML = `
        <div class="card-thumb-box">
            <img class="card-thumb-img" src="${art.src}" alt="${art.title}" loading="lazy" decoding="async" fetchpriority="low" width="54" height="54">
        </div>
        <div class="card-details">
            <div class="card-header-row">
                <div class="card-title">${index + 1}. ${art.title}</div>
                ${isCurrent ? '<span class="card-badge-viewing">👑 观赏中</span>' : ''}
            </div>
            ${art.enTitle ? `<div class="card-entitle">${art.enTitle}</div>` : ''}
            <div class="card-artist">${art.artist}</div>
            <div class="card-tags-row">
                ${art.genre ? `<span class="card-tag card-tag-genre">${art.genre}</span>` : ''}
                ${catLabel ? `<span class="card-tag card-tag-cat">${catLabel}</span>` : ''}
            </div>
        </div>
    `;

    card.addEventListener('click', () => {
        switchMasterpiece(index);
        if (window.innerWidth <= 640) {
            closeGallery();
        }
    });

    return card;
}

/**
 * 追加渲染下一批画作卡片
 */
export function appendGalleryBatch() {
    const { galleryListContainer } = elements;
    if (!galleryListContainer || galleryRenderedCount >= galleryFilteredItems.length) {
        if (gallerySentinelEl && gallerySentinelEl.parentNode) {
            gallerySentinelEl.style.display = 'none';
        }
        return;
    }

    const nextCount = Math.min(galleryFilteredItems.length, galleryRenderedCount + GALLERY_BATCH_SIZE);
    const frag = document.createDocumentFragment();

    for (let i = galleryRenderedCount; i < nextCount; i++) {
        frag.appendChild(createGalleryCard(galleryFilteredItems[i]));
    }

    galleryRenderedCount = nextCount;

    if (gallerySentinelEl && gallerySentinelEl.parentNode === galleryListContainer) {
        galleryListContainer.insertBefore(frag, gallerySentinelEl);
        gallerySentinelEl.style.display = (galleryRenderedCount < galleryFilteredItems.length) ? 'block' : 'none';
    } else {
        galleryListContainer.appendChild(frag);
        if (galleryRenderedCount < galleryFilteredItems.length) {
            ensureGallerySentinel();
        }
    }
}

function ensureGallerySentinel() {
    const { galleryListContainer } = elements;
    if (!gallerySentinelEl) {
        gallerySentinelEl = document.createElement('div');
        gallerySentinelEl.className = 'gallery-scroll-sentinel';
        gallerySentinelEl.style.height = '40px';
        gallerySentinelEl.style.width = '100%';
        gallerySentinelEl.style.pointerEvents = 'none';
    }
    gallerySentinelEl.style.display = 'block';
    galleryListContainer.appendChild(gallerySentinelEl);
    initGalleryObserver();
}

function initGalleryObserver() {
    if (galleryObserver) {
        galleryObserver.disconnect();
    }
    const { galleryListContainer } = elements;
    if (!gallerySentinelEl || !('IntersectionObserver' in window)) return;

    galleryObserver = new IntersectionObserver((entries) => {
        if (entries[0] && entries[0].isIntersecting) {
            appendGalleryBatch();
        }
    }, {
        root: galleryListContainer,
        rootMargin: '300px 0px',
        threshold: 0.01
    });

    galleryObserver.observe(gallerySentinelEl);
}

/**
 * 重新渲染画廊抽屉列表 (高性能分批增量渲染)
 */
export function renderGalleryList() {
    const { galleryListContainer, galleryResultCount, galleryResetBtn, galleryFilterDesc } = elements;
    if (!galleryListContainer) return;

    galleryFilteredItems = getFilteredMasterpieces();
    const hasActiveFilter = galleryFilterState.query.trim() !== '' ||
        galleryFilterState.genre !== 'all' ||
        galleryFilterState.artist !== 'all' ||
        galleryFilterState.category !== 'all';

    if (galleryResultCount) galleryResultCount.textContent = galleryFilteredItems.length;
    if (galleryResetBtn) {
        galleryResetBtn.style.display = hasActiveFilter ? 'inline-block' : 'none';
    }

    if (galleryFilterDesc) {
        const parts = [];
        if (galleryFilterState.genre !== 'all') {
            const g = GENRE_DEFINITIONS.find(item => item.id === galleryFilterState.genre);
            if (g) parts.push(g.label);
        }
        if (galleryFilterState.artist !== 'all') parts.push(galleryFilterState.artist.split('(')[0].trim());
        if (galleryFilterState.category !== 'all' && window.ART_CATEGORIES) {
            const c = window.ART_CATEGORIES.find(item => item.id === galleryFilterState.category);
            if (c) parts.push(c.name.split('(')[0].replace(/[^\u4e00-\u9fa5]/g, ''));
        }
        galleryFilterDesc.textContent = parts.length > 0 ? `(${parts.join(' · ')})` : '';
    }

    if (galleryObserver) {
        galleryObserver.disconnect();
    }

    galleryListContainer.innerHTML = '';
    galleryRenderedCount = 0;

    if (galleryFilteredItems.length === 0) {
        const emptyEl = document.createElement('div');
        emptyEl.className = 'gallery-empty-state';
        emptyEl.innerHTML = `
            <div class="empty-icon">🎨</div>
            <div class="empty-title">未寻得匹配的名画作品</div>
            <p class="empty-desc">换个搜索词试试，或者重置当前题材与画家分类筛选。</p>
            <button class="empty-reset-btn" type="button">重置所有筛选</button>
        `;
        const emptyResetBtn = emptyEl.querySelector('.empty-reset-btn');
        if (emptyResetBtn) {
            emptyResetBtn.addEventListener('click', resetAllFilters);
        }
        galleryListContainer.appendChild(emptyEl);
        return;
    }

    let initialLimit = GALLERY_BATCH_SIZE;
    const currentArtIndexInList = galleryFilteredItems.findIndex(item => item.index === appState.currentMasterpieceIndex);
    if (currentArtIndexInList >= 0 && currentArtIndexInList >= GALLERY_BATCH_SIZE) {
        initialLimit = Math.min(galleryFilteredItems.length, Math.ceil((currentArtIndexInList + 8) / GALLERY_BATCH_SIZE) * GALLERY_BATCH_SIZE);
    }

    const frag = document.createDocumentFragment();
    const limit = Math.min(galleryFilteredItems.length, initialLimit);
    for (let i = 0; i < limit; i++) {
        frag.appendChild(createGalleryCard(galleryFilteredItems[i]));
    }
    galleryRenderedCount = limit;
    galleryListContainer.appendChild(frag);

    if (galleryRenderedCount < galleryFilteredItems.length) {
        ensureGallerySentinel();
    }
}

/**
 * 重置所有筛选与搜索
 */
export function resetAllFilters() {
    galleryFilterState.query = '';
    galleryFilterState.genre = 'all';
    galleryFilterState.artist = 'all';
    galleryFilterState.category = 'all';

    const { gallerySearchInput, gallerySearchClear, genrePillsContainer, artistFilterSelect, categoryFilterSelect, quickArtistsContainer } = elements;

    if (gallerySearchInput) gallerySearchInput.value = '';
    if (gallerySearchClear) gallerySearchClear.style.display = 'none';

    if (genrePillsContainer) {
        const pills = genrePillsContainer.querySelectorAll('.genre-pill');
        pills.forEach(p => p.classList.toggle('active', p.getAttribute('data-genre') === 'all'));
    }

    if (artistFilterSelect) artistFilterSelect.value = 'all';
    if (categoryFilterSelect) categoryFilterSelect.value = 'all';

    if (quickArtistsContainer) {
        const qp = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
        qp.forEach(p => p.classList.remove('active'));
    }

    renderGalleryList();
}

/**
 * 更新画廊抽屉列表中的激活高亮项
 */
export function updateActiveCardHighlight(activeIndex) {
    const { galleryListContainer } = elements;
    if (!galleryListContainer) return;
    const cards = galleryListContainer.querySelectorAll('.gallery-card');
    cards.forEach(card => {
        const idx = parseInt(card.getAttribute('data-index'), 10);
        const isTarget = idx === activeIndex;
        card.classList.toggle('is-active', isTarget);
        let badge = card.querySelector('.card-badge-viewing');
        if (isTarget) {
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'card-badge-viewing';
                badge.textContent = '👑 观赏中';
                const header = card.querySelector('.card-header-row');
                if (header) header.appendChild(badge);
            }
        } else if (badge) {
            badge.remove();
        }
    });
}

/**
 * 切换当前激活的名画
 * @param {number} index 画作索引 (0 ~ masterpieces.length - 1)
 */
export function switchMasterpiece(index) {
    const { masterpieces } = appState;
    if (index < 0 || index >= masterpieces.length) return;
    appState.currentMasterpieceIndex = index;
    const art = masterpieces[index];

    // 复位全彩模式与微距缩放
    if (appState.isFullColorLocked) {
        toggleFullColor(false);
    }
    resetMacroZoom(true);

    const {
        quoteTextEl, quoteAuthorEl, currentArtThumb, currentArtTitle,
        currentArtArtist, masterpieceIndexBadge, scratchHudPercent,
        scratchHudFill, scratchRatioDisplay, scratchMiniBarFill, scratchHud
    } = elements;
    const { revealCtx } = contexts;

    // 1. 重置显色状态网格与离屏采样遮罩
    if (appState.appMode === 'scratch') {
        if (appState.gridAlpha) appState.gridAlpha.fill(1.0);
        appState.scratchedCellsCount = 0;
        scratchConfig.ratio = 0;
        scratchConfig.isLocked = false;
        scratchConfig.isTransitioning = false;
        appState.lastRenderedHudPct = 0;
        if (scratchHudPercent) scratchHudPercent.textContent = '0%';
        if (scratchHudFill) scratchHudFill.style.width = '0%';
        if (scratchRatioDisplay) scratchRatioDisplay.textContent = '0%';
        if (scratchMiniBarFill) scratchMiniBarFill.style.width = '0%';
        if (scratchHud) scratchHud.classList.remove('locked');
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
    }

    // 2. 更新诗意名言与作者署名
    if (quoteTextEl) quoteTextEl.textContent = art.quote;
    if (quoteAuthorEl) quoteAuthorEl.textContent = art.quoteAuthor;

    // 3. 更新画笔面板当前名画卡片展示与徽章
    if (currentArtThumb) {
        currentArtThumb.src = art.src;
        currentArtThumb.alt = art.title;
    }
    if (currentArtTitle) currentArtTitle.textContent = art.title;
    if (currentArtArtist) currentArtArtist.textContent = `${art.artist} · 🔍 检索画廊`;
    if (masterpieceIndexBadge) masterpieceIndexBadge.textContent = `${index + 1} / ${masterpieces.length}`;

    // 4. 同步更新画廊展厅卡片激活高亮状态与背景故事
    updateActiveCardHighlight(index);
    updateStoryContent(art);

    // 5. 载入新名画原图并重新渲染古典灰阶底图
    appState.isImageLoaded = false;
    appState.gardenImage.src = art.src;

    // 6. 智能双向预加载池：触发 index ± 1 预加载，消除切画黑屏
    preloadPool.preloadAdjacent(masterpieces, index);

    markDirty();
}

/**
 * 打开名画抽屉展厅
 */
export function openGallery() {
    const { galleryDrawer, brushPopup, brushToggleBtn, gallerySearchInput, galleryListContainer } = elements;
    if (!galleryDrawer) return;

    if (brushPopup && brushPopup.classList.contains('open')) {
        brushPopup.classList.remove('open');
        if (brushToggleBtn) brushToggleBtn.classList.remove('active');
    }

    document.body.classList.add('gallery-open');
    galleryDrawer.classList.add('open');
    galleryDrawer.setAttribute('aria-hidden', 'false');

    setTimeout(() => {
        if (gallerySearchInput) gallerySearchInput.focus();
    }, 150);

    setTimeout(() => {
        if (galleryListContainer) {
            const activeCard = galleryListContainer.querySelector('.gallery-card.is-active');
            if (activeCard) {
                activeCard.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        }
    }, 220);
}

/**
 * 关闭名画抽屉展厅
 */
export function closeGallery() {
    const { galleryDrawer } = elements;
    if (!galleryDrawer) return;
    document.body.classList.remove('gallery-open');
    galleryDrawer.classList.remove('open');
    galleryDrawer.setAttribute('aria-hidden', 'true');
    appState.isCursorActive = false;
}

/**
 * 初始化名画画廊与多维分类检索 UI
 */
export function setupGalleryUI() {
    const {
        genrePillsContainer, artistFilterSelect, categoryFilterSelect,
        quickArtistsContainer, gallerySearchInput, gallerySearchClear,
        galleryResetBtn, galleryOpenBtn, openGalleryModalBtn, galleryCloseBtn,
        galleryBackdrop, prevArtBtn, nextArtBtn, galleryListContainer
    } = elements;
    const { masterpieces } = appState;

    // 1. 初始化题材药丸按钮
    if (genrePillsContainer) {
        genrePillsContainer.innerHTML = '';
        GENRE_DEFINITIONS.forEach(def => {
            const count = def.id === 'all'
                ? masterpieces.length
                : masterpieces.filter(def.test).length;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `genre-pill ${def.id === 'all' ? 'active' : ''}`;
            btn.setAttribute('data-genre', def.id);
            btn.innerHTML = `<span>${def.icon} ${def.label}</span><span class="genre-pill-count">(${count})</span>`;

            btn.addEventListener('click', () => {
                galleryFilterState.genre = def.id;
                const allPills = genrePillsContainer.querySelectorAll('.genre-pill');
                allPills.forEach(p => p.classList.toggle('active', p === btn));
                renderGalleryList();
            });

            genrePillsContainer.appendChild(btn);
        });
    }

    const gallerySubInfo = document.querySelector('.gallery-sub-info');
    if (gallerySubInfo) {
        gallerySubInfo.textContent = `World Masterpieces · ${masterpieces.length} 幅传世杰作`;
    }

    // 2. 统计所有画家作品数
    const artistCounts = {};
    masterpieces.forEach(art => {
        const a = art.artist || '未知艺术家';
        artistCounts[a] = (artistCounts[a] || 0) + 1;
    });
    const sortedArtists = Object.keys(artistCounts).sort((a, b) => artistCounts[b] - artistCounts[a]);

    if (artistFilterSelect) {
        artistFilterSelect.innerHTML = `<option value="all">🎨 全部画家 (${sortedArtists.length}位大师)</option>`;
        sortedArtists.forEach(artist => {
            const opt = document.createElement('option');
            opt.value = artist;
            opt.textContent = `${artist} (${artistCounts[artist]}幅)`;
            artistFilterSelect.appendChild(opt);
        });

        artistFilterSelect.addEventListener('change', (e) => {
            galleryFilterState.artist = e.target.value;
            if (quickArtistsContainer) {
                const qp = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
                qp.forEach(p => p.classList.toggle('active', p.getAttribute('data-artist') === e.target.value));
            }
            renderGalleryList();
        });
    }

    // 3. 填充时期画派流派下拉
    if (categoryFilterSelect && window.ART_CATEGORIES) {
        categoryFilterSelect.innerHTML = `<option value="all">🏛️ 全部画派时期 (${window.ART_CATEGORIES.length}大流派)</option>`;
        window.ART_CATEGORIES.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = `${cat.name} (${cat.count || 0}幅)`;
            categoryFilterSelect.appendChild(opt);
        });

        categoryFilterSelect.addEventListener('change', (e) => {
            galleryFilterState.category = e.target.value;
            renderGalleryList();
        });
    }

    // 4. 填充热门艺术大师快捷直选胶囊
    if (quickArtistsContainer) {
        quickArtistsContainer.innerHTML = '';
        const topArtists = sortedArtists.slice(0, 8);
        topArtists.forEach(artist => {
            const shortMatch = artist.match(/\((.*?)\)/);
            const shortName = shortMatch ? shortMatch[1] : artist.split(' ')[0];
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'quick-artist-pill';
            btn.setAttribute('data-artist', artist);
            btn.textContent = `${shortName} (${artistCounts[artist]})`;

            btn.addEventListener('click', () => {
                if (galleryFilterState.artist === artist) {
                    galleryFilterState.artist = 'all';
                    btn.classList.remove('active');
                    if (artistFilterSelect) artistFilterSelect.value = 'all';
                } else {
                    galleryFilterState.artist = artist;
                    const allPills = quickArtistsContainer.querySelectorAll('.quick-artist-pill');
                    allPills.forEach(p => p.classList.toggle('active', p === btn));
                    if (artistFilterSelect) artistFilterSelect.value = artist;
                }
                renderGalleryList();
            });

            quickArtistsContainer.appendChild(btn);
        });
    }

    // 5. 搜索栏输入与实时清除事件
    if (gallerySearchInput) {
        gallerySearchInput.addEventListener('input', (e) => {
            galleryFilterState.query = e.target.value;
            if (gallerySearchClear) {
                gallerySearchClear.style.display = e.target.value ? 'flex' : 'none';
            }
            renderGalleryList();
        });

        gallerySearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (gallerySearchInput.value) {
                    gallerySearchInput.value = '';
                    galleryFilterState.query = '';
                    if (gallerySearchClear) gallerySearchClear.style.display = 'none';
                    renderGalleryList();
                } else {
                    closeGallery();
                }
                e.stopPropagation();
            }
        });
    }

    if (gallerySearchClear) {
        gallerySearchClear.addEventListener('click', () => {
            if (gallerySearchInput) gallerySearchInput.value = '';
            galleryFilterState.query = '';
            gallerySearchClear.style.display = 'none';
            if (gallerySearchInput) gallerySearchInput.focus();
            renderGalleryList();
        });
    }

    // 6. 重置所有筛选按钮
    if (galleryResetBtn) {
        galleryResetBtn.addEventListener('click', resetAllFilters);
    }

    // 7. 展厅打开/关闭触发器
    if (galleryOpenBtn) {
        galleryOpenBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openGallery();
        });
    }

    if (openGalleryModalBtn) {
        openGalleryModalBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openGallery();
        });
    }

    if (galleryCloseBtn) {
        galleryCloseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeGallery();
        });
    }

    if (galleryBackdrop) {
        galleryBackdrop.addEventListener('click', (e) => {
            e.stopPropagation();
            closeGallery();
        });
    }

    // 8. 上一幅 / 下一幅快捷切换
    if (prevArtBtn) {
        prevArtBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const nextIdx = (appState.currentMasterpieceIndex - 1 + masterpieces.length) % masterpieces.length;
            switchMasterpiece(nextIdx);
        });
    }

    if (nextArtBtn) {
        nextArtBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const nextIdx = (appState.currentMasterpieceIndex + 1) % masterpieces.length;
            switchMasterpiece(nextIdx);
        });
    }

    // 9. 滚动时无感追加下一批画作
    if (galleryListContainer) {
        galleryListContainer.addEventListener('scroll', () => {
            if (galleryRenderedCount < galleryFilteredItems.length) {
                const remaining = galleryListContainer.scrollHeight - (galleryListContainer.scrollTop + galleryListContainer.clientHeight);
                if (remaining < 450) {
                    appendGalleryBatch();
                }
            }
        }, { passive: true });
    }

    renderGalleryList();
}
