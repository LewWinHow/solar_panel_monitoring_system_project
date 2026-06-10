import os
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime

# ✅ 配置模型路径和结果保存目录（修改为你自己的 best.pt 路径）
MODEL_PATH = r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\ai_model\detect_solar_panel_model\best.pt"
SAVE_DIR = r"C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\media\detect_solar_panel_result"  # 检测结果图片保存目录

# ✅ 创建保存目录（如果不存在）
os.makedirs(SAVE_DIR, exist_ok=True)

# ✅ 加载 YOLO 模型（只加载一次）
model = YOLO(MODEL_PATH)
print("📦 模型已加载，支持类别:", model.names)

def detect_solar_panel_with_image(image_file, device: str = "cuda"):
    """
    参数:
        image_file: InMemoryUploadedFile 或文件路径
    """
    if hasattr(image_file, 'read'):  # 是上传的内存文件
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    elif isinstance(image_file, str):  # 是路径字符串
        img = cv2.imread(image_file)
    else:
        print("❌ 无法识别图片来源")
        return None

    if img is None:
        print("❌ 图片解码失败")
        return None

    # 之后一样
    results = model.predict(source=img, conf=0.25, device=device, verbose=False)

    if results and len(results[0].boxes) > 0:
        boxes = results[0].boxes
        detections = []

        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i])
            conf = float(boxes.conf[i])
            class_name = results[0].names[cls_id]
            detections.append({
                'class': class_name,
                'confidence': conf
            })

        # 保存图片
        annotated_img = results[0].plot()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"result_{timestamp}.jpg"
        result_path = os.path.join(SAVE_DIR, result_filename)
        cv2.imwrite(result_path, annotated_img)

        return {
            'detections': detections,
            'result_path': result_path
        }

    else:
        print("⚠️ 未检测到目标！")
        return None



# ✅ 示例调用（用于单独运行测试）
if __name__ == "__main__":
    test_image = r"C:\Users\xiaoh\Downloads\low-angle-view-and-close-up-of-dusty-solar-panel-photo.jpg"
    result = detect_solar_panel_with_image(test_image, device="cuda")  # 使用 GPU

    if result:
        print("\n🎉 检测完成！结果信息：")
        for det in result['detections']:
            print(f"📌 标签: {det['class']} - 置信度: {det['confidence']:.2f}")
        print("🖼️ 结果图片路径:", result['result_path'])
