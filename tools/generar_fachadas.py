"""PERÚ RACING: Generate 3 modular urban building samples with Blender.
All meshes and materials are original, generic, and not surveyed San Vicente landmarks.
Run: blender -b --factory-startup --python tools/generar_fachadas.py -- --output output
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path.cwd()
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
dest=Path(args[args.index("--output")+1]) if "--output" in args else Path("output")
dest.mkdir(parents=True,exist_ok=True)

def material(name,rgb,rough=0.7,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m
def box(name,loc,scale,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new("soft corners","BEVEL");mod.width=bevel;mod.segments=2
        o.modifiers.new("weighted normals","WEIGHTED_NORMAL")
    return o
def set_scene(kind):
    bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
    palette={
      "wall":material("stucco",{"tienda":(.62,.38,.29),"vivienda":(.79,.71,.52),"esquina":(.79,.77,.66)}[kind]),
      "concrete":material("aged concrete",(.55,.52,.46)),
      "cream":material("white moulding",(.87,.83,.73)),
      "dark":material("dark metal",(.09,.14,.16),.4,.65),
      "glass":material("blue dark window",(.16,.28,.32),.25),
      "wood":material("wooden shutters",(.32,.20,.13)),
      "awning":material("shop awning",(.11,.32,.33)),
      "stone":material("stone threshold",(.40,.36,.30))
    }
    p=palette
    w=9.5;depth=6;height=7.7
    box("building body",(0,0,height/2),(w,depth,height),p["wall"])
    front=-depth/2
    box("stone ground base",(0,front-.09,.32),(w+.12,.22,.64),p["stone"])
    box("horizontal cornice",(0,front-.16,3.48),(w+.32,.38,.22),p["cream"],.035)
    box("roof parapet",(0,0,height+.19),(w+.18,depth+.18,.4),p["cream"])
    box("upper trim",(0,front-.14,height-.2),(w+.4,.38,.24),p["stone"],.035)
    for x in (-3,0,3):
        box("window glass",(x,front-.08,5.48),(1.52,.10,1.53),p["glass"])
        for dx in (-.83,.83):
            box("window vertical frame",(x+dx,front-.19,5.48),(.12,.22,1.71),p["cream"])
        for dz in (-.83,.83):
            box("window lintel",(x,front-.19,5.48+dz),(1.78,.22,.12),p["cream"])
        box("window sill",(x,front-.3,4.58),(1.91,.45,.14),p["stone"],.03)
        if kind!="tienda":
            box("balcony slab",(x,front-.58,4.62),(2.02,.95,.15),p["stone"])
            box("balcony rail",(x,front-1.02,5.21),(2.04,.08,.085),p["dark"])
            for i in range(9):
                box("balcony bar",(x-0.94+i*.235,front-1.02,4.9),(.05,.05,.58),p["dark"])
    box("main entrance",(-1.55,front-.11,1.5),(2.2,.12,2.7),p["wood" if kind=="vivienda" else "glass"])
    for x in (-2.73,-.37):
        box("door frame",(x,front-.24,1.5),(.14,.23,2.85),p["stone"])
    box("door lintel",(-1.55,front-.24,2.92),(2.45,.24,.16),p["stone"])
    box("shopfront",(2.18,front-.10,1.55),(3.14,.12,2.65),p["glass"])
    for x in (.56,3.78):
        box("storefront frame",(x,front-.22,1.55),(.15,.23,2.8),p["dark"])
    box("storefront crossbar",(2.18,front-.22,2.76),(3.4,.23,.08),p["dark"])
    if kind!="vivienda":
        box("sign backing",(0,front-.28,3.12),(6.8,.20,.47),p["awning"],.03)
        box("awning shade",(2.12,front-.93,2.98),(3.8,1.38,.13),p["awning"],.025)
        for x in (0.4,1.2,2,2.8,3.6):
            box("awning edge",(x,front-1.62,2.91),(.16,.08,.15),p["cream"])
    for x in (-w/2+.18,w/2-.18):
        box("facade pilaster",(x,front-.08,5.25),(.18,.2,3.75),p["cream"])
    if kind=="esquina":
        box("side window",(w/2+.07,-.15,2),(.1,2.65,2.05),p["glass"])
        for y in (-1.52,1.22):
            box("side window frame",(w/2+.13,y,2),(.10,.11,2.22),p["dark"])
    return len([o for o in bpy.context.scene.objects if o.type=="MESH"])

def make_preview(path):
    s=bpy.context.scene
    s.render.engine="CYCLES";s.cycles.samples=12
    bpy.context.view_layer.cycles.use_denoising=False
    s.render.resolution_x=720;s.render.resolution_y=480;s.render.resolution_percentage=100
    world=bpy.data.worlds.new("sky");world.use_nodes=True;s.world=world
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.65,.77,.95,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.8
    ground=material("preview ground",(.47,.46,.41))
    box("preview only pavement",(0,0,-.2),(26,26,.32),ground)
    light=bpy.data.lights.new("large area light","AREA");light.energy=1500;light.shape="DISK";light.size=8
    obj=bpy.data.objects.new("light",light);s.collection.objects.link(obj);obj.location=(-5,-10,14)
    camera=bpy.data.cameras.new("review camera");cam=bpy.data.objects.new("camera",camera)
    s.collection.objects.link(cam);cam.location=(12,-17,9.4)
    direction=Vector((0,0,3.8))-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    camera.type="ORTHO";camera.ortho_scale=14;s.camera=cam
    s.render.image_settings.file_format="PNG";s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)

records=[]
for kind in ("tienda","vivienda","esquina"):
    meshes=set_scene(kind)
    glb=dest/("fachada_"+kind+".glb")
    bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",export_apply=True)
    preview=dest/("fachada_"+kind+".png")
    make_preview(preview)
    assert glb.is_file() and glb.stat().st_size>8000
    assert preview.is_file() and preview.stat().st_size>10000
    records.append(dict(name=kind,file=glb.name,preview=preview.name,meshes=meshes))
    print("ASSET_OK",kind,meshes,glb.stat().st_size,flush=True)
(dest/"manifest.json").write_text(json.dumps({"assets":records,"blender":bpy.app.version_string},indent=2))
print("PERU_RACING_ASSETS_COMPLETE",flush=True)
