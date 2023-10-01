import os


def replace_strings_in_file(file_path):
    with open(file_path, "r") as f:
        file_contents = f.read()

    modified_contents = file_contents.replace("allstars", "allstars")
    modified_contents = modified_contents.replace("SQL All ⭐ Stars", "SQL All ⭐ Stars")

    if modified_contents != file_contents:
        with open(file_path, "w") as f:
            f.write(modified_contents)
        print(f"Updated {file_path}")


def crawl_directory(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith((".py", ".md")):
                file_path = os.path.join(root, file_name)
                replace_strings_in_file(file_path)


if __name__ == "__main__":
    start_directory = "/Users/max/code/allstars"  # Replace with your directory path
    crawl_directory(start_directory)
