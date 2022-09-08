from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font
import mimetypes, subprocess, os, stat
from openpyxl.styles import Alignment

common_file_types = ['image', 'video', 'audio']

def trID_MIME(wd, file):
    trid_path = wd.joinpath(r"binaries\trid.exe")
    process = subprocess.run(
        [str(trid_path), str(file)], capture_output=True, text=True, shell=False
    )
    stdout = process.stdout

    split_text = stdout.split("%")
    if len(split_text) == 1:
        print(file)
        return "document"
    else:
        return "".join(split_text[1:])


def is_hidden(file):
    attrs = os.stat(file).st_file_attributes
    hidden = bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
    return hidden


def generate_excel_file(wd, destination_folder, filetype_to_model, security_policy):
    exclude_files = []
    excel_template_path = wd.joinpath(r"data\Excel Files\AMPIngestTemplate.xlsx")

    try:
        temp_path = Path.home() / 'Documents/AMPIngest/'
        temp_path.mkdir(parents=True)
        excel_result_path = temp_path / 'AMPIngestFile.xlsx'
    except FileExistsError:
        excel_result_path = Path.home() / 'Documents/AMPIngest/AMPIngestFile.xlsx'
    
    row_num = 2

    wb = load_workbook(filename=excel_template_path)
    ws1 = wb.active
    main_font = Font(
        name="Calibri",
        size=11,
        bold=False,
        italic=False,
        vertAlign=None,
        underline="none",
        strike=False,
        color="FF000000",
    )

    for root, dirs, files in os.walk(destination_folder):
        for i in files:
            i = Path(root).joinpath(Path(i))
            print(i)
            if is_hidden(i) or i.name in exclude_files:
                continue

            filetype_guess = mimetypes.guess_type(i)[0]

            if filetype_guess is not None:
                filetype = filetype_guess.split("/")[0]
            else:
                filetype = trID_MIME(wd, i)
                for types in common_file_types:
                    if types in filetype.lower():
                        filetype = types
                        break

            if filetype not in common_file_types:
                filetype = "document"

            final_path = i
            DAM_folder_path = Path(*i.parts[1:-1])
            DAM_folder_policy = f"Basic|{security_policy}"
            DAM_folder_field = f"{DAM_folder_path}|{DAM_folder_policy}"

            print(DAM_folder_field)

            print(f"{final_path}")
            print(f"{filetype}")
            print(f"Finished processing {row_num} files \n")

            metadata_model_cell = ws1[f"A{row_num}"]
            file_path_cell = ws1[f"B{row_num}"]
            security_cell = ws1[f"C{row_num}"]
            folder_cell = ws1[f"D{row_num}"]

            metadata_model_cell.value = filetype_to_model[filetype]
            file_path_cell.value = str(final_path)
            security_cell.value = security_policy
            folder_cell.value = DAM_folder_field


            for cells in [metadata_model_cell, file_path_cell, security_cell, folder_cell]:
                cells.font = main_font
                cells.alignment = Alignment(wrap_text=True)
    
            row_num += 1

    end_cell = ws1[f"A{row_num}"]
    end_cell.value = "End Manifest"
    end_cell.font = Font(bold=True)

    wb.save(filename=excel_result_path)
