"""CTR-001 details verified in Nintendo's original hardware manual.

The full-size SD envelope comes from the SD Association. Indicator and strap
locations are fitted to the official diagrams, not factory measurements.
"""
import FreeCAD as App
import Part

from .core import V
from .geometry import appearance
from .handheld_refinement import replace


def _inlay(m, host, key, tool, label, material, assembly, layer, pose='Base'):
    """Split an existing external skin without enlarging the closed envelope."""
    skin = m.parts[host].Shape.common(tool)
    assert skin.isValid() and skin.Solids and skin.Volume > 1e-5, key
    m.cut(host, tool, label + ' aperture')
    return m.feature(key, label, skin, assembly, layer, material, False, pose)


def _strap_passages(m):
    # The two front corner openings are shown from below on manual page 22.
    # Each joins a rear entry to a side entry around a retained molded bridge.
    for side in (-1, 1):
        x, y = side * 62.3, -33.8
        rear = m.rr(2.2, 2.0, 3.8, (x, y, -.15), .55)
        start = V(side * 60.8, y, 2.65)
        side_entry = Part.makeCylinder(.90, 7.3, start, V(side, 0, 0))
        passage = rear.fuse(side_entry).removeSplitter()
        # A separate reinforced corner keeps the lanyard tunnel away from the
        # electronics cavity. Its exact molding thickness remains an estimate.
        block = m.rr(5.3, 4.6, 3.9, (side * 63.1, y, 1.05), .65)
        lower_outline = m.rr(134, 74, 5.2, (0, 0, 0), 5.6)
        block = block.common(lower_outline)
        anchor = block.cut(passage).removeSplitter()
        assert anchor.isValid() and len(anchor.Solids) == 1
        for host in ('BackCover', 'MainFrame', 'RearSupportPlate'):
            m.cut(host, [block, passage], 'CTR-001 corner strap tunnel and reinforced anchor seat')
        m.feature('StrapAnchor' + str(side), 'Molded corner strap anchor', anchor,
                  'Body', -5, 'accent')


def _standard_sd(m):
    # Side entry runs in X. The old 20.7 x 23.5 x 1.25 study card was undersize
    # and its contact row faced the wrong edge of the side-entry reader.
    x, y, z = -49.0, -12.0, 3.65
    points = [(-16, -12), (16, -12), (16, 9.2), (13.2, 12),
              (-16, 12), (-16, -12)]
    wire = Part.makePolygon([V(x + dx, y + dy, z) for dx, dy in points])
    card = Part.Face(Part.Wire(wire.Edges)).extrude(V(0, 0, 2.1))
    # The characteristic lock-slider notch is a fitted detail; its dimensions
    # are deliberately not asserted as an SD mechanical standard tolerance.
    lock_notch = Part.makeBox(6.2, 1.15, 1.2, V(x - 10.0, y + 11.0, z + .45))
    card = card.cut(lock_notch)
    replace(m, 'SDCard', card, 'SD Association full-size 32 x 24 x 2.1 mm envelope; fitted keyed corner')
    m.parts['SDCard'].Label = 'Full-size SD memory card, 32 x 24 x 2.1 mm'
    m.parts['SDCard'].Fidelity = 'Standard SD envelope; estimated key, contact and installation geometry'

    pcb = m.rr(34.0, 26.4, .60, (x, y, 2.7), .7)
    replace(m, 'SDReaderPCB', pcb, 'Carrier enlarged for the full-size side-entry SD card')
    outer = m.rr(33.7, 25.7, 2.95, (x + .05, y, 3.35), .6)
    cavity = m.rr(34.0, 24.5, 2.35, (x - .55, y, 3.52), .25)
    cage = outer.cut(cavity)
    replace(m, 'SDReaderCage', cage, 'Side-opening shield with clearance around the standard SD envelope')

    # Keep all nine physical identifiers and their registration order. Each
    # spring faces the terminal edge of the inserted card rather than the lid.
    terminals = []
    for i in range(9):
        yy = y - 10.0 + i * 2.5
        contact = m.rr(5.8, 1.55, .08, (x + 11.7, yy, z + 2.04), .06)
        replace(m, 'SDContact' + str(i), contact,
                'Nine SD spring terminals aligned to the side-entry card')
        terminals.append(contact)
    m.cut('SDCard', terminals, 'Full-size SD terminal recesses')
    m.cut('SDReaderCage', terminals, 'SD spring-contact seats')
    m.cut('SDReaderCage', [m.parts[k].Shape for k in
                         ('NANDPackage', 'Passive1', 'Passive1End-1', 'Passive1End1')],
          'Low SD shield relief below adjacent schematic NAND and passive packages')
    m.cut('EMIShield', m.parts['SDReaderPCB'].Shape,
          'Full-size SD reader carrier clearance in the lower shield')
    m.cut('MainFrame', [m.parts['SDReaderPCB'].Shape, m.parts['SDReaderCage'].Shape],
          'Full-size SD reader side-frame mounting rebate')
    # The card and shield enter through the existing removable side door.
    entry = Part.makeBox(3.6, 24.7, 2.9, V(-67.2, y - 12.35, 3.45))
    m.cut('MainFrame', entry, 'Full-size SD side insertion opening behind removable cover')


def stage15(m):
    """Apply after iteration 14, in a fresh or restored Study instance."""
    m.set_pose(180)
    p = m.profile
    hy, hz = p['hinge_y'], p['hinge_z']
    cy = 2 * hy
    back_z = 2 * hz - p['closed_depth']
    camera_y = cy + p['lid_height'] / 2 - 7.3
    m.colors['indicator_off'] = (.33, .36, .34)
    m.colors['wireless_amber'] = (.72, .49, .08)

    # The notification window occupies the fixed right hinge corner, not the
    # rotating upper display. Intersecting the host retains its curved surface.
    _inlay(m, 'RightHingeSleeve', 'NotificationLens',
           m.rr(2.2, 1.9, 1.2, (63.1, hy, hz + 1.9), .25),
           'Right-hinge notification light lens', 'indicator_off', 'Hinge', 0)
    _inlay(m, 'LidBackCover', 'OuterCameraLEDLens',
           Part.makeCylinder(.55, 1.15, V(26.5, camera_y, back_z - .1)),
           'Outer-camera activity indicator lens', 'indicator_off', 'Lid', -6, 'Lid')
    _inlay(m, 'MainFrame', 'WirelessLEDLens',
           Part.makeBox(.8, 1.6, .9, V(66.35, -3.9, 6.55)),
           'Right-side wireless indicator lens', 'wireless_amber', 'Ports', 0)

    # Nintendo identifies the 3D glyph as a green status indicator, whereas the
    # OFF glyph is a printed legend. Preserve the existing 3D part identifier.
    indicator = m.parts['DepthLegend']
    indicator.MaterialDescription = 'led'
    indicator.Label = '3D indicator diffuser glyph'
    appearance(indicator, m.colors['led'])

    _strap_passages(m)
    _standard_sd(m)
    m.doc.recompute()
    for key in ('SDCard', 'SDReaderCage', 'SDReaderPCB', 'NotificationLens',
                'OuterCameraLEDLens', 'WirelessLEDLens', 'StrapAnchor-1', 'StrapAnchor1'):
        shape = m.parts[key].Shape
        assert shape.isValid() and shape.Solids, key
    p['stages'] = 15
    m.checkpoint(15, 'manual_indicators_strap_tunnels_and_standard_sd',
                 '依据原版手册补齐通知灯、外摄像头工作灯、无线指示窗与双侧挂绳通道，区分 3D 指示字形和 OFF 印字；将 SD 卡修正为标准 32×24×2.1 mm，并同步侧向卡座与九个触点。局部灯窗、挂绳孔及卡座位置为图像估计。')
