import random
import numpy as np
from comfy_api import ComfyClient

comfy = ComfyClient("10.0.0.3:8188")
comfy.length = 72
comfy.prompt = "A fractal"
comfy.boomerang = False

def generator(initial, end, increment):
    value = initial
    while True:
        if value > end: value = initial
        if value < initial: value = end
        yield round(value, 2)
        value = round(value + increment, 2)

# x_gen = generator(0.0, 1.0, 0.01)
# y_gen = generator(0.8, 1.0, 0.01)
# z_gen = generator(0.4, 1.0, -0.02)

gens = [generator(0.0, 1.0, 0.01), generator(0.8, 1.0, 0.01), generator(0.4, 1.0, -0.02)]

num_loras = 3
loras = comfy.get_loras("persons")
try:
    while True:
        total = 1.5
        strengths = np.round(np.random.dirichlet([1] * num_loras) * total, 2)
        selected_loras = random.sample(loras, num_loras)
        comfy.lora = []
        for i in range(num_loras):
            comfy.lora.append(f"{selected_loras[i]}={strengths[i]}")
        videos = comfy.run_workflow()
except KeyboardInterrupt:
    print("\nLoop terminated by user.")

# comfy.view_video(videos)
#
