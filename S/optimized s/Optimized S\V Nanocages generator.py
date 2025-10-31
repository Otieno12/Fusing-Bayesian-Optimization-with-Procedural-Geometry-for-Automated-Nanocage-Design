import bpy
import os

# Directory to save meshes
export_dir = r"C:\Users\otien\OneDrive\Desktop\nanocages"
os.makedirs(export_dir, exist_ok=True)

# Target object and modifier name
obj = bpy.data.objects["Nanocage"]  # <-- replace with your object name
modifier = obj.modifiers["GeometryNodes"]

# Range of deformation amplitudes (δ)
deform_values = [0.2, 0.4, 0.6, 0.8]

for δ in deform_values:
    # Set the deformation amplitude parameter
    modifier["Input_1"] = δ  # replace "Input_1" with your actual input name if different

    # Update geometry
    bpy.context.view_layer.update()

    # Define file path
    filename = f"nanocage_{δ:.2f}.obj"
    export_path = os.path.join(export_dir, filename)

    # Export mesh
    bpy.ops.wm.obj_export(
        filepath=export_path,
        export_selected_objects=True,
        export_materials=False
    )

    print(f"✅ Exported nanocage for δ = {δ:.2f} → {filename}")
