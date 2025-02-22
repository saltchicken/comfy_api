import argparse
import time
import numpy as np
import random
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
    parser.add_argument('--show', action="store_true", help='Show the returned output')
    parser.add_argument('--randomize', help='Randomize the loras and run the workflow')

    args = parser.parse_args()

    # Extract optional arguments into a dictionary
    workflow_options = { 
        k: v for k, v in vars(args).items() 
        if k not in ['host', 'show'] and v is not None
    }

    comfy = ComfyClient(args.host, **workflow_options)
    if args.randomize:
        print(f"Randomizing {args.randomize}")

        rand_params = args.randomize.split(":")
        if len(rand_params) == 1:
            num_loras = int(rand_params[0])
            print("Total for loras defaulting to 1")
            total = 1
        elif len(rand_params) == 2:
            num_loras = int(rand_params[0])
            total = float(rand_params[1])
        else:
            print("Incorrect randomize format. Exiting.")
            exit(1)

        loras = comfy.get_loras("")
        try:
            while True:
                strengths = np.round(np.random.dirichlet([1] * num_loras) * total, 2)
                selected_loras = random.sample(loras, num_loras)
                comfy.lora = []
                for i in range(num_loras):
                    comfy.lora.append(f"{selected_loras[i]}={strengths[i]}")
                videos = comfy.run_workflow()
                if args.show:
                    comfy.view_video(videos)
        except KeyboardInterrupt:
            print("\nLoop terminated by user.")

    else:
        # videos = comfy.run_workflow()
        video_path = comfy.run_workflow()
        # return video_path

        if args.show:
            comfy.view_video(videos)
