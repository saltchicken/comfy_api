import argparse
import time
from .classes import ComfyClient

def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    # parser.add_argument('workflow', type=str, help='Workflow JSON')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI server address')

    # Optional arguments stored in a dictionary
    parser.add_argument('--seed', help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')
    parser.add_argument('--length', help='Length of hunyuan output')
    parser.add_argument('--boomerang', action="store_true", help='Enable boomerang effect')
    parser.add_argument('--resolution', help='Resolution of the output image')
    parser.add_argument('--lora', nargs="+", help='Set strength of lora')
    parser.add_argument('--steps', help='Set steps for the diffusion process')
    parser.add_argument('--sampler', help='Set sampler for the diffusion process')
    parser.add_argument('--scheduler', help='Set scheduler for the diffusion process')
    parser.add_argument('--guidance', help='Set guidance scale for the diffusion process')

    args = parser.parse_args()

    # Extract optional arguments into a dictionary
    workflow_options = { 
        k: v for k, v in vars(args).items() 
        if k not in ['host'] and v is not None
    }

    comfy_client = ComfyClient(args.host, **workflow_options)
    videos = comfy_client.run_workflow()

    comfy_client.view_video(videos)

