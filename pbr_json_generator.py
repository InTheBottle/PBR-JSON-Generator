import os
import json
import shutil
from pathlib import Path
import mobase

try:
    from PyQt6.QtWidgets import (
        QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget,
        QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox, QLineEdit
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
            QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox, QLineEdit
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
                QListWidgetItem, QPushButton, QDialogButtonBox, QScrollArea, QCheckBox, QLineEdit
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
            class QLineEdit:
                def __init__(self, parent=None):
                    pass
                def text(self):
                    return ""
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
        self.setWindowTitle("Select Mods")
        self.setMinimumWidth(400)
        self.mods = mods
        self.filtered_mods = mods
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Search mods by name:"))
        self.mod_search_bar = QLineEdit(self)
        self.mod_search_bar.textChanged.connect(self.filter_mods)
        layout.addWidget(self.mod_search_bar)

        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(self.handle_select_all)
        layout.addWidget(self.select_all_checkbox)

        self.update_existing_checkbox = QCheckBox("Only update texture paths in existing JSONs")
        self.update_existing_checkbox.clicked.connect(self.toggle_mod_selection)
        layout.addWidget(self.update_existing_checkbox)

        self.rename_checkbox = QCheckBox("Enable renaming")
        layout.addWidget(self.rename_checkbox)

        self.list_widget = QListWidget(self)
        self.populate_mod_list(self.filtered_mods)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def filter_mods(self):
        search_text = self.mod_search_bar.text().lower()
        self.filtered_mods = [mod for mod in self.mods if search_text in mod.name.lower()]
        self.list_widget.clear()
        self.populate_mod_list(self.filtered_mods)

    def populate_mod_list(self, mods):
        for mod_folder in mods:
            item_text = mod_folder.name
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, mod_folder)
            item.setFlags(item.flags() | ITEM_IS_USER_CHECKABLE | ITEM_IS_ENABLED)
            item.setCheckState(UNCHECKED)
            self.list_widget.addItem(item)

    def handle_select_all(self):
        all_checked = self.select_all_checkbox.isChecked()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(CHECKED if all_checked else UNCHECKED)

    def toggle_mod_selection(self):
        enabled = not self.update_existing_checkbox.isChecked()
        self.list_widget.setEnabled(enabled)
        self.select_all_checkbox.setEnabled(enabled)
        if not enabled:
            for i in range(self.list_widget.count()):
                self.list_widget.item(i).setCheckState(UNCHECKED)

    def get_selected_mods(self):
        selected_mods = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == CHECKED:
                mod_folder = item.data(USER_ROLE)
                selected_mods.append(mod_folder)
        return selected_mods

    def is_update_existing_only(self):
        return self.update_existing_checkbox.isChecked()

    def is_rename_enabled(self):
        return self.rename_checkbox.isChecked()

class PBRNifPatcherSelectionDialog(QDialog):
    def __init__(self, mods, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Mods With PBRNifPatcher Folders")
        self.setMinimumWidth(400)
        self.mods = mods
        self.filtered_mods = mods
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Search mods by name:"))
        self.mod_search_bar = QLineEdit(self)
        self.mod_search_bar.textChanged.connect(self.filter_mods)
        layout.addWidget(self.mod_search_bar)

        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(self.handle_select_all)
        layout.addWidget(self.select_all_checkbox)

        self.rename_checkbox = QCheckBox("Enable rename")
        layout.addWidget(self.rename_checkbox)

        self.list_widget = QListWidget(self)
        self.populate_mod_list(self.filtered_mods)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def filter_mods(self):
        search_text = self.mod_search_bar.text().lower()
        self.filtered_mods = [mod for mod in self.mods if search_text in mod.name.lower()]
        self.list_widget.clear()
        self.populate_mod_list(self.filtered_mods)

    def populate_mod_list(self, mods):
        for mod_folder in mods:
            item_text = mod_folder.name
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, mod_folder)
            item.setFlags(item.flags() | ITEM_IS_USER_CHECKABLE | ITEM_IS_ENABLED)
            item.setCheckState(UNCHECKED)
            self.list_widget.addItem(item)

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

    def is_rename_enabled(self):
        return self.rename_checkbox.isChecked()

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
            mods_with_pbrnifpatcher = []
            for mod_folder in mods_path.iterdir():
                if any(skip in mod_folder.name.lower() for skip in ["texgen", "dyndolod"]):
                    continue
                if (mod_folder / "meta.ini").exists() and (mod_folder / "Textures" / "PBR").exists():
                    mods_with_pbr.append(mod_folder)
                if (mod_folder / "PBRNifPatcher").exists():
                    mods_with_pbrnifpatcher.append(mod_folder)

            if not mods_with_pbr and not mods_with_pbrnifpatcher:
                QMessageBox.information(
                    self.__parent_widget,
                    "No Mods Found",
                    "No mods with a Textures/PBR or PBRNifPatcher folder were found. Ensure your mods are correctly set up."
                )
                return

            dialog = ModSelectionDialog(mods_with_pbr, self.__parent_widget)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            update_existing_only = dialog.is_update_existing_only()
            rename_enabled = dialog.is_rename_enabled()
            overall_log = []

            if update_existing_only:
                if not mods_with_pbrnifpatcher:
                    QMessageBox.information(
                        self.__parent_widget,
                        "No PBRNifPatcher Folders Found",
                        "No mods with a PBRNifPatcher folder were found."
                    )
                    return
                pbrnifpatcher_dialog = PBRNifPatcherSelectionDialog(mods_with_pbrnifpatcher, self.__parent_widget)
                if pbrnifpatcher_dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                selected_mods = pbrnifpatcher_dialog.get_selected_mods()
                rename_enabled = pbrnifpatcher_dialog.is_rename_enabled()
                if not selected_mods:
                    QMessageBox.information(
                        self.__parent_widget,
                        "No Mods Selected",
                        "You did not select any mods to process."
                    )
                    return

                pbr_existing_json_mod = mods_path / "PBR Existing JSON Output"
                pbr_existing_json_mod.mkdir(exist_ok=True)
                meta_ini = pbr_existing_json_mod / "meta.ini"
                if not meta_ini.exists():
                    with open(meta_ini, "w", encoding="utf-8") as f:
                        f.write("[General]\n")
                        f.write("managed=false\n")
                        f.write("version=1.0.0\n")
                        f.write("modid=0\n")
                        f.write("category=0\n")

                total_entries_updated = 0
                total_entries_copied = 0
                total_jsons_processed = 0
                mods_processed = 0
                for mod_folder in selected_mods:
                    mod_name = mod_folder.name
                    mod_pbr_folder = mod_folder / "Textures" / "PBR"
                    pbrnifpatcher_folder = mod_folder / "PBRNifPatcher"
                    if not mod_pbr_folder.exists() or not pbrnifpatcher_folder.exists():
                        continue

                    mod_log = []
                    json_updated = False
                    for json_file in pbrnifpatcher_folder.rglob("*.json"):
                        with open(json_file, "r", encoding="utf-8") as f:
                            existing_data = json.load(f)
                        
                        entries_to_process = []
                        if isinstance(existing_data, dict) and "entries" in existing_data:
                            entries_to_process = existing_data["entries"]
                            if not isinstance(entries_to_process, list):
                                continue
                        elif isinstance(existing_data, list):
                            entries_to_process = existing_data
                        else:
                            continue

                        if not entries_to_process:
                            continue

                        entries_updated = 0
                        entries_copied = 0
                        new_entries = []
                        for entry in entries_to_process:
                            if not (isinstance(entry, dict) and "texture" in entry):
                                new_entries.append(entry)  # Copy non-standard entries as-is
                                entries_copied += 1
                                continue
                            texture_path = entry["texture"]

                            # Search for _rmaos.dds in Textures/PBR and all subfolders
                            rmaos_found = False
                            for dds_file in mod_pbr_folder.rglob(f"{texture_path.replace('\\', '/')}_rmaos.dds"):
                                relative_path = dds_file.relative_to(mod_pbr_folder)
                                new_texture = str(relative_path.parent / relative_path.stem.replace("_rmaos", "")).replace('/', '\\')

                                new_entry = {}
                                new_entry["texture"] = new_texture
                                if rename_enabled and "_d" in new_texture:
                                    renamed_texture = new_texture.replace("_d", "")
                                    new_entry["rename"] = renamed_texture
                                    mod_log.append(f"Added rename field: {new_texture} → {renamed_texture}")

                                for key, value in entry.items():
                                    if key not in ["texture", "rename"]:
                                        new_entry[key] = value

                                new_entries.append(new_entry)
                                entries_updated += 1
                                rmaos_found = True
                                break

                            if not rmaos_found:
                                # If no _rmaos.dds is found, copy the existing entry as-is
                                new_entries.append(entry)
                                entries_copied += 1
                                mod_log.append(f"Copied unchanged texture entry: {texture_path} (No _rmaos.dds found)")

                        if entries_updated > 0 or entries_copied > 0:
                            if isinstance(existing_data, dict) and "entries" in existing_data:
                                existing_data["entries"] = new_entries
                            else:
                                existing_data = new_entries
                            output_folder = pbr_existing_json_mod / mod_name / "PBRNifPatcher" / json_file.relative_to(pbrnifpatcher_folder).parent
                            output_folder.mkdir(parents=True, exist_ok=True)
                            output_json_path = output_folder / json_file.name
                            with open(output_json_path, "w", encoding="utf-8") as f:
                                json.dump(existing_data, f, indent=4)
                            total_entries_updated += entries_updated
                            total_entries_copied += entries_copied
                            total_jsons_processed += 1
                            json_updated = True
                            mod_log.append(f"Updated texture path in: {output_json_path}")

                    if json_updated:
                        mods_processed += 1
                        log_file = pbr_existing_json_mod / mod_name / "PBRNifPatcher" / "update_log.txt"
                        log_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(log_file, "w", encoding="utf-8") as f:
                            f.write("\n".join(mod_log))

                log_message = (
                    f"Operation complete.\n"
                    f"Mods processed: {mods_processed}\n"
                    f"JSON files processed: {total_jsons_processed}\n"
                    f"Entries updated: {total_entries_updated}\n"
                    f"Entries copied unchanged: {total_entries_copied}"
                )
                QMessageBox.information(
                    self.__parent_widget,
                    "PBR Json Generator",
                    log_message
                )

            else:
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

                selected_mods = dialog.get_selected_mods()
                if not selected_mods:
                    QMessageBox.information(
                        self.__parent_widget,
                        "No Mods Selected",
                        "You did not select any mods to process."
                    )
                    return

                total_files_processed = 0
                for base_path in selected_mods:
                    mod_name = base_path.name
                    mod_pbr_folder = base_path / "Textures" / "PBR"
                    output_folder = pbr_json_mod / mod_name / "PBRNifPatcher"
                    output_folder.mkdir(parents=True, exist_ok=True)
                    mod_log = []
                    found_dds = False
                    for dds_file in mod_pbr_folder.rglob("*_rmaos.dds"):
                        relative_path = dds_file.relative_to(mod_pbr_folder)
                        base_name = dds_file.stem.replace("_rmaos", "")
                        final_path = relative_path.parent / base_name
                        texture_str = str(final_path).replace('/', '\\')

                        found_dds = True
                        parent_folder = output_folder / relative_path.parent
                        parent_folder.mkdir(parents=True, exist_ok=True)
                        json_path = parent_folder / f"{base_name}.json"

                        if json_path.exists():
                            with open(json_path, "r", encoding="utf-8") as f:
                                existing_data = json.load(f)
                            if existing_data and isinstance(existing_data, list) and len(existing_data) > 0:
                                new_entry = {}
                                new_entry["texture"] = texture_str
                                if rename_enabled and "_d" in texture_str:
                                    renamed_texture = texture_str.replace("_d", "")
                                    new_entry["rename"] = renamed_texture
                                    mod_log.append(f"Added rename field: {texture_str} → {renamed_texture}")

                                for key, value in existing_data[0].items():
                                    if key not in ["texture", "rename"]:
                                        new_entry[key] = value

                                with open(json_path, "w", encoding="utf-8") as f:
                                    json.dump([new_entry], f, indent=4)
                                mod_log.append(f"Updated texture path in: {json_path}")
                                total_files_processed += 1
                                continue

                        glow_exists = (dds_file.parent / f"{base_name}_g.dds").exists()
                        fuzz_exists = (dds_file.parent / f"{base_name}_f.dds").exists()
                        parallax_exists = (dds_file.parent / f"{base_name}_p.dds").exists()
                        subsurface_exists = (dds_file.parent / f"{base_name}_s.dds").exists()
                        cnr_exists = (dds_file.parent / f"{base_name}_cnr.dds").exists()

                        entry = {}
                        entry["texture"] = texture_str
                        if rename_enabled and "_d" in texture_str:
                            renamed_texture = texture_str.replace("_d", "")
                            entry["rename"] = renamed_texture
                            mod_log.append(f"Added rename field: {texture_str} → {renamed_texture}")

                        entry["emissive"] = glow_exists
                        entry["parallax"] = parallax_exists
                        entry["subsurface"] = subsurface_exists
                        entry["subsurface_foliage"] = False
                        entry["specular_level"] = 0.04
                        entry["subsurface_color"] = [1, 1, 1]
                        entry["roughness_scale"] = 1
                        entry["subsurface_opacity"] = 1
                        entry["smooth_angle"] = 75
                        entry["displacement_scale"] = 1

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

                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump([entry], f, indent=4)
                        mod_log.append(f"Created: {json_path}")
                        total_files_processed += 1
                    if not found_dds:
                        mod_log.append(f"Skipped {mod_name}: No _rmaos.dds files found in Textures/PBR")

                    log_file = output_folder / "generation_log.txt"
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(mod_log))

                log_message = f"Operation complete. Files processed: {total_files_processed}"
                QMessageBox.information(
                    self.__parent_widget,
                    "PBR Json Generator",
                    log_message
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
