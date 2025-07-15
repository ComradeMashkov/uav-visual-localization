import os
import shutil
import random

def split_labeled_data(
    labeled_dir: str,
    output_dir: str,
    val_ratio: float = 0.2,
    seed: int = 42
):
    random.seed(seed)

    images_dir = os.path.join(labeled_dir, 'images')
    labels_dir = os.path.join(labeled_dir, 'labels')

    out_images = os.path.join(output_dir, 'images')
    out_labels = os.path.join(output_dir, 'labels')

    for split in ['train', 'val']:
        os.makedirs(os.path.join(out_images, split), exist_ok=True)
        os.makedirs(os.path.join(out_labels, split), exist_ok=True)

    images = sorted([
        f for f in os.listdir(images_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    ])
    random.shuffle(images)

    valid_images = []
    for img_file in images:
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)
        if os.path.exists(label_path):
            valid_images.append(img_file)

    if not valid_images:
        print("No valid image-label pairs found!")
        return

    val_size = int(len(valid_images) * val_ratio)
    val_files = set(valid_images[:val_size])

    copied = 0
    skipped = len(images) - len(valid_images)

    for img_file in valid_images:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        if img_file in val_files:
            split = 'val'
        else:
            split = 'train'

        shutil.copy2(
            os.path.join(images_dir, img_file),
            os.path.join(out_images, split, img_file)
        )

        shutil.copy2(
            os.path.join(labels_dir, label_file),
            os.path.join(out_labels, split, label_file)
        )

        copied += 1

    print(f"Dataset split into train/val and saved to {output_dir}")
    print(f"Total images: {len(images)}")
    print(f"Used (with labels): {copied}")
    print(f"Skipped (no labels): {skipped}")

if __name__ == "__main__":
    labeled = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/labeled"))
    yolo_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/yolo_dataset"))
    split_labeled_data(labeled, yolo_out)
