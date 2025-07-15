import os
import cv2
import numpy as np

def save_rgb_image(image_data, index, output_dir):
    if image_data is None:
        print(f"[!] No image at {index}")
        return
    
    img_array = np.frombuffer(image_data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"img_{index:05d}.png")
    cv2.imwrite(path, img)
    print(f"Saved {path}")