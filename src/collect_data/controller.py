import airsim
import time
from logging import Logger
from .saver import save_rgb_image
from .utils import print_state, print_sensors


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


def collect_dataset(config, logger: Logger):
    client = airsim.MultirotorClient()
    client.confirmConnection()

    route = generate_grid(config["area"])

    logger.info("Starting data collection in ComputerVision mode...")
    logger.info(f"Total waypoints: {len(route)}")

    for i, (x, y, z) in enumerate(route):
        logger.info(f"Teleporting to {x}, {y}, {z}")
        pose = airsim.Pose()
        pose.position.x_val = x
        pose.position.y_val = y
        pose.position.z_val = z
        client.simSetVehiclePose(pose, True)
        time.sleep(0.1)

        logger.info(f"Capturing image at waypoint {i}")
        response = client.simGetImage(config["camera_name"], config["image_type"])
        save_rgb_image(response, i, config["output_dir"])

    logger.info("Done.")
