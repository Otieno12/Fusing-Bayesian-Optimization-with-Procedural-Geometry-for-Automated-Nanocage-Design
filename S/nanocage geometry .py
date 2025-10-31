import bpy
import math
import os

# ============================================================
# CONFIGURATION
# ============================================================
EXPORT_PATH = "/tmp/nanocages/"
os.makedirs(EXPORT_PATH, exist_ok=True)

# Parameters: curvature radius (rc), pore diameter (dp), strut thickness (ts),
# symmetry order (S), deformation amplitude (delta)
params = {
    "rc": 1.5,
    "dp": 0.4,
    "ts": 0.1,
    "S": 6,
    "delta": 0.25,
}

# ============================================================
# CLEAN SCENE
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================
# CREATE BASE MESH
# ============================================================
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1)
base_obj = bpy.context.active_object
base_obj.name = "Nanocage"

# ============================================================
# CREATE GEOMETRY NODES GROUP
# ============================================================
mod = base_obj.modifiers.new(name="GeometryNodes", type='NODES')
node_group = bpy.data.node_groups.new("NanocageGeometry", 'GeometryNodeTree')
mod.node_group = node_group

# Clear any default nodes
for node in node_group.nodes:
    node_group.nodes.remove(node)

# ============================================================
# ADD NODE GROUP INTERFACE INPUTS/OUTPUTS (New API)
# ============================================================
interface = node_group.interface

# Create input sockets
interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
interface.new_socket(name="rc", in_out='INPUT', socket_type='NodeSocketFloat')
interface.new_socket(name="dp", in_out='INPUT', socket_type='NodeSocketFloat')
interface.new_socket(name="ts", in_out='INPUT', socket_type='NodeSocketFloat')
interface.new_socket(name="S", in_out='INPUT', socket_type='NodeSocketFloat')
interface.new_socket(name="delta", in_out='INPUT', socket_type='NodeSocketFloat')

# Create output socket
interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# ============================================================
# CREATE NODES
# ============================================================
nodes = node_group.nodes
links = node_group.links

group_in = nodes.new("NodeGroupInput")
group_in.location = (-600, 0)

group_out = nodes.new("NodeGroupOutput")
group_out.location = (600, 0)

pos_node = nodes.new("GeometryNodeInputPosition")
pos_node.location = (-400, 200)

noise_node = nodes.new("ShaderNodeTexNoise")
noise_node.location = (-200, 200)

vec_math = nodes.new("ShaderNodeVectorMath")
vec_math.operation = 'MULTIPLY'
vec_math.location = (0, 200)

set_pos = nodes.new("GeometryNodeSetPosition")
set_pos.location = (200, 0)

# ============================================================
# LINK NODES
# ============================================================
links.new(group_in.outputs["Geometry"], set_pos.inputs["Geometry"])
links.new(pos_node.outputs["Position"], noise_node.inputs["Vector"])
links.new(noise_node.outputs["Color"], vec_math.inputs[0])
links.new(vec_math.outputs["Vector"], set_pos.inputs["Offset"])
links.new(set_pos.outputs["Geometry"], group_out.inputs["Geometry"])

# Connect parameters to noise and displacement
links.new(group_in.outputs["rc"], noise_node.inputs["Scale"])
links.new(group_in.outputs["delta"], vec_math.inputs[1])

# ============================================================
# APPLY PARAMETERS
# ============================================================
mod["Input_2"] = params["rc"]
mod["Input_3"] = params["dp"]
mod["Input_4"] = params["ts"]
mod["Input_5"] = params["S"]
mod["Input_6"] = params["delta"]

# ============================================================
# ADD THICKNESS AND DEFORMATION
# ============================================================
solidify = base_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = params["ts"]

bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_add(type='DISPLACE')
disp = base_obj.modifiers["Displace"]
disp.strength = params["delta"]
tex = bpy.data.textures.new("DisplaceTex", type='CLOUDS')
disp.texture = tex
disp.texture.noise_scale = params["rc"]

# ============================================================
# DUPLICATE FOR SYMMETRY
# ============================================================
for i in range(1, int(params["S"])):
    obj_copy = base_obj.copy()
    obj_copy.data = base_obj.data.copy()
    obj_copy.rotation_euler[2] = (2 * math.pi / params["S"]) * i
    bpy.context.collection.objects.link(obj_copy)

# ============================================================
# EXPORT RESULT
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.join()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

export_name = f"nanocage_rc{params['rc']}_dp{params['dp']}_S{params['S']}.stl"
export_path = os.path.join(EXPORT_PATH, export_name)
bpy.ops.wm.save_mainfile(filepath="C:/Users/otien/OneDrive/Desktop/nanocage_iteration.blend")


print(f"✅ Nanocage exported to: {export_path}")
