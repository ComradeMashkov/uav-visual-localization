import torch

def check_cuda():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is not available! Check PyTorch, NVIDIA drivers and GPU availability"
        )

    gpu_name = torch.cuda.get_device_name(0)
    print(f"CUDA is ready. Using GPU: {gpu_name}")
