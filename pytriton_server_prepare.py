import os
import subprocess

def prepare(message):
    #try:
    output = "empty"
    model_to_run = message["model"]
    repo_url = message["model_info"]["repo_url"]
    git_lfs_command = "git lfs install"
    git_clone_command = f"git clone {repo_url}"
    #output = subprocess.check_output(git_lfs_command, shell=True)
    #output = subprocess.check_output(git_clone_command, shell=True)
    pytriton_file_name = "pytriton_server.py"
    pytriton_file = open(pytriton_file_name, "w")
    with open ("codegen_pre.txt", "r") as f:
        for line in f.readlines():
            pytriton_file.write(line)
    with open (f"{model_to_run}/interface.txt", "r") as f:
        for line in f.readlines():
            pytriton_file.write(line)
    with open ("codegen_post.txt", "r") as f:
        for line in f.readlines():
            pytriton_file.write(line)
    pytriton_file.close()
    return pytriton_file_name

def run_pytriton(pytriton_file_name):
    command = f"python {pytriton_file_name}"
    os.system(command)
