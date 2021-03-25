import yaml
from ffripper.theme import Theme


class Settings:

    def __init__(self, settings_file):
        self.settings_file = settings_file
        with open(settings_file, "r") as self.file:
            self.settings = yaml.load(self.file, Loader=yaml.FullLoader)
        self.theme = Theme()

    def __del__(self):
        self.commit()
        self.file.close()

    def set_eject(self, value: bool):
        self.settings['always_eject'] = value

    def set_output_folder(self, path: str):
        self.settings['outputFolder'] = path

    def set_default_format(self, format: str):
        self.settings['standardFormat'] = format

    def set_theme(self, theme: str):
        if theme.lower() == "light":
            self.theme.set_light_theme()
            self.settings['theme'] = theme.lower()
        elif theme.lower() == "dark":
            self.theme.set_dark_theme()
            self.settings['theme'] = theme.lower()
        elif theme.lower() == "system":
            self.theme.set_system_default()
            self.settings['theme'] = theme.lower()
        self.commit()

    def set_create_album_directory(self, value: bool):
        self.settings["albumdirectory"] = value

    def set_create_artist_directory(self, value: bool):
        self.settings["artistdirectory"] = value

    def commit(self):
        with open(self.settings_file, "w") as file:
            yaml.dump(self.settings, file)

    def get_eject(self) -> bool:
        return self.settings['always_eject']
    
    def get_output_folder(self) -> str:
        return self.settings['outputFolder']

    def get_default_format(self) -> str:
        return self.settings['standardFormat']

    def get_create_album_directory(self) -> bool:
        return self.settings["albumdirectory"]

    def get_create_artist_directory(self) -> bool:
        return self.settings["artistdirectory"]

    def get_theme(self) -> str:
        return self.settings["theme"]
