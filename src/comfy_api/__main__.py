import argparse
from .classes import ComfyClient


def print_keys(d):
    for key, value in d.items():
        print(f"Key: {key}")
        print(value['_meta']['title'])
        # print(f"Value: {value}")


def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    parser.add_argument('workflow', type=str, help='Workflow JSON')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI server address')
    parser.add_argument('--seed', default=None, help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')

    args = parser.parse_args()

    comfy_client = ComfyClient(args.host + ":8188")
    comfy_client.run_worflow(args.workflow, args.seed, args.prompt)
