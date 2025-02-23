import argparse
import easygui

def values_dict_to_command(values_dict):
    values_dict["lora"] = values_dict["lora"].replace("[", "").replace("]", "").replace(",", "").replace("'", "")
    values_dict["prompt"] = '"' + values_dict["prompt"] + '"'
    if values_dict["boomerang"] == "False":
        del values_dict["boomerang"]
    else:
        values_dict["boomerang"] = " "
    command = " ".join([f"--{key} {value}" for key, value in values_dict.items() if value != ""])
    return command

def main():
    parser = argparse.ArgumentParser(description='ComfyUI prompt')
    parser.add_argument('--lora', nargs="+", help='Set strength of lora')
    parser.add_argument('--steps', help='Set steps for the diffusion process')
    parser.add_argument('--guidance', help='Set guidance scale for the diffusion process')
    parser.add_argument('--scheduler', help='Set scheduler for the diffusion process')
    parser.add_argument('--sampler', help='Set sampler for the diffusion process')
    parser.add_argument('--length', help='Length of hunyuan output')
    parser.add_argument('--seed', help='Random seed for RandomNoise')
    parser.add_argument('--prompt', default='', help='Prompt text')
    parser.add_argument('--resolution', help='Resolution of the output image')
    parser.add_argument('--boomerang', action="store_true", help='Enable boomerang effect')
    args = parser.parse_args()

    # user_input = easygui.enterbox("Enter something:")
    # print("You entered:", user_input)
    #
    fields = ["lora", "steps", "guidance", "scheduler", "sampler", "length", "seed", "prompt", "resolution", "boomerang"]
    default_values = [args.lora, args.steps, args.guidance, args.scheduler, args.sampler, args.length, args.seed, args.prompt, args.resolution, args.boomerang]
    values = easygui.multenterbox("Enter something:", "Title", fields, default_values)
    if values:  # Check if user didn't cancel
        values_dict = dict(zip(fields, values))
        command = values_dict_to_command(values_dict)
        print(command)
    else:
        print("None")

if __name__ == "__main__":
    main()
