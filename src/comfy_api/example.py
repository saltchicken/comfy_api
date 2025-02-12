from comfy_api import ComfyClient

comfy = ComfyClient("10.0.0.3:8188")
comfy.length = 72
comfy.prompt = "A sample prompt"
comfy.boomerang = True

def generator(initial, end, increment):
    value = initial
    while True:
        if value > end: value = initial
        if value < initial: value = end
        yield round(value, 2)
        value = round(value + increment, 2)

x_gen = generator(0.0, 1.0, 0.01)

for i in range(100):
    print(x_gen.__next__())

# c mfy.view_video(videos)
