"""Original OLED Vita media interfaces, from Sony and hardware pinout evidence."""
import FreeCAD as App
import Part

from .core import V
from .handheld_refinement import replace


def _retire(m, key):
    obj = m.parts.pop(key)
    obj.PhysicalPart = False
    obj.Visibility = False
    if 'RevisionReason' not in obj.PropertiesList:
        obj.addProperty('App::PropertyString', 'RevisionReason', 'Revision')
    obj.RevisionReason = 'Retired surplus contact: original Vita game interface has ten mating contacts'
    m.profile.setdefault('retired_part_ids', []).append(key)
    m.profile.setdefault('retired_part_numbers', []).append(obj.PartNumber)


def stage16(m):
    """Correct contact counts, memory-card axes and the missing card access lens."""
    m.set_pose(180)
    # Assign the old stable identities before removing any component. This also
    # reproduces their original numbers during a fresh full-source rebuild.
    for i, obj in enumerate(m.parts.values(), 1):
        if 'PartNumber' not in obj.PropertiesList:
            obj.addProperty('App::PropertyString', 'PartNumber', 'Study')
        if not obj.PartNumber:
            obj.PartNumber = 'PSV-' + f'{i:04d}'
    m.profile['preserve_part_numbers'] = True
    m.profile['part_number_baseline'] = {key: obj.PartNumber for key, obj in m.parts.items()}
    for prefix in ('GameCardContact', 'VitaGamePad'):
        for i in range(10, 20):
            _retire(m, prefix + str(i))

    for i in range(10):
        # Ten mating lands, with approximately 1.4 mm spacing documented by
        # the hardware researchers. Cross sections and spring forms estimated.
        contact = m.rr(.95, 6.0, .07, (-31 + (i - 4.5) * 1.4, 23.0, 9.86), .035)
        replace(m, 'GameCardContact' + str(i), contact,
                'Ten-pin original Vita game-card interface; fitted terminal geometry')

    x = 126.0
    game = m.rr(22.5, 30.5, 1.9, (x, 15, 0), 1.0)
    game = game.cut(Part.makeBox(2.8, 3.5, 2.4, V(x + 9.5, 27.5, -.2)))
    pads = []
    for i in range(10):
        pad = m.rr(1.05, 4.5, .025, (x + (i - 4.5) * 1.4, 25.2, 1.875), .04)
        replace(m, 'VitaGamePad' + str(i), pad,
                'Ten gold game-card lands corroborated by firsthand cartridge teardown')
        pads.append(pad)
    game = game.cut(Part.makeCompound(pads + [m.parts['VitaGameMark'].Shape]))
    replace(m, 'VitaGameCard', game,
            'Remove the twenty-land study recesses and rebuild the ten-contact terminal edge')

    # Sony's September 2011 accessory announcement gives H12.5 x W15 x T1.6.
    # The previous model transposed the two in-plane axes.
    memory = m.rr(15.0, 12.5, 1.6, (x, -30, 0), .7)
    pads = []
    for i in range(9):
        pad = m.rr(.75, 3.0, .025, (x + (i - 4) * 1.2, -25.75, 1.575), .04)
        if i < 8:
            replace(m, 'VitaMemoryPad' + str(i), pad,
                    'Nine-terminal original proprietary Vita memory-card interface')
        else:
            m.feature('VitaMemoryPad8', 'Ninth Vita memory-card gold terminal', pad,
                      'Accessories', 0, 'gold')
        pads.append(pad)
    memory = memory.cut(Part.makeCompound(pads + [m.parts['VitaMemoryMark'].Shape]))
    replace(m, 'VitaMemoryCard', memory,
            'Sony published width 15, height 12.5 and thickness 1.6 mm with nine terminal lands')
    m.parts['VitaMemoryCard'].Fidelity = 'Sony published card envelope; estimated corner and contact geometry'

    for i in range(9):
        contact = m.rr(.60, 4.7, .07, (54 + (i - 4) * 1.2, -31.5, 4.9), .025)
        if i < 8:
            replace(m, 'MemoryCardContact' + str(i), contact,
                    'Nine mating terminals for the original proprietary memory card')
        else:
            m.feature('MemoryCardContact8', 'Ninth memory-reader spring terminal', contact,
                      'CardReaders', -3, 'gold', True)
    outer = m.rr(16.7, 14.5, 2.55, (54, -32, 4.35), .5)
    cavity = m.rr(15.3, 14.8, 1.9, (54, -32.2, 4.70), .25)
    replace(m, 'MemoryCardCage', outer.cut(cavity),
            'Schematic reader widened for the Sony 15 mm memory-card terminal edge')
    pcb = m.rr(18.4, 16, .45, (54, -32, 7.0), .6)
    pcb = pcb.common(m.rr(177.8, 79.3, .45, (0, 0, 7.0), 33.9))
    replace(m, 'MemoryReaderPCB', pcb,
            'Schematic carrier follows the corrected proprietary memory-reader width')
    entry = Part.makeBox(15.7, 4.6, 2.1, V(54 - 7.85, -42.0, 4.60))
    for host in ('MainFrame', 'SilverRim'):
        m.cut(host, [entry, m.parts['MemoryCardCage'].Shape, pcb],
              'Memory-card insertion and schematic widened-reader installation clearance')

    # Sony's original quick-start diagram locates the access indicator beside
    # the game-card mouth, to its left as seen from the front. The lens is fixed
    # to the rail rather than attached to the moving cover. Local size estimated.
    m.colors['indicator_off'] = (.31, .34, .33)
    tool = Part.makeCylinder(.48, 1.0, V(-50.3, 41.0, 11.4), V(0, 1, 0))
    lens = m.parts['SilverRim'].Shape.common(tool)
    assert lens.isValid() and lens.Solids and lens.Volume > 1e-5
    for host in ('MainFrame', 'SilverRim'):
        m.cut(host, tool, 'Original Vita card-access indicator aperture')
    m.feature('GameCardAccessLens', 'Original game-card access indicator lens',
              lens, 'Ports', 0, 'indicator_off')
    # Boolean operations register replacement objects; restore the same number
    # on those replacements as on the original component before final export.
    for key, obj in m.parts.items():
        if key in m.profile['part_number_baseline']:
            if 'PartNumber' not in obj.PropertiesList:
                obj.addProperty('App::PropertyString', 'PartNumber', 'Study')
            obj.PartNumber = m.profile['part_number_baseline'][key]
    m.doc.recompute()
    m.profile['stages'] = 16
    m.checkpoint(16, 'documented_media_contacts_dimensions_and_access_light',
                 '依据实物拆解与接口针脚记录，将游戏卡和卡座改为十触点，专用存储卡和卡座改为九触点；按索尼规格修正存储卡宽高方向，补齐卡槽访问指示窗。保留现有零件编号，停用二十个多余触点，卡座与局部灯窗仍为近似设计。')
