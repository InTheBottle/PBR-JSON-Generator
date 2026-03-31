import json
from pathlib import Path

import mobase

# ---------------------------------------------------------------------------
# Qt Compatibility: PyQt6 -> PyQt5 -> PySide2 -> minimal stubs
# ---------------------------------------------------------------------------

try:
    from PyQt6.QtWidgets import (
        QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLabel, QListWidget, QListWidgetItem, QDialogButtonBox,
        QCheckBox, QLineEdit, QTabWidget, QDoubleSpinBox, QWidget,
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
            QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
            QLabel, QListWidget, QListWidgetItem, QDialogButtonBox,
            QCheckBox, QLineEdit, QTabWidget, QDoubleSpinBox, QWidget,
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
                QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                QLabel, QListWidget, QListWidgetItem, QDialogButtonBox,
                QCheckBox, QLineEdit, QTabWidget, QDoubleSpinBox, QWidget,
            )
            from PySide2.QtGui import QIcon
            from PySide2.QtCore import Qt

            ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
            ITEM_IS_ENABLED = Qt.ItemIsEnabled
            USER_ROLE = Qt.UserRole
            CHECKED = Qt.Checked
            UNCHECKED = Qt.Unchecked
        except ImportError:
            # Fallback stubs so the module can at least be imported in
            # environments that lack a Qt binding (e.g. linting, testing).

            class _Signal:
                """Dummy signal supporting .connect() calls."""
                def connect(self, slot):
                    pass

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

                def setWindowTitle(self, title):
                    pass

                def setMinimumWidth(self, w):
                    pass

                def setMinimumHeight(self, h):
                    pass

                def accept(self):
                    pass

                def reject(self):
                    pass

            class QVBoxLayout:
                def __init__(self, parent=None):
                    pass

                def addWidget(self, widget):
                    pass

            class QLabel:
                def __init__(self, text=""):
                    self._text = text

                def setText(self, text):
                    self._text = text

            class QListWidget:
                def __init__(self, parent=None):
                    self._items = []

                def addItem(self, item):
                    self._items.append(item)

                def count(self):
                    return len(self._items)

                def item(self, index):
                    return self._items[index]

                def clear(self):
                    self._items.clear()

                def setEnabled(self, enabled):
                    pass

            class QListWidgetItem:
                def __init__(self, text=""):
                    self._text = text
                    self._checked = False
                    self._data = None
                    self._flags = 0

                def text(self):
                    return self._text

                def setData(self, role, value):
                    self._data = value

                def data(self, role):
                    return self._data

                def flags(self):
                    return self._flags

                def setFlags(self, flags):
                    self._flags = flags

                def setCheckState(self, state):
                    self._checked = (state == 2)

                def checkState(self):
                    return 2 if self._checked else 0

            class QDialogButtonBox:
                class StandardButton:
                    Ok = 1024
                    Cancel = 4194304

                def __init__(self, buttons=0):
                    pass

                @property
                def accepted(self):
                    return _Signal()

                @property
                def rejected(self):
                    return _Signal()

            class QCheckBox:
                def __init__(self, text=""):
                    self._checked = False

                def isChecked(self):
                    return self._checked

                @property
                def clicked(self):
                    return _Signal()

                def setEnabled(self, enabled):
                    pass

            class QLineEdit:
                def __init__(self, parent=None):
                    pass

                def text(self):
                    return ""

                @property
                def textChanged(self):
                    return _Signal()

            class QTabWidget:
                def __init__(self, parent=None): pass
                def addTab(self, widget, label): pass

            class QDoubleSpinBox:
                def __init__(self, parent=None):
                    self._value = 0.0
                def setRange(self, min_val, max_val): pass
                def setDecimals(self, decimals): pass
                def setSingleStep(self, step): pass
                def setValue(self, value): self._value = value
                def value(self): return self._value
                def setEnabled(self, enabled): pass

            class QHBoxLayout:
                def __init__(self, parent=None): pass
                def addWidget(self, widget): pass

            class QFormLayout:
                def __init__(self, parent=None): pass
                def addRow(self, *args): pass

            class QWidget:
                def __init__(self, parent=None): pass
                def setLayout(self, layout): pass

            class QIcon:
                pass

            ITEM_IS_USER_CHECKABLE = 1
            ITEM_IS_ENABLED = 2
            USER_ROLE = 32
            CHECKED = 2
            UNCHECKED = 0

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLUGIN_NAME = "PBR Json Generator"
SKIP_KEYWORDS = ("texgen", "dyndolod")
PBR_TEX_REL = Path("Textures") / "PBR"
PATCHER_DIR = "PBRNifPatcher"
OUTPUT_MOD_NAME = "PBR JSON Output"
EXISTING_OUTPUT_MOD_NAME = "PBR Existing JSON Output"
META_INI_CONTENT = (
    "[General]\n"
    "managed=false\n"
    "version=1.0.0\n"
    "modid=0\n"
    "category=0\n"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rename_texture(texture_str: str):
    """Strip a trailing ``_d`` diffuse suffix and return the renamed path.

    Returns *None* when the texture does not end with ``_d``.
    """
    if texture_str.endswith("_d"):
        return texture_str[:-2]
    return None


def _build_rmaos_index(pbr_folder: Path) -> dict:
    """Build a {normalised_stem: Path} lookup for every ``*_rmaos.dds`` file.

    Keys are lower-cased, forward-slash paths relative to *pbr_folder* with
    the ``_rmaos.dds`` suffix removed (e.g. ``landscape/dirt``).
    """
    index = {}
    for dds in pbr_folder.rglob("*_rmaos.dds"):
        rel = dds.relative_to(pbr_folder)
        key = str(rel).replace("\\", "/").lower()
        key = key[: -len("_rmaos.dds")]
        index[key] = dds
    return index


# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------

class BaseModSelectionDialog(QDialog):
    """Reusable dialog: search bar, select-all, rename checkbox, mod list."""

    def __init__(self, mods, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        self.mods = sorted(mods, key=lambda m: m.name.lower())
        self.filtered_mods = list(self.mods)

        self.main_layout = QVBoxLayout(self)

        # Search
        self.main_layout.addWidget(QLabel("Search mods by name:"))
        self.mod_search_bar = QLineEdit(self)
        self.mod_search_bar.textChanged.connect(self._filter_mods)
        self.main_layout.addWidget(self.mod_search_bar)

        # Select all
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(self._handle_select_all)
        self.main_layout.addWidget(self.select_all_checkbox)

    def _finish_layout(self):
        """Append the rename checkbox, mod list, and OK/Cancel buttons.

        Call this at the *end* of every subclass ``__init__`` (after any
        extra widgets have been added to ``self.main_layout``).
        """
        self.rename_checkbox = QCheckBox("Enable renaming")
        self.main_layout.addWidget(self.rename_checkbox)

        self.count_label = QLabel(f"{len(self.mods)} mods found")
        self.main_layout.addWidget(self.count_label)

        self.list_widget = QListWidget(self)
        self._populate_mod_list(self.filtered_mods)
        self.main_layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(buttons)

    # -- Slots ----------------------------------------------------------------

    def _filter_mods(self):
        search_text = self.mod_search_bar.text().lower()
        self.filtered_mods = [
            m for m in self.mods if search_text in m.name.lower()
        ]
        self.list_widget.clear()
        self._populate_mod_list(self.filtered_mods)
        self.count_label.setText(
            f"Showing {len(self.filtered_mods)} of {len(self.mods)} mods"
        )

    def _populate_mod_list(self, mods):
        for mod_folder in mods:
            item = QListWidgetItem(mod_folder.name)
            item.setData(USER_ROLE, mod_folder)
            item.setFlags(
                item.flags() | ITEM_IS_USER_CHECKABLE | ITEM_IS_ENABLED
            )
            item.setCheckState(UNCHECKED)
            self.list_widget.addItem(item)

    def _handle_select_all(self):
        state = CHECKED if self.select_all_checkbox.isChecked() else UNCHECKED
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(state)

    # -- Public API -----------------------------------------------------------

    def get_selected_mods(self):
        return [
            self.list_widget.item(i).data(USER_ROLE)
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == CHECKED
        ]

    def is_rename_enabled(self):
        return self.rename_checkbox.isChecked()


class ModSelectionDialog(BaseModSelectionDialog):
    """Mod-selection dialog with an extra *update existing only* option."""

    def __init__(self, mods, parent=None):
        super().__init__(mods, "Select Mods", parent)

        self.update_existing_checkbox = QCheckBox(
            "Only update texture paths in existing JSONs"
        )
        self.update_existing_checkbox.clicked.connect(
            self._toggle_mod_selection
        )
        self.main_layout.addWidget(self.update_existing_checkbox)

        self._finish_layout()

    def _toggle_mod_selection(self):
        enabled = not self.update_existing_checkbox.isChecked()
        self.list_widget.setEnabled(enabled)
        self.select_all_checkbox.setEnabled(enabled)
        if not enabled:
            for i in range(self.list_widget.count()):
                self.list_widget.item(i).setCheckState(UNCHECKED)

    def is_update_existing_only(self):
        return self.update_existing_checkbox.isChecked()


class PBRNifPatcherSelectionDialog(BaseModSelectionDialog):
    """Simpler dialog for mods that already contain PBRNifPatcher folders."""

    def __init__(self, mods, parent=None):
        super().__init__(
            mods, "Select Mods With PBRNifPatcher Folders", parent
        )
        self._finish_layout()


class PBRSettingsDialog(QDialog):
    """Dialog for configuring which PBR JSON fields to include and their
    default values.  Organised in tabs matching the PGPatcher wiki sections.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PBR JSON Settings")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)

        self._float_settings = {}   # key -> (QCheckBox, QDoubleSpinBox)
        self._bool_settings = {}    # key -> (QCheckBox include, QCheckBox val)
        self._color_settings = {}   # key -> (QCheckBox, [QDoubleSpinBox, ...])

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Configure which fields to include in generated JSON and "
            "their default values.\nEmissive, parallax, subsurface, fuzz,"
            " and coat are auto-detected from companion textures."
        ))

        tabs = QTabWidget()
        layout.addWidget(tabs)
        tabs.addTab(self._build_general_tab(), "General")
        tabs.addTab(self._build_emissive_tab(), "Emissive")
        tabs.addTab(self._build_parallax_tab(), "Parallax")
        tabs.addTab(self._build_subsurface_tab(), "Subsurface")
        tabs.addTab(self._build_coat_tab(), "Coat")
        tabs.addTab(self._build_fuzz_tab(), "Fuzz")
        tabs.addTab(self._build_extras_tab(), "Hair / Glint")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # -- Tab builders -------------------------------------------------------

    def _build_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self._add_float("specular_level", form, "Specular Level",
                        0.04, 0, 10)
        self._add_float("roughness_scale", form, "Roughness Scale",
                        1.0, 0, 10)
        self._add_float("smooth_angle", form, "Smooth Angle",
                        75, 0, 180, decimals=1)
        self._add_bool("subsurface_foliage", form, "Subsurface Foliage",
                       False, True)
        self._add_bool("vertex_colors", form, "Vertex Colors",
                       True, False)
        self._add_float("vertex_color_lum_mult", form,
                        "Vertex Color Lum Mult", 1.0, 0, 10, included=False)
        self._add_float("vertex_color_sat_mult", form,
                        "Vertex Color Sat Mult", 1.0, 0, 10, included=False)
        self._add_bool("zbuffer_write", form, "ZBuffer Write", True, False)
        self._add_bool("auto_uv", form, "Auto UV", False, False)
        self._add_float("uv_scale", form, "UV Scale",
                        1.0, 0, 100, included=False)
        return w

    def _build_emissive_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel(
            "Emissive is auto-detected from _g.dds textures."
        ))
        self._add_float("emissive_scale", form, "Emissive Scale",
                        1.0, 0, 100, included=False)
        self._add_color("emissive_color", form, "Emissive Color",
                        (0, 0, 0, 0), included=False)
        return w

    def _build_parallax_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel(
            "Parallax is auto-detected from _p.dds textures."
        ))
        self._add_float("displacement_scale", form, "Displacement Scale",
                        1.0, 0, 10)
        return w

    def _build_subsurface_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel(
            "Subsurface is auto-detected from _s.dds textures."
        ))
        self._add_color("subsurface_color", form, "Subsurface Color",
                        (1, 1, 1))
        self._add_float("subsurface_opacity", form, "Subsurface Opacity",
                        1.0, 0, 1)
        return w

    def _build_coat_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel(
            "Coat is auto-detected when both _cnr.dds and _s.dds exist."
        ))
        self._add_bool("coat_diffuse", form, "Coat Diffuse", True, True)
        self._add_bool("coat_parallax", form, "Coat Parallax", True, True)
        self._add_float("coat_strength", form, "Coat Strength",
                        1.0, 0, 10)
        self._add_float("coat_roughness", form, "Coat Roughness",
                        1.0, 0, 10)
        self._add_float("coat_specular_level", form,
                        "Coat Specular Level", 0.018, 0, 1)
        return w

    def _build_fuzz_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QLabel(
            "Fuzz is auto-detected from _f.dds textures."
        ))
        self._add_color("fuzz_color", form, "Fuzz Color",
                        (1, 1, 1), included=False)
        self._add_float("fuzz_weight", form, "Fuzz Weight",
                        1.0, 0, 10, included=False)
        return w

    def _build_extras_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self._add_bool("hair", form, "Hair", False, False)
        form.addRow(QLabel(""))
        form.addRow(QLabel("Glint parameters (creates glint object):"))
        self._add_float("glint_screen_space_scale", form,
                        "Screen Space Scale", 1.0, 0, 100, included=False)
        self._add_float("glint_log_microfacet_density", form,
                        "Log Microfacet Density", 1.0, 0, 100, included=False)
        self._add_float("glint_microfacet_roughness", form,
                        "Microfacet Roughness", 1.0, 0, 100, included=False)
        self._add_float("glint_density_randomization", form,
                        "Density Randomization", 1.0, 0, 100, included=False)
        return w

    # -- Row helpers --------------------------------------------------------

    def _add_float(self, key, form, label, default, min_val=0, max_val=100,
                   decimals=3, included=True):
        row = QHBoxLayout()
        cb = QCheckBox()
        cb.setChecked(included)
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setDecimals(decimals)
        spin.setSingleStep(0.01)
        spin.setValue(default)
        spin.setEnabled(included)
        cb.clicked.connect(
            lambda _=None, s=spin, c=cb: s.setEnabled(c.isChecked())
        )
        row.addWidget(cb)
        row.addWidget(spin)
        form.addRow(label, row)
        self._float_settings[key] = (cb, spin)

    def _add_bool(self, key, form, label, default=False, included=False):
        row = QHBoxLayout()
        include_cb = QCheckBox("Include")
        include_cb.setChecked(included)
        value_cb = QCheckBox("Enabled")
        value_cb.setChecked(default)
        value_cb.setEnabled(included)
        include_cb.clicked.connect(
            lambda _=None, v=value_cb, i=include_cb:
                v.setEnabled(i.isChecked())
        )
        row.addWidget(include_cb)
        row.addWidget(value_cb)
        form.addRow(label, row)
        self._bool_settings[key] = (include_cb, value_cb)

    def _add_color(self, key, form, label, default, included=True):
        row = QHBoxLayout()
        cb = QCheckBox()
        cb.setChecked(included)
        row.addWidget(cb)
        channels = "RGBA" if len(default) == 4 else "RGB"
        spins = []
        for ch, val in zip(channels, default):
            row.addWidget(QLabel(ch))
            spin = QDoubleSpinBox()
            spin.setRange(0, 1)
            spin.setDecimals(3)
            spin.setValue(val)
            spin.setEnabled(included)
            cb.clicked.connect(
                lambda _=None, s=spin, c=cb: s.setEnabled(c.isChecked())
            )
            row.addWidget(spin)
            spins.append(spin)
        form.addRow(label, row)
        self._color_settings[key] = (cb, spins)

    # -- Public API ---------------------------------------------------------

    def get_settings(self):
        """Return ``{field: value}`` for every included setting."""
        result = {}
        for key, (cb, spin) in self._float_settings.items():
            if cb.isChecked():
                result[key] = spin.value()
        for key, (include_cb, value_cb) in self._bool_settings.items():
            if include_cb.isChecked():
                result[key] = value_cb.isChecked()
        for key, (cb, spins) in self._color_settings.items():
            if cb.isChecked():
                result[key] = [s.value() for s in spins]
        return result


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------

class PBRJsonGenerator(mobase.IPluginTool):
    def __init__(self):
        super().__init__()
        self.__organizer = None
        self.__parent_widget = None

    # -- mobase boilerplate ---------------------------------------------------

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.__organizer = organizer
        return True

    def name(self):
        return PLUGIN_NAME

    def author(self):
        return "Bottle"

    def description(self):
        return (
            "Generates JSON configs into PBR JSON Output/[ModName]/"
            "PBRNifPatcher folders, single pass."
        )

    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

    def isActive(self):
        return True

    def settings(self):
        return []

    def displayName(self):
        return PLUGIN_NAME

    def tooltip(self):
        return (
            "Scans Textures/PBR once, building JSON with "
            "fuzz/glow/coat in the same pass."
        )

    def icon(self):
        return QIcon()

    def setParentWidget(self, widget):
        self.__parent_widget = widget

    # -- Entry point ----------------------------------------------------------

    def display(self):
        try:
            self._run()
        except Exception as e:
            QMessageBox.critical(
                self.__parent_widget,
                f"{PLUGIN_NAME} - Error",
                f"An error occurred:\n{e}",
            )

    # -- Private orchestration ------------------------------------------------

    def _run(self):
        mods_path = Path(self.__organizer.modsPath())
        mods_with_pbr = []
        mods_with_patcher = []

        for mod_folder in mods_path.iterdir():
            if not mod_folder.is_dir():
                continue
            if any(kw in mod_folder.name.lower() for kw in SKIP_KEYWORDS):
                continue
            has_meta = (mod_folder / "meta.ini").exists()
            if has_meta and (mod_folder / PBR_TEX_REL).exists():
                mods_with_pbr.append(mod_folder)
            if has_meta and (mod_folder / PATCHER_DIR).exists():
                mods_with_patcher.append(mod_folder)

        if not mods_with_pbr and not mods_with_patcher:
            QMessageBox.information(
                self.__parent_widget,
                "No Mods Found",
                "No mods with a Textures/PBR or PBRNifPatcher folder "
                "were found.\nEnsure your mods are correctly set up.",
            )
            return

        dialog = ModSelectionDialog(mods_with_pbr, self.__parent_widget)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if dialog.is_update_existing_only():
            self._handle_update_existing(mods_path, mods_with_patcher)
        else:
            selected = dialog.get_selected_mods()
            rename = dialog.is_rename_enabled()

            settings_dialog = PBRSettingsDialog(self.__parent_widget)
            if settings_dialog.exec() != QDialog.DialogCode.Accepted:
                return
            settings = settings_dialog.get_settings()

            self._handle_generate_new(
                mods_path, selected, rename, settings
            )

        try:
            self.__organizer.refresh(True)
        except Exception:
            pass

    # -- Update existing JSONs ------------------------------------------------

    def _handle_update_existing(self, mods_path, mods_with_patcher):
        if not mods_with_patcher:
            QMessageBox.information(
                self.__parent_widget,
                "No PBRNifPatcher Folders Found",
                "No mods with a PBRNifPatcher folder were found.",
            )
            return

        # Only show mods that have BOTH Textures/PBR and PBRNifPatcher,
        # because we need PBR textures for the lookup.
        eligible = [
            m for m in mods_with_patcher if (m / PBR_TEX_REL).exists()
        ]
        if not eligible:
            QMessageBox.information(
                self.__parent_widget,
                "No Eligible Mods",
                "No mods with both a PBRNifPatcher and a Textures/PBR "
                "folder were found.",
            )
            return

        pbr_dialog = PBRNifPatcherSelectionDialog(
            eligible, self.__parent_widget
        )
        if pbr_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        selected = pbr_dialog.get_selected_mods()
        rename_enabled = pbr_dialog.is_rename_enabled()
        if not selected:
            QMessageBox.information(
                self.__parent_widget,
                "No Mods Selected",
                "You did not select any mods to process.",
            )
            return

        output_mod = self._ensure_output_mod(mods_path, EXISTING_OUTPUT_MOD_NAME)
        stats = {
            "mods": 0,
            "jsons": 0,
            "updated": 0,
            "copied": 0,
            "errors": 0,
        }

        for mod_folder in selected:
            mod_pbr = mod_folder / PBR_TEX_REL
            patcher = mod_folder / PATCHER_DIR

            rmaos_index = _build_rmaos_index(mod_pbr)
            mod_log = []
            json_touched = False

            for json_file in patcher.rglob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, OSError) as exc:
                    mod_log.append(f"ERROR reading {json_file.name}: {exc}")
                    stats["errors"] += 1
                    continue

                entries, is_wrapped = self._extract_entries(existing_data)
                if entries is None:
                    continue

                new_entries = []
                entries_updated = 0
                entries_copied = 0

                for entry in entries:
                    if not (isinstance(entry, dict) and "texture" in entry):
                        new_entries.append(entry)
                        entries_copied += 1
                        continue

                    texture_key = (
                        entry["texture"].replace("\\", "/").lower()
                    )
                    dds_file = rmaos_index.get(texture_key)

                    # Fallback: match by filename only
                    if dds_file is None:
                        fname = texture_key.rsplit("/", 1)[-1]
                        candidates = [
                            v
                            for k, v in rmaos_index.items()
                            if k.rsplit("/", 1)[-1] == fname
                        ]
                        dds_file = candidates[0] if candidates else None

                    if dds_file is not None:
                        rel = dds_file.relative_to(mod_pbr)
                        new_tex = str(
                            rel.parent / rel.stem.replace("_rmaos", "")
                        ).replace("/", "\\")

                        new_entry = {"texture": new_tex}
                        if rename_enabled:
                            renamed = _rename_texture(new_tex)
                            if renamed:
                                new_entry["rename"] = renamed
                                mod_log.append(
                                    f"Renamed: {new_tex} -> {renamed}"
                                )

                        for k, v in entry.items():
                            if k not in ("texture", "rename"):
                                new_entry[k] = v

                        new_entries.append(new_entry)
                        entries_updated += 1
                    else:
                        new_entries.append(entry)
                        entries_copied += 1
                        mod_log.append(
                            f"Copied unchanged: {entry['texture']} "
                            "(no _rmaos.dds found)"
                        )

                if entries_updated > 0 or entries_copied > 0:
                    if is_wrapped:
                        output_data = {
                            **existing_data,
                            "entries": new_entries,
                        }
                    else:
                        output_data = new_entries

                    out_dir = (
                        output_mod
                        / mod_folder.name
                        / PATCHER_DIR
                        / json_file.relative_to(patcher).parent
                    )
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / json_file.name

                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=4)

                    stats["updated"] += entries_updated
                    stats["copied"] += entries_copied
                    stats["jsons"] += 1
                    json_touched = True
                    mod_log.append(f"Wrote: {out_path.name}")

            if json_touched:
                stats["mods"] += 1
                self._write_log(
                    output_mod
                    / mod_folder.name
                    / PATCHER_DIR
                    / "update_log.txt",
                    mod_log,
                )

        summary = (
            f"Update complete.\n\n"
            f"Mods processed:  {stats['mods']}\n"
            f"JSON files:      {stats['jsons']}\n"
            f"Entries updated: {stats['updated']}\n"
            f"Entries copied:  {stats['copied']}\n"
            f"Errors:          {stats['errors']}"
        )
        QMessageBox.information(self.__parent_widget, PLUGIN_NAME, summary)

    # -- Generate new JSONs ---------------------------------------------------

    def _handle_generate_new(self, mods_path, selected, rename_enabled,
                             settings):
        if not selected:
            QMessageBox.information(
                self.__parent_widget,
                "No Mods Selected",
                "You did not select any mods to process.",
            )
            return

        output_mod = self._ensure_output_mod(mods_path, OUTPUT_MOD_NAME)
        total_files = 0
        total_errors = 0

        for base_path in selected:
            mod_pbr = base_path / PBR_TEX_REL
            out_root = output_mod / base_path.name / PATCHER_DIR
            out_root.mkdir(parents=True, exist_ok=True)
            mod_log = []
            found_any = False

            for dds_file in mod_pbr.rglob("*_rmaos.dds"):
                found_any = True
                rel = dds_file.relative_to(mod_pbr)
                base_name = dds_file.stem.replace("_rmaos", "")
                texture_str = str(rel.parent / base_name).replace("/", "\\")

                parent_out = out_root / rel.parent
                parent_out.mkdir(parents=True, exist_ok=True)
                json_path = parent_out / f"{base_name}.json"

                # If a JSON already exists, update the texture path only,
                # preserving all other fields from the first entry.
                if json_path.exists():
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            existing_data = json.load(f)
                    except (json.JSONDecodeError, OSError) as exc:
                        mod_log.append(
                            f"ERROR reading {json_path.name}: {exc}"
                        )
                        total_errors += 1
                        continue

                    if isinstance(existing_data, list) and existing_data:
                        new_entry = {"texture": texture_str}
                        if rename_enabled:
                            renamed = _rename_texture(texture_str)
                            if renamed:
                                new_entry["rename"] = renamed
                                mod_log.append(
                                    f"Renamed: {texture_str} -> {renamed}"
                                )

                        for k, v in existing_data[0].items():
                            if k not in ("texture", "rename"):
                                new_entry[k] = v

                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump([new_entry], f, indent=4)
                        mod_log.append(f"Updated: {json_path.name}")
                        total_files += 1
                        continue

                # Probe for companion textures next to the _rmaos file.
                parent_dir = dds_file.parent
                glow = (parent_dir / f"{base_name}_g.dds").exists()
                fuzz = (parent_dir / f"{base_name}_f.dds").exists()
                parallax = (parent_dir / f"{base_name}_p.dds").exists()
                subsurface = (parent_dir / f"{base_name}_s.dds").exists()
                cnr = (parent_dir / f"{base_name}_cnr.dds").exists()

                entry = {"texture": texture_str}
                if rename_enabled:
                    renamed = _rename_texture(texture_str)
                    if renamed:
                        entry["rename"] = renamed
                        mod_log.append(
                            f"Renamed: {texture_str} -> {renamed}"
                        )

                # Auto-detected features
                entry["emissive"] = glow
                entry["parallax"] = parallax
                entry["subsurface"] = subsurface

                # User-configured general settings
                for key in ("specular_level", "roughness_scale",
                            "smooth_angle", "subsurface_foliage",
                            "vertex_colors", "vertex_color_lum_mult",
                            "vertex_color_sat_mult", "zbuffer_write",
                            "auto_uv", "uv_scale"):
                    if key in settings:
                        entry[key] = settings[key]

                # Emissive extras (only when detected)
                if glow:
                    for key in ("emissive_scale", "emissive_color"):
                        if key in settings:
                            entry[key] = settings[key]

                # Parallax extras (only when detected)
                if parallax:
                    if "displacement_scale" in settings:
                        entry["displacement_scale"] = (
                            settings["displacement_scale"]
                        )

                # Subsurface extras (only when detected)
                if subsurface:
                    for key in ("subsurface_color", "subsurface_opacity"):
                        if key in settings:
                            entry[key] = settings[key]

                # Fuzz or Coat (mutually exclusive, fuzz wins)
                if fuzz:
                    fuzz_obj = {"texture": True}
                    if "fuzz_color" in settings:
                        fuzz_obj["color"] = settings["fuzz_color"]
                    if "fuzz_weight" in settings:
                        fuzz_obj["weight"] = settings["fuzz_weight"]
                    entry["fuzz"] = fuzz_obj
                elif subsurface and cnr:
                    entry["coat_normal"] = True
                    for key in ("coat_diffuse", "coat_parallax",
                                "coat_strength", "coat_roughness",
                                "coat_specular_level"):
                        if key in settings:
                            entry[key] = settings[key]

                # Hair
                if "hair" in settings:
                    entry["hair"] = settings["hair"]

                # Glint
                _glint_map = {
                    "glint_screen_space_scale": "screen_space_scale",
                    "glint_log_microfacet_density":
                        "log_microfacet_density",
                    "glint_microfacet_roughness": "microfacet_roughness",
                    "glint_density_randomization":
                        "density_randomization",
                }
                _glint = {}
                for s_key, j_key in _glint_map.items():
                    if s_key in settings:
                        _glint[j_key] = settings[s_key]
                if _glint:
                    entry["glint"] = _glint

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump([entry], f, indent=4)
                mod_log.append(f"Created: {json_path.name}")
                total_files += 1

            if not found_any:
                mod_log.append(
                    f"Skipped {base_path.name}: "
                    "no *_rmaos.dds in Textures/PBR"
                )

            self._write_log(out_root / "generation_log.txt", mod_log)

        summary = (
            f"Generation complete.\n\n"
            f"Files processed: {total_files}\n"
            f"Errors:          {total_errors}"
        )
        QMessageBox.information(self.__parent_widget, PLUGIN_NAME, summary)

    # -- Utilities ------------------------------------------------------------

    @staticmethod
    def _ensure_output_mod(mods_path: Path, name: str) -> Path:
        """Create the output mod folder with a ``meta.ini`` if needed."""
        mod = mods_path / name
        mod.mkdir(exist_ok=True)
        meta = mod / "meta.ini"
        if not meta.exists():
            meta.write_text(META_INI_CONTENT, encoding="utf-8")
        return mod

    @staticmethod
    def _extract_entries(data):
        """Return ``(entries_list, is_wrapped_in_dict)`` or ``(None, None)``.

        Handles both ``{"entries": [...]}`` and plain ``[...]`` formats.
        """
        if isinstance(data, dict) and "entries" in data:
            entries = data["entries"]
            if isinstance(entries, list) and entries:
                return entries, True
        elif isinstance(data, list) and data:
            return data, False
        return None, None

    @staticmethod
    def _write_log(path: Path, lines):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")


def createPlugin():
    return PBRJsonGenerator()
