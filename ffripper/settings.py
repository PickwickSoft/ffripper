import yaml


class Settings:

    def __init__(self, settings_file):
        self.settings_file = settings_file
        with open(settings_file, "r") as self.file:
            self.settings = yaml.load(self.file, Loader=yaml.FullLoader)

    def __del__(self):
        self.apply_changes()
        self.file.close()

    def set_eject(self, value: bool):
        self.settings['always_eject'] = value

    def set_output_folder(self, path: str):
        self.settings['outputFolder'] = path

    def set_default_format(self, format: str):
        self.settings['standardFormat'] = format

    def apply_changes(self):
        with open(self.settings_file, "w") as file:
            yaml.dump(self.settings, file)

    def get_eject(self) -> bool:
        return self.settings['always_eject']
    
    def get_output_folder(self) -> str:
        return self.settings['outputFolder']

    def get_default_format(self) -> str:
        return self.settings['standardFormat']
