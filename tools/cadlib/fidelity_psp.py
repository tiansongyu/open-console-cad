"""PSP-1000 iteration 16: documented pack, HPRM contacts and indicators."""
import FreeCAD as App
import Part
from .core import V
from .clamshell import _move
from .geometry import appearance
from .handheld_refinement import replace


def stage16(m):
    m.set_pose(180)
    # Sony PSP-110: approximately 52 x 12.5 x 36 mm excluding projections.
    # Installed axes are X=36, Y=52, Z=12.5. Corner radius and internals remain
    # fitted geometry; they are not battery manufacturer's mechanical drawings.
    x, y, z = -63.8, 0, 1.8
    outer = m.rr(36, 52, 12.5, (x, y, z), 12)
    cavity = m.rr(34.4, 50.4, 10.9, (x, y, z+.8), 11.2)
    replace(m, 'BatteryPouch', outer.cut(cavity), 'Sony PSP-110 published 52 x 12.5 x 36 mm pack envelope')
    m.parts['BatteryPouch'].Fidelity = 'Schematic internal walls; published approximate PSP-110 pack envelope'
    replace(m, 'BatteryCell', m.rr(34.1, 50.1, 10.6, (x, y, z+.95), 11.05),
            'Schematic cell volume inside the corrected battery envelope')
    tray = m.rr(36.8, 52.8, .30, (x, y, 1.35), 12.4).cut(m.rr(35.1, 51.1, .5, (x, y, 1.25), 11.55))
    replace(m, 'BatteryTray', tray, 'Schematic locating rim follows corrected battery envelope')
    for key in ['BatteryConnector', 'BatteryContact0', 'BatteryContact1', 'BatteryContact2']:
        _move(m, key, (0, 2.6, 0))
    for key in ['BatteryType', 'BatteryCapacity', 'BatteryStudy']:
        _move(m, key, (0, 0, -.2))

    # A taller published battery requires a new arrangement of the existing
    # schematic reader/controls. No claim is made for exact PCB layer heights.
    reader_keys = ['MemoryReaderPCB', 'MemoryReaderCage'] + ['MemoryContact'+str(i) for i in range(10)]
    for key in reader_keys:
        _move(m, key, (4.0, 8.0, 1.6))
    _move(m, 'MemoryFlex', (4, 6, 1.4))
    _move(m, 'DPadPCB', (0, 0, 1.0))
    for i in range(4):
        _move(m, 'ControlContact'+str(i), (0, 0, 1.0))
        _move(m, 'ControlPill'+str(i), (0, 0, 1.0))
        key = 'ControlRubber'+str(i)
        b = m.parts[key].Shape.optimalBoundingBox(False, False)
        replace(m, key, Part.makeCylinder(2.6, 1.0, V(b.Center.x, b.Center.y, b.ZMin+1.0)),
                'Schematic membrane height preserves control travel above raised reader')
    # The external door follows the side-entry reader rather than leaving its
    # opening behind. Edit the old tool so no obsolete cover-shaped hole remains.
    band=m.rr(169.96,73.96,5.1,(0,0,14.5),30.98).cut(m.rr(168.6,72.6,5.4,(0,0,14.4),30.3))
    door=band.common(Part.makeBox(4,26,6,V(-85,-5,14.1)))
    replace(m,'MemoryStickDoor',door,'Side cover aligned with corrected Memory Stick reader installation')
    next(o for o in m.doc.Objects if o.Label.startswith('Memory Stick side cover seat · tool')).Shape=door.copy()
    # Explicit cavity for the standard battery leaves the external shell intact.
    clearance=m.rr(36.2,52.2,12.7,(x,y,z-.1),12.1)
    m.cut('MainFrame',clearance,'PSP-110 package clearance; internal frame remains schematic')
    m.cut('MainFrame',m.parts['BatteryTray'].Shape,'Corrected battery locating-rim seat')
    m.cut('Mainboard',m.rr(31.2,23.2,1.2,(-63.3,8,14.45),1.1),
          'Memory-reader daughterboard edge clearance; PCB outline remains schematic')

    # Firsthand PSP-1000 HPRM documentation shows two rows of three contacts.
    bottom=App.Rotation(V(0,0,1),V(0,-1,0))
    contacts=[]
    for i in range(6):
        shape=m.rr(.55,.38,.10,(-60+(i%3)*2,-36.09,10.65-(i//3)*1.3),.04,bottom)
        key='RemoteContact'+str(i)
        if key in m.parts:replace(m,key,shape,'PSP-1000 HPRM six-contact, two-row arrangement')
        else:m.feature(key,'HPRM remote contact',shape,'Ports',0,'gold')
        contacts.append(shape)
    # The existing black insert was solid across the mating mouth.
    mouth=m.rr(5.5,2.2,2.6,(-58,-36.18,10.0),.22,App.Rotation(V(0,0,1),V(0,1,0)))
    m.cut('HeadsetRemotePort',mouth,'Open original HPRM mating cavity')
    m.cut('MainFrame',contacts,'Six HPRM contact seats')
    m.cut('HeadsetRemotePort',contacts,'HPRM terminal carrier relief')

    m.colors['access_orange']=(.95,.42,.035)
    led=m.parts['MemoryLED'];led.MaterialDescription='access_orange';appearance(led,m.colors['access_orange'])
    led.Fidelity='Orange Memory Stick access light observed in firsthand LED replacement; presentation color approximate'
    # HOLD is a mechanical state indicator, not an additional powered LED.
    flag=m.rr(1.8,.65,.12,(77,-19,22.94),.15)
    m.cut('FrontBezel',flag,'HOLD mechanical indicator window')
    o=m.feature('HoldIndicator','HOLD mechanical indicator (unlocked state)',flag,'Ports',4,'black')
    o.Fidelity='HOLD indicator existence and side from Sony manual; fitted size; unlocked presentation'
    m.profile['stages']=16
    m.checkpoint(16,'published_battery_six_pin_remote_and_hold_indicator',
                 '按索尼规格扩大 PSP-110 电池包并同步示意内部安装层，补齐原版遥控口双排六接点及开口，修正记忆棒橙色指示灯并增加 HOLD 状态窗。电池圆角、孔位和内部层高仍为近似值。')
