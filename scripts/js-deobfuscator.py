import os
import argparse
import jsbeautifier
import re

from loguru import logger

options = jsbeautifier.default_options()
options.indent_size = 4
options.unescape_strings = True


def is_potentially_obfuscated(original_code, beautified_code):
    # Set a threshold for line count reduction (adjust as needed)
    line_threshold = 0.8  # 80% reduction

    original_lines = original_code.split('\n')
    beautified_lines = beautified_code.split('\n')

    original_line_count = len(original_lines)
    beautified_line_count = len(beautified_lines)

    line_ratio = original_line_count / beautified_line_count

    return line_ratio < line_threshold

def transform_brackets_to_dots(input_code):
    input_code = re.sub(r"\['([a-zA-Z_]\w*)'\](\('?[^\)]*'?\))", r".\1\2", input_code)
    input_code = re.sub(r"\['([a-zA-Z_]\w*)'\](.\w+)", r".\1\2", input_code)
    input_code = re.sub(r"(_?this)\['([a-zA-Z_$]\w*)'\]", r"\1.\2", input_code)
    input_code = re.sub(r"\['length'\]", r".length", input_code)

    return input_code


def write_to_file(output_path, content):
    try:
        with open(output_path, 'w') as file:
            file.write(content)
        return True
    except:
        return False

def process_file(input_path, output_path):
    with open(input_path, 'r') as file:
        original_code = file.read()

    fail = False

    try:
        beautified_code = jsbeautifier.beautify(original_code, options)
        beautified_code = transform_brackets_to_dots(beautified_code)
    except:
        logger.error(f"Failed to deobfuscate file: {input_path}")
        fail = True

    if not fail:
        if not is_potentially_obfuscated(original_code, beautified_code):
            logger.info(f"Skipping non-obfuscated file: {input_path}")
        else:
            if not write_to_file(output_path, beautified_code):
                logger.error(f"Failed to save deobfuscated file: {input_path}")
                fail = True
            else:
                logger.info(f"Deobfuscated file: {input_path}")

    if fail:
        write_to_file(output_path, "// Beautification failed")

#def process_directory(input_dir, skip_dirs):
def process_directory(input_dir):
    for root, dirs, files in os.walk(input_dir):
        #dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file_name in files:
            if file_name.endswith(".deobfuscated.js"):
                logger.info(f"Skipping already-obfuscated file: {file_name}")
            elif file_name.endswith('.js'):
                input_path = os.path.join(root, file_name)
                output_path = os.path.join(root, f"{file_name}.deobfuscated.js")
                process_file(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(description="Recursively beautify JavaScript files in a directory.")
    parser.add_argument("input_directory", help="Path to the input directory containing JavaScript files.")
    #parser.add_argument("--skip-dirs", nargs='+', default=[], help="List of directories to skip during processing.")
    args = parser.parse_args()

    input_directory = args.input_directory
    #skip_dirs = args.skip_dirs

    process_directory(input_directory)
    #process_directory(input_directory, skip_dirs)
    logger.info("Beautification complete.")

if __name__ == "__main__":
    main()
