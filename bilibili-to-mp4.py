import os
import json
import subprocess
import re
import tempfile

def sanitize_filename(name):
    """去除文件名中的系统非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_clean_m4s(file_path, temp_dir, suffix):
    """
    检查并去除B站特殊的 000000000 文件头。
    """
    with open(file_path, 'rb') as f:
        header = f.read(9)
        if header == b'000000000':
            temp_path = os.path.join(temp_dir, f"clean_{suffix}.m4s")
            with open(temp_path, 'wb') as tf:
                while chunk := f.read(8192 * 1024):
                    tf.write(chunk)
            return temp_path
        else:
            return file_path

def process_single_directory(target_dir, output_root_dir):
    info_path = os.path.join(target_dir, "videoInfo.json")
    
    # 1. 解析 videoInfo.json 获取视频标题和合集名
    title = "未命名视频"
    group_title = ""
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            try:
                info = json.load(f)
                # 获取真实标题
                title = info.get("title", "未命名视频")
                # 获取合集标题
                group_title = info.get("groupTitle", "")
            except json.JSONDecodeError:
                pass
    
    # 确定输出的目录（按 groupTitle 分类）
    current_output_dir = output_root_dir
    if group_title:
        safe_group_title = sanitize_filename(group_title)
        current_output_dir = os.path.join(output_root_dir, safe_group_title)
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)

    safe_title = sanitize_filename(title)
    output_mp4 = os.path.join(current_output_dir, f"{safe_title}.mp4")
    
    # 2. 处理重名问题（如果不同文件夹下有同名视频，自动加序号避免覆盖）
    counter = 1
    while os.path.exists(output_mp4):
        output_mp4 = os.path.join(current_output_dir, f"{safe_title}_{counter}.mp4")
        counter += 1
    
    # 3. 寻找 m4s 音视频流
    m4s_files = [f for f in os.listdir(target_dir) if f.endswith('.m4s') and not f.startswith('clean_')]
    if len(m4s_files) < 2:
        return False
        
    # 区分音视频文件 (按文件大小降序，最大的一般是视频，第二大的是音频)
    m4s_files_with_size = [
        (os.path.join(target_dir, f), os.path.getsize(os.path.join(target_dir, f))) 
        for f in m4s_files
    ]
    m4s_files_with_size.sort(key=lambda x: x[1], reverse=True)
    
    raw_video_file = m4s_files_with_size[0][0]
    raw_audio_file = m4s_files_with_size[1][0]
    
    # 4. 去除头部并调用 FFmpeg 合成
    with tempfile.TemporaryDirectory() as temp_dir:
        video_file = get_clean_m4s(raw_video_file, temp_dir, "video")
        audio_file = get_clean_m4s(raw_audio_file, temp_dir, "audio")
        
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-y', 
            output_mp4
        ]
        
        print(f"🎬 正在合成: {title}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            print(f"❌ 合成失败: {title}，可能是流文件损坏。")
            return False
        except FileNotFoundError:
            print("❌ 未找到 FFmpeg，请检查环境变量配置。")
            return False

def batch_convert(root_directory, output_directory):
    if not os.path.exists(root_directory):
        print(f"❌ 根目录不存在: {root_directory}")
        return
        
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"📁 已创建输出目录: {output_directory}")
        
    print(f"🔍 开始扫描目录: {root_directory}")
    success_count = 0
    
    # 遍历所有子目录
    for item in os.listdir(root_directory):
        item_path = os.path.join(root_directory, item)
        
        # 只处理包含 videoInfo.json 的文件夹
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "videoInfo.json")):
            if process_single_directory(item_path, output_directory):
                success_count += 1
                
    print(f"\n🎉 批量处理完成！共成功合成 {success_count} 个视频。")
    print(f"📂 视频已保存至: {output_directory}")

if __name__ == "__main__":
    # B站视频缓存的根目录
    ROOT_DIR = r"D:\AppData\bilibili-video"
    
    # 转换后 MP4 文件统一存放的目录
    OUTPUT_DIR = r"D:\AppData\bilibili-video\Output"
    
    batch_convert(ROOT_DIR, OUTPUT_DIR)
    