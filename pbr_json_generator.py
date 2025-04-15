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
            item.setCheckState(CHECKED if all_checked else UNCHECKED)
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
        return "Generates JSON configs into PBR JSON Output/[ModName]/PBRNifPatcher folders, single pass."
    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)
    def isActive(self):
        return True
    def settings(self):
        return []
    def displayName(self):
        return "PBR Json Generator"
    def tooltip(self):
        return "Scans Textures/PBR once, building JSON with fuzz/glow/coat in the same pass."
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
            pbr_json_mod = mods_path / "PBR JSON Output"
            pbr_json_mod.mkdir(exist_ok=True)
            meta_ini = pbr_json_mod / "meta.ini"
            if not meta_ini.exists():
                with open(meta_ini, "w", encoding="utf-8") as f:
                    f.write("[General]\n")
                    f.write("managed=false\n")
                    f.write("version=1.0.0\n")
                    f.write("modid=0\n")
                    f.write("category=0\n")
            for base_path in selected_mods:
                mod_name = base_path.name
                mod_pbr_folder = base_path / "Textures" / "PBR"
                output_folder = pbr_json_mod / mod_name / "PBRNifPatcher"
                output_folder.mkdir(parents=True, exist_ok=True)
                for dds_file in mod_pbr_folder.rglob("*_rmaos.dds"):
                    relative_path = dds_file.relative_to(mod_pbr_folder)
                    parent_folder = output_folder / relative_path.parent
                    parent_folder.mkdir(parents=True, exist_ok=True)
                    base_name = dds_file.stem.replace("_rmaos", "")
                    final_path = relative_path.parent / base_name
                    texture_str = str(final_path).replace('/', '\\')

                    glow_exists = (dds_file.parent / f"{base_name}_g.dds").exists()
                    fuzz_exists = (dds_file.parent / f"{base_name}_f.dds").exists()
                    parallax_exists = (dds_file.parent / f"{base_name}_p.dds").exists()
                    subsurface_exists = (dds_file.parent / f"{base_name}_s.dds").exists()
                    cnr_exists = (dds_file.parent / f"{base_name}_cnr.dds").exists()

                    entry = {
                        "texture": texture_str,
                        "emissive": glow_exists,
                        "parallax": parallax_exists,
                        "subsurface": subsurface_exists,
                        "subsurface_foliage": False,
                        "specular_level": 0.04,
                        "subsurface_color": [1, 1, 1],
                        "roughness_scale": 1,
                        "subsurface_opacity": 1,
                        "smooth_angle": 75,
                        "displacement_scale": 1
                    }

                    if fuzz_exists:
                        entry["fuzz"] = {"texture": True}
                    elif subsurface_exists and cnr_exists:
                        entry["multilayer"] = True
                        entry["coat_diffuse"] = True
                        entry["coat_normal"] = True
                        entry["coat_parallax"] = True
                        entry["coat_strength"] = 1.0
                        entry["coat_roughness"] = 1.0
                        entry["coat_specular_level"] = 0.018

                    new_json = parent_folder / f"{base_name}.json"
                    with open(new_json, "w", encoding="utf-8") as f:
                        json.dump([entry], f, indent=4)
                    overall_log.append(f"Created: {new_json}")
            QMessageBox.information(
                self.__parent_widget,
                "PBR Json Generator",
                f"Operation complete. Files processed: {len(overall_log)}"
            )
            try:
                self.__organizer.refresh(True)
            except:
                pass
        except Exception as e:
            QMessageBox.critical(
                self.__parent_widget,
                "PBR Json Generator - Error",
                f"An error occurred:\n{str(e)}"
            )

def createPlugin():
    return PBRJsonGenerator()
