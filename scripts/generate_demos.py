import os
import time
import math
import shutil
import subprocess
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "assets", "demo")
TEMP_VIDEO_DIR = os.path.join(WORKSPACE_DIR, "assets", "demo", "temp_record")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

def smooth_move(page, start_x, start_y, end_x, end_y, steps=25, delay=0.015):
    for i in range(1, steps + 1):
        t = i / steps
        # 平滑缓动
        ease = 0.5 - 0.5 * math.cos(math.pi * t)
        curr_x = start_x + (end_x - start_x) * ease
        curr_y = start_y + (end_y - start_y) * ease
        page.mouse.move(curr_x, curr_y)
        time.sleep(delay)

def draw_spiral(page, center_x, center_y, max_r=180, revolutions=3.5, steps=100, delay=0.015):
    for i in range(steps):
        angle = (i / steps) * revolutions * 2 * math.pi
        r = (i / steps) * max_r
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle) * 0.75
        page.mouse.move(x, y)
        time.sleep(delay)

def main():
    print("[1/5] 启动 Chrome 并开启高分辨率录制 (1280x800)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            record_video_dir=TEMP_VIDEO_DIR,
            record_video_size={"width": 1280, "height": 800}
        )
        page = context.new_page()

        print("[2/5] 访问本地艺术展页面并等待名画加载...")
        page.goto("http://localhost:8080", wait_until="networkidle")
        time.sleep(2.0)

        # 1. 沉睡模式初始灰阶状态截图
        init_screenshot = os.path.join(OUTPUT_DIR, "preview-initial-dormant.png")
        page.screenshot(path=init_screenshot)
        print(f"已生成初始素描截图: {init_screenshot}")

        # 2. 模拟沉睡唤醒交互
        print("[3/5] 模拟沉睡唤醒互动（渐进涂抹与焦点充能）...")
        page.mouse.move(640, 400)
        time.sleep(0.3)
        page.mouse.down()
        # 画出中央盛放螺旋
        draw_spiral(page, 640, 400, max_r=220, revolutions=4, steps=120, delay=0.02)
        # 往左侧擦拭几下
        smooth_move(page, 640 + 200, 400, 380, 300, steps=30)
        smooth_move(page, 380, 300, 380, 520, steps=30)
        smooth_move(page, 380, 520, 520, 420, steps=25)
        # 在花芯核心停留充能
        page.mouse.move(640, 400)
        time.sleep(0.8) # 停驻充能绽放
        page.mouse.up()
        time.sleep(0.5)

        # 截图保存沉睡唤醒高光效果
        awakening_screenshot = os.path.join(OUTPUT_DIR, "preview-dormant-awakening.png")
        page.screenshot(path=awakening_screenshot)
        print(f"已生成唤醒盛放截图: {awakening_screenshot}")
        time.sleep(1.0)

        # 3. 展开控制面板截图
        print("[4/5] 展开设置面板与模式切换...")
        page.click("#brush-toggle-btn")
        time.sleep(0.6)
        controls_screenshot = os.path.join(OUTPUT_DIR, "preview-controls.png")
        page.screenshot(path=controls_screenshot)
        print(f"已生成控制面板截图: {controls_screenshot}")

        # 4. 切换到随机漫游模式
        page.click("#mode-scratch-btn")
        time.sleep(0.5)
        
        # 将画笔调大到 115px 便于展示擦除体验
        page.evaluate("""() => {
            const slider = document.getElementById('brush-size-slider');
            if (slider) {
                slider.value = 115;
                slider.dispatchEvent(new Event('input'));
            }
        }""")
        time.sleep(0.3)
        # 再次点击收起控制面板
        page.click("#brush-toggle-btn")
        time.sleep(0.5)

        # 5. 模拟随机漫游擦拭
        print("[5/5] 模拟随机漫游擦拭与露底过渡...")
        # 在画布上进行 S 型折线擦除
        points = [
            (250, 220), (1030, 240),
            (1000, 380), (280, 390),
            (300, 530), (1020, 520),
            (950, 640), (350, 630)
        ]
        
        page.mouse.move(points[0][0], points[0][1])
        page.mouse.down()
        
        # 抹到一半时截取一张双画重叠效果图
        for i in range(len(points) - 1):
            smooth_move(page, points[i][0], points[i][1], points[i+1][0], points[i+1][1], steps=22, delay=0.015)
            if i == 3:
                # 中间状态截图
                page.mouse.up()
                time.sleep(0.2)
                wander_screenshot = os.path.join(OUTPUT_DIR, "preview-random-wander.png")
                page.screenshot(path=wander_screenshot)
                print(f"已生成随机漫游擦拭中交错效果截图: {wander_screenshot}")
                page.mouse.down()

        # 继续擦拭中心密集区域，使其突破 85% 阈值
        smooth_move(page, 400, 300, 880, 300, steps=25)
        smooth_move(page, 880, 450, 400, 450, steps=25)
        smooth_move(page, 640, 200, 640, 650, steps=25)
        smooth_move(page, 450, 350, 850, 350, steps=20)
        page.mouse.up()

        # 等待 85% 自动平滑展开动画执行完毕 (480ms 缓动 + 预热缓冲)
        print("等待自动平滑完全展开新画...")
        time.sleep(2.5)

        # 完整展开后的新画状态截图
        revealed_screenshot = os.path.join(OUTPUT_DIR, "preview-next-revealed.png")
        page.screenshot(path=revealed_screenshot)
        print(f"已生成新画完全展现截图: {revealed_screenshot}")

        time.sleep(1.0)
        page.close()
        context.close()
        video_path = page.video.path()
        browser.close()

    print(f"Playwright 录制原始视频完成: {video_path}")
    return video_path

if __name__ == "__main__":
    raw_video = main()
    
    # 查找录制的 webm 文件
    if os.path.exists(raw_video):
        full_mp4 = os.path.join(OUTPUT_DIR, "demo-full-showcase.mp4")
        print(f"正在使用 ffmpeg 转码生成完整 MP4: {full_mp4}...")
        subprocess.run([
            "ffmpeg", "-y", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium",
            full_mp4
        ], check=True)

        # 生成精美轻量 GIF 动图
        # 1. 唤醒模式动画 GIF (从 2.0s 到 9.5s)
        awakening_gif = os.path.join(OUTPUT_DIR, "demo-awakening.gif")
        awakening_mp4 = os.path.join(OUTPUT_DIR, "demo-awakening.mp4")
        print(f"生成沉睡唤醒模式动图与视频: {awakening_gif} ...")
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:02.0", "-t", "7.5", "-i", raw_video,
            "-vf", "fps=14,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
            awakening_gif
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:02.0", "-t", "7.5", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            awakening_mp4
        ], check=True)

        # 2. 随机漫游模式动画 GIF (从 13.0s 到 22.0s)
        wander_gif = os.path.join(OUTPUT_DIR, "demo-wander.gif")
        wander_mp4 = os.path.join(OUTPUT_DIR, "demo-wander.mp4")
        print(f"生成随机漫游模式动图与视频: {wander_gif} ...")
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:13.0", "-t", "9.0", "-i", raw_video,
            "-vf", "fps=14,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
            wander_gif
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:13.0", "-t", "9.0", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            wander_mp4
        ], check=True)

        # 清理临时录制文件
        shutil.rmtree(TEMP_VIDEO_DIR, ignore_errors=True)
        print("\n✅ 所有演示图片与视频生成完毕！目录：assets/demo/")
