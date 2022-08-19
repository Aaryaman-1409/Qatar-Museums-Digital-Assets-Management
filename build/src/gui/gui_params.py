from enum import Enum
from dataclasses import dataclass
from typing import Any


@dataclass
class fa:
    # defines common attributes for the fields
    form_size: tuple = (30, 4)
    seperator_padding: tuple = (0, 10)
    models_size = 4


@dataclass
class fields_info:
    key: Any = None  # defines the key for the main element. i.e: listbox
    value: Any = None  # defines any values associated with the field's main element, i.e: values for listbox
    output: Any = None  # defines the key for a field's output element, i.e: TextBox
    error: Any = (
        None  # defines the key for a field's error output element, i.e: TextBox
    )


# weird thing about enums where to get value you must to enum.field.value or enum['field'].value.
# If you do enum.field, you get enum object
# However, assigning to enum is as expected: enum.field = new_value
# That's why i changed it to dict.

fields = {
    # detailed definition of all fields in the gui.
    "src": fields_info(key="-SRC-", error="-FILE_ERROR-"),
    "dest": fields_info(key="-DEST-", error="-FILE_ERROR-"),
    "security": fields_info(
        key="-SECURITY-",
        output="-SECURITY_OUTPUT-",
        error="-SECURITY_ERROR-",
        value=(
            "ADP Designers Restricted Access",
            "G11_Reference_Mada_ext",
            "GMS Admin",
            "GMS Guest",
            "GMS Restricted",
            "GMS Unrestricted",
            "Hidden",
            "Int-dept OHS-BL Share",
            "NMOQ Collections Admin",
            "NMOQ Collections Restricted",
            "NMOQ Collections Unrestricted",
            "NMOQ_All_Staff_P",
            "NMoQ_Collections&Copyrights_mada_ext",
        ),
    ),
    "models": fields_info(
        key=tuple([f"-MODEL{i}-" for i in range(fa.models_size)]),
        output=("image", "video", "audio", "document"),
        error="-MODEL_ERROR-",
        value=(
            "Basic Properties",
            "Collections Images",
            "GMS Audio",
            "GMS Documents",
            "GMS Image",
            "GMS Video",
            "Mathaf Audio",
            "Mathaf Documents",
            "Mathaf Image",
            "Mathaf Video",
            "NMOQ Collections Audio",
            "NMOQ Collections Documents",
            "NMOQ Collections Images",
            "NMOQ Collections Videos",
            "OHS Audio",
            "OHS Documents",
            "OHS Image",
            "OHS Video",
            "PUBART Audio",
            "PUBART Documents",
            "PUBART Image",
            "PUBART Video",
            "QOSM Audio",
            "QOSM Documents",
            "QOSM Image",
            "QOSM Video",
        ),
    ),
    "tasks": fields_info(
        key="-TASKS-",
        error="-TASK_STATUS-",
        value=(
            "Copy Source to Destination",
            "Generate AMP Manifest File",
            "Email results",
        ),
    ),
    "email": fields_info(key="-EMAIL-", error="-EMAIL_ERROR-"),
}
