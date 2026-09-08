"""First-generation PSP-1000: rounded black body, silver rim and UMD layout."""
from .core import V


def stage01(m):
    p=m.profile;w,h=p['width'],p['height']
    m.native('BackCover','PSP-1000 rear enclosure blank',w-1,h-1,30.5,1.2,(0,0,0),layer=-6)
    m.native('MainFrame','Original PSP structural perimeter',w,h,31.0,20.4,(0,0,1.3),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.4,h-3.4,20.8,(0,0,1.1),29.3),'Board, battery and UMD interior cavity')
    m.native('FrontBezel','Glossy PSP front face blank',w-.4,h-.4,30.8,1.2,(0,0,21.8),layer=4)
    trim=m.rr(w-.02,h-.02,1.0,(0,0,11.0),30.99).cut(m.rr(w-.6,h-.6,1.3,(0,0,10.85),30.7))
    m.feature('PerimeterTrim','Silver perimeter trim',trim,'Body',0,'metal')
    m.cut('MainFrame',trim,'Flush silver-trim seating recess')
    m.checkpoint(1,'psp1000_enclosure','按 PSP-1000 的 170 × 74 × 23 mm 主体尺寸建立圆端机身、内部空腔、独立前后外壳及银色周缘饰条。')


STAGES={1:stage01}
