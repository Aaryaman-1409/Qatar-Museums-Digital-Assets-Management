from .redmail import gmail
from pathlib import Path

gmail.use_jinja = False

def send_mail(wd, send_copy_logs, send_excel_file, recipients):
    gmail.username = "nmoqampingestscript@gmail.com"  # Your Gmail address with 2FA
    gmail.password = "hnpn qsna pzqc xiju"

    try:
        temp_path = Path.home() / 'AMPIngest/'
        temp_path.mkdir(parents=True)
        excel_file= temp_path / 'AMPIngestFile.xlsx'
        copy_log = temp_path / 'copy_logs.txt'
    except FileExistsError:
        excel_file = Path.home() / 'AMPIngest/AMPIngestFile.xlsx'
        copy_log = Path.home() / 'AMPIngest/copy_logs.txt'

    attachments = {}
    tasks = ""

    if send_copy_logs:
        attachments["CopyLogs.txt"] = copy_log
        tasks += (
            "<li>Copying files from the source folder to the destination folder</li>"
        )
    if send_excel_file:
        attachments["AMPIngest.xlsx"] = excel_file
        tasks += "<li>Generating the AMP manifest file</li>"

    if not tasks:
        if copy_log.is_file():
            attachments["CopyLogs.txt"] = copy_log
            tasks += "<li>No tasks selected. Old copy logs attached</li>"
        if excel_file.is_file():
            attachments["AMPIngest.xlsx"] = excel_file
            tasks += "<li>No tasks selected. Old AMP manifest file attached</li>"

    print("Sending mail...")
    gmail.send(
        subject="AMPIngest Script results",
        receivers=recipients,
        html=f"<p>The AMPIngest script has finished your tasks:<ul>{tasks}</ul></p><p>As requested, logs of the tasks are attached in this email.</p><p>Thank you.</p>",
        attachments=attachments,
    )
