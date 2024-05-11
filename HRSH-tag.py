from __future__ import annotations
from typing import Optional
from pathlib import Path
import bpy

TEXT_FONT: Path = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\The Horuss.ttf"
)
SERIAL_FONT: Path = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Bison-Bold.ttf"
)

class HRSH_Tag:
    length: float = 61.9125  # mm
    width: float = 14.2875  # mm
    depth: float = 1.5875  # mm
    text: str = "Hudson River Psychiatric Center"
    serial_prefix: str = "0008-"
    _tag : Optional[bpy.types.Object] = None

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
        bpy.ops.mesh.primitive_plane_add(size=1)
        self.tag = bpy.context.object
        self.tag.scale = (
            self.length / self.tag.dimensions.x,
            self.width / self.tag.dimensions.y,
            self.depth / self.tag.dimensions.z,
        )
        self.tag.location = (0, 0, 1)

        self.bevel_tag()
        metal_mat = bpy.data.materials.new(name="Metal")
        self.tag.data.materials.append(metal_mat)

    def bevel_tag(self):
        """Apply a bevel modifier to the tag."""
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bevel(
            offset_type="OFFSET", offset=0.1, segments=10, affect="VERTICES"
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.update()

    def add_text(self, text : str, text_height : float, inset : bool = False, kerning : float = 1, font_path : Path = TEXT_FONT):
        """Add text to the tag, convert to mesh, and handle optional inset."""
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.data.body = text.upper()
        text_obj.data.space_character = kerning
        if font_path:
            text_obj.data.font = bpy.data.fonts.load(font_path)

        bpy.ops.object.convert(target="MESH")
        bpy.context.view_layer.objects.active = text_obj
        bpy.context.view_layer.update()

        text_obj.scale = (
            text_obj.scale[0],
            text_height / text_obj.dimensions.y,
            text_obj.scale[2],
        )
        self.center_text(text_obj)

        black_mat = bpy.data.materials.new(name="Black")
        text_obj.data.materials.append(black_mat)
        text_obj.data.materials[0].diffuse_color = (0, 0, 0, 1)

        if inset:
            self.inset_text(text_obj)

    def center_text(self, text_obj : bpy.types.Object):
        """Center the text object on the base tag."""
        text_obj.location.x = -text_obj.dimensions.x / 2
        text_obj.location.y = -text_obj.dimensions.y / 2
        text_obj.location.z = self.tag.dimensions.z / 2 + self.tag.location.z

    def inset_text(self, text_obj : bpy.types.Object):
        """Perform a boolean difference to inset the text into the base tag."""
        modifier = self.tag.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.object = text_obj
        bpy.context.view_layer.update()

    def create_tag(self, serial_number : str = "17756"):
        """Create the complete tag with both types of text."""
        self.create_base_tag()
        number_text = f"{self.serial_prefix}{serial_number}"
        number = self.add_text(
            number_text, 3.175, True, 1.4, SERIAL_FONT
        )
        number.scale.x = 6
        self.center_text(number)

        hrpc = self.add_text(self.text, 3.175, False)
        hrpc.location.y += 4.0
        number.location.y = hrpc.location.y - hrpc.dimensions.y - 2.7

def main():
    tag = HRSH_Tag()
    tag.clear_scene()
    tag.set_units_to_mm()
    tag.create_tag()

if __name__ == "__main__":
    main()
