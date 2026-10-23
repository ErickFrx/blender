"""Fetch geographically anchored Miraflores OSM snapshot for PERÚ RACING.
Data: © OpenStreetMap contributors, ODbL 1.0. No made-up roads.
"""
import json, time, urllib.request, urllib.parse, pathlib, datetime
BBOX=(-12.1264,-77.0352,-12.1170,-77.0253)
Q=f"""[out:json][timeout:80];(
way[highway][area!=yes]({','.join(map(str,BBOX))});
way[building]({','.join(map(str,BBOX))});
way[leisure~"^(park|garden|playground)$"]({','.join(map(str,BBOX))});
way[landuse~"^(grass|meadow|recreation_ground|village_green)$"]({','.join(map(str,BBOX))});
way[highway~"^(footway|pedestrian)$"]({','.join(map(str,BBOX))});
node[natural=tree]({','.join(map(str,BBOX))});
);out geom;"""
urls=["https://overpass.kumi.systems/api/interpreter","https://overpass.private.coffee/api/interpreter","https://overpass-api.de/api/interpreter"]
data=None
for url in urls:
  try:
    post=urllib.parse.urlencode({"data":Q}).encode()
    req=urllib.request.Request(url,data=post,headers={"User-Agent":"PERU-RACING-independent-OSM-cache/0.1 (community game demo)","Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req,timeout=110) as response:
      candidate=json.load(response)
    elements=candidate.get("elements",[])
    roads=[e for e in elements if e.get("tags",{}).get("highway") in ("primary","secondary","tertiary","residential","unclassified","service","living_street") and len(e.get("geometry",[]))>1]
    buildings=[e for e in elements if e.get("tags",{}).get("building") and len(e.get("geometry",[]))>=4]
    parks=[e for e in elements if e.get("tags",{}).get("leisure")=="park" and len(e.get("geometry",[]))>=4]
    if len(roads)<25 or len(buildings)<20 or not parks: raise RuntimeError(f"insufficient roads/buildings/parks: {len(roads)}/{len(buildings)}/{len(parks)}")
    data=candidate;print(f"OSM_FETCH_OK {url}: roads={len(roads)}, buildings={len(buildings)}, parks={len(parks)}",flush=True);break
  except Exception as exc:
    print("OSM_SERVER_FAILED",url,str(exc)[:300],flush=True);time.sleep(2)
if data is None:raise SystemExit("Could not fetch real Miraflores OSM data from any Overpass server")
elems=data["elements"];nodes=[x for x in elems if x.get("type")=="node" and x.get("tags",{}).get("natural")=="tree"]
park=[e for e in elems if e.get("id")==28798160 and e.get("tags",{}).get("leisure")=="park"]
if not park:print("WARN: Kennedy way 28798160 not found; inspect parks manually",flush=True)
data["nodes"]=nodes
data["metadata"]={
"source":"OpenStreetMap","license":"ODbL-1.0","attribution":"© OpenStreetMap contributors",
"retrievedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"endpoint":url,"query":Q,"bbox":list(BBOX),
"area":"Parque Kennedy y avenida José Larco, Miraflores, Lima, Perú",
"parkOsmWayId":28798160 if park else None,
"roadWayCount":len(roads),"buildingWayCount":len(buildings),"parkWayCount":len(parks),
"treeNodeCount":len(nodes),
"notes":"Road network and building footprints from OSM; geometry coverage and feature completeness are not guaranteed."}
out=pathlib.Path("output");out.mkdir(exist_ok=True)
p=out/"miraflores_kennedy_osm.json";p.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
print("OSM_SNAPSHOT_READY",str(p),p.stat().st_size,flush=True)
