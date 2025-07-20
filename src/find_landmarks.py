import cv2
import torch
import csv
from ultralytics import YOLO
from tqdm import tqdm


def init_model(weights: str, device: str) -> YOLO:
    model = YOLO(weights)
    model.to(device)
    return model


def process_video(
    video_path: str,
    model: YOLO,
    output_csv: str,
    device: str = "cpu"
) -> None:
    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    landmark_count = 0

    with open(output_csv, "w", encoding="utf-8", newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["landmark_id", "class", "frame_id", "x1", "y1", "x2", "y2"])

        for frame_num in tqdm(range(1, total_frames + 1), desc="Processing frames"):
            ret, frame = cap.read()
            if not ret:
                break

            frame_tag = f"frame_{frame_num:03d}"

            results = model(frame, verbose=False, device=device)[0]

            for box in results.boxes:
                cls_id = int(box.cls)
                cls_name = model.names[cls_id]
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = xyxy

                landmark_count += 1
                landmark_tag = f"landmark_{landmark_count:03d}"

                writer.writerow([landmark_tag, cls_name, frame_tag, x1, y1, x2, y2])

    cap.release()

    print(f"Processed frames: {frame_num}")
    print(f"Landmarks found: {landmark_count}")
    print(f"Results written to: {output_csv}")


def main():
    video_path = "../videos/summer.avi"
    weights = "../resources/weights/best.pt"
    output_csv = "../resources/results/found_landmarks.csv"

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    model = init_model(weights, device)
    process_video(video_path, model, output_csv, device)


if __name__ == "__main__":
    main()
