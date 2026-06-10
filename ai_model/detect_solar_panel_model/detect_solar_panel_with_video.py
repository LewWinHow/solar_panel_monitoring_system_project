# # yolo_tracking.py
# from ultralytics import YOLO
# import torch
# import collections
# import cv2
# import os
# from datetime import datetime
# import tempfile
#
# def detect_solar_panel_with_video(
#     video_file,  # ✅ 改为接收文件对象（如 request.FILES['video']）
#     model_path=r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\ai_model\detect_solar_panel_model\best.pt",
#     class_names=['bird_drop', 'clean', 'damage', 'dusty'],
#     output_dir=r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\media\detect_solar_panel_result"
# ):
#     """
#     使用 YOLOv8 + ByteTrack 对视频目标进行检测与追踪，并保存带框视频。
#
#     参数：
#         video_file (InMemoryUploadedFile): Django上传的视频文件对象
#         model_path (str): 训练好的 YOLO 权重文件路径（.pt）
#         class_names (list[str]): 类别名称列表（与 data.yaml 顺序一致）
#         output_dir (str): 输出视频保存目录
#
#     返回：
#         dict: 每类目标累计出现次数（不重复 ID），以及视频输出路径
#     """
#
#     # 将上传文件写入临时文件
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
#         for chunk in video_file.chunks():
#             tmp.write(chunk)
#         temp_video_path = tmp.name
#
#     # 检查 GPU / CPU
#     device = 'cuda' if torch.cuda.is_available() else 'cpu'
#     print("✅ 使用设备:", device)
#
#     # 加载模型
#     model = YOLO(model_path)
#
#     # 视频读取
#     cap = cv2.VideoCapture(temp_video_path)
#     if not cap.isOpened():
#         raise FileNotFoundError(f"❌ 无法打开视频文件: {temp_video_path}")
#
#     # 视频属性
#     fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
#     width = 1280
#     height = 720
#
#     # 输出路径
#     os.makedirs(output_dir, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"detected_{timestamp}.mp4"
#     output_path = os.path.join(output_dir, filename)
#
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
#
#     print(f"📹 输出视频将保存为：{output_path}")
#
#     cumulative_counter = collections.Counter()
#     seen_ids = set()
#
#     results = model.track(
#         source=temp_video_path,
#         show=False,
#         stream=True,
#         tracker="bytetrack.yaml",
#         device=0 if device == 'cuda' else 'cpu',
#         verbose=False
#     )
#
#     for result in results:
#         frame = result.orig_img.copy()
#
#         if result.boxes is not None:
#             for box in result.boxes:
#                 cls_id = int(box.cls[0])
#                 name = class_names[cls_id]
#                 obj_id = int(box.id[0]) if box.id is not None else None
#
#                 if obj_id is not None and obj_id not in seen_ids:
#                     cumulative_counter[name] += 1
#                     seen_ids.add(obj_id)
#
#                 xyxy = box.xyxy[0].cpu().numpy().astype(int)
#                 conf = float(box.conf[0])
#                 label = f"{name} {conf:.2f}"
#                 cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
#                 cv2.putText(frame, label, (xyxy[0], xyxy[1] - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#
#         y = 30
#         for name in class_names:
#             count = cumulative_counter.get(name, 0)
#             cv2.putText(frame, f"{name} total: {count}", (10, y),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
#             y += 30
#
#         frame = cv2.resize(frame, (width, height))
#         out_writer.write(frame)
#
#     cap.release()
#     out_writer.release()
#     os.remove(temp_video_path)  # ✅ 清理临时文件
#
#     print("✅ 视频处理完成！")
#     print("📊 检测统计结果：")
#     for name in class_names:
#         print(f"  - {name}: {cumulative_counter.get(name, 0)}")
#
#     return {
#         "counts": dict(cumulative_counter),
#         "video_path": output_path.replace("\\", "/")
#     }
# yolo_tracking.py
from ultralytics import YOLO
import torch
import collections
import cv2
import os
from datetime import datetime
import tempfile
import subprocess
from pathlib import Path
from django.conf import settings
# from django.utils.http import urlquote


def detect_solar_panel_with_video(
    video_file,  # e.g. request.FILES['video']
    model_path=r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\ai_model\detect_solar_panel_model\best.pt",
    class_names=['bird_drop', 'clean', 'damage', 'dusty'],
    output_dir=r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\media\detect_solar_panel_result"
):
    """
    使用 YOLOv8 + ByteTrack 对视频目标进行检测与追踪，并保存带框视频。
    自动转码为浏览器兼容格式。
    返回 Django 模板可用的 video_url。
    """

    # 保存上传文件到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        for chunk in video_file.chunks():
            tmp.write(chunk)
        temp_video_path = tmp.name

    # 设备检测
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("✅ 使用设备:", device)

    # 加载模型
    model = YOLO(model_path)

    # 视频读取
    cap = cv2.VideoCapture(temp_video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"❌ 无法打开视频文件: {temp_video_path}")

    # 视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    width = 1280
    height = 720

    # 输出路径
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_filename = f"detected_{timestamp}_raw.mp4"
    raw_path = os.path.join(output_dir, raw_filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))
    print(f"📹 原始输出视频：{raw_path}")

    cumulative_counter = collections.Counter()
    seen_ids = set()

    results = model.track(
        source=temp_video_path,
        show=False,
        stream=True,
        tracker="bytetrack.yaml",
        device=0 if device == 'cuda' else 'cpu',
        verbose=False
    )

    for result in results:
        frame = result.orig_img.copy()

        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                name = class_names[cls_id]
                obj_id = int(box.id[0]) if box.id is not None else None

                if obj_id is not None and obj_id not in seen_ids:
                    cumulative_counter[name] += 1
                    seen_ids.add(obj_id)

                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                label = f"{name} {conf:.2f}"
                cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 5)
                cv2.putText(frame, label, (xyxy[0], xyxy[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)

        y = 120
        for name in class_names:
            count = cumulative_counter.get(name, 0)
            cv2.putText(frame, f"{name} total: {count}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 0), 5)
            y += 120

        frame = cv2.resize(frame, (width, height))
        out_writer.write(frame)

    cap.release()
    out_writer.release()
    os.remove(temp_video_path)

    # 转码为 H.264 + AAC
    final_filename = f"detected_{timestamp}.mp4"
    final_path = os.path.join(output_dir, final_filename)
    ffmpeg_path = r"C:\Users\xiaoh\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"  # ⚠️ 改成你自己解压后实际路径
    subprocess.run([
        ffmpeg_path, "-y",
        "-i", raw_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        final_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(raw_path)  # 清除原始未压缩视频

    print("✅ 视频转码完成！")
    print("📊 检测统计结果：")
    for name in class_names:
        print(f"  - {name}: {cumulative_counter.get(name, 0)}")

    # 构造 Django 可访问的 URL（相对 MEDIA_ROOT）
    relative_path = Path(final_path).relative_to(settings.MEDIA_ROOT)

    return {
        "counts": dict(cumulative_counter),
        "video_path": final_path.replace("\\", "/"),  # 本地完整路径
    }