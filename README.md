# Bilibili 视频缓存批量转换工具

这是一个用于将 Bilibili PC 端下载的缓存视频（`.m4s` 格式）批量无损转换为标准 `.mp4` 格式的 Python 脚本。

## ✨ 主要功能

1. **自动提取真实标题**：解析 B 站缓存目录下的 `videoInfo.json`，使用视频的真实名称来命名生成的 MP4 文件，告别乱码文件名。
2. **按合集自动分类**：读取 `groupTitle` 字段，自动为属于同一系列/课程的视频创建专属子文件夹，整理井井有条。
3. **无损极速转换**：调用 FFmpeg 的 `copy` 指令进行音视频流合并，不进行二次压制，转换速度极快且画质无损。
4. **智能去除混淆头**：自动检测并去除 B 站缓存文件特有的 `000000000` 混淆字节，解决 FFmpeg 无法直接读取的问题。
5. **防重名保护**：如果同名视频已存在，会自动添加后缀（如 `_1`, `_2`）避免覆盖原有文件。

## 🛠️ 环境依赖

在运行本脚本之前，请确保你的系统已安装以下环境：

1. **Python 3.x**：系统需安装 Python 运行环境。
2. **FFmpeg**：
   - 本脚本依赖 FFmpeg 进行音视频合成。
   - 请前往 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载。
   - **重要**：下载解压后，必须将 FFmpeg 的 `bin` 目录（包含 `ffmpeg.exe` 的文件夹）添加到 Windows 系统的**环境变量 (Path)** 中。

## 🚀 使用说明

### 1. 配置路径
使用文本编辑器或 IDE 打开脚本文件 [bilibili-to-mp4.py](file:///d:/workspaces/codes/vivid_admin/bilibili-to-mp4.py#L128-L131)，找到代码最下方的路径配置区域：

```python
if __name__ == "__main__":
    # B站视频缓存的根目录 (请修改为你电脑上实际的 B 站下载目录)
    ROOT_DIR = r"D:\AppData\bilibili-video"
    
    # 转换后 MP4 文件统一存放的目录 (可以根据需要修改)
    OUTPUT_DIR = r"D:\AppData\bilibili-video\Output"
    
    batch_convert(ROOT_DIR, OUTPUT_DIR)
```

### 2. 运行脚本
打开命令行（CMD 或 PowerShell），进入脚本所在目录，执行以下命令：

```bash
python bilibili-to-mp4.py
```

### 3. 查看输出结果
脚本运行过程中，会在控制台输出当前正在合成的视频标题和状态。
转换完成后，你可以前往你配置的 `OUTPUT_DIR` 目录查看。

**输出目录结构示例：**
```text
Output/
├── 视频/        <-- 根据 groupTitle 自动生成的分类文件夹
│   ├── 独立视频A.mp4
│   ├── 独立视频B.mp4
├── 独立视频A.mp4                         <-- 没有 groupTitle 的视频直接放在根目录
└── 独立视频B.mp4
```

## ⚠️ 常见问题

- **报错 `❌ 未找到 FFmpeg，请检查环境变量配置。`**
  说明系统找不到 FFmpeg。请检查 FFmpeg 是否已正确下载，并且其 `bin` 目录路径是否已经添加到了系统的“环境变量 -> Path”中。添加后可能需要重启终端/命令行窗口使其生效。
- **报错 `❌ 合成失败: xxx，可能是流文件损坏。`**
  可能是因为视频尚未在 B 站客户端下载完成就被中断，导致 `.m4s` 文件不完整。请在 B 站客户端中重新下载该视频后再试。
