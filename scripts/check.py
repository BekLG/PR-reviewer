for line in diff_output.splitlines():
    if line.startswith("+++ b/"):
        current_file = line[6:]
        files[current_file] = []
        position = 0
    elif line.startswith("@@"):
        # Example: @@ -12,0 +13,2 @@
        hunk_header = line
        parts = line.split()
        added_range = parts[2]  # e.g., +13,2
        start_line = int(added_range.split(",")[0][1:])
        position = start_line
    elif current_file and line.startswith("+") and not line.startswith("+++"):
        files[current_file].append({"line": position, "code": line[1:]})
        position += 1