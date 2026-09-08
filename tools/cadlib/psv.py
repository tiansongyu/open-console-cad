"""Original PCH-1000 Wi-Fi OLED Vita: native rounded enclosure and later stages."""
from .core import V


def stage01(m):
    p=m.profile;w,h,t=p['width'],p['height'],p['base_depth']
    p['envelope_groups']=['Body']
    p['envelope_basis']='Published PCH-1000 body envelope, excluding maximum projections.'
    m.native('BackCover','Original Vita rear shell blank',w-2.4,h-2.4,34.8,1.15,(0,0,0),layer=-6)
    m.native('MainFrame','PCH-1000 structural perimeter',w,h,36.0,t-2.65,(0,0,1.2),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-3.2,h-3.2,t-2.1,(0,0,1.05),34.4),'OLED, mainboard and battery interior cavity')
    m.native('FrontFace','Glossy Vita front face blank',w-.4,h-.4,35.8,1.30,(0,0,t-1.30),layer=4)
    rim=m.rr(w-.02,h-.02,1.45,(0,0,15.65),35.99).cut(m.rr(w-.8,h-.8,1.7,(0,0,15.52),35.6))
    m.feature('SilverRim','Original OLED-model silver perimeter rim',rim,'Body',0,'metal')
    m.cut('MainFrame',rim,'Silver perimeter rim seating recess')
    m.checkpoint(1,'pch1000_native_enclosure','按 PCH-1000 Wi-Fi OLED 初代的 182 × 83.5 × 18.6 mm 主体尺寸建立圆端壳体、内部空腔、独立前后面板及银色周缘。')


STAGES={1:stage01}
