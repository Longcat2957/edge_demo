import os
import cv2
import torch
import time
import numpy as np
from PIL import Image
from torchvision import transforms as T
from libs.model import edgeSR
from libs.qt import get_q_model, qat_wrapper, qat_q_convert

def get_jit_model(weight_path:str):
    try:
        net = torch.jit.load(weight_path)
    except:
        raise RuntimeError(f"weight_path({weight_path}) is wrong")
    return net


torch.backends.quantized.engine = "qnnpack"
QAT_WEIGHT_PATH = "./weights/qat_180.pth"
q_model = get_q_model(QAT_WEIGHT_PATH)
net = torch.jit.script(q_model)
torch.jit.save(net, "edgeSR_int8_rasp_jit.pth")
net = get_jit_model("edgeSR_int8_rasp_jit.pth")

preprocess = T.Compose([
    T.CenterCrop(size=(240, 426)),
    T.ToTensor()
])
postprocess = T.Compose([
    T.ToPILImage()
])

with torch.no_grad():
    img = Image.open("input.jpeg")
    started = time.time()
    permuted = preprocess(img).unsqueeze(0)
    pred = net(permuted)
    time_elapsed = time.time() - started
    output = postprocess(pred.squeeze(0))

print(f"# BENCHMARK (SINGLE IMG) [{time_elapsed * 1000:.3f}ms]")

# SHOW IMG
output.save("output.jpg", "JPEG")