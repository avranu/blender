from __future__ import annotations
import math
import random
from typing import Optional
from pathlib import Path
import bpy

SERIAL_FONT: Path = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\The Horuss.ttf"
)
TEXT_FONT: Path = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Bison-Bold.ttf"
)


class HRSH_Tag:
    length: float = 61.9125  # mm
    width: float = 14.2875  # mm
    depth: float = 1.5875  # mm
    text: str = "Hudson River Psychiatric Center"
    serial_prefix: str = "0008-"
    _tag: Optional[bpy.types.Object] = None

    @property
    def tag(self) -> bpy.types.Object:
        if not self._tag:
            self.create_base_tag()
        return self._tag

    @tag.setter
    def tag(self, value: bpy.types.Object) -> None:
        self._tag = value

    def __init__(self) -> None:
        pass

    def clear_scene(self) -> None:
        """Remove all objects from the scene."""
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    def set_units_to_mm(self) -> None:
        """Set scene units to millimeters."""
        scene: bpy.types.Scene = bpy.context.scene
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.scale_length = 0.001
        scene.unit_settings.length_unit = "MILLIMETERS"

    def setup_scene(self):
        """Clear the scene and set units to millimeters."""
        self.clear_scene()
        self.set_units_to_mm()

    def create_base_tag(self):
        """Create a rectangular base tag and apply bevel to corners."""
        bpy.ops.mesh.primitive_plane_add(
            size=1, enter_editmode=False, location=(0, 0, 0)
        )
        self.tag = bpy.context.object
        self.tag.scale = (
            self.length / (self.tag.dimensions.x or 2),
            self.width / (self.tag.dimensions.y or 2),
            self.depth / (self.tag.dimensions.z or 1),
        )

        self.bevel_tag()
        metal_mat = bpy.data.materials.new(name="Metal")
        self.tag.data.materials.append(metal_mat)

        # Solidify
        bpy.ops.object.modifier_add(type="SOLIDIFY")
        self.tag.modifiers["Solidify"].thickness = 2
        bpy.context.view_layer.update()

    def bevel_tag(self):
        """Apply a bevel modifier to the tag."""
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bevel(
            offset_type="OFFSET", offset=0.1, segments=20, affect="VERTICES"
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.update()

    def add_text(
        self,
        text: str,
        kerning: float,
        font_path: Path,
        size: float,
    ):
        """Add text to the tag, convert to mesh, and handle optional inset."""
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.data.body = text.upper()
        text_obj.data.space_character = kerning
        text_obj.data.font = bpy.data.fonts.load(str(font_path))
        text_obj.data.size = size
        bpy.context.view_layer.update()

        # Calculate the top surface of the base tag
        tag_top_z = self.tag.location.z + (self.tag.dimensions.z / 2)
        # Set the text object's top to align with the tag's top
        text_obj.location.z = tag_top_z - (text_obj.dimensions.z / 2)

        black_mat = bpy.data.materials.new(name="Black")
        text_obj.data.materials.append(black_mat)
        text_obj.data.materials[0].diffuse_color = (0, 0, 0, 1)

        bpy.ops.object.convert(target="MESH")
        bpy.context.view_layer.objects.active = text_obj

        self.inset_text(text_obj)

        return text_obj

    def scale_text(self, text_obj: bpy.types.Object, text_height: float):
        """Scale the text object to the desired height."""
        text_obj.scale = (
            text_obj.scale[0],
            text_height / text_obj.dimensions.y,
            text_obj.scale[2],
        )
        self.center_text(text_obj)

    def center_text(self, text_obj: bpy.types.Object):
        """Center the text object on the base tag."""
        text_obj.location.x = -text_obj.dimensions.x / 2
        text_obj.location.y = -text_obj.dimensions.y / 2
        text_obj.location.z = self.tag.dimensions.z / 2 + self.tag.location.z

    def inset_text(self, text_obj: bpy.types.Object):
        """Perform a boolean difference to inset the text into the base tag."""
        # Set the text object to active
        bpy.context.view_layer.objects.active = text_obj
        
        # Add a solidify modifier to extrude the text downwards
        solidify_modifier = text_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify_modifier.thickness = -0.2

        boolean_modifier = self.tag.modifiers.new(name="Boolean", type='BOOLEAN')
        boolean_modifier.operation = 'DIFFERENCE'
        boolean_modifier.object = text_obj
        bpy.context.view_layer.update()

    def create_tag(self):
        """Create the complete tag with both types of text."""
        self.create_base_tag()
        # Create a random number from 10000 to 99999
        serial_number = math.floor(random.random() * 90000 + 10000)
        number_text = f"{self.serial_prefix}{serial_number}"
        number = self.add_text(number_text, 1.4, SERIAL_FONT, 5.6)
        self.scale_text(number, 3.175)

        hrpc = self.add_text(self.text, 1.0, TEXT_FONT, 5.5)
        self.scale_text(hrpc, 3.175)
        hrpc.location.y += 4.0
        number.location.y = hrpc.location.y - hrpc.dimensions.y - 2.7
        bpy.context.view_layer.update()


def main():
    tag = HRSH_Tag()
    tag.setup_scene()
    tag.create_tag()


if __name__ == "__main__":
    main()