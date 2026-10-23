"""Validate Blender GLB artifacts and preview images with Python standard library."""
import json
import struct
from pathlib import Path

out=Path("output")
manifest=json.loads((out/"manifest.json").read_text())
assets=manifest["assets"]
assert len(assets)==3, "Expected three facades"
for a in assets:
    glb=out/a["file"];png=out/a["preview"]
    raw=glb.read_bytes()
    assert len(raw)>8000 and raw[:4]==b"glTF"
    magic,version,length=struct.unpack_from("<4sII",raw)
    assert (magic,version,length)==(b"glTF",2,len(raw))
    chunk_length,kind=struct.unpack_from("<I4s",raw,12)
    assert kind==b"JSON"
    data=json.loads(raw[20:20+chunk_length].decode("utf-8").rstrip(" \\x00"))
    assert data["meshes"] and len(data["meshes"])>=30
    assert len(data["materials"])>=4
    img=png.read_bytes()
    assert len(img)>10000 and img[:8]==b"\\x89PNG\\r\\n\\x1a\\n"
    w,h=struct.unpack_from(">II",img,16)
    assert w>=640 and h>=400
    print(f"VALIDATED {glb.name}: {len(data['meshes'])} meshes, {len(data['materials'])} materials; {png.name} {w}x{h}")
print("PERU_RACING_VALIDATION_OK")
