from pathlib import Path
import traceback
from .copy_task import copy_task
from .excel_task import excel_task
from .email_task import email_task
from ..gui.gui_params import fields
import os

def winapi_path(dos_path, encoding=None):
    if (not isinstance(dos_path, str) and encoding is not None): 
        dos_path = dos_path.decode(encoding)
    path = os.path.abspath(dos_path)
    if path.startswith(u"\\\\?\\UNC"):
        return path
    elif path.startswith(u"\\\\"):
        return u"\\\\?\\UNC\\" + path[2:]
    return u"\\\\?\\" + path

def main_task(
    wd,
    source_folder,
    destination_folder,
    security_policy,
    filetype_to_model,
    tasks,
    recipients,
):
    try:
        to_copy = fields['tasks'].value["Copy Task"] in tasks
        to_excel = fields['tasks'].value["Excel Task"] in tasks
        to_email = fields['tasks'].value["Email Task"] in tasks

        if to_copy:
            print("Copying Files...")
            copy_task.copy_source_to_destination(
                wd,
                Path(source_folder), Path(destination_folder)
            )

        if to_excel:
            excel_task.generate_excel_file(
                wd,
                Path(destination_folder),
                filetype_to_model,
                security_policy,
            )

        if to_email:
            email_task.send_mail(wd, to_copy, to_excel, recipients)

        print("Done with all tasks")
        return True
    except:
        print("Some error occured")
        print(traceback.format_exc())
        return False
