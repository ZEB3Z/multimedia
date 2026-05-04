"""Saturn — body + ring mesh. Ring texture: saturn_ring.png (RGBA). Safe to re-run."""

import importlib
import sys
from pathlib import Path

import bpy


def _ensure_solar_common_path() -> None:
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
    raise ImportError("Could not find solar_common.py next to this script or your .blend folder.")


_ensure_solar_common_path()
import solar_common as sc

importlib.reload(sc)  # pick up solar_common.py edits without restarting Blender

BODY = "Saturn"


def main():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    sc.ensure_base_scene()
    sc.clear_objects_for_planet(BODY)
    d = sc.PLANETS[BODY]
    sc.create_orbit_ring(
        sc.orbit_bu(d["semi_major_axis_au"]),
        f"OrbitRing_{BODY}",
        d["ring_color"],
        d["ring_strength"],
    )
    sc.build_saturn_with_rings(d)
    bpy.context.scene.frame_set(1)
    print(f"✅ {BODY} added (textures: {sc.texture_path_for_key('saturn')}, {sc.TEXTURE_DIR / sc.TEXTURE_FILES['saturn_ring']}).")


if __name__ == "__main__":
    main()
