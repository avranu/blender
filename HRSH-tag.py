from pathlib import Path
import bpy

TEXT_FONT = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\The Horuss.ttf"
)
SERIAL_FONT = Path(
    "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Bison-Bold.ttf"
)


class HRSH_Tag:
    def __init__(self):
        self.length = 61.9125  # mm
        self.width = 14.2875  # mm
        self.depth = 1.5875  # mm
        self.text = "Hudson River Psychiatric Center"
        self.serial_prefix = "0008-"
        self.tag = None

    def clear_scene(self):
        """Remove all objects from the scene."""
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

    def set_units_to_mm(self):
        """Set scene units to millimeters."""
        scene = bpy.context.scene
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.scale_length = 0.001
        scene.unit_settings.length_unit = "MILLIMETERS"

    def create_base_tag(self):
        """Create a rectangular base tag and apply bevel to corners."""
        bpy.ops.mesh.primitive_plane_add(
            size=1, enter_editmode=False, location=(0, 0, 0)
        )
        self.tag = bpy.context.object
        self.tag.scale = (
            self.length / 2,
            self.width / 2,
            self.depth,
        )  # Adjusted for correct scale calculation
        bpy.context.view_layer.update()  # Ensure the context is updated after scaling

        # Apply bevel modifier
        bevel_mod = self.tag.modifiers.new(name="Bevel", type="BEVEL")
        bevel_mod.width = 0.5  # Set as required
        bevel_mod.segments = 5  # Adjust for smoother bevel
        bevel_mod.profile = 0.5
        bevel_mod.affect = "VERTICES"  # Affects only vertices

        # Apply material
        metal_mat = bpy.data.materials.new(name="Metal")
        self.tag.data.materials.append(metal_mat)

    def add_text(self, text, text_height, inset=False, kerning=1, font_path=TEXT_FONT):
        """Add text to the tag, convert to mesh, and handle optional inset."""
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.data.body = text.upper()
        text_obj.data.space_character = kerning
        text_obj.data.font = bpy.data.fonts.load(str(font_path))

        bpy.ops.object.convert(target="MESH")
        text_obj.dimensions.y = text_height  # Directly set the desired text height
        self.center_text(text_obj)

        black_mat = bpy.data.materials.new(name="Black")
        text_obj.data.materials.append(black_mat)
        text_obj.data.materials[0].diffuse_color = (0, 0, 0, 1)

        if inset:
            self.inset_text(text_obj)

    def center_text(self, text_obj):
        """Center the text object on the base tag."""
        text_obj.location.x = -self.tag.dimensions.x / 2
        text_obj.location.y = -self.tag.dimensions.y / 2
        text_obj.location.z = self.tag.dimensions.z + self.depth

    def inset_text(self, text_obj):
        """Perform a boolean difference to inset the text into the base tag."""
        modifier = self.tag.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.object = text_obj
        bpy.context.view_layer.update()

    def create_tag(self, serial_number="17756"):
        """Create the complete tag with both types of text."""
        self.create_base_tag()
        number_text = f"{self.serial_prefix}{serial_number}"
        self.add_text(number_text, 3.175, True, 1.4, SERIAL_FONT)
        self.add_text(self.text, 3.175, False)


def main():
    tag = HRSH_Tag()
    tag.clear_scene()
    tag.set_units_to_mm()
    tag.create_tag()


if __name__ == "__main__":
    main()