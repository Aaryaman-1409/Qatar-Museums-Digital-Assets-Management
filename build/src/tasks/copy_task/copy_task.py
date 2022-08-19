import subprocess
from pathlib import Path

def copy_source_to_destination(wd, src, dest):
    dest = dest / src.name
    tee = wd.joinpath(r"binaries\tee.exe")
    
    try:
        temp_path = Path.home() / 'AMPIngest/'
        temp_path.mkdir(parents=True)
        output = temp_path / 'copy_logs.txt'
    except FileExistsError:
        output = Path.home() / 'AMPIngest/copy_logs.txt'

    subprocess.run(
        [
            "robocopy",
            r"/MIR",
            r"/FP",
            r"/NDL",
            r"/NP",
            str(src),
            str(dest),
            "|",
            tee,
            output,
        ],
        shell=True,
    )


# use this function if you're unsure of the copy progress
def compare_source_to_destination(wd, src, dest):
    dest = dest / src.name
    tee = wd.joinpath(r"binaries\tee.exe")
    try:
        temp_path = Path.home() / 'AMPIngest/'
        temp_path.mkdir(parents=True)
        output = temp_path / 'copy_validation.txt'
    except FileExistsError:
        output = Path.home() / 'AMPIngest/copy_validation.txt'
    subprocess.run(
        [
            "robocopy",
            r"/MIR",
            r"/FP",
            r"/NDL",
            r"/L",
            r"/NP",
            str(src),
            str(dest),
            "|",
            tee,
            output,
        ],
        shell=True,
    )
    # runs a pseudo robocopy to check which files would have been copied. If the copied field is 0, the two dirs are identical.
