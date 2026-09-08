"""2022 LCD Steam Deck: native shell and hollow curved grip studies."""
from .core import V
import FreeCAD as App
import Part


def _ellipsoid(rx,ry,rz,center):
    transform=App.Matrix();transform.A11=rx;transform.A22=ry;transform.A33=rz
    shape=Part.makeSphere(1).transformGeometry(transform)
    shape.translate(V(*center));return shape


def stage01(m):
    p=m.profile;w,h=p['width'],p['height']
    p['envelope_basis']='Published complete handheld envelope includes controls; 37 mm shell datum is a model construction parameter.'
    m.native('RearPlate','LCD model rear shell bridge',w-1.4,h-1.4,17.3,1.2,(0,0,13.7),layer=-6)
    m.native('MainFrame','Steam Deck structural perimeter',w,h,18.0,20.7,(0,0,15.0),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.4,h-3.4,21.1,(0,0,14.8),16.3),'Main electronics cavity')
    m.native('FrontFace','LCD model control and display face blank',w-.4,h-.4,17.8,1.2,(0,0,35.8),layer=4)
    lower=Part.makeBox(320,140,14.65,V(-160,-70,-1))
    for side in [-1,1]:
        center=(side*119,-7,18)
        outer=_ellipsoid(30,50,18,center).common(lower)
        inner=_ellipsoid(28.5,48.5,16.5,center)
        m.feature('RearGrip'+str(side),'Hollow curved rear grip',outer.cut(inner),'Body',-6,'accent')
        m.cut('RearPlate',inner,'Grip cavity opening in rear shell bridge')
    m.checkpoint(1,'lcd_shell_and_hollow_grips','建立 2022 LCD 版的大尺寸机身、原生前面板与周框、后壳桥板和中空曲面握把；49 mm 总厚度将在控制件完成后核对。')


STAGES={1:stage01}
