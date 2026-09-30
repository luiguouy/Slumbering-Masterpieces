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

def smooth_move(page, start_x, start_y, end_x, end_y, steps=20, delay=0.015):
    for i in range(1, steps + 1):
        t = i / steps
        ease = 0.5 - 0.5 * math.cos(math.pi * t)
        curr_x = start_x + (end_x - start_x) * ease
        curr_y = start_y + (end_y - start_y) * ease
        page.mouse.move(curr_x, curr_y)
        time.sleep(delay)

def main():
    print("[1/5] 启动 Chrome 并录制 1280x800 高清视频...")
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

        print("[2/5] 访问画廊并切换至《拿破仑一世及皇后加冕典礼 (1807)》...")
        page.goto("http://localhost:8080", wait_until="networkidle")
        time.sleep(1.0)

        # 切换至指定名作：拿破仑一世及皇后加冕典礼 (Index: 125)
        page.evaluate("window.__gardenEngine.setMasterpiece(125)")
        time.sleep(2.0)

        # 1. 沉睡模式初始灰阶素描截图
        init_screenshot = os.path.join(OUTPUT_DIR, "preview-initial-dormant.png")
        page.screenshot(path=init_screenshot)
        print(f"已生成初始素描截图: {init_screenshot}")

        # 2. 模拟沉睡唤醒交互（重点唤醒拿破仑皇冠与约瑟芬皇后红金长袍）
        print("[3/5] 模拟沉睡唤醒互动（加冕焦点渐进涂抹与停驻充能）...")
        page.mouse.move(680, 680)
        time.sleep(0.3)
        page.mouse.down()
        
        # 拂过教皇 -> 拿破仑 -> 金冠
        smooth_move(page, 680, 680, 580, 650, steps=25)
        smooth_move(page, 580, 650, 550, 580, steps=20) # 高举的皇冠
        smooth_move(page, 550, 580, 530, 560, steps=15)
        smooth_move(page, 530, 560, 560, 590, steps=15)
        
        # 顺着拿破仑华服向下拂向跪地的约瑟芬皇后
        smooth_move(page, 560, 590, 580, 660, steps=20)
        smooth_move(page, 580, 660, 500, 720, steps=25) # 约瑟芬皇后
        
        # 来回抚摸约瑟芬皇后的红色丝绒锦缎大氅
        smooth_move(page, 500, 720, 390, 770, steps=25)
        smooth_move(page, 390, 770, 480, 740, steps=20)
        smooth_move(page, 480, 740, 360, 780, steps=25)
        smooth_move(page, 360, 780, 510, 700, steps=25) # 回到皇后发髻与加冕处
        
        # 停驻充能绽放 (Hover Focus Charge)
        time.sleep(0.9)
        page.mouse.up()
        
        # 将光标轻移开，不遮挡加冕核心画面
        smooth_move(page, 510, 700, 720, 520, steps=25)
        time.sleep(0.5)

        # 截图保存沉睡唤醒高光效果
        awakening_screenshot = os.path.join(OUTPUT_DIR, "preview-dormant-awakening.png")
        page.screenshot(path=awakening_screenshot)
        print(f"已生成唤醒盛放截图: {awakening_screenshot}")
        time.sleep(1.2)

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
        
        # 调大画笔至 115px 便于展示擦除体验
        page.evaluate("""() => {
            const slider = document.getElementById('brush-size-slider');
            if (slider) {
                slider.value = 115;
                slider.dispatchEvent(new Event('input'));
            }
        }""")
        time.sleep(0.3)
        page.click("#brush-toggle-btn")
        time.sleep(0.5)

        # 5. 模拟随机漫游擦拭
        print("[5/5] 模拟随机漫游擦拭与露出底图...")
        points = [
            (250, 220), (1030, 240),
            (1000, 380), (280, 390),
            (300, 530), (1020, 520),
            (950, 640), (350, 630)
        ]
        
        page.mouse.move(points[0][0], points[0][1])
        page.mouse.down()
        
        for i in range(len(points) - 1):
            smooth_move(page, points[i][0], points[i][1], points[i+1][0], points[i+1][1], steps=22, delay=0.015)
            if i == 3:
                page.mouse.up()
                time.sleep(0.2)
                wander_screenshot = os.path.join(OUTPUT_DIR, "preview-random-wander.png")
                page.screenshot(path=wander_screenshot)
                print(f"已生成随机漫游交错截图: {wander_screenshot}")
                page.mouse.down()

        # 擦拭中心直至突破 85%
        smooth_move(page, 400, 300, 880, 300, steps=25)
        smooth_move(page, 880, 450, 400, 450, steps=25)
        smooth_move(page, 640, 200, 640, 650, steps=25)
        smooth_move(page, 450, 350, 850, 350, steps=20)
        page.mouse.up()

        print("等待自动平滑完全展开新画...")
        time.sleep(2.5)

        revealed_screenshot = os.path.join(OUTPUT_DIR, "preview-next-revealed.png")
        page.screenshot(path=revealed_screenshot)
        print(f"已生成新画完全展现截图: {revealed_screenshot}")

        time.sleep(1.0)
        page.close()
        context.close()
        video_path = page.video.path()
        browser.close()

    print(f"Playwright 录制完成: {video_path}")
    return video_path

if __name__ == "__main__":
    raw_video = main()
    
    if os.path.exists(raw_video):
        full_mp4 = os.path.join(OUTPUT_DIR, "demo-full-showcase.mp4")
        print(f"正在使用 ffmpeg 生成完整 MP4: {full_mp4}...")
        subprocess.run([
            "ffmpeg", "-y", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium",
            full_mp4
        ], check=True)

        # 1. 沉睡唤醒模式动图与视频 (截取 2.5s 到 10.5s，正是拿破仑皇后加冕唤醒片段！)
        awakening_gif = os.path.join(OUTPUT_DIR, "demo-awakening.gif")
        awakening_mp4 = os.path.join(OUTPUT_DIR, "demo-awakening.mp4")
        print(f"生成《拿破仑皇后加冕》唤醒动图与视频: {awakening_gif} ...")
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:02.5", "-t", "8.0", "-i", raw_video,
            "-vf", "fps=14,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
            awakening_gif
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:02.5", "-t", "8.0", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            awakening_mp4
        ], check=True)

        # 2. 随机漫游模式动图与视频 (截取漫游擦拭片段)
        wander_gif = os.path.join(OUTPUT_DIR, "demo-wander.gif")
        wander_mp4 = os.path.join(OUTPUT_DIR, "demo-wander.mp4")
        print(f"生成随机漫游模式动图与视频: {wander_gif} ...")
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:14.0", "-t", "9.0", "-i", raw_video,
            "-vf", "fps=14,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
            wander_gif
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:14.0", "-t", "9.0", "-i", raw_video,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            wander_mp4
        ], check=True)

        # 清理临时文件与测试图
        shutil.rmtree(TEMP_VIDEO_DIR, ignore_errors=True)
        for f in ["test_napoleon_init.png", "test_napoleon_awakened.png"]:
            p = os.path.join(OUTPUT_DIR, f)
            if os.path.exists(p):
                os.remove(p)

        print("\n✅ 《拿破仑一世及皇后加冕典礼》沉睡唤醒演示物料生成完毕！")
