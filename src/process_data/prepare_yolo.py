from .split_dataset import split_labeled_data
import os

def prepare():
    labeled = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/labeled"))
    yolo_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/yolo_dataset"))

    split_labeled_data(labeled, yolo_out)