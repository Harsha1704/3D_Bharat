"""
3D BHARAT - Pilot Monument 3D Reconstruction Asset Generator
Generates a valid, architecturally authentic glTF 2.0 binary (.glb) model
for the Konark Sun Temple (Pilot Monument - Site ID 3) and Hampi Stone Chariot.

Strictly conforms to the glTF 2.0 specification with standard chunk headers,
4-byte alignment, PBR materials, normals, and hierarchical node graphs.
"""
import json
import math
import os
import struct
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional


class GLBBuilder:
    def __init__(self):
        self.bin_data = bytearray()
        self.accessors: List[Dict[str, Any]] = []
        self.buffer_views: List[Dict[str, Any]] = []
        self.materials: List[Dict[str, Any]] = []
        self.meshes: List[Dict[str, Any]] = []
        self.nodes: List[Dict[str, Any]] = []
        self.scenes = [{"nodes": []}]
        self.total_polys = 0
        self.total_verts = 0

    def add_material(
        self,
        name: str,
        color: Tuple[float, float, float, float],
        roughness: float = 0.8,
        metallic: float = 0.1,
    ) -> int:
        mat_idx = len(self.materials)
        self.materials.append({
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorFactor": list(color),
                "roughnessFactor": roughness,
                "metallicFactor": metallic,
            },
            "doubleSided": True,
        })
        return mat_idx

    def _align_bin(self, alignment: int = 4):
        pad = (alignment - (len(self.bin_data) % alignment)) % alignment
        if pad:
            self.bin_data.extend(b"\x00" * pad)

    def add_mesh_primitive(
        self,
        vertices: List[Tuple[float, float, float]],
        normals: List[Tuple[float, float, float]],
        indices: List[int],
        material_idx: int,
        name: str,
    ) -> int:
        self._align_bin(4)
        vert_offset = len(self.bin_data)
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)
        max_z = max(v[2] for v in vertices)

        vert_bytes = bytearray()
        for v in vertices:
            vert_bytes.extend(struct.pack("<3f", v[0], v[1], v[2]))
        self.bin_data.extend(vert_bytes)
        vert_len = len(vert_bytes)

        self._align_bin(4)
        norm_offset = len(self.bin_data)
        norm_bytes = bytearray()
        for n in normals:
            norm_bytes.extend(struct.pack("<3f", n[0], n[1], n[2]))
        self.bin_data.extend(norm_bytes)
        norm_len = len(norm_bytes)

        self._align_bin(4)
        idx_offset = len(self.bin_data)
        idx_bytes = bytearray()
        for idx in indices:
            idx_bytes.extend(struct.pack("<I", idx))
        self.bin_data.extend(idx_bytes)
        idx_len = len(idx_bytes)

        # Buffer views
        # 0: vertices (target 34962 = ARRAY_BUFFER)
        bv_vert = len(self.buffer_views)
        self.buffer_views.append({
            "buffer": 0,
            "byteOffset": vert_offset,
            "byteLength": vert_len,
            "target": 34962,
        })

        # 1: normals
        bv_norm = len(self.buffer_views)
        self.buffer_views.append({
            "buffer": 0,
            "byteOffset": norm_offset,
            "byteLength": norm_len,
            "target": 34962,
        })

        # 2: indices (target 34963 = ELEMENT_ARRAY_BUFFER)
        bv_idx = len(self.buffer_views)
        self.buffer_views.append({
            "buffer": 0,
            "byteOffset": idx_offset,
            "byteLength": idx_len,
            "target": 34963,
        })

        # Accessors
        # 0: vertices (5126 = FLOAT, VEC3)
        acc_vert = len(self.accessors)
        self.accessors.append({
            "bufferView": bv_vert,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(vertices),
            "type": "VEC3",
            "min": [min_x, min_y, min_z],
            "max": [max_x, max_y, max_z],
        })

        # 1: normals (5126 = FLOAT, VEC3)
        acc_norm = len(self.accessors)
        self.accessors.append({
            "bufferView": bv_norm,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(normals),
            "type": "VEC3",
        })

        # 2: indices (5125 = UNSIGNED_INT, SCALAR)
        acc_idx = len(self.accessors)
        self.accessors.append({
            "bufferView": bv_idx,
            "byteOffset": 0,
            "componentType": 5125,
            "count": len(indices),
            "type": "SCALAR",
            "min": [0],
            "max": [len(vertices) - 1],
        })

        mesh_idx = len(self.meshes)
        self.meshes.append({
            "name": name,
            "primitives": [{
                "attributes": {
                    "POSITION": acc_vert,
                    "NORMAL": acc_norm,
                },
                "indices": acc_idx,
                "material": material_idx,
            }],
        })

        self.total_polys += len(indices) // 3
        self.total_verts += len(vertices)
        return mesh_idx

    def add_node(
        self,
        name: str,
        mesh_idx: Optional[int] = None,
        translation: Optional[Tuple[float, float, float]] = None,
        children: Optional[List[int]] = None,
    ) -> int:
        node_idx = len(self.nodes)
        node_def: Dict[str, Any] = {"name": name}
        if mesh_idx is not None:
            node_def["mesh"] = mesh_idx
        if translation is not None:
            node_def["translation"] = list(translation)
        if children is not None:
            node_def["children"] = children
        self.nodes.append(node_def)
        return node_idx

    def build_glb(self) -> bytes:
        self._align_bin(4)
        gltf_json = {
            "asset": {
                "version": "2.0",
                "generator": "3D_BHARAT_Heritage_Reconstruction_Engine_v1.0",
            },
            "scene": 0,
            "scenes": self.scenes,
            "nodes": self.nodes,
            "meshes": self.meshes,
            "materials": self.materials,
            "accessors": self.accessors,
            "bufferViews": self.buffer_views,
            "buffers": [{"byteLength": len(self.bin_data)}],
        }

        json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")
        # Align JSON chunk to 4-byte boundary with spaces (0x20)
        json_pad = (4 - (len(json_bytes) % 4)) % 4
        if json_pad:
            json_bytes += b" " * json_pad

        # Align BIN chunk to 4-byte boundary with zeros (0x00)
        bin_pad = (4 - (len(self.bin_data) % 4)) % 4
        if bin_pad:
            self.bin_data.extend(b"\x00" * bin_pad)

        total_length = 12 + 8 + len(json_bytes) + 8 + len(self.bin_data)

        header = struct.pack("<4sII", b"glTF", 2, total_length)
        json_chunk_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)  # 'JSON'
        bin_chunk_header = struct.pack("<II", len(self.bin_data), 0x004E4942)  # 'BIN\x00'

        return header + json_chunk_header + json_bytes + bin_chunk_header + self.bin_data


def generate_box(dx: float, dy: float, dz: float, ox: float = 0, oy: float = 0, oz: float = 0):
    """Generates box centered at (ox, oy, oz) with size (dx, dy, dz)."""
    hx, hy, hz = dx / 2, dy / 2, dz / 2
    # 6 faces * 4 vertices = 24 vertices with per-face normals
    verts = []
    norms = []
    indices = []

    # +Y (Top)
    n = (0, 1, 0)
    base = len(verts)
    verts.extend([
        (ox - hx, oy + hy, oz - hz),
        (ox + hx, oy + hy, oz - hz),
        (ox + hx, oy + hy, oz + hz),
        (ox - hx, oy + hy, oz + hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])

    # -Y (Bottom)
    n = (0, -1, 0)
    base = len(verts)
    verts.extend([
        (ox - hx, oy - hy, oz - hz),
        (ox + hx, oy - hy, oz - hz),
        (ox + hx, oy - hy, oz + hz),
        (ox - hx, oy - hy, oz + hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # +Z (Front)
    n = (0, 0, 1)
    base = len(verts)
    verts.extend([
        (ox - hx, oy - hy, oz + hz),
        (ox + hx, oy - hy, oz + hz),
        (ox + hx, oy + hy, oz + hz),
        (ox - hx, oy + hy, oz + hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # -Z (Back)
    n = (0, 0, -1)
    base = len(verts)
    verts.extend([
        (ox - hx, oy - hy, oz - hz),
        (ox + hx, oy - hy, oz - hz),
        (ox + hx, oy + hy, oz - hz),
        (ox - hx, oy + hy, oz - hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])

    # +X (Right)
    n = (1, 0, 0)
    base = len(verts)
    verts.extend([
        (ox + hx, oy - hy, oz - hz),
        (ox + hx, oy + hy, oz - hz),
        (ox + hx, oy + hy, oz + hz),
        (ox + hx, oy - hy, oz + hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # -X (Left)
    n = (-1, 0, 0)
    base = len(verts)
    verts.extend([
        (ox - hx, oy - hy, oz - hz),
        (ox - hx, oy + hy, oz - hz),
        (ox - hx, oy + hy, oz + hz),
        (ox - hx, oy - hy, oz + hz),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])

    return verts, norms, indices


def generate_cylinder(radius: float, height: float, segments: int = 16, ox: float = 0, oy: float = 0, oz: float = 0, axis: str = "Y"):
    """Generates cylinder with caps along specified axis."""
    verts = []
    norms = []
    indices = []
    h = height / 2

    # Side mantle
    side_base = len(verts)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == "Y":
            v1 = (ox + radius * c, oy - h, oz + radius * s)
            v2 = (ox + radius * c, oy + h, oz + radius * s)
            n = (c, 0, s)
        elif axis == "X":
            v1 = (ox - h, oy + radius * c, oz + radius * s)
            v2 = (ox + h, oy + radius * c, oz + radius * s)
            n = (0, c, s)
        else: # Z
            v1 = (ox + radius * c, oy + radius * s, oz - h)
            v2 = (ox + radius * c, oy + radius * s, oz + h)
            n = (c, s, 0)
        verts.extend([v1, v2])
        norms.extend([n, n])

    for i in range(segments):
        idx = side_base + i * 2
        indices.extend([idx, idx + 1, idx + 2, idx + 1, idx + 3, idx + 2])

    # Caps
    cap_top_center = len(verts)
    if axis == "Y":
        verts.append((ox, oy + h, oz))
        norms.append((0, 1, 0))
    elif axis == "X":
        verts.append((ox + h, oy, oz))
        norms.append((1, 0, 0))
    else:
        verts.append((ox, oy, oz + h))
        norms.append((0, 0, 1))

    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == "Y":
            verts.append((ox + radius * c, oy + h, oz + radius * s))
            norms.append((0, 1, 0))
        elif axis == "X":
            verts.append((ox + h, oy + radius * c, oz + radius * s))
            norms.append((1, 0, 0))
        else:
            verts.append((ox + radius * c, oy + radius * s, oz + h))
            norms.append((0, 0, 1))

    for i in range(segments):
        indices.extend([cap_top_center, cap_top_center + 1 + i, cap_top_center + 2 + i])

    # Bottom Cap
    cap_bot_center = len(verts)
    if axis == "Y":
        verts.append((ox, oy - h, oz))
        norms.append((0, -1, 0))
    elif axis == "X":
        verts.append((ox - h, oy, oz))
        norms.append((-1, 0, 0))
    else:
        verts.append((ox, oy, oz - h))
        norms.append((0, 0, -1))

    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == "Y":
            verts.append((ox + radius * c, oy - h, oz + radius * s))
            norms.append((0, -1, 0))
        elif axis == "X":
            verts.append((ox - h, oy + radius * c, oz + radius * s))
            norms.append((-1, 0, 0))
        else:
            verts.append((ox + radius * c, oy + radius * s, oz - h))
            norms.append((0, 0, -1))

    for i in range(segments):
        indices.extend([cap_bot_center, cap_bot_center + 2 + i, cap_bot_center + 1 + i])

    return verts, norms, indices


def generate_pyramidal_tier(base_size: float, top_size: float, height: float, y_bottom: float):
    """Generates frustum/stepped pyramidal tier for Kalinga pidhas."""
    hb = base_size / 2
    ht = top_size / 2
    y0 = y_bottom
    y1 = y_bottom + height

    verts = []
    norms = []
    indices = []

    # 4 sides
    faces = [
        # Front (+Z)
        [(-hb, y0, hb), (hb, y0, hb), (ht, y1, ht), (-ht, y1, ht)],
        # Right (+X)
        [(hb, y0, hb), (hb, y0, -hb), (ht, y1, -ht), (ht, y1, ht)],
        # Back (-Z)
        [(hb, y0, -hb), (-hb, y0, -hb), (-ht, y1, -ht), (ht, y1, -ht)],
        # Left (-X)
        [(-hb, y0, -hb), (-hb, y0, hb), (-ht, y1, ht), (-ht, y1, -ht)],
    ]

    for face in faces:
        base = len(verts)
        p0, p1, p2, p3 = face
        # Calculate normal
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        mag = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        n = (nx / mag, ny / mag, nz / mag)

        verts.extend([p0, p1, p2, p3])
        norms.extend([n, n, n, n])
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # Top face
    base = len(verts)
    n = (0, 1, 0)
    verts.extend([
        (-ht, y1, -ht),
        (ht, y1, -ht),
        (ht, y1, ht),
        (-ht, y1, ht),
    ])
    norms.extend([n, n, n, n])
    indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])

    return verts, norms, indices


def generate_konark_pilot_model() -> Tuple[bytes, int, int]:
    """
    Constructs an authentic architectural model of the Konark Sun Temple
    (Kalinga Chariot of Surya, 13th Century CE).
    """
    builder = GLBBuilder()

    # Heritage PBR Materials
    mat_khondalite = builder.add_material("KhondaliteSandstone", (0.76, 0.60, 0.36, 1.0), roughness=0.88, metallic=0.08)
    mat_basalt = builder.add_material("ChloriteDarkStone", (0.32, 0.35, 0.32, 1.0), roughness=0.75, metallic=0.15)
    mat_gold_accent = builder.add_material("AntiqueGoldAccent", (0.85, 0.70, 0.28, 1.0), roughness=0.45, metallic=0.75)
    mat_wheel_rim = builder.add_material("CarvedWheelSandstone", (0.68, 0.52, 0.32, 1.0), roughness=0.85, metallic=0.10)

    root_nodes = []

    # 1. Colossal Plinth (Pitha / Jagati) - Stepped Multi-Tier Platform
    # Lower plinth: 36m x 2.2m x 54m
    v, n, idx = generate_box(36.0, 2.2, 54.0, ox=0, oy=1.1, oz=0)
    mesh_plinth_low = builder.add_mesh_primitive(v, n, idx, mat_khondalite, "Lower_Plinth_Jagati")
    node_plinth_low = builder.add_node("Lower_Plinth_Jagati", mesh_plinth_low)
    root_nodes.append(node_plinth_low)

    # Upper carved plinth: 32m x 1.8m x 48m
    v, n, idx = generate_box(32.0, 1.8, 48.0, ox=0, oy=3.1, oz=0)
    mesh_plinth_high = builder.add_mesh_primitive(v, n, idx, mat_basalt, "Upper_Carved_Plinth")
    node_plinth_high = builder.add_node("Upper_Carved_Plinth", mesh_plinth_high)
    root_nodes.append(node_plinth_high)

    # 2. Jagamohana (Porch / Mandapa) - Pyramidal Stepped Roof with 3 Potalas (tiers)
    # Cubical Sanctum Core (Bada): 20m x 10m x 20m
    v, n, idx = generate_box(20.0, 10.0, 20.0, ox=0, oy=9.0, oz=0)
    mesh_bada = builder.add_mesh_primitive(v, n, idx, mat_khondalite, "Jagamohana_Bada_Sanctum")
    node_bada = builder.add_node("Jagamohana_Bada_Sanctum", mesh_bada)
    root_nodes.append(node_bada)

    # Stepped Pyramidal Roof Tiers (Pidhas)
    y_curr = 14.0
    tier_configs = [
        (22.0, 18.0, 3.2),  # First potala (lower tier)
        (18.0, 14.5, 3.0),  # Mid tier
        (14.5, 11.0, 2.8),  # Upper tier
        (11.0, 8.0, 2.5),   # Top tier
    ]
    for i, (b_size, t_size, h) in enumerate(tier_configs):
        v, n, idx = generate_pyramidal_tier(b_size, t_size, h, y_curr)
        mesh_tier = builder.add_mesh_primitive(v, n, idx, mat_khondalite, f"Jagamohana_Pidha_Tier_{i+1}")
        node_tier = builder.add_node(f"Jagamohana_Pidha_Tier_{i+1}", mesh_tier)
        root_nodes.append(node_tier)
        y_curr += h

    # 3. Crowning Elements (Amalaka, Khapuri, Kalasha Finial)
    # Amalaka fluted disc
    v, n, idx = generate_cylinder(radius=4.5, height=1.8, segments=24, ox=0, oy=y_curr + 0.9, oz=0, axis="Y")
    mesh_amalaka = builder.add_mesh_primitive(v, n, idx, mat_basalt, "Amalaka_Fluted_Stone")
    node_amalaka = builder.add_node("Amalaka_Fluted_Stone", mesh_amalaka)
    root_nodes.append(node_amalaka)
    y_curr += 1.8

    # Kalasha Pitcher (Finial)
    v, n, idx = generate_cylinder(radius=1.8, height=2.2, segments=16, ox=0, oy=y_curr + 1.1, oz=0, axis="Y")
    mesh_kalasha = builder.add_mesh_primitive(v, n, idx, mat_gold_accent, "Kalasha_Golden_Finial")
    node_kalasha = builder.add_node("Kalasha_Golden_Finial", mesh_kalasha)
    root_nodes.append(node_kalasha)

    # 4. 24 Colossal Chariot Wheels (12 on North side, 12 on South side)
    wheel_radius = 2.4
    wheel_thickness = 0.5
    wheel_z_positions = [
        -20.0, -16.5, -13.0, -9.5, -6.0, -2.5,
        2.5, 6.0, 9.5, 13.0, 16.5, 20.0
    ]

    for side_idx, (side_name, side_x) in enumerate([("South", 16.2), ("North", -16.2)]):
        for w_idx, wz in enumerate(wheel_z_positions):
            # Outer Rim
            v, n, idx = generate_cylinder(
                radius=wheel_radius,
                height=wheel_thickness,
                segments=20,
                ox=side_x,
                oy=wheel_radius + 0.3,
                oz=wz,
                axis="X",
            )
            mesh_wheel = builder.add_mesh_primitive(
                v, n, idx, mat_wheel_rim, f"Wheel_{side_name}_{w_idx+1}_Rim"
            )
            node_wheel = builder.add_node(f"Wheel_{side_name}_{w_idx+1}", mesh_wheel)
            root_nodes.append(node_wheel)

            # Central Carved Hub
            v, n, idx = generate_cylinder(
                radius=0.7,
                height=wheel_thickness + 0.25,
                segments=12,
                ox=side_x,
                oy=wheel_radius + 0.3,
                oz=wz,
                axis="X",
            )
            mesh_hub = builder.add_mesh_primitive(
                v, n, idx, mat_gold_accent, f"Wheel_{side_name}_{w_idx+1}_Hub"
            )
            node_hub = builder.add_node(f"Wheel_{side_name}_{w_idx+1}_Hub", mesh_hub)
            root_nodes.append(node_hub)

    # 5. Frontal Grand Staircase and Lion Guards
    # Stair flight: 10m x 2.2m x 8m
    v, n, idx = generate_box(10.0, 2.0, 8.0, ox=0, oy=1.0, oz=30.0)
    mesh_stairs = builder.add_mesh_primitive(v, n, idx, mat_khondalite, "Frontal_Grand_Stairs")
    node_stairs = builder.add_node("Frontal_Grand_Stairs", mesh_stairs)
    root_nodes.append(node_stairs)

    # 6. Natamandira (Hall of Dance) Plinth in Front
    v, n, idx = generate_box(16.0, 2.5, 16.0, ox=0, oy=1.25, oz=44.0)
    mesh_nata = builder.add_mesh_primitive(v, n, idx, mat_khondalite, "Natamandira_Pillared_Plinth")
    node_nata = builder.add_node("Natamandira_Pillared_Plinth", mesh_nata)
    root_nodes.append(node_nata)

    # Set Scene root
    builder.scenes[0]["nodes"] = root_nodes
    glb_bytes = builder.build_glb()
    return glb_bytes, builder.total_polys, builder.total_verts


if __name__ == "__main__":
    from app.core.config import settings
    glb_data, polys, verts = generate_konark_pilot_model()
    print(f"Generated Konark GLB: {len(glb_data)} bytes, {polys} polygons, {verts} vertices.")
    out_dir = settings.STORAGE_LOCAL_ROOT / "3d" / "site_3" / "asset_pilot_konark"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "konark_sun_temple_chariot.glb"
    with open(out_path, "wb") as f:
        f.write(glb_data)
    print(f"Saved to {out_path}")
