#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random
import cv2
import io
import numpy as np
import tempfile
import time
import platform
import sys
from pathlib import Path

script_dir = Path(__file__).parent
# print(f"{script_dir=}")

def print_keys(d):
    for key, value in d.items():
        print(f"Key: {key}")
        print(value['_meta']['title'])
        # print(f"Value: {value}")

class ComfyClient:
    def __init__(self, server_address, **kwargs):
        self.client_id = str(uuid.uuid4())
        self.server_address = server_address
        self.workflow = None
        self.running = False
        self.lora = kwargs["lora"] if "lora" in kwargs else []
        self.seed = kwargs["seed"] if "seed" in kwargs else None
        self.length = kwargs["length"] if "length" in kwargs else None
        self.boomerang = kwargs["boomerang"] if "boomerang" in kwargs else None
        self.prompt = kwargs["prompt"] if "prompt" in kwargs else None
        self.resolution = kwargs["resolution"] if "resolution" in kwargs else None
        self.steps = kwargs["steps"] if "steps" in kwargs else None
        self.sampler = kwargs["sampler"] if "sampler" in kwargs else None
        self.scheduler = kwargs["scheduler"] if "scheduler" in kwargs else None
        self.guidance = kwargs["guidance"] if "guidance" in kwargs else None

    def get_loras(self, folder=None):
        req = urllib.request.Request("http://{}/models/loras".format(self.server_address))
        lora_list = json.loads(urllib.request.urlopen(req).read())
        loras = [l.removesuffix(".safetensors") for l in lora_list]
        if folder:
            loras = [l for l in loras if l.startswith(folder)]
        return loras

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    # def get_image(filename, subfolder, folder_type):
    #     data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    #     url_values = urllib.parse.urlencode(data)
    #     with urllib.request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
    #         return response.read()

    def get_video(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        # "http://{}/view?{}".format(server_address, url_values)
        url_request = "http://{}/view?{}".format(self.server_address, url_values)
        print(url_request)
        with urllib.request.urlopen(url_request) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    # def get_images(self, ws, prompt):
    #     prompt_id = self.queue_prompt(prompt)['prompt_id']
    #     output_images = {}
    #     while True:
    #         out = ws.recv()
    #         if isinstance(out, str):
    #             message = json.loads(out)
    #             if message['type'] == 'executing':
    #                 data = message['data']
    #                 if data['node'] is None and data['prompt_id'] == prompt_id:
    #                     break #Execution is done
    #         else:
    #             # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
    #             # bytesIO = BytesIO(out[8:])
    #             # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
    #             continue #previews are binary data
    #
    #     history = self.get_history(prompt_id)[prompt_id]
    #     for node_id in history['outputs']:
    #         node_output = history['outputs'][node_id]
    #         print(node_output)
    #         images_output = []
    #         if 'images' in node_output:
    #             for image in node_output['images']:
    #                 image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
    #                 images_output.append(image_data)
    #         output_images[node_id] = images_output
    #
    #     return output_images

    def get_videos(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_videos = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            # print(node_output)
            videos_output = []
            if 'gifs' in node_output:
                for video in node_output['gifs']:
                    print(f"{video['fullpath']=}")
                    video_data = self.get_video(video['filename'], video['subfolder'], video['type'])
                    videos_output.append(video_data)
            output_videos[node_id] = videos_output

        return output_videos

    def get_videos_filename(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_videos = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            # print(node_output)
            videos_output = []
            if 'gifs' in node_output:
                for video in node_output['gifs']:
                    return video['filename']

    def view_video(self, videos):
        for node_id in videos:
            for video_data in videos[node_id]:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                    temp_video.write(video_data)
                    temp_filename = temp_video.name  # Get the file path

                    cv2.namedWindow("Video", cv2.WINDOW_NORMAL)

                    if platform.system() == "Linux":
                        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                    cap = cv2.VideoCapture(temp_filename)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cv2.resizeWindow("Video", width, height)

                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_time = 1 / fps if fps > 0 else 1 / 30  # Default to 30 FPS if unknown

                    self.running = True
                    while self.running:  # Infinite loop for replaying video
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start

                        while cap.isOpened():
                            start_time = time.time()  # Track frame start time

                            ret, frame = cap.read()
                            if not ret:
                                break  # Video ended, restart from the beginning

                            cv2.imshow("Video", frame)

                            # Wait to maintain FPS
                            elapsed_time = time.time() - start_time
                            delay = max(1, int((frame_time - elapsed_time) * 1000))  # Convert to ms
                            key = cv2.waitKey(delay)
                            if key == ord('q'):  # Press 'q' to exit
                                self.running = False
                                break
                            elif key == ord('f'):
                                if platform.system() == "Linux":
                                    pass
                                else:
                                    fullscreen_status = cv2.getWindowProperty("Video", cv2.WND_PROP_FULLSCREEN)
                                    if fullscreen_status == cv2.WINDOW_FULLSCREEN:
                                        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                                    else:
                                        x, y, width, height = cv2.getWindowImageRect("Video")
                                        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                                        cv2.moveWindow("Video", x, y)
                                        cv2.resizeWindow("Video", (width, height))

                    cap.release()
                    cv2.destroyAllWindows()

    # def view_images(self, images):
    #     for node_id in images:
    #         for image_data in images[node_id]:
    #             from PIL import Image
    #             import io
    #             image = Image.open(io.BytesIO(image_data))
    #             image.show()


    def set_seed(self, seed):
        for key, value in self.workflow.items():
            if value['class_type'] == 'RandomNoise':
                self.workflow[key]['inputs']['noise_seed'] = seed
                print(f"Seed: {seed}")

    def set_length(self, length):
        for key, value in self.workflow.items():
            if value['class_type'] == 'EmptyHunyuanLatentVideo':
                self.workflow[key]['inputs']['length'] = length
                print(f"Length: {length}")

    def set_boomerang(self, boomerang=True):
        for key, value in self.workflow.items():
            if value['class_type'] == 'VHS_VideoCombine':
                self.workflow[key]['inputs']['pingpong'] = boomerang
                print(f"Boomerang: {boomerang}")

    def set_prompt(self, prompt):
        for key, value in self.workflow.items():
            if value['class_type'] == 'CLIPTextEncode':
                self.workflow[key]['inputs']['text'] = prompt
                print(f"Prompt: {prompt}")

    def set_resolution(self, resolution):
        for key, value in self.workflow.items():
            if value['class_type'] == 'EmptyHunyuanLatentVideo':
                resolution = resolution.split("x")
                if len(resolution) != 2:
                    print("Bad resolution format. Staying to default")
                    return
                self.workflow[key]['inputs']['width'] = resolution[0]
                self.workflow[key]['inputs']['height'] = resolution[1]
                print(f"Resolution: {resolution[0]}x{resolution[1]}")

    def set_lora_strength(self, lora_key, lora, lora_strength):
        for key, value in self.workflow.items():
            if key == lora_key:
                self.workflow[key]['inputs']['lora_name'] = lora + ".safetensors"
                self.workflow[key]['inputs']['strength_model'] = lora_strength
                print(f"Setting strength for {lora} to {lora_strength}")

    def set_steps(self, steps):
        for key, value in self.workflow.items():
            if value['class_type'] == 'BasicScheduler':
                self.workflow[key]['inputs']['steps'] = steps
                print(f"Steps: {steps}")

    def set_sampler(self, sampler):
        for key, value in self.workflow.items():
            if value['class_type'] == 'KSamplerSelect':
                self.workflow[key]['inputs']['sampler_name'] = sampler
                print(f"Sampler: {sampler}")

    def set_scheduler(self, scheduler):
        for key, value in self.workflow.items():
            if value['class_type'] == 'BasicScheduler':
                self.workflow[key]['inputs']['scheduler'] = scheduler
                print(f"Scheduler: {scheduler}")

    def set_guidance(self, guidance):
        for key, value in self.workflow.items():
            if value['class_type'] == 'FluxGuidance':
                self.workflow[key]['inputs']['guidance'] = guidance
                print(f"Guidance: {guidance}")

    # def get_lora_strength(self, workflow, lora):
    #     for key, value in workflow.items():
    #         if value['class_type'] == 'LoraLoaderModelOnly':
    #             if workflow[key]['inputs']['lora_name'].split(".")[0] == lora:
    #                 return workflow[key]['inputs']['strength_model']

    def get_lora_nodes(self):
        lora_nodes = []
        for key, value in self.workflow.items():
            if value['class_type'] == 'LoraLoaderModelOnly':
                lora_nodes.append(key)
        return lora_nodes

    def set_workflow(self):
        if len(self.lora) > 0:
            if len(self.lora) == 1:
                workflow_file = f"{script_dir}/templates/SingleLoraHunyuan.json"
            elif len(self.lora) == 2:
                workflow_file = f"{script_dir}/templates/DoubleLoraHunyuan.json"
            elif len(self.lora) == 3:
                workflow_file = f"{script_dir}/templates/TripleLoraHunyuan.json"
            elif len(self.lora) == 4:
                workflow_file = f"{script_dir}/templates/FourLoraHunyuan.json"
            else:
                print("Too many Loras. Exiting")
            with open(workflow_file, "r") as f:
                try:
                    self.workflow = json.load(f)
                except:
                    print("Could not open file {}".format(workflow_file))
                    exit(1)

            lora_nodes = self.get_lora_nodes()
            # print(f"{lora_nodes=}")
            if len(lora_nodes) != len(self.lora):
                print("Lora parameter mismatched. Exiting")
                sys.exit(1)
            for l in self.lora:
                l = l.split("=")
                if len(l) != 2:
                    print("Lora parameter incorrect. Exiting")
                    sys.exit(1)
                if 'trirandom' in l[1]:
                    print(f"Setting triangular random lora strength for {l[0]}")
                    trirandom_split = l[1].split(":")
                    if len(trirandom_split) == 2:
                        random_strength = random.triangular(0.0, 1.3, float(trirandom_split[1]))
                    elif len(trirandom_split) == 1:
                        random_strength = random.triangular(0.0, 1.3, 0.85)
                    else:
                        print(f"Malformed lora {l}")
                        exit(1)
                    # current_lora_strength = self.get_lora_strength(workflow, l[0])
                    random_strength = random.triangular(0.0, 1.3, 0.85)
                    self.set_lora_strength(lora_nodes.pop(), l[0], round(random_strength, 2))
                elif l[1] == 'random':
                    print(f"Setting random lora strength for {l[0]}")
                    self.set_lora_strength(lora_nodes.pop(), l[0], round(random.uniform(0.0, 1.5), 2))
                elif float(l[1]) < 2.0 or float(l[1]) > 0.0:
                    self.set_lora_strength(lora_nodes.pop(), l[0], l[1])
                else:
                    print("Lora strength out of range. Staying to default")
                    continue
        else:
            workflow_file = f"{script_dir}/templates/BasicHunyuan.json"

            with open(workflow_file, "r") as f:
                try:
                    self.workflow = json.load(f)
                except:
                    print("Could not open file {}".format(workflow_file))
                    exit(1)

        if self.seed:
            self.set_seed(self.seed)
        else:
            self.set_seed(random.randint(10**14, 10**15 -1))

        if self.length:
            self.set_length(self.length)

        if self.boomerang:
            self.set_boomerang(self.boomerang)

        if self.prompt:
            self.set_prompt(self.prompt)

        if self.resolution:
            if self.resolution == "random":
                resolutions = ["640x480", "480x640", "512x512"]
                self.set_resolution(random.choice(resolutions))
            else:
                self.set_resolution(self.resolution)

        if self.steps:
            if self.steps == 'trirandom' or self.steps == 'random':
                self.set_steps(random.triangular(6, 40, 20))
            else:
                self.set_steps(self.steps)

        if self.sampler:
            samplers = ['euler', # 20 Better, 10 Good, 8 decent
                        # 'euler_cfg_pp',  # Trash at 20 steps
                        # 'euler_ancestral', # NEED TO TEST 
                        # 'euler_ancestral_cfg_pp', # NEED TO TEST
                        'heun', # 30 steps at least. 50 is good.
                        'heunpp2', # Good at 30
                        # 'dpm_2',  # Test higher than 20
                        # 'dpm_2_ancestral', # Blurry
                        # 'lms',  #Might need more than 40
                        # 'dpm_fast', # blurry
                        # 'dpm_adaptive', 
                        # 'dpm_2_ancestral',  #Trash at 20 and long load
                        # 'dpm_2_ancestral_cfg_pp', 
                        # 'dpmpp_sde', 
                        # 'dpmpp_sde_gpu', 
                        # 'dpmpp_2m',  # 30 steps at least
                        # 'dpmpp_2m_cfg_pp',  #Complete trash at 20
                        # 'dpmpp_2m_sde', # NEED TO TEST
                        # 'dpmpp_2m_sde_gpu', # NEED TO TEST
                        # 'dpmpp_3m_sde', 
                        # 'dpmpp_3m_sde_gpu', 
                        # 'ddpm', 
                        'lcm',  # Good
                        # 'ipndm', # NEED TO TEST
                        # 'ipndm_v', # Blurry at 40 
                        'deis', # 30 steps. Maybe less
                        # 'res_multistep', # NEED TO TEST
                        # 'res_multistep_cfg_pp', 
                        'gradient_estimation',  # 30 steps decent
                        # 'ddim', # NEED TO TEST
                        # 'uni_pc', # Trash
                        # 'uni_pc_bh2' # NEED TO TEST
                        ]
            if self.sampler in samplers:
                self.set_sampler(self.sampler)
            elif sampler == 'random':
                self.set_sampler(random.choice(samplers))
            else:
                print("Sampler doesn't exit. Using default")

        if self.scheduler:
            schedulers = ['normal',
                          'karras', # Don't use with euler at 20 steps
                          'exponential',
                          'sgm_uniform',
                          'simple',
                          # 'ddm_uniform', # DOUBLE CHECK NAME
                          'beta',
                          'linear_quadratic',
                          'kl_optimal']
            if self.scheduler in schedulers:
                self.set_scheduler(self.scheduler)
            elif self.scheduler == 'random':
                self.set_scheduler(random.choice(schedulers))
            else:
                print("Scheduler doesn't exit. Using default")

        if self.guidance:
            if self.guidance == 'random':
                self.set_guidance(random.uniform(1.0, 15.0))
            else:
                self.set_guidance(self.guidance)

    def run_workflow(self):
        self.set_workflow()

        self.client_id = random.randint(10**14, 10**15 -1)
        self.client_id = str(self.client_id)

        start_time = time.time()

        ws = websocket.WebSocket()

        ws.connect("ws://{}/ws?clientId={}".format(self.server_address, self.client_id))
        # images = get_images(ws, workflow)
        # videos = self.get_videos(ws, self.workflow)
        video_path = self.get_videos_filename(ws, self.workflow)
        ws.close()

        elapsed_time = round(time.time() - start_time, 2)
        print(f"{elapsed_time=} seconds elapsed")
        print(f"video_path: {video_path}")
        # return videos
        return video_path


