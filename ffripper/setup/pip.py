import subprocess, shlex


def install_pip3():
    pip_cmd = ""
    try:
        subprocess.call(["pip3", "-V"], stdout=subprocess.DEVNULL)
        pip_cmd = "pip3"
    except FileNotFoundError:
        try:
            subprocess.call(["pip", "-V"], stdout=subprocess.DEVNULL)
            pip_cmd = "pip"
        except FileNotFoundError:  # Pip not installed yet
            subprocess.call(shlex.split("python3 -m ensurepip"), stdout=subprocess.DEVNULL)
            install_pip3()
    return pip_cmd

print(install_pip3())
