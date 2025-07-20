import airsim

config = {
    "area": {
        "xmin": -100,
        "xmax": 100,
        "ymin": -100,
        "ymax": 100,
        "z": -30,
        "step": 1
    },
    "camera_name": "0",
    "image_type": airsim.ImageType.Scene,
    "output_dir": "./videos"
}