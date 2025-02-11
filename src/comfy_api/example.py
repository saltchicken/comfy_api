from comfy_api import ComfyClient

comfy = ComfyClient("10.0.0.3:8188")
comfy.lora = ["fractalanimationfrost=1.0"]
comfy.length = 10
comfy.prompt = "fractal"
videos = comfy.run_workflow()

comfy.view_video(videos)
