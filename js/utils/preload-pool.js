/**
 * Masterpiece Garden · Smart Artwork Preload Pool
 * 传世名画智能双向预加载池与 LRU 缓存管理器
 */

class ArtworkPreloadPool {
    constructor(maxCacheSize = 12) {
        this.maxCacheSize = maxCacheSize;
        this.cache = new Map(); // key: src -> Image object
    }

    /**
     * 获取或预加载指定名画图片
     * @param {string} src 图片地址
     * @returns {Promise<HTMLImageElement>}
     */
    preload(src) {
        if (!src) return Promise.reject(new Error('Invalid image src'));

        if (this.cache.has(src)) {
            const img = this.cache.get(src);
            // 刷新 LRU 顺序
            this.cache.delete(src);
            this.cache.set(src, img);
            if (img.complete && img.naturalWidth > 0) {
                return Promise.resolve(img);
            }
        }

        return new Promise((resolve) => {
            const img = new Image();
            let handled = false;

            const onFinish = () => {
                if (handled) return;
                handled = true;
                // 限制缓存池大小，淘汰最久未使用的图片
                if (this.cache.size >= this.maxCacheSize) {
                    const oldestKey = this.cache.keys().next().value;
                    this.cache.delete(oldestKey);
                }
                this.cache.set(src, img);
                resolve(img);
            };

            img.onload = onFinish;
            img.onerror = () => {
                console.warn(`[PreloadPool] 预加载名画失败: ${src}`);
                onFinish();
            };

            img.src = src;
            if (img.complete && img.naturalWidth > 0) {
                onFinish();
            }
        });
    }

    /**
     * 智能预测预加载相邻名画 (当前索引的前一幅与后一幅)
     * @param {Array} masterpieces 全量名画列表
     * @param {number} currentIndex 当前正在观赏的名画索引
     */
    preloadAdjacent(masterpieces, currentIndex) {
        if (!masterpieces || masterpieces.length <= 1) return;
        const total = masterpieces.length;

        // 预加载后一幅 (Next)
        const nextIdx = (currentIndex + 1) % total;
        if (masterpieces[nextIdx] && masterpieces[nextIdx].src) {
            this.preload(masterpieces[nextIdx].src);
        }

        // 预加载前一幅 (Prev)
        const prevIdx = (currentIndex - 1 + total) % total;
        if (masterpieces[prevIdx] && masterpieces[prevIdx].src) {
            this.preload(masterpieces[prevIdx].src);
        }
    }

    /**
     * 清理所有缓存
     */
    clear() {
        this.cache.clear();
    }
}

export const preloadPool = new ArtworkPreloadPool(12);
