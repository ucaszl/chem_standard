import torch
print("torch:", torch.__version__)
print("torch.cuda.is_available():", torch.cuda.is_available())
print("torch.version.cuda:", torch.version.cuda)
print("cuda device count:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("device 0 name:", torch.cuda.get_device_name(0))
    a = torch.randn(512, 512, device="cuda")
    b = torch.randn(512, 512, device="cuda")
    c = a @ b
    print("matrix multiply on cuda OK, c[0,0] =", float(c[0,0].cpu()))
else:
    print("CUDA not available. Please check nvidia-smi and driver.")
