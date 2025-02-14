local mp = require("mp")
local utils = require("mp.utils")

-- TODO: Add check if video was retrieved from API
local function is_windows()
	local windows = package.config:sub(1, 1) == "\\"

	if windows then
		print("Running on Windows")
		return true
	else
		print("Running on Linux or macOS")
		return false
	end
end

local function get_field(parsed_comment, field)
	local output_field = {}
	for key, value in pairs(parsed_comment) do
		-- Attempt to parse each value as JSON if it's a string
		local comfy_data = type(value) == "string" and utils.parse_json(value) or value
		if comfy_data then
			-- mp.msg.info("Processing key: " .. key)
			-- Print contents of comfy_data
			if type(comfy_data) == "table" then
				for sub_key, sub_value in pairs(comfy_data) do
					if sub_value["class_type"] == "LoraLoaderModelOnly" and field == "lora" then
						if sub_value["inputs"] then
							output_field[sub_value["inputs"]["lora_name"]] = sub_value["inputs"]["strength_model"]
						end
					else
						if sub_value["class_type"] == "CLIPTextEncode" and field == "prompt" then
							table.insert(output_field, sub_value["inputs"]["text"])
						end
					end
				end
			else
				mp.msg.info("  Value: " .. tostring(comfy_data))
			end
		else
			mp.msg.warn("Failed to parse value under key: " .. key)
		end
	end
	return output_field
end

-- Get metadatao
local function print_comfy_data()
	local metadata = mp.get_property_native("metadata")

	if not metadata or not metadata["comment"] then
		mp.msg.info("No comment metadata found.")
		return
	end

	local comment = metadata["comment"]
	-- mp.msg.info("Raw Comment: " .. comment)

	-- Try parsing the top-level comment as JSON
	local parsed_comment = utils.parse_json(comment)
	if not parsed_comment then
		mp.msg.warn("Failed to parse comment as JSON")
		return
	end

	local loras = get_field(parsed_comment, "lora")
	for key, value in pairs(loras) do
		print(key .. ": " .. value)
	end
	local prompt = get_field(parsed_comment, "prompt")
	print(prompt[1])

	local command = "--randomize"
	return command

	-- Iterate through the parsed JSON structure
end

local function run_comfy_data()
	-- local command = print_comfy_data()
	if is_windows() then
		os.execute("comfy --host 10.0.0.3:8188 --length 5" .. " " .. command)
	else
		os.execute("conda run -n comfy_api bash comfy --host 10.0.0.3:8188" .. " " .. command)
	end
end

mp.add_key_binding("p", "print", print_comfy_data)
mp.add_key_binding("P", "run_comfy_data", function()
	print("Running")
	run_comfy_data()
end)
