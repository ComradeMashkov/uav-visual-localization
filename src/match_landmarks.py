import cv2
import torch
import csv
import os
from ultralytics import YOLO
from tqdm import tqdm


def load_landmarks(csv_path: str) -> dict:
    landmarks_by_frame = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame = int(row["frame_id"].split("_")[-1])
            landmark = {
                "landmark_id": row["landmark_id"],
                "class": row["class"],
                "bbox": tuple(map(int, (row["x1"], row["y1"], row["x2"], row["y2"])))
            }
            landmarks_by_frame.setdefault(frame, []).append(landmark)
    print(f"Loaded landmarks for {len(landmarks_by_frame)} frames")
    return landmarks_by_frame


def compute_iou(boxA, boxB) -> float:
    # box: (x1, y1, x2, y2)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0
    return iou


def process_second_video(
    video_path: str,
    save_path: str,
    weights: str,
    landmarks_by_frame: dict,
    device: str = "cpu",
    iou_threshold: float = 0.5
):
    cap = cv2.VideoCapture(video_path)
    model = YOLO(weights).to(device)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(
        save_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    for frame_num in tqdm(range(1, total_frames + 1), desc="Matching landmarks"):
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False, device=device)[0]

        current_landmarks = landmarks_by_frame.get(frame_num, [])
        expected_ids = {lm["landmark_id"] for lm in current_landmarks}
        found_ids = set()

        for box in results.boxes:
            cls_id = int(box.cls)
            cls_name = model.names[cls_id]
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy
            det_bbox = (x1, y1, x2, y2)

            matched = False
            for lm in current_landmarks:
                if lm["landmark_id"] in found_ids:
                    continue
                if lm["class"] == cls_name:
                    iou = compute_iou(lm["bbox"], det_bbox)
                    if iou >= iou_threshold:
                        found_ids.add(lm["landmark_id"])
                        matched = True
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"{cls_name} ({lm['landmark_id']})", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        break
            if not matched:
                pass

        not_found_ids = expected_ids - found_ids
        for nf_id in not_found_ids:
            lm = next(lm for lm in current_landmarks if lm["landmark_id"] == nf_id)
            x1, y1, x2, y2 = lm["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"{lm['class']} ({nf_id})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        total_expected = len(current_landmarks)
        percent_found = len(found_ids) / total_expected * 100 if total_expected else 100
        cv2.putText(frame, f"Found: {percent_found:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Matched Landmarks", frame)
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Second video processed and saved as: {save_path}")


def main():
    landmarks_csv = "../resources/results/found_landmarks.csv"
    second_video = "../videos/winter.avi"
    save_path = "../resources/media/winter_annotated.mp4"
    weights = "../resources/weights/best.pt"

    media_dir = os.path.dirname(save_path)
    os.makedirs(media_dir, exist_ok=True)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    landmarks_by_frame = load_landmarks(landmarks_csv)
    process_second_video(second_video, save_path, weights, landmarks_by_frame, device)


if __name__ == "__main__":
    main()
