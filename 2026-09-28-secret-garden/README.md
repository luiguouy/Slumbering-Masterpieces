# The Slumbering Garden (沉睡的花园)

> **Fine Arts Digital Exhibition · An Interactive Chromatic Awakening**  
> *"Touch the dormant monochrome; breathe fleeting vividness into the petals."*

---

## 🎨 艺术理念 (Artistic Philosophy)

《The Slumbering Garden》是一件融合古典油画美学与数字交互的参赛级网络艺术装置。
整个画面以一座阳光沐浴下的欧洲古典庄园花园为主体——满园繁花（紫藤花廊、爬藤玫瑰、飞燕草、牡丹、绣球花丛与鸢尾花海）和透彻湛蓝的天空。

未触碰时，整座花园宛如静止沉睡的古典灰阶版画，庄严素穆；  
而当观者的鼠标或指尖轻抚画面，沉睡的生机在指尖被瞬间点亮——划过之处绽放真实的缤纷原彩，并伴随若隐若现的微光花粉；  
当指尖离去，绚烂的色彩随时间如水波般静静退去，再度归于宁静的黑白。

---

## ✨ 核心技术与交互特色 (Technical Highlights)

1. **双缓冲像素级严格对齐 (Dual-Layer Pixel-Perfect Compositing)**：
   - 底层为经过高级明暗对比与素描质感调色（CSS Grayscale & Contrast）的静态画卷；
   - 顶层由高帧率 HTML5 Canvas 通过几何映射实时自适应视口尺寸（Cover Mode），确保色彩唤醒区域与底层素描背景 100.00% 严丝合缝重叠。
2. **水彩柔焦羽化与轨迹插值算法 (Smooth Trajectory Interpolation & Radial Mask)**：
   - 采用两点间直线插值补点算法，高速挥动光标也不会产生断点或齿状裂纹；
   - 采用径向渐变柔和晕染（Radial Gradient），模拟水彩在宣纸上渗透的柔润光晕。
3. **触碰悬停与衰减记忆机制 (Hover Persistence & Smooth Decay)**：
   - 光标悬停在任意花朵或天空上时，该处持续保持灿烂绽放；
   - 移动后的轨迹在设定的秒数（默认 2.8 秒，可自由调节）内按非线性平滑曲线自然淡隐。
4. **金色光尘粒子系统 (Golden Pollen Sparkle Engine)**：
   - 随笔触轻盈诞生，伴随向上微风与微弱辉光，赋予画面生命觉醒的灵性氛围。
5. **典雅艺术排版与纯净模式 (Curator Typography & Pure Mode)**：
   - 引入经典文艺复兴雕刻与衬线字体（Cinzel & Cormorant Garamond）；
   - 在用户沉浸作画时，文字自动轻柔淡隐；
   - 右下角提供半透明毛玻璃调控台（支持笔刷粗细、记忆时间微调、全彩保留模式、一键全屏纯净模式以及自定义本地画作更换）。

---

## 🚀 启动与预览方式 (Quick Start)

本项目为**零第三方依赖**的原生前端纯粹架构，任何现代浏览器均可直接运行：

1. **直接双击打开**：
   - 直接双击打开 `index.html` 即可在本地浏览器中体验。
2. **轻量静态服务器运行（推荐）**：
   - 在当前目录打开命令行执行：
     ```bash
     npx serve .
     # 或
     python -m http.server 8080
     ```
   - 浏览器访问 `http://localhost:8080` 获得最佳体验。
