import bpy

# Clear existing objects using low-level API access
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# Set units to millimeters
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"


class HRSH_Tag:
    tag: bpy.types.Object

    def __init__(self):
        self.tag = None

    def create_base_tag(self):
        # Create a rectangular base tag
        bpy.ops.mesh.primitive_plane_add(size=1)
        self.tag = bpy.context.object
        self.tag.scale = (
            61.9125 / 2,
            14.2875 / 2,
            1,
        )  # Scale to convert dimensions to mm and divide by 2 because size is full dimension
        self.tag.location = (0, 0, 1)  # Center on grid, elevate by 1mm

        # Enter edit mode to bevel corners
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")  # Select all vertices of the plane
        bpy.ops.mesh.bevel(
            offset_type="OFFSET", offset=0.1, segments=10, affect="VERTICES"
        )  # Adjust offset as needed for the desired corner radius
        bpy.ops.object.mode_set(mode="OBJECT")

        # Set the tag's material (optional)
        mat = bpy.data.materials.new(name="Metal")
        self.tag.data.materials.append(mat)

        return self.tag

    # Function to add and position text on the base tag
    def add_text(self, text, text_height, inset=False, kerning=1, font=None):
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.data.body = text.upper()
        # Adjust kerning
        text_obj.data.space_character = kerning
        # Set font to "bison demi bold"
        if not font:
            font = "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Bison-Bold.ttf"
        text_obj.data.font = bpy.data.fonts.load(font)

        bpy.ops.object.convert(target="MESH")

        # Set dimensions and position to lay flat
        bpy.context.view_layer.objects.active = text_obj
        bpy.context.view_layer.update()

        bpy.ops.object.mode_set(mode="EDIT")
        # Adjust scale based on desired text height
        current_height = text_obj.dimensions.y or 1
        scale_factor = text_height / current_height
        text_obj.scale *= scale_factor
        bpy.ops.object.mode_set(mode="OBJECT")

        # Center text on the base tag
        self.center_text(text_obj)

        # Set material color to black
        bpy.ops.object.mode_set(mode="EDIT")
        mat = bpy.data.materials.new(name="Black")
        text_obj.data.materials.append(mat)
        text_obj.data.materials[0].diffuse_color = (0, 0, 0, 1)

        # Give the text_obj a width of 2mm
        # self.solidify(text_obj, 0.2)
        # self.extrude(text_obj)

        if inset:
            self.inset_text(text_obj)

        bpy.ops.object.mode_set(mode="OBJECT")

        return text_obj

    def solidify(self, obj, thickness=0.2):
        bpy.ops.object.modifier_add(type="SOLIDIFY")
        obj.modifiers["Solidify"].thickness = thickness
        bpy.ops.object.modifier_apply(modifier="Solidify")

    def extrude(self, obj, depth=0.2):
        # Ensure the object is the active object
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")

        # Select all geometry of the object
        bpy.ops.mesh.select_all(action="SELECT")

        # Extrude the selected geometry
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, -depth)}
        )

        # Return to object mode
        bpy.ops.object.mode_set(mode="OBJECT")

    def center_text(self, text_obj):
        bpy.ops.object.mode_set(mode="EDIT")
        text_obj.location.x = text_obj.dimensions.x / -2
        text_obj.location.y = text_obj.dimensions.y / -2

        # Z needs to be precisely the surface of base tag
        text_obj.location.z = self.tag.dimensions.z / 2 + self.tag.location.z

        bpy.ops.object.mode_set(mode="OBJECT")

    def inset_text(self, text_obj):
        # Boolean operation to inset the text into the base tag
        modifier = self.tag.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.object = text_obj
        bpy.context.view_layer.update()

    def create(self, code="17756"):
        self.create_base_tag()

        # Adding inseted text "0008-1756"
        number = self.add_text(
            f"0008-{code}",
            3.175,
            True,
            1.4,
            "C:\\Users\\jessa\\AppData\\Local\\Microsoft\\Windows\\Fonts\\The Horuss.ttf",
        )
        number.scale.x = 6
        self.center_text(number)

        # Adding flat text "Hudson River Psychiatric Center"
        hrpc = self.add_text("Hudson  River  Psychiatric  Center", 3.175, False)

        hrpc.location.y += 4.0
        number.location.y = (
            hrpc.location.y - hrpc.dimensions.y - 2.7
        )  # Positiowidth 1.25


tag = HRSH_Tag()
tag.create()