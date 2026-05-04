"""
Shared solar system setup for Blender 4.2 LTS (EEVEE Next).
Each planet script imports this module; keep this file beside the planet scripts.

Texture folder: C:\\BlenderTextures\\
Expected files: see TEXTURE_FILES in this module.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import bpy

# ── Paths ───────────────────────────────────────────────────────────────────
TEXTURE_DIR = Path(r"C:\BlenderTextures")

# Base names (without path). Earth uses earth_color.jpg per your setup.
TEXTURE_FILES = {
    "sun": "sun_color.jpg",  # optional; sun_bg still supports procedural if missing
    "mercury": "mercury_color.jpg",
    "venus": "venus_color.jpg",
    "earth": "earth_color.jpg",
    "mars": "mars_color.jpg",
    "jupiter": "jupiter_color.jpg",
    "saturn": "saturn_color.jpg",
    "saturn_ring": "saturn_ring.png",  # RGBA ring texture (NASA-style)
    "uranus": "uranus_color.jpg",
    "neptune": "neptune_color.jpg",
    "pluto": "pluto_color.jpg",
}

# ── Time / scale (visual: compressed orbits, correct period ratios) ─────────
TOTAL_FRAMES = 500
FRAMES_PER_YEAR = 250.0

ORBIT_SCALE = 5.0
ORBIT_EXP = 0.55

EARTH_RADIUS_KM = 6371.0
BASE_RADIUS = 0.38
SIZE_EXP = 0.50

SUN_LIGHT_ENERGY = 800.0
SUN_LIGHT_RADIUS = 0.8

# NASA/JPL approximate values — orbital & rotation periods drive animation ratios
PLANETS: dict[str, dict] = {
    "Mercury": {
        "key": "mercury",
        "radius_km": 2439.7,
        "axial_tilt_deg": 0.034,
        "retrograde": False,
        "semi_major_axis_au": 0.387,
        "orbital_period_days": 87.969,
        "rotation_period_days": 58.646,
        "start_angle_deg": 20.0,
        "ring_color": (0.72, 0.72, 0.74, 1.0),
        "ring_strength": 0.42,
    },
    "Venus": {
        "key": "venus",
        "radius_km": 6051.8,
        "axial_tilt_deg": 177.36,
        "retrograde": True,
        "semi_major_axis_au": 0.723,
        "orbital_period_days": 224.701,
        "rotation_period_days": 243.025,
        "start_angle_deg": 85.0,
        "ring_color": (0.94, 0.82, 0.45, 1.0),
        "ring_strength": 0.42,
    },
    "Earth": {
        "key": "earth",
        "radius_km": 6371.0,
        "axial_tilt_deg": 23.44,
        "retrograde": False,
        "semi_major_axis_au": 1.0,
        "orbital_period_days": 365.256,
        "rotation_period_days": 0.99726968,
        "start_angle_deg": 160.0,
        "ring_color": (0.18, 0.50, 0.92, 1.0),
        "ring_strength": 0.48,
    },
    "Mars": {
        "key": "mars",
        "radius_km": 3389.5,
        "axial_tilt_deg": 25.19,
        "retrograde": False,
        "semi_major_axis_au": 1.5237,
        "orbital_period_days": 686.98,
        "rotation_period_days": 1.02595675,
        "start_angle_deg": 240.0,
        "ring_color": (0.92, 0.42, 0.22, 1.0),
        "ring_strength": 0.45,
    },
    "Jupiter": {
        "key": "jupiter",
        "radius_km": 69911.0,
        "axial_tilt_deg": 3.13,
        "retrograde": False,
        "semi_major_axis_au": 5.2044,
        "orbital_period_days": 4332.59,
        "rotation_period_days": 0.41354,
        "start_angle_deg": 30.0,
        "ring_color": (0.85, 0.65, 0.45, 1.0),
        "ring_strength": 0.40,
    },
    "Saturn": {
        "key": "saturn",
        "radius_km": 58232.0,
        "axial_tilt_deg": 26.73,
        "retrograde": False,
        "semi_major_axis_au": 9.5826,
        "orbital_period_days": 10759.22,
        "rotation_period_days": 0.44401,
        "start_angle_deg": 120.0,
        "ring_color": (0.90, 0.78, 0.55, 1.0),
        "ring_strength": 0.40,
    },
    "Uranus": {
        "key": "uranus",
        "radius_km": 25362.0,
        "axial_tilt_deg": 97.77,
        "retrograde": True,
        "semi_major_axis_au": 19.2184,
        "orbital_period_days": 30688.5,
        "rotation_period_days": 0.71833,
        "start_angle_deg": 200.0,
        "ring_color": (0.55, 0.82, 0.92, 1.0),
        "ring_strength": 0.38,
    },
    "Neptune": {
        "key": "neptune",
        "radius_km": 24622.0,
        "axial_tilt_deg": 28.32,
        "retrograde": False,
        "semi_major_axis_au": 30.11,
        "orbital_period_days": 60182.0,
        "rotation_period_days": 0.67125,
        "start_angle_deg": 300.0,
        "ring_color": (0.35, 0.45, 0.95, 1.0),
        "ring_strength": 0.38,
    },
    "Pluto": {
        "key": "pluto",
        "radius_km": 1188.3,
        "axial_tilt_deg": 122.53,
        "retrograde": True,
        "semi_major_axis_au": 39.48,
        "orbital_period_days": 90560.0,
        "rotation_period_days": 6.38723,
        "start_angle_deg": 50.0,
        "ring_color": (0.80, 0.78, 0.76, 1.0),
        "ring_strength": 0.36,
        # Elliptical orbit (Sun at focus); e ≈ Pluto fact sheet
        "eccentricity": 0.2488,
        "mean_anomaly0_deg": 0.0,
    },
}


def script_dir() -> Path:
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path(r"c:\Users\FSOS\Desktop\blenderpy")


def ensure_import_path():
    d = str(script_dir())
    if d not in sys.path:
        sys.path.insert(0, d)


def days_to_frames(days: float) -> float:
    return days * (FRAMES_PER_YEAR / 365.256)


def planet_radius_bu(radius_km: float) -> float:
    return BASE_RADIUS * ((radius_km / EARTH_RADIUS_KM) ** SIZE_EXP)


def orbit_bu(au: float) -> float:
    return (au ** ORBIT_EXP) * ORBIT_SCALE


def solve_kepler_mean_to_eccentric(M: float, e: float, iterations: int = 80) -> float:
    """Kepler equation M = E - e sin(E); Newton–Raphson on E."""
    if e < 1e-12:
        return M
    E = M if e < 0.85 else math.pi
    for _ in range(iterations):
        f = E - e * math.sin(E) - M
        fp = 1.0 - e * math.cos(E)
        if abs(fp) < 1e-14:
            break
        step = f / fp
        E -= step
        if abs(step) < 1e-11:
            break
    return E


def pluto_xy_from_mean_anomaly(M: float, a_bu: float, e: float, orbit_rotation_z: float) -> tuple[float, float]:
    """Position in ecliptic XY with Sun at origin (elliptical focus)."""
    E = solve_kepler_mean_to_eccentric(M, e)
    x0 = a_bu * (math.cos(E) - e)
    y0 = a_bu * math.sqrt(max(0.0, 1.0 - e * e)) * math.sin(E)
    c = math.cos(orbit_rotation_z)
    s = math.sin(orbit_rotation_z)
    return c * x0 - s * y0, s * x0 + c * y0


def create_pluto_elliptical_orbit_ring(
    a_bu: float,
    e: float,
    name: str,
    color: tuple,
    strength: float,
    orbit_rotation_z: float,
) -> bpy.types.Object:
    """Ellipse in XY with Sun at a focus; major axis length 2a in our scaled units."""
    b_bu = a_bu * math.sqrt(max(0.0, 1.0 - e * e))
    bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, location=(0, 0, 0))
    ring = bpy.context.active_object
    ring.name = name
    ring.scale = (a_bu, b_bu, 1.0)
    cx = -a_bu * e * math.cos(orbit_rotation_z)
    cy = -a_bu * e * math.sin(orbit_rotation_z)
    ring.location = (cx, cy, 0.0)
    ring.rotation_euler[2] = orbit_rotation_z
    ring.data.bevel_depth = max(0.006, min(a_bu, b_bu) * 0.0028)
    ring.data.use_fill_caps = True
    ring.data.resolution_u = 256
    ring.data.bevel_resolution = 4

    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e_n = nt.nodes.new("ShaderNodeEmission")
    o.location = (300, 0)
    e_n.location = (80, 0)
    e_n.inputs["Color"].default_value = (*color[:3], 1.0) if len(color) >= 3 else (0.5, 0.7, 1.0, 1.0)
    e_n.inputs["Strength"].default_value = strength
    nt.links.new(e_n.outputs["Emission"], o.inputs["Surface"])
    ring.data.materials.append(mat)
    return ring


def build_pluto_elliptical(data: dict) -> tuple[bpy.types.Object, bpy.types.Object]:
    """
    Pluto on a Keplerian ellipse (non-uniform speed along path). Orbit empty translates;
    planet is a child at origin. Rotation spin matches other planets.
    """
    sc = bpy.context.scene
    body_name = "Pluto"
    r_bu = planet_radius_bu(data["radius_km"])
    a_au = float(data["semi_major_axis_au"])
    e = float(data["eccentricity"])
    a_bu = orbit_bu(a_au)
    orb_frames = days_to_frames(data["orbital_period_days"])
    rot_frames = days_to_frames(data["rotation_period_days"])
    num_orbits = TOTAL_FRAMES / orb_frames
    num_rots = TOTAL_FRAMES / rot_frames
    retro = data["retrograde"]
    phi = math.radians(float(data["start_angle_deg"]))
    M0 = math.radians(float(data.get("mean_anomaly0_deg", 0.0)))

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    orbit = bpy.context.active_object
    orbit.name = f"Orbit_{body_name}"

    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=r_bu, location=(0, 0, 0))
    planet = bpy.context.active_object
    planet.name = body_name
    bpy.ops.object.shade_smooth()
    planet.rotation_euler[0] = math.radians(data["axial_tilt_deg"])
    parent_keep_transform(planet, orbit)

    for f in range(1, TOTAL_FRAMES + 2):
        sc.frame_set(f)
        t = (f - 1) / TOTAL_FRAMES
        M = M0 + t * num_orbits * math.tau
        x, y = pluto_xy_from_mean_anomaly(M, a_bu, e, phi)
        orbit.location = (x, y, 0.0)
        orbit.keyframe_insert(data_path="location")

    make_linear(orbit)

    total_spin = num_rots * math.tau
    if retro:
        total_spin = -total_spin
    sc.frame_set(1)
    planet.rotation_euler[2] = 0.0
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(TOTAL_FRAMES + 1)
    planet.rotation_euler[2] = total_spin
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(planet)

    key = data["key"]
    img = load_image(texture_path_for_key(key), f"{key}_albedo", "sRGB")
    mat_textured_planet(planet, img, roughness=0.92, spec=0.05)

    sc.frame_set(1)
    return planet, orbit


def make_linear(obj: bpy.types.Object) -> None:
    if not obj.animation_data or not obj.animation_data.action:
        return
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def parent_keep_transform(child: bpy.types.Object, parent_obj: bpy.types.Object) -> None:
    """Parent while preserving world transform (fixes bodies stuck at origin)."""
    bpy.ops.object.select_all(action="DESELECT")
    child.select_set(True)
    parent_obj.select_set(True)
    bpy.context.view_layer.objects.active = parent_obj
    bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)


def load_image(path: Path, name: str, colorspace: str = "sRGB") -> bpy.types.Image | None:
    path = Path(path)
    if not path.is_file():
        return None
    s = str(path.resolve())
    for img in bpy.data.images:
        if Path(bpy.path.abspath(img.filepath)).resolve() == Path(s).resolve() or img.filepath == s:
            img.colorspace_settings.name = colorspace
            return img
    img = bpy.data.images.load(s)
    img.name = name
    img.colorspace_settings.name = colorspace
    return img


def texture_path_for_key(key: str) -> Path:
    return TEXTURE_DIR / TEXTURE_FILES.get(key, f"{key}_color.jpg")


def principled_set_specular(bsdf: bpy.types.Node, value: float) -> None:
    for spec_name in ("Specular IOR Level", "Specular"):
        if spec_name in bsdf.inputs:
            bsdf.inputs[spec_name].default_value = value
            break


def mat_textured_planet(obj: bpy.types.Object, image: bpy.types.Image | None, roughness: float = 0.72, spec: float = 0.22) -> None:
    """Principled BSDF with optional albedo; neutral gray if texture missing."""
    obj.data.materials.clear()
    mat = bpy.data.materials.new(f"Mat_{obj.name}")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    nt = mat.node_tree
    N = nt.nodes
    L = nt.links
    N.clear()

    uv = N.new("ShaderNodeTexCoord")
    uv.location = (-900, 260)
    out = N.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (520, 0)
    bsdf.inputs["Roughness"].default_value = roughness
    principled_set_specular(bsdf, spec)

    if image:
        tex = N.new("ShaderNodeTexImage")
        tex.location = (-560, 280)
        tex.image = image
        tex.image.colorspace_settings.name = "sRGB"
        L.new(uv.outputs["UV"], tex.inputs["Vector"])
        L.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (0.55, 0.55, 0.56, 1.0)

    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])


def create_orbit_ring(radius: float, name: str, color: tuple, strength: float = 0.45) -> bpy.types.Object:
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=(0, 0, 0))
    ring = bpy.context.active_object
    ring.name = name
    ring.data.bevel_depth = max(0.008, radius * 0.0025)
    ring.data.use_fill_caps = True
    ring.data.resolution_u = 256
    ring.data.bevel_resolution = 4

    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    o.location = (300, 0)
    e.location = (80, 0)
    e.inputs["Color"].default_value = (*color[:3], 1.0) if len(color) >= 3 else (0.5, 0.7, 1.0, 1.0)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    ring.data.materials.append(mat)
    return ring


def create_sun_light() -> bpy.types.Object:
    if bpy.data.objects.get("Sun_Light"):
        return bpy.data.objects["Sun_Light"]
    bpy.ops.object.light_add(type="POINT", location=(0.0, 0.0, 0.0))
    light = bpy.context.active_object
    light.name = "Sun_Light"
    ld = light.data
    ld.energy = SUN_LIGHT_ENERGY
    ld.shadow_soft_size = SUN_LIGHT_RADIUS
    ld.color = (1.0, 0.96, 0.88)
    ld.use_shadow = True
    return light


def clear_scene_default():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)


def build_sun_material(sun: bpy.types.Object) -> None:
    mat = bpy.data.materials.new("Sun_Material")
    mat.use_nodes = True
    sun.data.materials.append(mat)
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    emit = nodes.new("ShaderNodeEmission")
    emit.location = (640, 0)
    emit.inputs["Strength"].default_value = 7.0
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)

    n_gran = nodes.new("ShaderNodeTexNoise")
    n_gran.location = (-560, 220)
    n_gran.inputs["Scale"].default_value = 10.0
    n_gran.inputs["Detail"].default_value = 16.0
    n_gran.inputs["Roughness"].default_value = 0.60
    n_gran.inputs["Distortion"].default_value = 0.35

    r_gran = nodes.new("ShaderNodeValToRGB")
    r_gran.location = (-220, 220)
    cr = r_gran.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.25
    cr.elements[0].color = (0.55, 0.08, 0.0, 1)
    cr.elements[1].position = 0.90
    cr.elements[1].color = (1.00, 0.85, 0.22, 1)
    cr.elements.new(0.60).color = (1.00, 0.42, 0.02, 1)

    n_spot = nodes.new("ShaderNodeTexNoise")
    n_spot.location = (-560, -80)
    n_spot.inputs["Scale"].default_value = 2.6
    n_spot.inputs["Detail"].default_value = 5.0
    n_spot.inputs["Roughness"].default_value = 0.85
    n_spot.inputs["Distortion"].default_value = 1.8

    r_spot = nodes.new("ShaderNodeValToRGB")
    r_spot.location = (-220, -80)
    cr2 = r_spot.color_ramp
    cr2.interpolation = "EASE"
    cr2.elements[0].position = 0.0
    cr2.elements[0].color = (0.04, 0.01, 0.0, 1)
    cr2.elements[1].position = 0.50
    cr2.elements[1].color = (1.00, 1.00, 1.00, 1)

    mix = nodes.new("ShaderNodeMixRGB")
    mix.location = (120, 80)
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.55

    links.new(tc.outputs["UV"], n_gran.inputs["Vector"])
    links.new(tc.outputs["UV"], n_spot.inputs["Vector"])
    links.new(n_gran.outputs["Fac"], r_gran.inputs["Fac"])
    links.new(n_spot.outputs["Fac"], r_spot.inputs["Fac"])
    links.new(r_gran.outputs["Color"], mix.inputs["Color1"])
    links.new(r_spot.outputs["Color"], mix.inputs["Color2"])
    links.new(mix.outputs["Color"], emit.inputs["Color"])
    links.new(emit.outputs["Emission"], out.inputs["Surface"])


def create_sun_sphere() -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.0, location=(0, 0, 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    bpy.ops.object.shade_smooth()
    tex_path = texture_path_for_key("sun")
    img = load_image(tex_path, "sun_color", "sRGB")
    if img:
        sun.data.materials.clear()
        mat = bpy.data.materials.new("Sun_Textured")
        mat.use_nodes = True
        sun.data.materials.append(mat)
        nt = mat.node_tree
        N = nt.nodes
        L = nt.links
        N.clear()
        uv = N.new("ShaderNodeTexCoord")
        tex = N.new("ShaderNodeTexImage")
        tex.image = img
        emit = N.new("ShaderNodeEmission")
        out = N.new("ShaderNodeOutputMaterial")
        uv.location = (-800, 0)
        tex.location = (-500, 0)
        emit.location = (0, 0)
        out.location = (280, 0)
        emit.inputs["Strength"].default_value = 8.0
        L.new(uv.outputs["UV"], tex.inputs["Vector"])
        L.new(tex.outputs["Color"], emit.inputs["Color"])
        L.new(emit.outputs["Emission"], out.inputs["Surface"])
    else:
        build_sun_material(sun)
    return sun


def animate_sun_rotation(sun: bpy.types.Object, frames_for_one_spin: int = 250) -> None:
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = TOTAL_FRAMES
    sc.frame_set(1)
    sun.rotation_euler = (0.0, 0.0, 0.0)
    sun.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(frames_for_one_spin + 1)
    sun.rotation_euler[2] = math.tau
    sun.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(sun)
    sc.frame_set(1)


def create_starry_world() -> None:
    """
    Calm deep-purple sky with a few pinprick stars (no busy Voronoi/noise static).
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputWorld")
    out.location = (520, 0)
    bg = nodes.new("ShaderNodeBackground")
    bg.location = (260, 0)
    bg.inputs["Strength"].default_value = 1.0

    # Flat deep purple base (no procedural grain)
    purple = nodes.new("ShaderNodeRGB")
    purple.location = (-620, 140)
    purple.outputs[0].default_value = (0.042, 0.014, 0.092, 1.0)

    tc_w = nodes.new("ShaderNodeTexCoord")
    tc_w.location = (-980, -80)

    # Single low-frequency Voronoi → few bright cell centers = sparse stars
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-720, -80)
    vor.voronoi_dimensions = "3D"
    vor.feature = "SMOOTH_F1"
    vor.inputs["Scale"].default_value = 38.0
    vor.inputs["Smoothness"].default_value = 0.85

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-460, -80)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (1.0, 1.0, 1.0, 1)
    cr.elements[1].position = 0.055
    cr.elements[1].color = (0.0, 0.0, 0.0, 1)

    # Dim cool star tint, low strength
    star_tint = nodes.new("ShaderNodeRGB")
    star_tint.location = (-280, -200)
    star_tint.outputs[0].default_value = (0.55, 0.62, 0.85, 1.0)

    mul_tint = nodes.new("ShaderNodeMixRGB")
    mul_tint.location = (-240, -80)
    mul_tint.blend_type = "MULTIPLY"
    mul_tint.inputs[0].default_value = 1.0

    dim = nodes.new("ShaderNodeMixRGB")
    dim.location = (-40, -40)
    dim.blend_type = "MULTIPLY"
    dim.inputs[0].default_value = 1.0
    dim.inputs[2].default_value = (0.14, 0.14, 0.14, 1.0)

    add_stars = nodes.new("ShaderNodeMixRGB")
    add_stars.location = (80, 100)
    add_stars.blend_type = "ADD"
    add_stars.inputs[0].default_value = 1.0

    links.new(tc_w.outputs["Generated"], vor.inputs["Vector"])
    links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], mul_tint.inputs["Color1"])
    links.new(star_tint.outputs["Color"], mul_tint.inputs["Color2"])
    links.new(mul_tint.outputs["Color"], dim.inputs["Color1"])
    links.new(dim.outputs["Color"], add_stars.inputs["Color2"])
    links.new(purple.outputs["Color"], add_stars.inputs["Color1"])
    links.new(add_stars.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])


def setup_camera_main():
    cam = bpy.data.objects.get("Camera_Main")
    if cam:
        bpy.context.scene.camera = cam
        return cam
    bpy.ops.object.camera_add(location=(0.0, -14.0, 2.2))
    cam = bpy.context.active_object
    cam.name = "Camera_Main"
    cam.rotation_euler = (math.radians(82.0), 0.0, 0.0)
    cam.data.lens = 35.0
    cam.data.clip_start = 0.01
    cam.data.clip_end = 100000.0
    bpy.context.scene.camera = cam
    return cam


def setup_compositor_bloom(threshold: float = 0.8, quality: str = 'HIGH') -> None:
    """Add a Compositor Glare (Bloom) node — replaces the removed EEVEE bloom."""
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    # Avoid duplicates
    for nd in list(tree.nodes):
        if nd.type == 'GLARE':
            tree.nodes.remove(nd)
    rl = None
    comp = None
    for nd in tree.nodes:
        if nd.type == 'R_LAYERS':
            rl = nd
        elif nd.type == 'COMPOSITE':
            comp = nd
    if not rl:
        rl = tree.nodes.new('CompositorNodeRLayers')
    if not comp:
        comp = tree.nodes.new('CompositorNodeComposite')
    glare = tree.nodes.new('CompositorNodeGlare')
    glare.glare_type = 'BLOOM'
    glare.threshold = threshold
    try:
        glare.quality = quality
    except Exception:
        pass
    glare.location = (rl.location.x + 300, rl.location.y)
    comp.location = (glare.location.x + 300, glare.location.y)
    # Rewire: RL → Glare → Composite
    for lnk in list(tree.links):
        if lnk.to_node == comp and lnk.to_socket.name == 'Image':
            tree.links.remove(lnk)
    tree.links.new(rl.outputs['Image'], glare.inputs['Image'])
    tree.links.new(glare.outputs['Image'], comp.inputs['Image'])


def setup_render_viewport(fps: int = 24, samples: int = 64) -> None:
    sc = bpy.context.scene
    rd = sc.render
    rd.engine = "BLENDER_EEVEE_NEXT"
    rd.resolution_x = 1920
    rd.resolution_y = 1080
    rd.resolution_percentage = 100
    rd.fps = fps
    sc.frame_start = 1
    sc.frame_end = TOTAL_FRAMES
    ev = sc.eevee
    try:
        ev.taa_render_samples = samples
    except AttributeError:
        pass
    # Bloom via compositor (EEVEE Next removed built-in bloom)
    setup_compositor_bloom(threshold=0.8)
    sc.view_settings.view_transform = "Filmic"
    sc.view_settings.look = "Medium High Contrast"


def ensure_base_scene():
    """If Sun is missing, build full Phase-1 scene (non-destructive if Sun exists)."""
    if bpy.data.objects.get("Sun"):
        create_sun_light()
        if not bpy.context.scene.world or not bpy.context.scene.world.node_tree:
            create_starry_world()
        setup_camera_main()
        setup_render_viewport()
        return
    clear_scene_default()
    sun = create_sun_sphere()
    animate_sun_rotation(sun)
    create_starry_world()
    create_sun_light()
    setup_camera_main()
    setup_render_viewport()


def clear_objects_for_planet(body_name: str) -> None:
    prefixes = (f"Orbit_{body_name}", f"OrbitRing_{body_name}", f"Atm_{body_name}", f"Ring_{body_name}")
    exact = {body_name, f"{body_name}_Rings"}
    to_del = []
    for obj in bpy.data.objects:
        if obj.name in exact:
            to_del.append(obj)
        elif any(obj.name.startswith(p) for p in prefixes):
            to_del.append(obj)
    for obj in to_del:
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for item in list(coll):
            if item.users == 0:
                try:
                    coll.remove(item)
                except Exception:
                    pass


def build_planet(
    body_name: str,
    data: dict,
    *,
    with_atmosphere: bool = False,
    atmosphere_scale: float = 1.08,
    roughness: float = 0.72,
    specular: float = 0.22,
) -> tuple[bpy.types.Object, bpy.types.Object]:
    """Create orbit empty + planet mesh, animations, texture; optional Earth-like atmosphere."""
    sc = bpy.context.scene
    r_bu = planet_radius_bu(data["radius_km"])
    orb_dist = orbit_bu(data["semi_major_axis_au"])
    orb_frames = days_to_frames(data["orbital_period_days"])
    rot_frames = days_to_frames(data["rotation_period_days"])
    num_orbits = TOTAL_FRAMES / orb_frames
    num_rots = TOTAL_FRAMES / rot_frames
    start_rad = math.radians(data["start_angle_deg"])
    retro = data["retrograde"]

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    orbit = bpy.context.active_object
    orbit.name = f"Orbit_{body_name}"

    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=r_bu, location=(orb_dist, 0, 0))
    planet = bpy.context.active_object
    planet.name = body_name
    bpy.ops.object.shade_smooth()
    planet.rotation_euler[0] = math.radians(data["axial_tilt_deg"])
    parent_keep_transform(planet, orbit)

    sc.frame_set(1)
    orbit.rotation_euler[2] = start_rad
    orbit.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(TOTAL_FRAMES + 1)
    orbit.rotation_euler[2] = start_rad + num_orbits * math.tau
    orbit.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(orbit)

    total_spin = num_rots * math.tau
    if retro:
        total_spin = -total_spin
    sc.frame_set(1)
    planet.rotation_euler[2] = 0.0
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(TOTAL_FRAMES + 1)
    planet.rotation_euler[2] = total_spin
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(planet)

    key = data["key"]
    img = load_image(texture_path_for_key(key), f"{key}_albedo", "sRGB")
    mat_textured_planet(planet, img, roughness=roughness, spec=specular)

    if with_atmosphere:
        pc = planet.matrix_world.translation.copy()
        bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=r_bu * atmosphere_scale, location=pc)
        atm = bpy.context.active_object
        atm.name = f"Atm_{body_name}"
        bpy.ops.object.shade_smooth()
        atm.parent = planet
        atm.matrix_parent_inverse = planet.matrix_world.inverted()
        atm.location = (0.0, 0.0, 0.0)
        mat = bpy.data.materials.new(f"Mat_Atm_{body_name}")
        mat.use_nodes = True
        try:
            mat.surface_render_method = "BLENDED"
        except AttributeError:
            pass
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        trans = nt.nodes.new("ShaderNodeBsdfTransparent")
        emit = nt.nodes.new("ShaderNodeEmission")
        mix_sh = nt.nodes.new("ShaderNodeMixShader")
        emit.inputs["Color"].default_value = (0.30, 0.68, 1.00, 1.0)
        emit.inputs["Strength"].default_value = 0.32
        mix_sh.inputs[0].default_value = 0.14
        nt.links.new(trans.outputs["BSDF"], mix_sh.inputs[1])
        nt.links.new(emit.outputs["Emission"], mix_sh.inputs[2])
        nt.links.new(mix_sh.outputs["Shader"], out.inputs["Surface"])
        atm.data.materials.append(mat)

    sc.frame_set(1)
    return planet, orbit


def build_saturn_with_rings(data: dict) -> tuple[bpy.types.Object, bpy.types.Object]:
    sc = bpy.context.scene
    r_bu = planet_radius_bu(data["radius_km"])
    orb_dist = orbit_bu(data["semi_major_axis_au"])
    orb_frames = days_to_frames(data["orbital_period_days"])
    rot_frames = days_to_frames(data["rotation_period_days"])
    num_orbits = TOTAL_FRAMES / orb_frames
    num_rots = TOTAL_FRAMES / rot_frames
    start_rad = math.radians(data["start_angle_deg"])

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    orbit = bpy.context.active_object
    orbit.name = "Orbit_Saturn"

    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=r_bu, location=(orb_dist, 0, 0))
    planet = bpy.context.active_object
    planet.name = "Saturn"
    bpy.ops.object.shade_smooth()
    planet.rotation_euler[0] = math.radians(data["axial_tilt_deg"])
    parent_keep_transform(planet, orbit)

    sc.frame_set(1)
    orbit.rotation_euler[2] = start_rad
    orbit.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(TOTAL_FRAMES + 1)
    orbit.rotation_euler[2] = start_rad + num_orbits * math.tau
    orbit.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(orbit)

    total_spin = num_rots * math.tau
    sc.frame_set(1)
    planet.rotation_euler[2] = 0.0
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    sc.frame_set(TOTAL_FRAMES + 1)
    planet.rotation_euler[2] = total_spin
    planet.keyframe_insert(data_path="rotation_euler", index=2)
    make_linear(planet)

    major = r_bu * 1.55
    minor = r_bu * 0.12
    pw = planet.matrix_world.translation
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        location=pw,
        rotation=(0.0, 0.0, 0.0),
        mode="MAJOR_MINOR",
        major_radius=major,
        minor_radius=minor,
        major_segments=128,
        minor_segments=32,
        generate_uvs=True,
    )
    ring_obj = bpy.context.active_object
    ring_obj.name = "Ring_Saturn"
    bpy.ops.object.shade_smooth()
    parent_keep_transform(ring_obj, planet)

    img_planet = load_image(texture_path_for_key("saturn"), "saturn_albedo", "sRGB")
    mat_textured_planet(planet, img_planet, roughness=0.62, spec=0.18)

    ring_tex_path = TEXTURE_DIR / TEXTURE_FILES["saturn_ring"]
    ring_img = load_image(ring_tex_path, "saturn_ring", "sRGB")
    ring_obj.data.materials.clear()
    rmat = bpy.data.materials.new("Mat_Saturn_Ring")
    rmat.use_nodes = True
    try:
        rmat.surface_render_method = "BLENDED"
    except AttributeError:
        pass
    ring_obj.data.materials.append(rmat)
    nt = rmat.node_tree
    N = nt.nodes
    L = nt.links
    N.clear()
    uv = N.new("ShaderNodeTexCoord")
    tex = N.new("ShaderNodeTexImage")
    out = N.new("ShaderNodeOutputMaterial")
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    uv.location = (-800, 0)
    tex.location = (-520, 0)
    bsdf.location = (180, 0)
    out.location = (480, 0)
    if ring_img:
        tex.image = ring_img
        tex.image.colorspace_settings.name = "sRGB"
        L.new(uv.outputs["UV"], tex.inputs["Vector"])
        L.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if "Alpha" in tex.outputs:
            L.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    else:
        bsdf.inputs["Base Color"].default_value = (0.82, 0.76, 0.62, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    principled_set_specular(bsdf, 0.12)
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    sc.frame_set(1)
    return planet, orbit
