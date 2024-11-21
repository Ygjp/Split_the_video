import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox
from threading import Thread
# 定义分割时长为 2:59:00 (10740 秒)
SEGMENT_TIME = 10740  # 秒
def get_video_duration(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return int(float(result.stdout.strip()))
    except Exception as e:
        return 0
def split_video(file_path, output_box):
    file_name, file_ext = os.path.splitext(file_path)
    duration = get_video_duration(file_path)
    if duration == 0:
        output_box.insert(tk.END, f"警告: 无法获取 {os.path.basename(file_path)} 的时长，跳过...\n")
        output_box.see(tk.END)
        return
    if duration <= SEGMENT_TIME:
        output_box.insert(tk.END, f"{os.path.basename(file_path)} 时长小于 2:59:00，无需分割。\n")
        output_box.see(tk.END)
        return
    output_box.insert(tk.END, f"{os.path.basename(file_path)} 时长为 {duration} 秒，开始分割...\n")
    output_box.see(tk.END)
    output_template = f"{file_name}_part%03d{file_ext}"
    command = [
        "ffmpeg", "-i", file_path,
        "-c:v", "copy", "-c:a", "copy",
        "-f", "segment", "-segment_time", str(SEGMENT_TIME),
        "-reset_timestamps", "1", output_template
    ]
    try:
        subprocess.run(command, check=True)
        output_box.insert(tk.END, f"{os.path.basename(file_path)} 分割完成！\n")
        output_box.see(tk.END)
        os.remove(file_path)
        output_box.insert(tk.END, f"原视频 {os.path.basename(file_path)} 已删除。\n")
        output_box.see(tk.END)

    except subprocess.CalledProcessError as e:
        output_box.insert(tk.END, f"错误: 分割 {os.path.basename(file_path)} 失败。\n")
        output_box.see(tk.END)
    except Exception as e:
        output_box.insert(tk.END, f"错误: 无法删除原视频 {os.path.basename(file_path)}。\n")
        output_box.see(tk.END)
def process_videos(output_box, process_button):
    def task():
        current_dir = os.getcwd()
        files = [f for f in os.listdir(current_dir) if f.endswith(".mp4")]
        if not files:
            output_box.insert(tk.END, "提示: 当前文件夹中没有找到 .mp4 文件。\n")
            output_box.see(tk.END)
            process_button.config(state=tk.NORMAL)
            return
        total_files = len(files)
        output_box.insert(tk.END, f"开始分割任务，共找到 {total_files} 个视频文件。\n")
        output_box.see(tk.END)
        for index, file in enumerate(files, 1):
            output_box.insert(tk.END, f"正在处理文件 {index}/{total_files}: {file}...\n")
            output_box.see(tk.END)
            full_path = os.path.join(current_dir, file)
            split_video(full_path, output_box)
        output_box.insert(tk.END, "\n所有视频处理完成！\n")
        output_box.see(tk.END)
        process_button.config(state=tk.NORMAL)
    process_button.config(state=tk.DISABLED)
    thread = Thread(target=task)
    thread.start()
def create_gui():
    root = tk.Tk()
    root.title("视频分割工具")
    root.geometry("600x400")
    label = tk.Label(root, text="自动分割当前目录中大于 2:59:00 的 MP4 视频", font=("Arial", 14))
    label.pack(pady=10)
    output_box = scrolledtext.ScrolledText(root, width=70, height=15, font=("Arial", 10))
    output_box.pack(pady=10)
    process_button = tk.Button(
        root, text="开始处理", font=("Arial", 12),
        command=lambda: process_videos(output_box, process_button)
    )
    process_button.pack(pady=10)
    exit_button = tk.Button(root, text="退出", font=("Arial", 12), command=root.quit)
    exit_button.pack(pady=10)
    root.mainloop()
if __name__ == "__main__":
    create_gui()
