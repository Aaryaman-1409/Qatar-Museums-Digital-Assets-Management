from msilib.schema import File
import PySimpleGUI as sg
from pathlib import Path
from src.tasks import manager
from src.gui import gui_params


wd = Path(__file__).parent

try:
    temp_path = Path.home() / 'AMPIngest/'
    temp_path.mkdir(parents=True)
    SETTINGS_PATH = temp_path
except FileExistsError:
    SETTINGS_PATH = Path.home() / 'AMPIngest'

def the_gui(wd, fields, fa):
    wait_until_completion = False

    sg.theme("SystemDefault")
    models_dict = {
        f"model{i}": [
            [sg.Text(fields["models"].output[i])],
            [
                sg.Listbox(
                    fields["models"].value,
                    key=fields["models"].key[i],
                    size=fa.form_size,
                    default_values=sg.user_settings_get_entry(fields["models"].key[i]),
                )
            ],
        ]
        for i in range(fa.models_size)
    }

    try:
        security_policy_text = ",".join(
            sg.user_settings_get_entry(fields["security"].key)
        )
    except TypeError:
        security_policy_text = ""

    layout = [
        [sg.Text("Enter Source Folder:")],
        [
            sg.InputText(
                key=fields["src"].key,
                default_text=sg.user_settings_get_entry(fields["src"].key),
            ),
            sg.FolderBrowse(),
        ],
        [sg.Text("Enter Destination Folder:")],
        [
            sg.InputText(
                key=fields["dest"].key,
                default_text=sg.user_settings_get_entry(fields["dest"].key),
            ),
            sg.FolderBrowse(),
        ],
        [sg.Text("", key=fields["dest"].error)],
        [sg.HorizontalSeparator(pad=fa.seperator_padding)],
        [sg.Text("Enter security policy or choose from list below:")],
        [
            sg.InputText(
                key=fields["security"].output,
                default_text=security_policy_text,
            ),
        ],
        [
            sg.Listbox(
                values=fields["security"].value,
                size=fa.form_size,
                select_mode="multiple",
                key=fields["security"].key,
                enable_events=True,
                default_values=sg.user_settings_get_entry(fields["security"].key),
            ),
        ],
        [sg.Text("", key=fields["security"].error)],
        [sg.HorizontalSeparator(pad=fa.seperator_padding)],
        [
            sg.Text("Choose mappings from file type to model:"),
        ],
        [sg.Column(models) for models in models_dict.values()],
        [sg.Text("", key=fields["models"].error)],
        [sg.HorizontalSeparator(pad=fa.seperator_padding)],
        [sg.Text("Choose tasks:")],
        [
            sg.Listbox(
                values=fields["tasks"].value,
                key=fields["tasks"].key,
                size=fa.form_size,
                select_mode="multiple",
                default_values=sg.user_settings_get_entry(fields["tasks"].key),
            ),
        ],
        [
            sg.Text(
                "Choose email recipients (for multiple recipients, seperate emails by commas)"
            )
        ],
        [
            sg.InputText(
                key=fields["email"].key,
                default_text=sg.user_settings_get_entry(fields["email"].key),
            ),
            sg.Button("Run script", bind_return_key=True),
            sg.Button("Save all options"),
        ],
        [sg.Text("", key=fields["email"].error)],
        [sg.Text("", key=fields["tasks"].error)],
    ]
    window = sg.Window("AMP Ingest Script", layout)

    while True:
        event, values = window.read()

        if wait_until_completion:
            window[fields["tasks"].error].update(
                "Waiting for tasks to complete...", text_color="orange"
            )

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        elif event == fields["security"].key:
            try:
                security_policy = ",".join(values[event])
            except TypeError:
                security_policy = ""
            window[fields["security"].output].update(value=security_policy)

        elif event == "-TASK_END-":
            wait_until_completion = False
            return_value = values[event]
            if return_value:
                window[fields["tasks"].error].update(
                    "Tasks completed succesfully", text_color="green"
                )
            else:
                window[fields["tasks"].error].update(
                    "Some error occured. Check command prompt for more information",
                    text_color="red",
                )

        elif event == "Save all options":
            for field in fields.values():
                if field.key:
                    try:
                        sg.user_settings_set_entry(field.key, values[field.key])
                    except KeyError:  # models field
                        for i in range(fa.models_size):
                            sg.user_settings_set_entry(
                                field.key[i], values[field.key[i]]
                            )

        elif event == "Run script":
            revert_errors_to_default(window, fields)
            errors = check_errors_gui(window, values, fa, fields)
            if errors > 0:
                pass
            elif not wait_until_completion:

                wait_until_completion = True

                filetype_to_model = {
                    fields["models"].output[i]: values[fields["models"].key[i]][0]
                    for i in range(fa.models_size)
                }

                tasks_chosen = list(
                    set(fields["tasks"].value).intersection(
                        set(values[fields["tasks"].key])
                    )
                )

                recipients = values[fields["email"].key].strip().split(",")

                window[fields["tasks"].error].update(
                    "Waiting for tasks to complete...", text_color="orange"
                )

                window.perform_long_operation(
                    lambda: manager.main_task(
                        wd,
                        values[fields["src"].key],
                        values[fields["dest"].key],
                        values[fields["security"].output],
                        filetype_to_model,
                        tasks_chosen,
                        recipients,
                    ),
                    "-TASK_END-",
                )
            elif wait_until_completion:
                window[fields["tasks"].error].update(
                    "Waiting for tasks to complete...", text_color="orange"
                )


def check_errors_gui(window, values, fa, fields):
    errors = 0
    all_models_chosen = all(
        [values[fields["models"].key[i]] for i in range(fa.models_size)]
    )
    if not all_models_chosen:
        errors += 1
        window[fields["models"].error].update(
            "You must choose a mapping for all file types!", text_color="red"
        )

    if len(values[fields["security"].key]) < 1:
        errors += 1
        window[fields["security"].error].update(
            "You must choose at least one security policy!", text_color="red"
        )

    if not values[fields["tasks"].key]:
        errors += 1
        window[fields["tasks"].error].update(
            "You must choose at least one task", text_color="red"
        )

    if fields["tasks"].value[0] in values[fields["tasks"].key]:
        if not (
            Path(values[fields["src"].key].rstrip()).is_dir()
            and Path(values[fields["dest"].key].rstrip()).is_dir()
            and values[fields["src"].key]
            and values[fields["dest"].key]
        ):
            errors += 1
            window[fields["dest"].error].update(
                "Invalid Path. Either use the Browse button or type the path correctly",
                text_color="red",
            )

    if fields["tasks"].value[1] in values[fields["tasks"].key]:
        if not values[fields['security'].output]:
            errors+=1
            window[fields['security'].error].update(
                "You must choose at least one security policy!", text_color="red"
            )
        if (
            not values[fields["dest"].key]
            or not Path(values[fields["dest"].key].rstrip()).is_dir()
        ):
            errors += 1
            window[fields["dest"].error].update(
                "Invalid Path. Either use the Browse button or type the path correctly",
                text_color="red",
            )

    if fields["tasks"].value[2] in values[fields["tasks"].key]:
        if not values[fields["email"].key]:
            errors += 1
            window[fields["email"].error].update(
                "Email recipients field can't be empty.",
                text_color="red",
            )

    return errors


def revert_errors_to_default(window, fields):
    for field in fields.values():
        if field.error:
            window[field.error].update("")


if __name__ == "__main__":
    sg.user_settings_filename(path=SETTINGS_PATH)
    the_gui(wd, gui_params.fields, gui_params.fa)
