import os
import json
import shutil
from pathlib import Path
import mobase

try:
    from PyQt6.QtWidgets import (
        QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget,
        QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox
    )
    from PyQt6.QtGui import QIcon
    from PyQt6.QtCore import Qt
    ITEM_IS_USER_CHECKABLE = Qt.ItemFlag.ItemIsUserCheckable
    ITEM_IS_ENABLED = Qt.ItemFlag.ItemIsEnabled
    USER_ROLE = Qt.ItemDataRole.UserRole
    CHECKED = Qt.CheckState.Checked
    UNCHECKED = Qt.CheckState.Unchecked
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget,
            QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox
        )
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import Qt
        ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
        ITEM_IS_ENABLED = Qt.ItemIsEnabled
        USER_ROLE = Qt.UserRole
        CHECKED = Qt.Checked
        UNCHECKED = Qt.Unchecked
    except ImportError:
        try:
            from PySide2.QtWidgets import (
                QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget,
                QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox
            )
            from PySide2.QtGui import QIcon
            from PySide2.QtCore import Qt
            ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
            ITEM_IS_ENABLED = Qt.ItemIsEnabled
            USER_ROLE = Qt.UserRole
            CHECKED = Qt.Checked
            UNCHECKED = Qt.Unchecked
        except ImportError:
            class QMessageBox:
                @staticmethod
                def information(parent, title, message):
                    print(f"INFO [{title}]: {message}")
                @staticmethod
                def warning(parent, title, message):
                    print(f"WARNING [{title}]: {message}")
                @staticmethod
                def critical(parent, title, message):
                    print(f"CRITICAL [{title}]: {message}")
                class StandardButton:
                    Ok = 1024
                    Cancel = 4194304
                    Yes = 16384
                    No = 65536
            class QDialog:
                class DialogCode:
                    Accepted = 1
                    Rejected = 0
                def __init__(self, parent=None):
                    pass
                def exec(self):
                    return 0
            class QVBoxLayout:
                def __init__(self, parent=None):
                    pass
                def addWidget(self, widget):
                    pass
                def addLayout(self, layout):
                    pass
            class QLabel:
                def __init__(self, text=""):
                    pass
            class QListWidget:
                def __init__(self, parent=None):
                    self._items = []
                def addItem(self, item):
                    self._items.append(item)
                def count(self):
                    return len(self._items)
                def item(self, index):
                    return self._items[index]
            class QListWidgetItem:
                def __init__(self, text=""):
                    self._text = text
                    self._checked = False
                    self._data = None
                def text(self):
                    return self._text
                def setData(self, role, value):
                    self._data = value
                def data(self, role):
                    return self._data
                def setFlags(self, flags):
                    pass
                def setCheckState(self, state):
                    self._checked = (state == 2)
                def checkState(self):
                    return 2 if self._checked else 0
            class QPushButton:
                def __init__(self, text=""):
                    pass
            class QDialogButtonBox:
                class StandardButton:
                    Ok = 1024
                    Cancel = 4194304
                def __init__(self, buttons):
                    pass
                def accepted(self):
                    pass
                def rejected(self):
                    pass
            class QScrollArea:
                def __init__(self, parent=None):
                    pass
            class QCheckBox:
                def __init__(self, text=""):
                    pass
            class QIcon:
                pass
            class Qt:
                ItemIsUserCheckable = 1
                ItemIsEnabled = 2
                Checked = 2
                Unchecked = 0
                class DialogCode:
                    Accepted = 1
                    Rejected = 0
            ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
            ITEM_IS_ENABLED = Qt.ItemIsEnabled
            USER_ROLE = 32
            CHECKED = 2
            UNCHECKED = 0

class ModSelectionDialog(QDialog):
    def __init__(self, mods, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Mods With PBR Textures")
        self.setMinimumWidth(400)
        self.mods = mods

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select one or more mods containing a Textures/PBR folder:"))

        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(self.handle_select_all)
        layout.addWidget(self.select_all_checkbox)

        self.list_widget = QListWidget(self)
        for mod_folder in mods:
            item_text = mod_folder.name
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, mod_folder)
            item.setFlags(item.flags() | ITEM_IS_USER_CHECKABLE | ITEM_IS_ENABLED)
            item.setCheckState(UNCHECKED)
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def handle_select_all(self):
        all_checked = self.select_all_checkbox.isChecked()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if all_checked:
                item.setCheckState(CHECKED)
            else:
                item.setCheckState(UNCHECKED)

    def get_selected_mods(self):
        selected_mods = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == CHECKED:
                mod_folder = item.data(USER_ROLE)
                selected_mods.append(mod_folder)
        return selected_mods

class PBRJsonGenerator(mobase.IPluginTool):
    def __init__(self):
        super().__init__()
        self.__organizer = None
        self.__parent_widget = None

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.__organizer = organizer
        return True

    def name(self):
        return "PBR Json Generator"

    def author(self):
        return "Bottle"

    def description(self):
        return "Generates and updates JSON configs based on textures."

    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

    def isActive(self):
        return True

    def settings(self):
        return []

    def displayName(self):
        return "PBR Json Generator"

    def tooltip(self):
        return "Scans Textures/PBR and creates/upgrades JSON configs."

    def icon(self):
        return QIcon()

    def setParentWidget(self, widget):
        self.__parent_widget = widget

    def display(self):
        try:
            mods_path = Path(self.__organizer.modsPath())
            mods_with_pbr = []
            for mod_folder in mods_path.iterdir():
                if any(skip in mod_folder.name.lower() for skip in ["texgen", "dyndolod"]):
                    continue
                if (mod_folder / "meta.ini").exists() and (mod_folder / "Textures" / "PBR").exists():
                    mods_with_pbr.append(mod_folder)

            if not mods_with_pbr:
                QMessageBox.information(
                    self.__parent_widget,
                    "No Mods Found",
                    "No mods with a Textures/PBR folder were found."
                )
                return

            dialog = ModSelectionDialog(mods_with_pbr, self.__parent_widget)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            selected_mods = dialog.get_selected_mods()
            if not selected_mods:
                QMessageBox.information(
                    self.__parent_widget,
                    "No Mods Selected",
                    "You did not select any mods to process."
                )
                return

            overall_log = []

            for base_path in selected_mods:
                textures_folder = base_path / "Textures" / "PBR"
                output_folder = base_path / "PBRNifPatcher"
                example_config = base_path / "ExampleConfig.json"

                output_folder.mkdir(parents=True, exist_ok=True)
                log = []

                for dds_file in textures_folder.rglob("*_rmaos.dds"):
                    relative_path = dds_file.relative_to(textures_folder)
                    parent_folder = relative_path.parent
                    stem = dds_file.stem.replace("_rmaos", "")
                    final_path = parent_folder / stem
                    texture_str = str(final_path).replace('/', '\\')
                    target_dir = output_folder / parent_folder
                    target_dir.mkdir(parents=True, exist_ok=True)
                    new_json = target_dir / f"{stem}.json"
                    with open(new_json, "w", encoding="utf-8") as f:
                        json.dump([
                            {
                                "texture": texture_str,
                                "emissive": False,
                                "parallax": True,
                                "subsurface_foliage": False,
                                "subsurface": False,
                                "specular_level": 0.04,
                                "subsurface_color": [1, 1, 1],
                                "roughness_scale": 1,
                                "subsurface_opacity": 1,
                                "smooth_angle": 75,
                                "displacement_scale": 1
                            }
                        ], f, indent=4)
                    log.append("Created: {}".format(new_json))

                for json_file in output_folder.rglob("*.json"):
                    base_name = json_file.stem
                    rmaos_candidates = list(textures_folder.rglob(f"{base_name}_rmaos.dds"))
                    if rmaos_candidates:
                        rel_path = rmaos_candidates[0].relative_to(textures_folder)
                        parent_folder = rel_path.parent
                        new_stem = rmaos_candidates[0].stem.replace("_rmaos", "")
                        final_path = parent_folder / new_stem
                        full_texture_path = str(final_path).replace('/', '\\')
                    else:
                        full_texture_path = base_name

                    checks = {
                        "glow": any(textures_folder.rglob(f"{base_name}_g.dds")),
                        "fuzz": any(textures_folder.rglob(f"{base_name}_f.dds")),
                        "parallax": any(textures_folder.rglob(f"{base_name}_p.dds")),
                        "subsurface": any(textures_folder.rglob(f"{base_name}_s.dds")),
                        "cnr": any(textures_folder.rglob(f"{base_name}_cnr.dds")),
                    }

                    try:
                        if checks["fuzz"]:
                            data = [{
                                "texture": full_texture_path,
                                "emissive": checks["glow"],
                                "parallax": checks["parallax"],
                                "subsurface_foliage": False,
                                "subsurface": checks["subsurface"],
                                "specular_level": 0.04,
                                "subsurface_color": [1, 1, 1],
                                "roughness_scale": 1,
                                "subsurface_opacity": 1,
                                "smooth_angle": 75,
                                "displacement_scale": 1,
                                "fuzz": {"texture": True}
                            }]
                        elif checks["subsurface"] and checks["cnr"]:
                            data = [{
                                "texture": full_texture_path,
                                "emissive": checks["glow"],
                                "parallax": checks["parallax"],
                                "subsurface_foliage": False,
                                "subsurface": checks["subsurface"],
                                "specular_level": 0.04,
                                "subsurface_color": [1, 1, 1],
                                "roughness_scale": 1,
                                "subsurface_opacity": 1,
                                "smooth_angle": 75,
                                "displacement_scale": 1,
                                "multilayer": True,
                                "coat_diffuse": True,
                                "coat_normal": True,
                                "coat_parallax": True,
                                "coat_strength": 1.0,
                                "coat_roughness": 1.0,
                                "coat_specular_level": 0.018
                            }]
                        else:
                            data = [{
                                "texture": full_texture_path,
                                "emissive": checks["glow"],
                                "parallax": checks["parallax"],
                                "subsurface_foliage": False,
                                "subsurface": checks["subsurface"],
                                "specular_level": 0.04,
                                "subsurface_color": [1, 1, 1],
                                "roughness_scale": 1,
                                "subsurface_opacity": 1,
                                "smooth_angle": 75,
                                "displacement_scale": 1
                            }]
                        with open(json_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)
                        log.append("Updated: {}".format(json_file))
                    except Exception as write_error:
                        log.append("Failed to update {}: {}".format(json_file, write_error))

                overall_log.extend(log)

            QMessageBox.information(
                self.__parent_widget,
                "PBR Json Generator",
                "Operation complete. Files processed: {}".format(len(overall_log))
            )

        except Exception as e:
            QMessageBox.critical(
                self.__parent_widget,
                "PBR Json Generator - Error",
                "An error occurred:\n{}".format(str(e))
            )

def createPlugin():
    return PBRJsonGenerator()