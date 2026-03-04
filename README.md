# PBR-JSON-Generator
MO2 tool for PBR JSON editing and creation, exported to a separate mod to prevent possible errors and does not touch existing jsons. Place the .py script into your mo2\plugins folder and run from mo2 tools dropdown menu.

## Select All

Checks/unchecks every mod in the list at once. Useful when you want to process all but a few — select all, then uncheck the ones you want to skip.

## Only update texture paths in existing JSONs

Switches the tool into update mode. Instead of generating new JSON files from scratch, it reads JSON files that already exist in mods' PBRNifPatcher folders and updates the texture field in each entry to match where the _rmaos.dds file actually lives on disk. All other fields (specular, roughness, coat settings, etc.) are left exactly as they are. Output is written to a new mod called PBR Existing JSON Output. Checking this also disables the mod list, since in this mode you pick from mods that have a PBRNifPatcher folder rather than a Textures/PBR folder.

## Enable renaming

When a texture path ends with _d (the conventional diffuse suffix, e.g. landscape\dirt_d), this adds a "rename" field to the JSON entry with the _d stripped off (landscape\dirt). PBRNifPatcher uses that field to apply the PBR material to meshes that reference the non-suffixed texture name.

## The mod list

The checkable list at the bottom is the set of mods the tool will process. Each entry is a mod folder under your MO2 mods directory that has both a meta.ini and a Textures/PBR subfolder. Only mods you check will be processed when you hit OK.
