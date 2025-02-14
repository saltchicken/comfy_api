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
					if type(sub_value) == "table" then
						if sub_value["class_type"] == "LoraLoaderModelOnly" and field == "lora" then
							if sub_value["inputs"] then
								output_field[sub_value["inputs"]["lora_name"]] = sub_value["inputs"]["strength_model"]
							end
						else
							if sub_value["class_type"] == "CLIPTextEncode" and field == "prompt" then
								table.insert(output_field, sub_value["inputs"]["text"])
							end
						end
					else
						print("Sub_value not a table")
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

	local parameters = ""

	local loras = get_field(parsed_comment, "lora")
	parameters = parameters .. "--lora "
	local suffix = ".safetensors"
	for key, value in pairs(loras) do
		key = key:sub(1, -#suffix - 1)
		parameters = parameters .. key .. "=" .. value .. " "
	end
	local prompt = get_field(parsed_comment, "prompt")
	parameters = parameters .. "--prompt "
	parameters = parameters .. '"' .. prompt[1] .. '"'

	return parameters

	-- Iterate through the parsed JSON structure
end

function replace_video(video_path)
	mp.commandv("loadfile", video_path, "replace")
end

-- local function get_video_path(str)
-- 	-- Find the line that starts with 'video_path: '
-- 	local line = string.match(str, "([^\n]*video_path:[^\n]*)")
-- 	if line then
-- 		-- Split the line into two parts based on 'video_path: '
-- 		local _, path = string.match(line, "video_path:%s*(.*)")
-- 		return path
-- 	end
-- end
local function run_comfy_data()
	local parameters = print_comfy_data()

	-- local command = "comfy --host 10.0.0.3:8188 " .. parameters
	local command = "comfy --host 10.0.0.3:8188 " .. parameters
	print(command)

	if is_windows() then
		os.execute(command)
	else
		local handle = io.popen(command)
		if handle then
			for line in handle:lines() do
				if string.find(line, "video_path") then
					local video_path = string.gsub(line, "video_path: ", "")
					handle:close()
					return video_path
				end
			end
			print("Video path not found")
			handle:close()
			return ""
		end
	end
end

mp.add_key_binding("p", "print", print_comfy_data)
mp.add_key_binding("P", "run_comfy_data", function()
	local video_path = run_comfy_data()
	-- print("YES " .. video_path)
	local cwd = os.getenv("PWD")
	replace_video(cwd .. "/" .. video_path)
end)
