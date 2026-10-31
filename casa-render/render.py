"""Build the apartment from casa.json (cm) in Blender and render a Cycles view.
Usage: python3 render.py x,y,z,tx,ty,tz fov /abs/out.png [samples] [w] [h]"""
import bpy, bmesh, json, math, sys
from mathutils import Vector
args = sys.argv[1:]
cam = [float(v) for v in args[0].split(',')]; FOV = float(args[1]); OUT = args[2]
SAMPLES = int(args[3]) if len(args) > 3 else 96; W = int(args[4]) if len(args) > 4 else 1280; H = int(args[5]) if len(args) > 5 else 800
import os
rows = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'casa.json')))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; S = 0.01

def node_mat(name, base, rough=0.5, metal=0.0, transm=0.0, emit=None, tex=None, scale=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if transm: b.inputs['Transmission Weight'].default_value = transm; b.inputs['IOR'].default_value = 1.45
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 6
    if tex:
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        cr = nt.nodes.new('ShaderNodeValToRGB')
        if tex in ('oak', 'walnut'):
            wv = nt.nodes.new('ShaderNodeTexWave'); wv.bands_direction = 'X' if tex == 'oak' else 'Z'
            wv.inputs['Scale'].default_value = 9.0; wv.inputs['Distortion'].default_value = 2.5; wv.inputs['Detail'].default_value = 4
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40
            mix = nt.nodes.new('ShaderNodeMath'); mix.operation = 'MULTIPLY'
            nt.links.new(mp.outputs['Vector'], wv.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
            nt.links.new(wv.outputs['Fac'], mix.inputs[0]); nt.links.new(nz.outputs['Fac'], mix.inputs[1]); nt.links.new(mix.outputs[0], cr.inputs['Fac'])
            if tex == 'oak': cr.color_ramp.elements[0].color = (0.50, 0.33, 0.19, 1); cr.color_ramp.elements[1].color = (0.66, 0.47, 0.29, 1)
            else: cr.color_ramp.elements[0].color = (0.15, 0.075, 0.035, 1); cr.color_ramp.elements[1].color = (0.25, 0.135, 0.065, 1)
        elif tex == 'marble':
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 12; nz.inputs['Distortion'].default_value = 3
            nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
            cr.color_ramp.elements[0].position = 0.495; cr.color_ramp.elements[0].color = (0.62, 0.61, 0.6, 1)
            cr.color_ramp.elements[1].position = 0.505; cr.color_ramp.elements[1].color = (0.93, 0.92, 0.9, 1)
        elif tex == 'parquet':
            # oak strips 2x25 cm, straight lay, water-based varnish (pale, natural, satin)
            wv = nt.nodes.new('ShaderNodeTexWave'); wv.bands_direction = 'Y'
            wv.inputs['Scale'].default_value = 40; wv.inputs['Distortion'].default_value = 3; wv.inputs['Detail'].default_value = 4
            nt.links.new(mp.outputs['Vector'], wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'], cr.inputs['Fac'])
            cr2 = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(wv.outputs['Fac'], cr2.inputs['Fac'])
            cr.color_ramp.elements[0].color = (0.55, 0.42, 0.28, 1); cr.color_ramp.elements[1].color = (0.68, 0.54, 0.37, 1)
            cr2.color_ramp.elements[0].color = (0.47, 0.35, 0.22, 1); cr2.color_ramp.elements[1].color = (0.60, 0.47, 0.31, 1)
            br = nt.nodes.new('ShaderNodeTexBrick'); br.offset = 0.5
            br.inputs['Scale'].default_value = 1; br.inputs['Mortar Size'].default_value = 0.0006
            br.inputs['Brick Width'].default_value = 0.25; br.inputs['Row Height'].default_value = 0.02
            br.inputs['Mortar'].default_value = (0.22, 0.16, 0.10, 1)
            nt.links.new(mp.outputs['Vector'], br.inputs['Vector']); nt.links.new(cr.outputs['Color'], br.inputs['Color1']); nt.links.new(cr2.outputs['Color'], br.inputs['Color2'])
            nt.links.new(br.outputs['Color'], b.inputs['Base Color']); return m
        elif tex == 'golden_moon':
            # HPL 'Golden Moon' approximated: warm ivory with few fine golden veins
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.3; nz.inputs['Detail'].default_value = 7; nz.inputs['Distortion'].default_value = 2
            nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
            e = cr.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.83, 0.78, 0.68, 1); e[1].position = 1.0; e[1].color = (0.80, 0.74, 0.63, 1)
            for pos, col in ((0.494, (0.83, 0.78, 0.68, 1)), (0.5, (0.66, 0.48, 0.22, 1)), (0.506, (0.82, 0.76, 0.66, 1))):
                el = e.new(pos); el.color = col
        elif tex == 'taj':
            # Taj Mahal porcelain stoneware: warm cream base with soft, wide taupe-gold veins
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.2; nz.inputs['Detail'].default_value = 6; nz.inputs['Distortion'].default_value = 1.5
            nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
            e = cr.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.80, 0.75, 0.66, 1); e[1].position = 1.0; e[1].color = (0.77, 0.71, 0.61, 1)
            for pos, col in ((0.47, (0.80, 0.75, 0.66, 1)), (0.5, (0.56, 0.47, 0.35, 1)), (0.53, (0.79, 0.73, 0.64, 1))):
                el = e.new(pos); el.color = col
        elif tex == 'nero_oro':
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.5; nz.inputs['Detail'].default_value = 8; nz.inputs['Distortion'].default_value = 2.5
            nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
            e = cr.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.012, 0.011, 0.010, 1); e[1].position = 1.0; e[1].color = (0.02, 0.018, 0.016, 1)
            for pos, col in ((0.4975, (0.012, 0.011, 0.010, 1)), (0.5, (0.62, 0.43, 0.15, 1)), (0.5025, (0.015, 0.013, 0.012, 1))):
                el = e.new(pos); el.color = col
        elif tex == 'grass':
            nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60
            nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
            cr.color_ramp.elements[0].color = (0.06, 0.16, 0.03, 1); cr.color_ramp.elements[1].color = (0.18, 0.35, 0.08, 1)
        nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    return m

def srgb(h):
    c = [((h >> s) & 255) / 255 for s in (16, 8, 0)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
MAT = {
 'oak': node_mat('oak', (0.6, 0.45, 0.3), 0.4, tex='parquet', scale=1.0), 'walnut': node_mat('walnut', (0.2, 0.1, 0.05), 0.42, tex='walnut', scale=2),
 'marble': node_mat('marble', (0.9, 0.9, 0.88), 0.12, tex='marble', scale=1.5), 'beige': node_mat('beige', srgb(0xcbbfae), 0.62),  # cashmere matte
 'taj': node_mat('taj', (0.8, 0.75, 0.66), 0.35, tex='golden_moon', scale=1.0),  # HPL Golden Moon (approximation)
 'tenda': node_mat('tenda', srgb(0xe3d9c8), 0.9),
 'nero': node_mat('nero', srgb(0x1c1c1c), 0.5), 'brass': node_mat('brass', srgb(0xb8893a), 0.3, 1.0),
 'nero_oro': node_mat('nero_oro', (0.015, 0.013, 0.012), 0.1, tex='nero_oro', scale=0.8),
 'anthr': node_mat('anthr', srgb(0x35373a), 0.5), 'black': node_mat('black', srgb(0x111112), 0.18, 0.3), 'steel': node_mat('steel', (0.75, 0.76, 0.78), 0.22, 1.0),
 'white': node_mat('white', srgb(0xf1efea), 0.5), 'ceramic': node_mat('ceramic', (0.95, 0.95, 0.94), 0.08), 'wall': node_mat('wall', srgb(0xf2ede4), 0.85),
 'fabric': node_mat('fabric', srgb(0x9a938a), 0.95), 'boucle': node_mat('boucle', srgb(0xefebe4), 1.0), 'corda': node_mat('corda', srgb(0xd9c7a2), 0.9), 'pillow': node_mat('pillow', srgb(0x8a4f2e), 1.0),
 'rug': node_mat('rug', srgb(0xe3d9c8), 1.0), 'linen': node_mat('linen', srgb(0xeae4d8), 0.95), 'glass': node_mat('glass', (1, 1, 1), 0.0, transm=1.0),
 'frame': node_mat('frame', srgb(0x3a3029), 0.45), 'grass': node_mat('grass', (0.1, 0.25, 0.05), 0.95, tex='grass', scale=1), 'paving': node_mat('paving', srgb(0xcfc7b8), 0.85),
 'hedge': node_mat('hedge', srgb(0x2f5a2a), 0.9), 'led': node_mat('led', (1, 0.85, 0.6), 0.5, emit=(1, 0.75, 0.45)), 'tv': node_mat('tv', (0.01, 0.01, 0.012), 0.08, 0.2),
 'red': node_mat('red', srgb(0xa0623a), 0.8), 'pot': node_mat('pot', srgb(0xb06a4a), 0.7), 'leaf': node_mat('leaf', srgb(0x2f6a2c), 0.6), 'grey': node_mat('grey', srgb(0xd9d7d1), 0.6),
 'pink': node_mat('pink', srgb(0xe2c4ba), 0.95), 'sage': node_mat('sage', srgb(0xcfdcc6), 1.0), 'seam': node_mat('seam', srgb(0x2a2622), 0.8), 'gola': node_mat('gola', srgb(0xa89c8a), 0.5), 'panna': node_mat('panna', srgb(0xefe8da), 0.4), 'oliva': node_mat('oliva', srgb(0x6f6e57), 0.85), 'pelle': node_mat('pelle', srgb(0x8a4f2e), 0.45), 'gyp': node_mat('gyp', srgb(0xbdb6aa), 0.85),
}
coll = sc.collection
def mesh_obj(name, verts, faces, mat):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); ob.data.materials.append(MAT[mat] if isinstance(mat, str) else mat); coll.objects.link(ob); return ob
def ellipse(cx, cy, rx, ry, z0, z1, mat, k=64):
    v = [((cx + rx*math.cos(2*math.pi*i/k))*S, (cy + ry*math.sin(2*math.pi*i/k))*S, z*S) for z in (z0, z1) for i in range(k)]
    f = [tuple(range(k-1, -1, -1)), tuple(range(k, 2*k))] + [(i, (i+1) % k, k + (i+1) % k, k + i) for i in range(k)]
    return mesh_obj('ell', v, f, mat)
def box(x0, y0, z0, x1, y1, z1, mat, name='b'):
    if x1 - x0 < 0.05 or y1 - y0 < 0.05 or z1 - z0 < 0.05: return
    v = [(x * S, y * S, z * S) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    f = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    return mesh_obj(name, v, f, mat)
def cyl_pts(p0, p1, r, mat, k=16, r1=None):
    r1 = r if r1 is None else r1
    a = Vector(p0) * S; b = Vector(p1) * S; d = (b - a).normalized()
    t = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(t).normalized(); w = d.cross(u)
    v = [tuple(c + (rr * S) * (math.cos(2 * math.pi * i / k) * u + math.sin(2 * math.pi * i / k) * w)) for c, rr in ((a, r), (b, r1)) for i in range(k)]
    f = [tuple(range(k - 1, -1, -1)), tuple(range(k, 2 * k))] + [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
    ob = mesh_obj('c', v, f, mat)
    for p in ob.data.polygons: p.use_smooth = True
    return ob
def arc_wall(cx, cy, r, a0, a1, z0, z1, t, mat, n=20):
    v = []; f = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        for rr in (r, r + t):
            for z in (z0, z1): v.append(((cx + rr * math.cos(a)) * S, (cy + rr * math.sin(a)) * S, z * S))
    for i in range(n):
        o = i * 4; p = o + 4
        f += [(o, p, p + 1, o + 1), (o + 2, o + 3, p + 3, p + 2), (o + 1, p + 1, p + 3, o + 3), (o, o + 2, p + 2, p)]
    f += [(0, 1, 3, 2), (n * 4, n * 4 + 2, n * 4 + 3, n * 4 + 1)]
    ob = mesh_obj('arc', v, f, mat)
    for p in ob.data.polygons: p.use_smooth = True

MAT['k_base'] = MAT['beige']; MAT['k_tall'] = MAT['beige']
SCHEME = os.environ.get('CASA_SCHEME'); NIGHT = bool(os.environ.get('CASA_NIGHT'))
if SCHEME == 'blu':
    MAT['k_base'] = node_mat('k_base', srgb(0x1f2d45), 0.6); MAT['k_tall'] = MAT['oak']
elif SCHEME == 'argilla':
    MAT['k_base'] = node_mat('k_base', srgb(0xa5664d), 0.7); MAT['k_tall'] = node_mat('k_tall', srgb(0xe9e1d3), 0.6)
elif SCHEME == 'tortora':
    MAT['k_base'] = node_mat('k_base', srgb(0x8b8176), 0.62); MAT['k_tall'] = MAT['walnut']
elif SCHEME == 'rovere':  # all cashmere beige, recessed lower wall units in oak
    MAT['k_base'] = MAT['beige']; MAT['k_tall'] = MAT['beige']
    MAT['oak_f'] = node_mat('oak_f', srgb(0xb88d5e), 0.55, tex='oak', scale=0.6)
elif SCHEME == 'sabbia':
    MAT['k_base'] = node_mat('k_base', srgb(0xb7a283), 0.65); MAT['k_tall'] = node_mat('k_tall', srgb(0xddd3c3), 0.62)
if SCHEME: MAT['gola'] = MAT['k_base']
MAT['champ'] = node_mat('champ', srgb(0xb89c74), 0.35, 0.7)
RULES = [['LED','led'],['Parete_TV_Cartongesso','oliva'],['Panca_Cuscino','pelle'],['Panca','walnut'],['Matrimoniale_Cuscini','linen'],['Poltrona','pink'],['Tappeto_Gioco','sage'],['Termo','anthr'],['Divano','fabric'],['Chaise','fabric'],['Cuscin','pillow'],['Tappeto','rug'],
 ['Comodino','white'],['Testiera','white'],['Armadio_Matrimoniale','white'],['Matrimoniale_Letto','linen'],['Ingresso_Bianc','white'],['Armadio_L','white'],['Pavimento_Bagno','grey'],['Pavimento','oak'],
 ['Penisola_Top','taj'],['Top','taj'],['Penisola','anthr'],['Piano_Induzione','black'],['Dispensa','beige'],['Colonna','walnut'],['Pensil','walnut'],['Mensola','walnut'],['Mobiletto','walnut'],['Mobile_Lavabo','walnut'],
 ['Base','beige'],['Zoccolo','anthr'],['TV_','tv'],['Controparete','gyp'],['Prato','grass'],['Terrazza','paving'],['Marciapiede','paving'],['Vialetto','paving'],['Area_Pranzo','paving'],['Siepe','hedge'],
 ['Lavabo','ceramic'],['WC','ceramic'],['Bidet','ceramic'],['Doccia','ceramic'],['Lavatrice','ceramic'],['Quadro','red'],['Lettino','white'],['Fasciatoio','white'],['Libreria','white'],['Cassettiera','walnut']]
def mat_for(n):
    for k, m in RULES:
        if k in n: return m
    return 'grey'
OPEN = [[-13,294.5,0,394.5,100,240],[-13,63,0,163,100,240],[244,560,344,573,0,240],[179,-165,192,-65,0,240],[450,560,550,573,0,240],[640,560,740,573,0,240],[845,560,945,573,0,240],[1204,100,1217,200,100,200],
 [432,50,445,130,0,210],[660,143,740,156,0,210],[850,250,930,263,0,210],[934,63,946,143,0,210],[522,40,602,53,0,210],[840,143,920,156,0,210]]
portals = []
def wall(n, x0, y0, x1, y1):
    horiz = (x1 - x0) >= (y1 - y0)
    ops = sorted([(max(o[0], x0), min(o[2], x1), o[4], o[5]) if horiz else (max(o[1], y0), min(o[3], y1), o[4], o[5]) for o in OPEN if o[0] < x1 - .5 and o[2] > x0 + .5 and o[1] < y1 - .5 and o[3] > y0 + .5])
    cur = x0 if horiz else y0; end = x1 if horiz else y1
    seg = (lambda a, b, za, zb: box(a, y0, za, b, y1, zb, 'wall')) if horiz else (lambda a, b, za, zb: box(x0, a, za, x1, b, zb, 'wall'))
    ext = n.startswith(('Parete_Ovest', 'Parete_Nord', 'Parete_Est_Esterna', 'Parete_Gradino'))
    for a, b, s, h in ops:
        seg(cur, a, 0, 270); seg(a, b, 0, s); seg(a, b, h, 270)
        if ext:
            if horiz: box(a, (y0+y1)/2-.4, s, b, (y0+y1)/2+.4, h, 'glass'); [box(*q, 'frame') for q in ((a, y0+3, s, a+5, y1-3, h), (b-5, y0+3, s, b, y1-3, h), (a, y0+3, h-5, b, y1-3, h), (a, y0+3, s, b, y1-3, s+4))]
            else: box((x0+x1)/2-.4, a, s, (x0+x1)/2+.4, b, h, 'glass'); [box(*q, 'frame') for q in ((x0+3, a, s, x1-3, a+5, h), (x0+3, b-5, s, x1-3, b, h), (x0+3, a, h-5, x1-3, b, h), (x0+3, a, s, x1-3, b, s+4))]
            hz = s + 105 if s < 50 else (s + h) / 2  # silver lever handle on both faces
            for f0, f1 in (((y1 if horiz else x1) - 3, (y1 if horiz else x1) - 1.5), ((y0 if horiz else x0) + 1.5, (y0 if horiz else x0) + 3)):
                lo, hi = (f0 - 2, f0) if f0 < (y0 + y1 if horiz else x0 + x1) / 2 else (f1, f1 + 2)
                if horiz: box(a + 1, f0, hz - 4, a + 4, f1, hz + 4, 'steel'); box(a + 2, lo, hz - 1, a + 14, hi, hz + 1, 'steel')
                else: box(f0, a + 1, hz - 4, f1, a + 4, hz + 4, 'steel'); box(lo, a + 2, hz - 1, hi, a + 14, hz + 1, 'steel')
            portals.append((horiz, a, b, s, h, x0, y0, x1, y1))
        cur = b
    seg(cur, end, 0, 270)

TC = (274.5, 355)
for g, n, x0, y0, z0, x1, y1, z1 in rows:
    if n.startswith('Parete') and 'TV' not in n: wall(n, x0, y0, x1, y1); continue
    if n.startswith('Albero'):
        cx, cy = (x0+x1)/2, (y0+y1)/2; cyl_pts((cx, cy, 0), (cx, cy, 200), 10, 'frame')
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.5, location=(cx*S, cy*S, 3.0)); bpy.context.object.data.materials.append(MAT['hedge']); continue
    if 'Ovale' in n:
        # light look: 2 cm oak top on a recessed apron, four slender splayed legs
        cx, cy = (x0+x1)/2, (y0+y1)/2; rx, ry = (x1-x0)/2, (y1-y0)/2
        ellipse(cx, cy, rx, ry, 74, 76, 'oak'); ellipse(cx, cy, rx-6, ry-8, 70, 74, 'oak')
        for sx_, sy_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            cyl_pts((cx+sx_*rx*.55, cy+sy_*ry*.58, 70), (cx+sx_*rx*.68, cy+sy_*ry*.70, 0), 1.8, 'oak', 12, 1.1)
        continue
    if 'Termo' in n:
        alx = (x1-x0) > (y1-y0); fx = (y0+y1)/2 if alx else (x0+x1)/2; a0 = (x0 if alx else y0) + 2; a1 = (x1 if alx else y1) - 2
        P = (lambda t, z: (t, fx, z)) if alx else (lambda t, z: (fx, t, z))
        tm = 'panna'  # all radiators cream
        for c in (a0, a1): cyl_pts(P(c, 18), P(c, 202), 2, tm, 12)
        z = 26
        while z < 199: cyl_pts(P(a0, z), P(a1, z), 1.25, tm, 8); z += 7
        continue
    if n.startswith('Sedia'):
        sx, sy = (x0+x1)/2, (y0+y1)/2; dx, dy = sx-TC[0], sy-TC[1]; ang = math.atan2(dy, dx)
        # light chair: thin oak ring with paper-cord seat, slender legs, open curved back rail
        cyl_pts((sx, sy, 42), (sx, sy, 44), 20, 'oak', 40); cyl_pts((sx, sy, 44), (sx, sy, 45), 18.8, 'corda', 40)
        P = lambda a, r, z: (sx + math.cos(ang + math.radians(a))*r, sy + math.sin(ang + math.radians(a))*r, z)
        for a in (135, -135): cyl_pts(P(a, 17, 0), P(a, 15, 42), 1.0, 'oak', 10, 1.3)
        for a in (40, -40): cyl_pts(P(a, 17, 0), P(a, 19, 76), 1.0, 'oak', 10, 1.3)
        arc_wall(sx, sy, 19.5, ang - math.radians(55), ang + math.radians(55), 70, 77, 1.8, 'oak')
        continue
    if 'Cappa' in n:
        box(x0, y0, z0, x1, y1, z1, 'black'); box(x0+2, y0+2, z0-.5, x1-2, y1-2, z0, 'led'); top = ((x0+x1)/2, (y0+y1)/2, 267)
        for px, py in ((x0+2, y0+4), (x1-2, y0+4), (x0+2, y1-4), (x1-2, y1-4)): cyl_pts((px, py, z1), top, .25, 'brass', 6)
        cyl_pts((top[0], top[1], 266.5), (top[0], top[1], 270), 6, 'brass', 24); continue
    if n.startswith('Boiserie'):
        box(362, y0, 0, 364, y1, 270, 'nero'); y = y0 + 2
        while y + 4 <= y1: box(359, y, 0, 362, y + 4, 270, 'walnut'); y += 7
        continue
    if n.startswith('Complemento'):
        # walnut slats wrap the corner onto the 20 cm return
        box(x0, 558, 0, x1, 560, 270, 'nero'); x = x0 + 1
        while x + 4 <= x1: box(x, 555, 0, x + 4, 558, 270, 'walnut'); x += 7
        continue
    if 'Libreria_Ingresso' in n:
        box(x0, y0, 0, x1, y0+2, 250, 'white'); box(x0, y1-2, 0, x1, y1, 250, 'white'); box(x0, y0, 0, x1, y1, 45, 'white')
        for z in (85, 125, 165, 205, 248): box(x0+2, y0, z, x1, y1, z+2, 'white')
        continue
    if n.startswith('Lavello'): box(x0, y0, z0 - 1, x1, y1, z1 + .3, 'nero'); continue
    if n == 'Penisola_Base': x0 = 60
    m = mat_for(n)
    if 'Induzione' in n: m = 'black'
    elif g == 'Cuc' and m in ('walnut', 'anthr', 'beige'): m = 'k_tall' if 'Colonna' in n else 'k_base'
    box(x0, y0, z0, x1, y1, max(z1, z0 + .5), m, n)
# blackout roller blinds (cream) dropping from a box above each opening; d = +1/-1 direction into the room
def blind(wall, c, d, a, b, top, low):
    if wall == 'x':
        box(min(c, c+8*d), a-1, top, max(c, c+8*d), b+1, top+10, 'beige'); box(min(c+4*d, c+4.6*d), a, low, max(c+4*d, c+4.6*d), b, top, 'tenda'); box(min(c+3.5*d, c+5*d), a, low-3, max(c+3.5*d, c+5*d), b, low, 'nero')
    else:
        box(a-1, min(c, c+8*d), top, b+1, max(c, c+8*d), top+10, 'beige'); box(a, min(c+4*d, c+4.6*d), low, b, max(c+4*d, c+4.6*d), top, 'tenda'); box(a, min(c+3.5*d, c+5*d), low-3, b, max(c+3.5*d, c+5*d), low, 'nero')
for args in [('x', 0, 1, 294.5, 394.5, 242, 130),     # kitchen window
             ('x', 0, 1, 63, 163, 242, 130),        # living window
             ('x', 192, 1, -165, -65, 242, 34),    # entrance patio door
             ('y', 560, -1, 244, 344, 242, 34)]:   # kitchen patio door
    blind(*args[:-1], 236 if NIGHT and SCHEME else args[-1])  # evening shots: blinds rolled up to show the dark sky
# designer variant (CASA_VARIANT=mia): brass pendant over the table, brass handle grooves, cognac boucle pouf
if os.environ.get('CASA_VARIANT') == 'mia':
    tx, ty = TC
    cyl_pts((tx, ty, 168), (tx, ty, 270), .3, 'nero', 6)
    cyl_pts((tx, ty, 150), (tx, ty, 168), 24, 'brass', 48, 6); cyl_pts((tx, ty, 149.5), (tx, ty, 150.5), 21, 'led', 48)
    box(60, 297, 84, 60.6, 500, 86, 'brass'); box(60, 355, 84, 157, 355.6, 86, 'brass'); box(157, 297, 84, 157.6, 355, 86, 'brass')
    cyl_pts((275, 240, 0), (275, 240, 38), 23, 'pillow', 48)
# extra details
if SCHEME == 'rovere':
    # two-tier wall units: beige upper row flush, lower row set back 5 cm in fluted oak with LED below
    box(0, 480, 205, 35, 525, 270, 'k_tall'); box(0, 525, 205, 122, 560, 270, 'k_tall')
    box(0, 480, 150, 30, 530, 205, 'oak_f'); box(0, 530, 150, 122, 560, 205, 'oak_f')
    for y in range(482, 530, 3): box(30, y, 150.5, 30.4, y + .25, 204.5, 'seam')
    for x in range(32, 122, 3): box(x, 529.6, 150.5, x + .25, 530, 204.5, 'seam')
    box(2, 482, 149.4, 28, 528, 150, 'led'); box(2, 532, 149.4, 120, 558, 150, 'led')
    box(0, 558.8, 90, 122, 560, 150, 'taj')
else:
    box(0, 480, 150, 35, 525, 270, 'k_tall'); box(2, 482, 149.4, 33, 558, 150, 'led')  # corner wall unit on the window wall, LED below
    box(0, 525, 150, 62, 560, 270, 'k_tall'); box(62, 525, 150, 122, 560, 270, 'k_tall')  # wall unit left of the oven column
box(0, 394.5, 90, 1.2, 560, 150, 'taj')  # Taj Mahal stoneware backsplash, same slab as the top
cyl_pts((15, 425, 90), (15, 425, 120), .9, 'white'); cyl_pts((15, 425, 120), (28, 425, 120), .9, 'white')
# downdraft extractor integrated in the induction hob (replaces the suspended hood)
box(121, 302, 90, 129, 347, 90.4, 'steel'); [box(122, y, 90.4, 128, y + 1, 90.5, 'nero') for y in range(304, 346, 3)]
box(126, 499, 88, 178, 500, 147, 'black'); box(126, 499, 150, 178, 500, 190, 'black')
# TV wall: deep olive microcement, ceiling wash light and soft glow under the floating unit
box(351, 145, 266.5, 352, 290, 267.5, 'led'); box(333, 152, 21.4, 349, 266, 22, 'led')
# dining: linear brass pendant over the table
for y in (310, 400): cyl_pts((TC[0], y, 152), (TC[0], y, 270), .3, 'nero', 6)
cyl_pts((TC[0], 305, 150), (TC[0], 405, 150), 2.2, 'brass', 24); box(TC[0] - 1.2, 307, 147.6, TC[0] + 1.2, 403, 148, 'led')
if SCHEME:
    box(157, 294, 0, 160, 354, 88, 'taj')  # waterfall end in the same top material, as in the kitchen designer's model
    if SCHEME in ('sabbia', 'rovere'):  # ceiling-mounted rectangular LED frame over the peninsula, champagne finish
        for a in ((12, 284, 150, 288), (12, 360, 150, 364), (12, 288, 16, 360), (146, 288, 150, 360)):
            box(a[0], a[1], 262, a[2], a[3], 270, 'champ'); box(a[0] + .8, a[1] + .8, 261.6, a[2] - .8, a[3] - .8, 262, 'led')
    else:
        for x in (75, 140): cyl_pts((x, 327, 168), (x, 327, 270), .3, 'nero', 6)
        cyl_pts((68, 327, 166), (148, 327, 166), 2.2, 'brass', 24); box(70, 326, 163.6, 146, 328, 164, 'led')
# recessed LED ceiling spots (kitchen + living)
for x, y in () if os.environ.get('CASA_NOCEIL') else ((60, 60), (60, 200), (180, 60), (180, 200), (290, 60), (290, 200), (30, 330), (30, 450), (110, 430), (260, 310), (260, 400)):
    cyl_pts((x, y, 269.2), (x, y, 270), 5, 'white', 24); cyl_pts((x, y, 269), (x, y, 269.3), 3.5, 'led', 24)
# kitchen fronts: door/drawer seams and handle-less gola grips (recessed channel, darker cashmere)
def front(ax, p, d, a, b, z0, z1, hs=(), vs=(), gola=True, vgola=None):
    q0, q1 = (p, p + .3 * d) if d > 0 else (p + .3 * d, p)
    B = (lambda u0, u1, w0, w1, m: box(q0, u0, w0, q1, u1, w1, m)) if ax == 'x' else (lambda u0, u1, w0, w1, m: box(u0, q0, w0, u1, q1, w1, m))
    for u in (a, b) + tuple(vs): B(u - .2, u + .2, z0, z1, 'seam')
    for z in (z0, z1) + tuple(hs): B(a, b, z - .2, z + .2, 'seam')
    if gola:
        for z in (z1,) + tuple(hs): B(a + .5, b - .5, z - 4, z - .8, 'gola')
    if vgola: B(vgola[0], vgola[1], z0 + 1, z1 - 1, 'gola')
# window run (fronts face +x at x=58)
front('x', 58, 1, 355, 380, 10, 88)                          # bottle pull-out 25
front('x', 58, 1, 380, 470, 10, 88, hs=(50,))               # sink base: U-shaped top drawer + deep waste-sorting drawer
front('x', 58, 1, 470, 530, 10, 88)                          # dishwasher panel
front('x', 58, 1, 530, 560, 10, 88)                          # corner door
# garden run (fronts face -y at y=500)
front('y', 500, -1, 62, 122, 10, 88)                         # single door left of the oven
front('y', 500, -1, 122, 182, 10, 88)                        # drawer under the ovens
front('y', 500, -1, 122, 182, 190, 270, gola=False)          # door above the ovens (push-to-open)
front('y', 500, -1, 182, 242, 10, 190, gola=False, vgola=(182.6, 185.5))   # fridge door, vertical gola
front('y', 500, -1, 182, 242, 190, 270, gola=False)          # door above the fridge
for x in (122, 182): box(x - .3, 499.5, 0, x + .3, 500, 10, 'seam')
# peninsula (fronts face +y at y=355): door + three pan drawers under the hob
front('y', 355, 1, 60, 97, 10, 88)
front('y', 355, 1, 97, 157, 10, 88, hs=(36, 62))
# wall units: push-to-open doors, shadow-gap outline only
if SCHEME == 'rovere':
    front('y', 525, -1, 0, 62, 205, 270, gola=False); front('y', 525, -1, 62, 122, 205, 270, gola=False)
    front('x', 35, 1, 480, 525, 205, 270, gola=False)
else:
    front('y', 525, -1, 0, 62, 150, 270, gola=False); front('y', 525, -1, 62, 122, 150, 270, gola=False)
    front('x', 35, 1, 480, 525, 150, 270, gola=False)
for y in (235, 290, 345, 400): box(754.5, y - .3, 0, 755, y + .3, 250, 'seam')
for y in (-140, -90): box(386.5, y - .3, 0, 387, y + .3, 250, 'seam')
for x in (1014, 1078, 1144): box(x - .3, 499.5, 0, x + .3, 500, 250, 'seam')
box(540, 282, 45, 587, 434, 48, 'fabric')
def plant(x, y, s=1.0):
    cyl_pts((x, y, 0), (x, y, 34*s), 12*s, 'pot', 24, 15*s)
    for i in range(14):
        a = i * 2.39; r = (6 + (i % 4) * 4) * s
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=(15 + (i % 3) * 4) * s * S, location=((x + math.cos(a)*r)*S, (y + math.sin(a)*r)*S, (55 + i*7)*s*S))
        o = bpy.context.object; o.scale = (1, 0.7, 1.25); o.rotation_euler = (0.3*math.sin(i), 0.3*math.cos(i), a); o.data.materials.append(MAT['leaf'])
        for p in o.data.polygons: p.use_smooth = True
pass  # piante rimosse
if not os.environ.get('CASA_NOCEIL'): box(-13, -215, 270, 1217, 573, 275, 'wall')
# world sky + sun
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING' if hasattr(sky, 'sky_type') and 'MULTIPLE_SCATTERING' in [i.identifier for i in sky.bl_rna.properties['sky_type'].enum_items] else sky.sky_type
sky.sun_elevation = math.radians(32); sky.sun_rotation = math.radians(215)
bg = w.node_tree.nodes['Background']; bg.inputs['Strength'].default_value = 0.004 if NIGHT else 0.35; w.node_tree.links.new(sky.outputs['Color'], bg.inputs['Color'])
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 0 if NIGHT else 3.5; sun.angle = math.radians(1.5); sun.color = (1, 0.95, 0.88)
so = bpy.data.objects.new('sun', sun); coll.objects.link(so); so.rotation_euler = (math.radians(58), 0, math.radians(215 - 90 + 180))
for horiz, a, b, s, h, x0, y0, x1, y1 in portals:
    L = bpy.data.lights.new('portal', 'AREA'); L.shape = 'RECTANGLE'; L.cycles.is_portal = True
    o = bpy.data.objects.new('portal', L); coll.objects.link(o)
    if horiz: L.size = (b-a)*S; L.size_y = (h-s)*S; o.location = ((a+b)/2*S, (y1+2)*S, (s+h)/2*S); o.rotation_euler = (math.radians(-90), 0, 0)
    else:
        L.size = (b-a)*S; L.size_y = (h-s)*S
        if x0 < 100: o.location = ((x0-2)*S, (a+b)/2*S, (s+h)/2*S); o.rotation_euler = (math.radians(90), 0, math.radians(-90))
        else: o.location = ((x1+2)*S, (a+b)/2*S, (s+h)/2*S); o.rotation_euler = (math.radians(90), 0, math.radians(90))
for x, y, z, e in ((125, 324, 150, 6), (262, 365, 240, 10), (150, 150, 262, 12), (300, 220, 262, 8), (596, 350, 262, 14), (1015, 410, 262, 10), (312, -100, 262, 8), (1110, 150, 262, 8)):
    L = bpy.data.lights.new('spot', 'POINT'); L.energy = e * (1.2 if NIGHT else 4); L.color = (1, 0.82, 0.62); L.shadow_soft_size = 0.08
    o = bpy.data.objects.new('spot', L); coll.objects.link(o); o.location = (x*S, y*S, z*S)
if NIGHT:  # evening: recessed spots, under-cabinet strip and pendants actually light the room
    for x, y in ((60, 60), (60, 200), (180, 60), (180, 200), (290, 60), (290, 200), (30, 330), (30, 450), (110, 430), (260, 310), (260, 400)):
        L = bpy.data.lights.new('nspot', 'SPOT'); L.energy = 35; L.spot_size = math.radians(80); L.spot_blend = .6; L.color = (1, 0.83, 0.64); L.shadow_soft_size = .02
        o = bpy.data.objects.new('nspot', L); coll.objects.link(o); o.location = (x*S, y*S, 2.68)
    for (x0, y0, x1, y1, z, e) in ((2, 482, 33, 558, 149, 25), (14, 286, 148, 362, 261, 70) if SCHEME in ('sabbia', 'rovere') else (70, 324, 146, 330, 163, 40 if SCHEME else 0), (TC[0]-2, 307, TC[0]+2, 403, 147, 35)):
        if not e: continue
        L = bpy.data.lights.new('nled', 'AREA'); L.shape = 'RECTANGLE'; L.size = (x1-x0)*S; L.size_y = (y1-y0)*S; L.energy = e; L.color = (1, 0.8, 0.58)
        o = bpy.data.objects.new('nled', L); coll.objects.link(o); o.location = ((x0+x1)/2*S, (y0+y1)/2*S, z*S)
# camera
c = bpy.data.cameras.new('cam'); c.sensor_fit = 'VERTICAL'; c.angle_y = math.radians(FOV)
co = bpy.data.objects.new('cam', c); coll.objects.link(co); sc.camera = co
if os.environ.get('CASA_ORTHO'): c.type = 'ORTHO'; c.ortho_scale = float(os.environ['CASA_ORTHO'])
co.location = Vector(cam[:3]) * S; co.rotation_euler = (Vector(cam[3:]) * S - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transmission_bounces = 6
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.resolution_percentage = 100
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: sc.view_settings.view_transform = 'Filmic'
sc.view_settings.exposure = -1.4 if os.environ.get('CASA_NOCEIL') else (0.15 if NIGHT else 0.6)
sc.render.filepath = OUT; sc.render.threads_mode = 'AUTO'
bpy.ops.render.render(write_still=True)
print('DONE', OUT)
