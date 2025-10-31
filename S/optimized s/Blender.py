# blender_export.py
import sys, bpy, os, math
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--rc", type=float, default=1.0)
    parser.add_argument("--dp", type=float, default=0.4)
    parser.add_argument("--ts", type=float, default=0.05)
    parser.add_argument("--S", type=int, default=6)
    parser.add_argument("--delta", type=float, default=0.2)
    return parser.parse_known_args()[0]

args = parse_args()

# find object (adjust name if needed)
obj_name = "Nanocage_Base"
obj = bpy.data.objects.get(obj_name)
if obj is None:
    raise RuntimeError(f"Object {obj_name} not found in scene")

# find first NODES modifier
modifier = None
for m in obj.modifiers:
    if m.type == 'NODES':
        modifier = m
        break
if modifier is None:
    raise RuntimeError("No Geometry Nodes modifier on object")

# Map parameter names to modifier inputs:
# Print available keys in interactive runs to confirm mapping
# e.g. modifier["Input_2"] = args.delta
# You might need to inspect modifier keys or set up the node tree with known indexes.
# Below we try to set common indices; adapt to your group.
try:
    modifier["Input_2"] = args.delta   # Deformation amplitude
    modifier["Input_3"] = args.rc      # Noise scale
    modifier["Input_4"] = args.dp      # pore diameter
    modifier["Input_5"] = args.ts      # thickness
    modifier["Input_6"] = float(args.S) # symmetry (could be used)
except Exception as e:
    print("Warning: could not set modifier inputs directly:", e)

# force depsgraph evaluation and get evaluated mesh
deps = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(deps)
mesh = eval_obj.to_mesh()

# create temporary object
temp = bpy.data.objects.new("temp_eval", mesh)
bpy.context.collection.objects.link(temp)

# select only temp and export
bpy.ops.object.select_all(action='DESELECT')
temp.select_set(True)
bpy.context.view_layer.objects.active = temp

outdir = os.path.dirname(args.out)
os.makedirs(outdir, exist_ok=True)
bpy.ops.export_scene.obj(filepath=args.out, use_selection=True, use_mesh_modifiers=True)

# cleanup
bpy.data.objects.remove(temp, do_unlink=True)
print("Exported", args.out)
