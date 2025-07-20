import os
import time
import cv2
import airsim
import numpy as np
from logging import Logger


def generate_grid(area: dict) -> list[tuple[float, float, float]]:
    xmin, xmax = area["xmin"], area["xmax"]
    ymin, ymax = area["ymin"], area["ymax"]
    z = area["z"]
    step = area["step"]

    route = []
    ys = list(range(int(ymin), int(ymax) + 1, step))
    xs = list(range(int(xmin), int(xmax) + 1, step))

    reverse = False
    for y in ys:
        row = [(x, y, z) for x in xs]
        if reverse:
            row.reverse()
        route.extend(row)
        reverse = not reverse
    return route


def record_video(config: dict, season: str, logger: Logger):
    client = airsim.MultirotorClient()
    client.confirmConnection()

    route = generate_grid(config["area"])

    output_dir = config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"{season}.avi")

    logger.info("Starting video recording in ComputerVision mode...")
    logger.info(f"Total waypoints: {len(route)}")

    # делаем первый кадр чтобы определить разрешение
    logger.info("Fetching initial frame to determine resolution...")
    response = client.simGetImage(config["camera_name"], config["image_type"])
    if response is None:
        raise RuntimeError("Failed to get initial image from camera.")
    
    img_arr = airsim.string_to_uint8_array(response)
    img_rgb = cv2.imdecode(np.frombuffer(response, np.uint8), cv2.IMREAD_COLOR)

    if img_rgb is None:
        logger.error("Failed to decode initial image.")
        return

    h, w, _ = img_rgb.shape
    logger.info(f"Detected frame resolution: {w}x{h}")

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 30
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, (w, h))

    for i, (x, y, z) in enumerate(route):
        logger.info(f"Waypoint {i+1}/{len(route)}: Teleporting to {x}, {y}, {z}")
        pose = airsim.Pose()
        pose.position.x_val = x
        pose.position.y_val = y
        pose.position.z_val = z
        client.simSetVehiclePose(pose, True)
        time.sleep(0.05)

        response = client.simGetImage(config["camera_name"], config["image_type"])
        if response is None:
            logger.warning(f"No image at waypoint {i}")
            continue

        img_arr = airsim.string_to_uint8_array(response)
        img_rgb = cv2.imdecode(np.frombuffer(response, np.uint8), cv2.IMREAD_COLOR)

        if img_rgb is None:
            logger.warning(f"Failed to decode image at waypoint {i}")
            continue

        video_writer.write(img_rgb)

    video_writer.release()
    logger.info(f"Video saved to {video_path}")
    logger.info("Done.")
