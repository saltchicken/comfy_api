local function get_script_dir()
	local script_path = debug.getinfo(1, "S").source:sub(2)
	local script_dir = script_path:match("(.*/)")
	return script_dir
end

local function get_user_input()
	local script_dir = get_script_dir()
	local script_path = script_dir .. "/input_gui.py"
	local handle = io.popen("python " .. script_path)
	local input = handle:read("*a")
	print(input)
end

mp.add_key_binding("i", "get_input", get_user_input)
