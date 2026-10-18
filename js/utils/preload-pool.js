/**
 * Masterpiece Garden · Smart Artwork Preload Pool
 * 传世名画智能双向预加载池与 LRU 缓存管理器
 */

// 豁免淘汰名单的容量上限
// 只需覆盖「当前展示 + 前一幅 + 后一幅 + 随机漫游下一幅候选」这一量级即可
const MAX_PROTECTED_ENTRIES = 6;

class ArtworkPreloadPool {
    constructor(maxCacheSize = 12) {
        this.maxCacheSize = maxCacheSize;
        this.cache = new Map();          // key: src -> Image（Map 的插入顺序即 LRU 顺序）
        this.protectedKeys = new Set();  // 豁免淘汰的 src 集合
    }

    /**
     * 登记豁免淘汰的 src（增量式，重复登记会刷新其顺序）
     *
     * 若不做保护，快速连续切画时 LRU 会按纯粹的「最久未用」淘汰，
     * 有可能恰好挤掉马上就要用到的相邻图，反而制造黑屏
     * ——这与「消除切画黑屏」的设计目标相悖。
     * @param {string[]} srcList 需要保护的 src 列表
     */
    protect(srcList) {
        if (!srcList) return;
        for (const s of srcList) {
            if (!s) continue;
            this.protectedKeys.delete(s);
            this.protectedKeys.add(s);
        }
        while (this.protectedKeys.size > MAX_PROTECTED_ENTRIES) {
            this.protectedKeys.delete(this.protectedKeys.keys().next().value);
        }
    }

    /**
     * 淘汰一个「未受保护且最久未使用」的条目
     * @returns {boolean} 是否成功淘汰
     */
    evictOne() {
        for (const key of this.cache.keys()) {
            if (!this.protectedKeys.has(key)) {
                this.cache.delete(key);
                return true;
            }
        }
        return false;
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

            const settle = (succeeded) => {
                if (handled) return;
                handled = true;

                // 加载失败的资源不写入缓存：
                // 否则坏图会占据缓存条目并被后续请求反复命中，污染缓存有效性
                if (!succeeded) {
                    resolve(img);
                    return;
                }

                // 限制缓存池大小，淘汰最久未使用且未受保护的条目
                if (this.cache.size >= this.maxCacheSize) {
                    this.evictOne();
                }
                this.cache.set(src, img);
                resolve(img);
            };

            img.onload = () => settle(true);
            img.onerror = () => {
                console.warn(`[PreloadPool] 预加载名画失败: ${src}`);
                settle(false);
            };

            img.src = src;
            if (img.complete && img.naturalWidth > 0) {
                settle(true);
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

        const nextIdx = (currentIndex + 1) % total;
        const prevIdx = (currentIndex - 1 + total) % total;

        const curSrc = masterpieces[currentIndex] && masterpieces[currentIndex].src;
        const nextSrc = masterpieces[nextIdx] && masterpieces[nextIdx].src;
        const prevSrc = masterpieces[prevIdx] && masterpieces[prevIdx].src;

        // 将「当前 + 前一幅 + 后一幅」登记为豁免淘汰项，避免刚预载完就被 LRU 挤掉
        this.protect([curSrc, nextSrc, prevSrc]);

        // 预加载后一幅 (Next)
        if (nextSrc) {
            this.preload(nextSrc);
        }

        // 预加载前一幅 (Prev)
        if (prevSrc) {
            this.preload(prevSrc);
        }
    }

    /**
     * 清理所有缓存与豁免名单
     */
    clear() {
        this.cache.clear();
        this.protectedKeys.clear();
    }
}

export const preloadPool = new ArtworkPreloadPool(12);
