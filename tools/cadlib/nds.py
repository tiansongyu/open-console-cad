"""Original NTR-001 Nintendo DS: thick silver body, dual 4:3 screens and GBA slot."""
from .core import V


def stage01(m):
    p=m.profile;w,h=p['width'],p['height'];fz=p['base_depth']-.8
    m.native('BackCover','NTR-001 rear cover',w-1.8,h-1.8,9.2,1.25,(0,0,0),layer=-6)
    m.native('MainFrame','Original DS deep lower frame',w,h,10.0,16.2,(0,0,1.3),layer=0,expr={'Width':'Parameters.Width','Height':'Parameters.Height'})
    m.cut('MainFrame',m.rr(w-4.0,h-4.0,17.0,(0,0,1.15),8.2),'Lower electronics cavity')
    m.native('FrontDeck','Original DS control deck',w-.7,h-.7,9.65,1.05,(0,0,fz-1.05),layer=4)
    seam=m.rr(w-.5,h-.5,.03,(0,0,17.51),9.65).cut(m.rr(w-4.2,h-4.2,.15,(0,0,17.45),7.8))
    m.feature('LowerCaseSeam','Lower case parting line',seam,layer=0,material='black')
    m.checkpoint(1,'ntr001_deep_enclosure','按 NTR-001 初代厚机身建立银色下壳、主框架、控制面板、原生尺寸约束与内部空腔。')

STAGES={1:stage01}
