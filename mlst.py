import os
import re
import shutil


source_folder = 'Enter your path'
base_folder = 'Enter your path'
extracted_info = []

for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the file line by line
            for line in file:
                # make sure the line is not empty
                if 'MCR_CVU_' in line:
                    # Extract the number and the name of the file
                    match = re.search(r'(MCR_CVU_\d+).*?(\d+)', line)
                    if match:
                        number = match.group(2)
                        # assign the name of the file to the number
                        target_folder = os.path.join(base_folder, number)
                        if not os.path.exists(target_folder):
                            os.makedirs(target_folder)
                        # generate the target file path
                        target_file_path = os.path.join(target_folder, match.group(1)+"_mysnps")
                        # move the file to the target folder
                        current_file_path = os.path.join(base_folder, match.group(1)+"_mysnps")
                        #print(current_file_path, target_file_path)
                        shutil.move(current_file_path, target_file_path)