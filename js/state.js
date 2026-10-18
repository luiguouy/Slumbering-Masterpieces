/**
 * Masterpiece Garden · Global State & Configuration Store
 * 全局状态管理中枢与配置中心
 */

// 古典黄铜透镜的 CSS 显示尺寸 (px)
// 必须与 style.css 中 .macro-loupe 的 width / height 保持一致：
// 透镜的后端像素缓冲按此值乘以 dpr 分配，两者不符会导致高分屏下放大模糊或采样偏移
export const LOUPE_CSS_SIZE = 220;

// 交互浮层选择器：新增任何浮层时只需在此登记一处，
// 事件命中判定与透镜隐匿判定统一引用，避免各处硬编码导致漏改
// 注意 .brush-control-panel 是画笔面板「容器」（含底部按钮坞），
// .brush-popup 仅是其内部展开的弹层，两者都需登记
export const MODAL_SELECTOR = '.gallery-panel, .story-panel, .help-dialog, .brush-control-panel, .brush-popup';
export const MACRO_HUD_SELECTOR = '.macro-zoom-hud';

// 核心画布与界面元素
export const elements = {
    bgCanvas: document.getElementById('bg-canvas'),
    revealCanvas: document.getElementById('reveal-canvas'),
    artQuote: document.getElementById('art-quote'),
    quoteTextEl: document.querySelector('#art-quote .quote-text'),
    quoteAuthorEl: document.querySelector('#art-quote .quote-author'),
    cursor: document.getElementById('custom-cursor'),
    cursorRing: document.querySelector('#custom-cursor .cursor-ring'),
    artStage: document.getElementById('art-stage'),

    // 画笔控制 UI 元素
    brushToggleBtn: document.getElementById('brush-toggle-btn'),
    brushPopup: document.getElementById('brush-popup'),
    brushSlider: document.getElementById('brush-size-slider'),
    brushSizeDisplay: document.getElementById('brush-size-display'),
    brushPreviewDot: document.getElementById('brush-preview-dot'),
    brushDurationSlider: document.getElementById('brush-duration-slider'),
    brushDurationDisplay: document.getElementById('brush-duration-display'),
    colorRatioSlider: document.getElementById('brush-color-ratio-slider'),
    colorRatioDisplay: document.getElementById('brush-color-ratio-display'),
    toggleFullColorBtn: document.getElementById('toggle-full-color-btn'),
    fullColorBtnText: document.getElementById('full-color-btn-text'),

    // 模式切换与随机漫游控制 UI 元素
    modeSleepBtn: document.getElementById('mode-sleep-btn'),
    modeScratchBtn: document.getElementById('mode-scratch-btn'),
    sleepModeControls: document.getElementById('sleep-mode-controls'),
    scratchModeControls: document.getElementById('scratch-mode-controls'),
    scratchThresholdSlider: document.getElementById('scratch-threshold-slider'),
    scratchThresholdDisplay: document.getElementById('scratch-threshold-display'),
    scratchRatioDisplay: document.getElementById('scratch-ratio-display'),
    scratchMiniBarFill: document.getElementById('scratch-mini-bar-fill'),
    scratchRevealNowBtn: document.getElementById('scratch-reveal-now-btn'),
    scratchHud: document.getElementById('scratch-hud'),
    scratchHudPercent: document.getElementById('scratch-hud-percent'),
    scratchHudTargetVal: document.getElementById('scratch-hud-target-val'),
    scratchHudFill: document.getElementById('scratch-hud-fill'),

    // 画面规格与缩放控制 UI 元素
    fitAutoBtn: document.getElementById('fit-auto-btn'),
    fitContainBtn: document.getElementById('fit-contain-btn'),
    fitCoverBtn: document.getElementById('fit-cover-btn'),
    fitModeDisplay: document.getElementById('fit-mode-display'),
    fitScaleSlider: document.getElementById('fit-scale-slider'),
    fitScaleDisplay: document.getElementById('fit-scale-display'),

    // 微距细节探索与古典黄铜透镜 UI 元素
    macroZoomHud: document.getElementById('macro-zoom-hud'),
    macroZoomPercent: document.getElementById('macro-zoom-percent'),
    macroZoomResetBtn: document.getElementById('macro-zoom-reset-btn'),
    macroLoupe: document.getElementById('macro-loupe'),
    macroLoupeCanvas: document.getElementById('macro-loupe-canvas'),
    toggleLoupeBtn: document.getElementById('toggle-loupe-btn'),
    loupePillStatus: document.getElementById('loupe-pill-status'),
    loupeOptionsBox: document.getElementById('loupe-options-box'),

    // 名画画廊切换 UI 元素 (画笔面板卡片)
    masterpieceIndexBadge: document.getElementById('masterpiece-index'),
    openGalleryModalBtn: document.getElementById('open-gallery-modal-btn'),
    currentArtThumb: document.getElementById('current-art-thumb'),
    currentArtTitle: document.getElementById('current-art-title'),
    currentArtArtist: document.getElementById('current-art-artist'),
    prevArtBtn: document.getElementById('prev-art-btn'),
    nextArtBtn: document.getElementById('next-art-btn'),

    // 传世名画博览馆 · 典藏搜索与多维分类抽屉展厅 UI 元素
    galleryOpenBtn: document.getElementById('gallery-open-btn'),
    galleryOpenBadge: document.getElementById('gallery-open-badge'),
    galleryDrawer: document.getElementById('gallery-drawer'),
    galleryBackdrop: document.getElementById('gallery-backdrop'),
    galleryCloseBtn: document.getElementById('gallery-close-btn'),
    gallerySearchInput: document.getElementById('gallery-search-input'),
    gallerySearchClear: document.getElementById('gallery-search-clear'),
    genrePillsContainer: document.getElementById('genre-pills-container'),
    artistFilterSelect: document.getElementById('artist-filter-select'),
    categoryFilterSelect: document.getElementById('category-filter-select'),
    quickArtistsContainer: document.getElementById('quick-artists-container'),
    galleryResultCount: document.getElementById('gallery-result-count'),
    galleryFilterDesc: document.getElementById('gallery-filter-desc'),
    galleryResetBtn: document.getElementById('gallery-reset-btn'),
    galleryListContainer: document.getElementById('gallery-list-container'),

    // 名画背景故事与艺术鉴赏抽屉 UI 元素
    storyToggleBtn: document.getElementById('story-toggle-btn'),
    brushStoryBtn: document.getElementById('brush-story-btn'),
    storyDrawer: document.getElementById('story-drawer'),
    storyBackdrop: document.getElementById('story-backdrop'),
    storyCloseBtn: document.getElementById('story-close-btn'),
    storyTitle: document.getElementById('story-title'),
    storyEntitle: document.getElementById('story-entitle'),
    storyArtist: document.getElementById('story-artist'),
    storyPeriod: document.getElementById('story-period'),
    storyGenre: document.getElementById('story-genre'),
    storyLocation: document.getElementById('story-location'),
    storyContext: document.getElementById('story-context'),
    storyAppreciation: document.getElementById('story-appreciation'),
    storyQuoteText: document.getElementById('story-quote-text'),
    storyQuoteAuthor: document.getElementById('story-quote-author'),
    storyPrevBtn: document.getElementById('story-prev-btn'),
    storyNextBtn: document.getElementById('story-next-btn'),

    // 操作引导与快捷键指南 UI 元素
    interactiveHint: document.getElementById('interactive-hint'),
    hintTextEl: document.getElementById('hint-text'),
    modeToast: document.getElementById('mode-toast'),
    toastIconEl: document.getElementById('toast-icon'),
    toastTextEl: document.getElementById('toast-text'),
    helpToggleBtn: document.getElementById('help-toggle-btn'),
    helpModal: document.getElementById('help-modal'),
    helpBackdrop: document.getElementById('help-backdrop'),
    helpCloseBtn: document.getElementById('help-close-btn'),
    helpGotItBtn: document.getElementById('help-got-it-btn')
};

// 画布上下文
export const contexts = {
    bgCtx: elements.bgCanvas ? elements.bgCanvas.getContext('2d') : null,
    revealCtx: elements.revealCanvas ? elements.revealCanvas.getContext('2d') : null,
    macroLoupeCtx: elements.macroLoupeCanvas ? elements.macroLoupeCanvas.getContext('2d') : null,
    maskCanvas: document.createElement('canvas'),
    maskCtx: null,
    maskSmallCanvas: document.createElement('canvas'),
    maskSmallCtx: null
};
contexts.maskCtx = contexts.maskCanvas.getContext('2d');
contexts.maskSmallCtx = contexts.maskSmallCanvas.getContext('2d', { willReadFrequently: true });

// 交互参数配置
export const config = {
    brushRadius: 75,             // 默认画笔半径 (px)
    minBrushRadius: 35,          // 最小画笔半径
    maxBrushRadius: 160,         // 最大画笔半径
    colorRatio: 1.0,             // 划过唤醒显色比例 (0.2 ~ 1.0)
    singlePassGain: 0.26,        // 单次划过最大显色增量
    hoverChargeGain: 0.12,       // 悬停充能增量 (每 45ms 递增)
    totalDurationSeconds: 12,    // 默认色彩留存总时长 (12 秒)
    solidDurationMs: 8500,       // 保持期 (8.5 秒)
    fadeDurationMs: 3500,        // 渐变衰减期 (3.5 秒)
    cellSize: 14,                // 空间衰减网格分辨率 (px)
    fitMode: 'auto',             // 画面规格模式: 'auto' | 'contain' | 'cover'
    scale: 1.0                   // 用户自定义缩放倍率 (0.6 ~ 1.4)
};

// 随机漫游擦画模式核心状态机配置
export const scratchConfig = {
    threshold: 0.85,             // 默认 85% 触发自动完全展开 (0.50 ~ 0.95)
    isLocked: false,             // 关键状态机锁：一幅画未完全展示出来前，严禁擦除！
    isTransitioning: false,      // 正在进行平滑揭晓过渡
    ratio: 0.0,                  // 当前已擦除露出面积比例 (0.0 ~ 1.0)
    historyQueue: [],            // 历史防重复队列
    maxHistoryLen: 30            // 记忆最近 30 幅画作防重复
};

// 题材分类正统体系定义
export const GENRE_DEFINITIONS = [
    { id: 'all', label: '全部题材', icon: '🎨', test: () => true },
    { id: 'life', label: '风俗生活', icon: '👥', test: (art) => art.genre && (art.genre.includes('风俗') || art.genre.includes('生活')) },
    { id: 'landscape', label: '自然风景', icon: '🌿', test: (art) => art.genre && (art.genre.includes('风景') || art.genre.includes('风光')) },
    { id: 'portrait', label: '人物肖像', icon: '👤', test: (art) => art.genre && art.genre.includes('人物') },
    { id: 'mythology', label: '神话宗教', icon: '🏛️', test: (art) => art.genre && (art.genre.includes('神话') || art.genre.includes('宗教')) },
    { id: 'history', label: '历史故事', icon: '⚔️', test: (art) => art.genre && (art.genre.includes('历史') || art.genre.includes('故事') || art.genre.includes('叙事')) },
    { id: 'still_life', label: '静物花卉', icon: '💐', test: (art) => art.genre && (art.genre.includes('静物') || art.genre.includes('花卉')) }
];

// 全局名画多维筛选与搜索状态
export const galleryFilterState = {
    query: '',
    genre: 'all',
    artist: 'all',
    category: 'all'
};

// 核心应用运行态数据
export const appState = {
    appMode: 'sleep',            // 'sleep' | 'scratch'
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    dpr: window.devicePixelRatio || 1,

    // 空间状态网格系统
    gridCols: 0,
    gridRows: 0,
    totalCells: 0,
    gridAlpha: null,             // Float32Array
    gridLastTouch: null,         // Float64Array
    gridLastStroke: null,        // Int32Array
    maskSmallImageData: null,
    paintingCells: 0,            // 画作在网格中实际覆盖的格子数 (随机漫游擦除进度的分母)

    // 鼠标与笔画状态
    isPointerActive: false,
    currentPointerPos: null,
    lastPointerPos: null,
    lastMoveTime: 0,
    lastHoverChargeTime: 0,
    currentStrokeId: 1,
    strokeMoveDistance: 0,
    lastMoveVector: { x: 0, y: 0 },
    isInitialized: false,
    isFullColorLocked: false,
    isCursorActive: false,
    isQuoteSubtle: false,

    // 渲染循环控制
    isDirty: true,
    isRenderingActive: false,
    scratchedCellsCount: 0,
    lastRenderedHudPct: -1,

    // 微距探索与平移漫游核心状态
    macroZoom: 1.0,
    panOffset: { x: 0, y: 0 },
    zoomAnimRaf: null,

    // 古典黄铜透镜状态
    isLoupeEnabled: false,
    loupeZoom: 3.5,
    loupeZoomLevels: [2.0, 3.5, 5.0],
    loupeZoomIndex: 1,
    lastLoupePointerPos: { x: -9999, y: -9999 },
    hasLoupePointerPos: false,       // 是否已记录过透镜光标位置（替代 x > 0 的哨兵判断）
    isLoupeVisible: false,
    loupeCssSize: LOUPE_CSS_SIZE,    // 透镜实际 CSS 尺寸，由 measureLoupeCssSize() 于 resize 时刷新

    // 名画图片实体与几何参数
    gardenImage: new Image(),
    isImageLoaded: false,
    imageBounds: { x: 0, y: 0, w: 0, h: 0, baseW: 0, baseH: 0, effectiveMode: 'auto' },

    // 下一幅名画（随机擦画底层）
    nextGardenImage: new Image(),
    isNextImageLoaded: false,
    nextMasterpieceIndex: -1,
    nextImageBounds: { x: 0, y: 0, w: 0, h: 0, baseW: 0, baseH: 0, effectiveMode: 'auto' },

    // 当前索引与名画列表
    currentMasterpieceIndex: 0,
    masterpieces: []
};

// 初始化名画数据源
export function initMasterpieces() {
    appState.masterpieces = (window.MASTERPIECES && window.MASTERPIECES.length) ? window.MASTERPIECES : [];
    return appState.masterpieces;
}

/**
 * 测量古典黄铜透镜的真实 CSS 显示尺寸
 *
 * LOUPE_CSS_SIZE 只是首屏与兜底值：style.css 在 max-width:640px 断点把 .macro-loupe
 * 改为 180px。若仍按常量 220 计算，会同时错三处——
 *   ① 采样跨度按 220 算，实际显示 180，真实放大倍率低于标注约 18%；
 *   ② 后端缓冲按 220×dpr 分配后被 CSS 缩到 180，取景范围比准星对应区域更大；
 *   ③ loupeArtCoverage() 用 R=110 判圆盘覆盖率，而真实半径只有 90，边缘提前隐匿。
 *
 * 该函数只在 resize 时调用一次（getComputedStyle 会触发样式重算，不可放进高频渲染路径），
 * 结果缓存到 appState.loupeCssSize 供渲染与命中判定读取。
 */
export function measureLoupeCssSize() {
    const el = elements.macroLoupe;
    if (el) {
        const w = parseFloat(getComputedStyle(el).width);
        if (Number.isFinite(w) && w > 0) {
            appState.loupeCssSize = w;
            return w;
        }
    }
    appState.loupeCssSize = LOUPE_CSS_SIZE;
    return LOUPE_CSS_SIZE;
}
