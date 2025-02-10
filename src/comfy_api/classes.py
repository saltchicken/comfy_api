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

def print_keys(d):
    for key, value in d.items():
        print(f"Key: {key}")
        print(value['_meta']['title'])
        # print(f"Value: {value}")

class ComfyClient:
    def __init__(self, server_address):
        self.client_id = str(uuid.uuid4())
        self.server_address = server_address
        self.workflow = None

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

    def view_video(self, videos):
        for node_id in videos:
            for video_data in videos[node_id]:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                    temp_video.write(video_data)
                    temp_filename = temp_video.name  # Get the file path

                    if platform.system() == "Linux":
                        cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
                        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                    cap = cv2.VideoCapture(temp_filename)

                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_time = 1 / fps if fps > 0 else 1 / 30  # Default to 30 FPS if unknown

                    while True:  # Infinite loop for replaying video
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
                            if cv2.waitKey(delay) & 0xFF == ord('q'):  # Press 'q' to exit
                                cap.release()
                                cv2.destroyAllWindows()
                                exit()

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
                print(f"{lora=}")
                self.workflow[key]['inputs']['lora_name'] = lora + ".safetensors"
                self.workflow[key]['inputs']['strength_model'] = lora_strength
                print(f"Setting strength for {lora} to {lora_strength}")
                print(self.workflow)

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

    def run_workflow(self, **kwargs):
        if "lora" in kwargs:
            lora = kwargs["lora"]
            if len(lora) == 1:
                workflow_file = "SingleLoraHunyuan.json"
            elif len(lora) == 2:
                workflow_file = "DoubleLoraHunyuan.json"
            elif len(lora) == 3:
                workflow_file = "TripleLoraHunyuan.json"
            elif len(lora) == 4:
                workflow_file = "QuadLoraHunyuan.json"
            elif len(lora) == 5:
                workflow_file = "PentaLoraHunyuan.json"
            elif len(lora) == 6:
                workflow_file = "HexaLoraHunyuan.json"
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
            if len(lora_nodes) != len(lora):
                print("Lora parameter mismatched. Exiting")
                sys.exit(1)
            for l in lora:
                l = l.split("=")
                if len(l) != 2:
                    print("Lora parameter incorrect. Exiting")
                    sys.exit(1)
                if l[1] == 'trirandom':
                    print(f"Setting triangular random lora strength for {l[0]}")
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
            workflow_file = "BasicHunyuan.json"

            with open(workflow_file, "r") as f:
                try:
                    self.workflow = json.load(f)
                except:
                    print("Could not open file {}".format(workflow_file))
                    exit(1)

        if "seed" in kwargs:
            self.set_seed(kwargs["seed"])
        else:
            self.set_seed(random.randint(10**14, 10**15 -1))

        if "length" in kwargs:
            self.set_length(kwargs["length"])

        if "boomerang" in kwargs:
            self.set_boomerang()

        if "prompt" in kwargs:
            self.set_prompt(kwargs["prompt"])

        if "resolution" in kwargs:
            resolution = kwargs["resolution"]
            if resolution == "random":
                resolutions = ["640x480", "480x640", "512x512"]
                self.set_resolution(random.choice(resolutions))
            else:
                self.set_resolution(resolution)

        if "steps" in kwargs:
            steps = kwargs["steps"]
            if steps == 'trirandom' or steps == 'random':
                self.set_steps(random.triangular(6, 40, 20))
            else:
                self.set_steps(steps)

        if "sampler" in kwargs:
            sampler = kwargs["sampler"]
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
            if sampler in samplers:
                self.set_sampler(sampler)
            elif sampler == 'random':
                self.set_sampler(random.choice(samplers))
            else:
                print("Sampler doesn't exit. Using default")

        if "scheduler" in kwargs:
            scheduler = kwargs["scheduler"]
            schedulers = ['normal',
                          'karras', # Don't use with euler at 20 steps
                          'exponential',
                          'sgm_uniform',
                          'simple',
                          # 'ddm_uniform', # DOUBLE CHECK NAME
                          'beta',
                          'linear_quadratic',
                          'kl_optimal']
            if scheduler in schedulers:
                self.set_scheduler(scheduler)
            elif scheduler == 'random':
                self.set_scheduler(random.choice(schedulers))
            else:
                print("Scheduler doesn't exit. Using default")


        if "guidance" in kwargs:
            guidance = kwargs["guidance"]
            if guidance == 'random':
                self.set_guidance(random.uniform(1.0, 15.0))
            else:
                self.set_guidance(guidance)

        self.client_id = random.randint(10**14, 10**15 -1)
        print(f"Client ID: {self.client_id}")
        self.client_id = str(self.client_id)


        ws = websocket.WebSocket()

        ws.connect("ws://{}/ws?clientId={}".format(self.server_address, self.client_id))
        # images = get_images(ws, workflow)
        videos = self.get_videos(ws, self.workflow)
        ws.close()
        return videos


