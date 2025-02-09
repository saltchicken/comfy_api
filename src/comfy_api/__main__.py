import argparse
from .classes import ComfyClient

def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    parser.add_argument('workflow', type=str, help='Workflow JSON')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI server address')
    parser.add_argument('--seed', default=None, help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')
    parser.add_argument('--length', default=None, help='Length of hunyuan output')

    args = parser.parse_args()

    comfy_client = ComfyClient(args.host + ":8188")
    videos = comfy_client.run_workflow(args.workflow, args.seed, args.prompt, args.length)
    comfy_client.view_video(videos)
