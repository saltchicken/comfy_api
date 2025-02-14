local function file_exists(path)
	local file = io.open(path, "rb")
	if file then
		file:close()
	end
	return file ~= nil
end

local function copy_file(source, destination)
	if file_exists(destination) then
		print("Skipping: File already exists at " .. destination)
		return false
	end

	local input_file = io.open(source, "rb")
	if not input_file then
		error("Could not open source file: " .. source)
	end

	local content = input_file:read("*all")
	input_file:close()

	local output_file = io.open(destination, "wb")
	if not output_file then
		error("Could not open destination file: " .. destination)
	end

	output_file:write(content)
	output_file:close()

	print("File copied from " .. source .. " to " .. destination)
end

function copy_current_file_to_backup_folder()
	local file_path = mp.get_property("path")
	-- mp.osd_message(filename)
	copy_file(file_path, "/home/saltchicken/saved_comfy/" .. file_path)
end

mp.add_key_binding("o", "filename", copy_current_file_to_backup_folder)
