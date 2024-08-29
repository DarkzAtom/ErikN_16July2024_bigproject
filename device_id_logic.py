import shortuuid
import os


def generate_and_save_uuid(file_path="device_id.txt"):
    if not os.path.exists(file_path):
        unique_id = shortuuid.uuid()

        with open(file_path, "w") as file:
            file.write(unique_id)

        print(f"UUID has been created and saved: {unique_id}")
    else:
        with open(file_path, "r") as file:
            unique_id = file.read().strip()

        print(f"UUID has been read from the file: {unique_id}")

    return unique_id




