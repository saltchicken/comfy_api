import argparse
import time
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
    parser.add_argument('--sampler', default=None, help='Set sampler for the diffusion process')
    parser.add_argument('--scheduler', default=None, help='Set scheduler for the diffusion process')
    parser.add_argument('--guidance', default=None, help='Set guidance scale for the diffusion process')

    args = parser.parse_args()

    comfy_client = ComfyClient(args.host + ":8188")
    start_time = time.time()
    videos = comfy_client.run_workflow(args.workflow, args.seed, args.prompt, args.length, args.boomerang, args.resolution, args.lora, args.steps, args.sampler, args.scheduler, args.guidance)
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f"{elapsed_time=}")
    comfy_client.view_video(videos)
