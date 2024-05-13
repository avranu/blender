from __future__ import annotations
import math
import random
from typing import Optional
from pathlib import Path
import bpy


def fix_orientation():
    obj = bpy.data.objects.get("TagSurface")
    obj.location = (0, 0, 0)


def clear_below_z():
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")


def extrude_down():
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, -2)})
    bpy.ops.object.mode_set(mode="OBJECT")


def smooth_surfaces():
    # Selects only the outer vertices for smoothing
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.vertices_smooth(factor=1)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")

def scale_to_size():
    # Scale to width 61.9125mm x height 14.2875mm x depth 2mm
    obj = bpy.data.objects["TagSurface"]
    obj.scale = (61.9125, 14.2875, 2)


def apply_black_material_to_inner_text():
    # Assigns a black material to the selected inner text
    text_material = bpy.data.materials.new(name="BlackMaterial")
    text_material.diffuse_color = (0, 0, 0, 1)  # RBGA, A is the alpha (transparency)
    obj = bpy.data.objects["TagSurface"]
    if not obj.data.materials:
        obj.data.materials.append(text_material)
    else:
        obj.data.materials[0] = text_material

    # Select text by its material
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.material_slot_select()
    bpy.ops.object.mode_set(mode="OBJECT")


def main():
    #fix_orientation()
    #clear_below_z()
    #extrude_down()
    smooth_surfaces()
    apply_black_material_to_inner_text()
    bpy.context.view_layer.update()


if __name__ == "__main__":
    main()
