import subprocess
import shlex

UNSAFE_CHARS = set("&;|$`<>")


def get_disk_usage(parameters: str):

    params = parameters or ""
    
    if any((c in params) for c in UNSAFE_CHARS):
        raise ValueError("Parámetros inválidos")

    tokens = shlex.split(params) if params else []

    cmd = ["df", "-h"] + tokens

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True
        )
        usage = result.stdout.strip()

    except:
        raise Exception("An unexpected error was observed")

    return usage