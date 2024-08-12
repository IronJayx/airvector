import os
import zipfile
import json


class FileToZip:
    def __init__(
            self, 
            write_client
        ):
        self.write_client = write_client


    def zip_folder(self, folder_path, output_path):
        """Zip the contents of an entire folder (with its paths) and save it to a zip file."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as ziph:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

    def run(
        self,
        file_path: str,
        destination_blob: str,
    ):
        zip_dir = f".cache/azure/chroma"
        os.makedirs(zip_dir, exist_ok=True)

        zip_file_path = os.path.join(zip_dir, destination_blob)

        # Zip the folder
        self.zip_folder(file_path, zip_file_path)

        self.write_client.write_blob(
            file_path=zip_file_path,
            blob_name=destination_blob
        )
