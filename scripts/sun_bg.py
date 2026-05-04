"""
Solar System — Phase 1: Sun + starfield + camera + EEVEE defaults
Blender 4.2 LTS | EEVEE Next

Tip: Text Editor → Open this file from disk, or save your .blend in the same folder as solar_common.py.
"""

import importlib
import sys
from pathlib import Path

import bpy


def _ensure_solar_common_path() -> None:
    """Find the folder that contains solar_common.py (Blender often has no __file__)."""
    roots: list[Path] = []
    try:
        roots.append(Path(__file__).resolve().parent)
    except NameError:
        pass
    blend_fp = getattr(bpy.data, "filepath", "") or ""
    if blend_fp:
        roots.append(Path(blend_fp).resolve().parent)
    roots.append(Path(r"c:\Users\FSOS\Desktop\blenderpy"))
    roots.append(Path.home() / "Desktop" / "blenderpy")
    seen: set[str] = set()
    for raw in roots:
        try:
            r = raw.resolve()
        except OSError:
            continue
        key = str(r)
        if key in seen:
            continue
        seen.add(key)
        if (r / "solar_common.py").is_file():
            if key not in sys.path:
                sys.path.insert(0, key)
            return
    raise ImportError(
        "Could not find solar_common.py. Put it next to this script, open the script from disk, "
        "or save your .blend in the folder that contains solar_common.py."
    )


_ensure_solar_common_path()
import solar_common as sc  # noqa: E402

importlib.reload(sc)  # noqa: E402

def main():
    print("\n── Solar System Phase 1 (Sun + background) ──")
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    sc.clear_scene_default()
    sun = sc.create_sun_sphere()
    sc.animate_sun_rotation(sun)
    sc.create_starry_world()
    sc.create_sun_light()
    sc.setup_camera_main()
    sc.setup_render_viewport()
    bpy.context.scene.frame_set(1)
    print("✅ Phase 1 complete — run Mercury, Venus, Earth, … in order.\n")


if __name__ == "__main__":
    main()
