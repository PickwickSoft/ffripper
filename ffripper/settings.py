import yaml


class Settings:

    def __init__(self, settings_file) -> None:
        with open(settings_file, "+") as self.file:
            self.settings = yaml.load(self.file, Loader=yaml.FullLoader)

    def __del__(self) -> None:
        self.apply_changes()
        self.file.close()

    def set_eject(self, value: bool) -> None:
        self.settings['always_eject'] = value

    def set_output_folder(self, path: str) -> None:
        self.settings['outputFolder'] = path

    def set_default_format(self, format: str) -> None:
        self.settings['standardFormat'] = format

    def apply_changes(self) -> None:
        yaml.dump(self.settings, self.file)

    def get_eject(self) -> bool:
        return self.settings['always_eject']
    
    def get_output_folder(self) -> str:
        return self.settings['outputFolder']

    def get_default_format(self) -> str:
        return self.settings['standardFormat']
