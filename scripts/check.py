for line in diff_output.splitlines():
    if line.startswith("+++ b/"):
        current_file = line[6:]
        files[current_file] = []
        position = 0
    elif line.startswith("@@"):
    elif current_file and line.startswith("+") and not line.startswith("+++"):
        files[current_file].append({"line": position, "code": line[1:]})
        position += 1
