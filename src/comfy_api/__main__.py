#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import argparse
import random
import cv2
import io
import numpy as np
import tempfile
import time

server_address = '10.0.0.3:8188'
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_video(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    # "http://{}/view?{}".format(server_address, url_values)
    url_request = "http://{}/view?{}".format(server_address, url_values)
    print(url_request)
    with urllib.request.urlopen(url_request) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
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

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        print(node_output)
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

def get_videos(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
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

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        print(node_output)
        videos_output = []
        if 'gifs' in node_output:
            print("found gif")
            for video in node_output['gifs']:
                video_data = get_video(video['filename'], video['subfolder'], video['type'])
                videos_output.append(video_data)
        output_videos[node_id] = videos_output

    return output_videos

def view_video(video_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_bytes)
        temp_filename = temp_video.name  # Get the file path

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

def view_video_boomerang(video_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_bytes)
        temp_filename = temp_video.name  # Get the file path

        cap = cv2.VideoCapture(temp_filename)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_time = 1 / fps if fps > 0 else 1 / 30  # Default to 30 FPS if unknown
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# **Fix: Adjust delay to compensate for double playthrough**
        delay = max(1, int((frame_time / 2) * 1000))  # Halve the delay

        while True:  # Infinite loop for boomerang effect
            # Play video forward
            for frame_num in range(total_frames):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Boomerang Video", frame)
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

            # Play video backward
            for frame_num in range(total_frames - 1, -1, -1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Boomerang Video", frame)
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

        cap.release()
        cv2.destroyAllWindows()

def view_images(images):
    for node_id in images:
        for image_data in images[node_id]:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            image.show()

def print_keys(d):
    for key, value in d.items():
        print(f"Key: {key}")
        print(value['_meta']['title'])
        # print(f"Value: {value}")

def set_seed(workflow, seed):
    for key, value in workflow.items():
        if value['class_type'] == 'RandomNoise':
            workflow[key]['inputs']['noise_seed'] = seed

def run_worflow(workflow, host, seed, prompt):
    # server_address = host + ":8188"
    # print(server_address)
    try:
        with open(workflow, "r") as f:
            workflow = json.load(f)
    except:
        print("Could not open file {}".format(workflow))
        exit(1)
    # print(workflow)
    # print_keys(workflow)
    #
    #     if value['class_type'] == 'RandomNoise':
    # for key, value in workflow.items():
    #         print(workflow[key]['inputs']['noise_seed'])
    if seed:
        set_seed(workflow, seed)
    else:
        set_seed(workflow, random.randint(10**14, 10**15 -1))

    # for key, value in workflow.items():
    #     if value['class_type'] == 'RandomNoise':
    #         print(workflow[key]['inputs']['noise_seed'])



    #set the text prompt for our positive CLIPTextEncode
    # prompt["6"]["inputs"]["text"] = "masterpiece best quality man"

    #set the seed for our KSampler node
    # prompt["3"]["inputs"]["seed"] = 5
    ws = websocket.WebSocket()

    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    # images = get_images(ws, workflow)
    videos = get_videos(ws, workflow)
    ws.close()
    # with urllib.request.urlopen("http://10.0.0.3:8188/view?filename=Hunyuan+_00447.mp4&subfolder=&type=output") as response:
    #     video = response.read()
    #     print(video)
    #     view_video_boomerang(video)

    for node_id in videos:
        for video_data in videos[node_id]:
            view_video(video_data)

def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    parser.add_argument('workflow', type=str, help='Workflow JSON')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI server address')
    parser.add_argument('--seed', default=None, help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')

    args = parser.parse_args()


    run_worflow(args.workflow, args.host, args.seed, args.prompt)






