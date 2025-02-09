import argparse
from .classes import ComfyClient

def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    parser.add_argument('workflow', type=str, help='Workflow JSON')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI server address')
    parser.add_argument('--seed', default=None, help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')
    parser.add_argument('--length', default=None, help='Length of hunyuan output')
    parser.add_argument('--boomerang', action="store_true", help='Enable boomerang effect')
    parser.add_argument('--resolution', default=None, help='Resolution of the output image')
    parser.add_argument('--lora', nargs="+", default=None, help='Set strength of lora')
    parser.add_argument('--steps', default=None, help='Set steps for the diffusion process')

    args = parser.parse_args()

    comfy_client = ComfyClient(args.host + ":8188")
    videos = comfy_client.run_workflow(args.workflow, args.seed, args.prompt, args.length, args.boomerang, args.resolution, args.lora, args.steps)
    comfy_client.view_video(videos)
