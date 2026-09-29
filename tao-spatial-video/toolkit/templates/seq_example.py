# 时间轴示例：2026-09-29《WorkBuddy 还是豆包工作？》完整成片（119.6 秒 + 片尾定格 1.5 秒）
# 新视频照这个结构改：换素材名、换时间点（用 align.py 输出的关键词时间），保留版式常量。
import math, json, os, cv2
import comp4k
from comp4k import CYAN, VIOLET, INDIGO, SPR

MOV = '~/mnt/自媒体/workbudy 还是豆包工作.MOV'   # 原片
SRC_HDR = True          # iPhone 录的 HLG/杜比视界 → True
N_SRC = 7177            # 原片按 60fps 的帧数 = floor(时长×60)
HOLD = 1.5              # 片尾定格秒数
TOTAL_SEC = (N_SRC + int(HOLD*60)) / 60
SFX_DB = -8             # 音效相对人声峰值的电平
def css(n):
    im = cv2.imread(comp4k.SP+n+'.png', cv2.IMREAD_UNCHANGED); return im.shape[1]/SPR, im.shape[0]/SPR
LX, RX, PY = 222, 890, 760
def PL(sp, tin, tout, **kw):   # 左侧玻璃面板（在人物身后）
    d = dict(sp=sp, layer='back', x=LX, y=PY, s=0.92, ry=26, dur=.65, glow=CYAN, gk=.9, glass=True, float=7, ph=0.3, out=tout, to=(460,780))
    d['in'] = tin; d['from'] = (460,790,0.45,55); d.update(kw); return d
def PR(sp, tin, tout, **kw):   # 右侧玻璃面板
    d = dict(sp=sp, layer='back', x=RX, y=PY, s=0.92, ry=-26, dur=.65, glow=VIOLET, gk=.9, glass=True, float=7, ph=1.3, out=tout, to=(640,780))
    d['in'] = tin; d['from'] = (640,790,0.45,-55); d.update(kw); return d
def FR(sp, tin, tout, x=540, y=1195, s=1.0, pop=1.5, **kw):   # 前景文字/按钮（压在胸前）
    d = dict(sp=sp, layer='front', x=x, y=y, s=s, dur=.4, back=1.2, out=tout)
    d['in'] = tin; d['from'] = (x, y, s*pop, 0); d.update(kw); return d
def BADGE(sp, tin, tout):
    d = dict(sp=sp, layer='front', x=540, y=330, s=1.15, dur=.45, glass=True, glow=VIOLET, gk=.6, out=tout)
    d['in'] = tin; d['from'] = (540,300,.5,0); return d
def seq():
    ws = [css('T_WB')[0], css('T_VS')[0], css('T_DB')[0]]
    k = 1000/sum(ws); x = (1080-1000)/2; cxs = []
    for w in ws: cxs.append(x+w*k/2); x += w*k
    TY = 1195
    E = []
    # ---- S1–S4 开场（与样片一致）----
    E += [
     dict(sp='P_WB', layer='back', **{'in':0.48}, x=890, y=760, s=0.92, ry=-26, **{'from':(640,790,0.45,-55)}, dur=.65, glow=VIOLET, gk=.9, glass=True, float=7, ph=1.0, out=7.35, to=(640,780)),
     dict(sp='P_DB', layer='back', **{'in':1.44}, x=222, y=760, s=0.92, ry=26,  **{'from':(460,790,0.45,55)},  dur=.65, glow=CYAN,   gk=.9, glass=True, float=7, ph=0.0, out=7.35, to=(460,780)),
     dict(sp='T_WB', layer='front', **{'in':0.45}, x=cxs[0], y=TY, s=k, **{'from':(cxs[0],TY,k*1.6,0)}, dur=.35, back=1.2, out=7.35),
     dict(sp='T_VS', layer='front', **{'in':1.15}, x=cxs[1], y=TY, s=k, **{'from':(cxs[1],TY,k*2.2,0)}, dur=.35, back=1.2, out=7.35),
     dict(sp='T_DB', layer='front', **{'in':1.44}, x=cxs[2], y=TY, s=k, **{'from':(cxs[2],TY,k*1.6,0)}, dur=.35, back=1.2, out=7.35),
     dict(sp='T_SUB', layer='front', **{'in':2.39}, x=540, y=1318, s=1.0, **{'from':(540,1350,0.9,0)}, dur=.45, back=1.0, out=7.35),
     dict(sp='F_doc',  layer='front', **{'in':2.86}, x=82, y=1092, s=0.90, ry=18,  **{'from':(250,1000,.3,40)}, float=10, ph=.3, blur=0.8, out=7.35),
     dict(sp='F_chat', layer='front', **{'in':3.10}, x=998, y=1092, s=0.90, ry=-18, **{'from':(830,1000,.3,-40)}, float=10, ph=1.3, blur=0.8, out=7.35),
     dict(sp='F_book', layer='front', **{'in':3.46}, x=300, y=1046, s=0.74, ry=14,  **{'from':(420,1060,.3,30)}, float=9, ph=2.1, blur=1.2, out=7.35),
     dict(sp='F_meet', layer='front', **{'in':3.70}, x=780, y=1046, s=0.74, ry=-14, **{'from':(660,1060,.3,-30)}, float=9, ph=2.9, blur=1.2, out=7.35),
     dict(sp='R01', layer='back', **{'in':7.53}, x=172, y=600, s=0.95, ry=28, **{'from':(470,640,.3,60)}, glow=CYAN, gk=.7, glass=True, float=6, ph=.2,
          moves=[(8.97, 9.55, dict(x=235, y=1250, s=1.05, ry=10, layer='front'))], out=12.1, to=(235,1250)),
     dict(sp='R02', layer='back', **{'in':7.83}, x=196, y=940, s=0.95, ry=22, **{'from':(470,900,.3,60)}, glow=CYAN, gk=.6, glass=True, float=6, ph=1.2, out=9.05, to=(430,900)),
     dict(sp='R03', layer='back', **{'in':8.07}, x=908, y=600, s=0.95, ry=-28, **{'from':(610,640,.3,-60)}, glow=VIOLET, gk=.7, glass=True, float=6, ph=2.2, out=9.05, to=(650,640)),
     dict(sp='R04', layer='back', **{'in':8.31}, x=884, y=940, s=0.95, ry=-22, **{'from':(610,900,.3,-60)}, glow=VIOLET, gk=.6, glass=True, float=6, ph=3.2, out=9.05, to=(650,900)),
     dict(sp='CH1', layer='front', **{'in':9.45}, x=648, y=1250, s=1.0, **{'from':(720,1250,.8,0)}, dur=.45, back=1.1, out=12.1),
    ]
    # ---- 第一点：生态 ----
    E += [ BADGE('BADGE1', 12.30, 50.60),
           PL('P_FEISHU', 12.37, 30.30, wipe=4.2),
           FR('V_DB', 19.38, 23.50),
           PR('P_NATIVE', 21.39, 30.30, wipe=5.6),
           PR('P_WECOM', 30.45, 46.70, wipe=4.4),
           FR('V_WB', 37.71, 40.30),
           PL('P_WBE', 39.61, 46.70, wipe=3.6),
           FR('Q_STEP1', 46.81, 50.70, y=1045, pop=1.3),
           FR('Q_NOTAI', 46.95, 50.70, y=1175, pop=1.3),
           FR('Q_STRIKE', 47.41, 50.70, y=1182, pop=1.0, dur=.25),
           FR('Q_ECO', 48.13, 50.70, y=1310, pop=1.6) ]
    # ---- 第二点：业务 ----
    E += [ BADGE('BADGE2', 50.77, 97.30),
           FR('T_INOUT', 52.45, 57.30),
           PL('P_IN', 53.23, 57.30),
           PR('P_OUT', 55.07, 72.90),
           PL('P_DBIN', 57.40, 72.90, wipe=5.6),
           FR('F_POSTER', 68.42, 72.90, x=300, y=1180, s=0.9, ry=12, float=8, pop=0.5),
           FR('F_VIDEO', 68.96, 72.90, x=780, y=1180, s=0.9, ry=-12, float=8, ph=1.5, pop=0.5),
           FR('T_MM', 69.50, 72.90, y=1370),
           PR('P_WBOUT', 73.01, 91.10, wipe=2.8, wipe_from=78.4, reveal0=0.30),
           PL('P_WECOMLINK', 76.14, 81.20, s=0.95, ry=22),
           PL('P_CORDYS', 81.31, 91.10, wipe=1.2, wipe_from=83.9, reveal0=0.45),
           FR('F_ONE', 85.51, 91.10, y=1100),
           FR('F_R1', 87.07, 91.10, x=245, y=1290, s=0.8, pop=0.5),
           FR('F_R2', 88.09, 91.10, x=540, y=1290, s=0.8, pop=0.5),
           FR('F_R3', 88.93, 91.10, x=835, y=1290, s=0.8, pop=0.5),
           FR('J1', 91.26, 97.30, y=1170),
           PR('P_WB', 93.48, 98.80),
           FR('J2', 94.74, 97.30, y=1330),
           PL('P_DB', 96.42, 98.80) ]
    # ---- 第三点：模型 ----
    cw = [css('C_COMP')[0], css('C_BACKUP')[0], css('C_SPEC')[0]]; s_c = 0.9; gap = 10
    tot = sum(cw)*s_c + gap*2; x = (1080-tot)/2; ccx = []
    for w in cw: ccx.append(x+w*s_c/2); x += w*s_c+gap
    E += [ BADGE('BADGE3', 97.44, 113.90),
           FR('W_WARN', 99.00, 100.85),
           PL('P_MDB', 100.94, 113.90),
           PR('P_MWB', 105.45, 113.90),
           FR('C_COMP', 109.30, 113.95, x=ccx[0], y=1150, s=s_c, pop=0.5),
           FR('C_BACKUP', 111.40, 113.95, x=ccx[1], y=1150, s=s_c, pop=0.5),
           FR('C_SPEC', 111.88, 113.95, x=ccx[2], y=1150, s=s_c, pop=0.5),
           FR('STAMP', 113.26, 113.95, y=1320, s=0.9, pop=1.8, dur=.3, back=1.0) ]
    # ---- 第四点：实测（与样片一致，+113.5s）----
    o = 113.5
    E += [ dict(sp='BADGE4', layer='front', **{'in':o+0.48}, x=540, y=330, s=1.15, **{'from':(540,300,.5,0)}, dur=.45, glass=True, glow=VIOLET, gk=.6),
           dict(sp='LAPTOP', layer='back', **{'in':o+0.62}, x=205, y=800, s=0.47, ry=30, **{'from':(470,800,.25,65)}, dur=.7, glow=INDIGO, gk=1.0, float=5, ph=.4),
           dict(sp='T_EVAL', layer='front', **{'in':o+1.14}, x=540, y=1160, s=1.2, **{'from':(540,1160,1.9,0)}, dur=.35, back=1.2),
           dict(sp='T_EVALSUB', layer='front', **{'in':o+2.10}, x=540, y=1275, s=1.0, **{'from':(540,1300,.9,0)}, dur=.45, back=1.0),
           dict(sp='RATING', layer='back', **{'in':o+3.42}, x=895, y=780, s=0.70, ry=-24, **{'from':(640,800,.35,-55)}, dur=.65, glow=VIOLET, gk=.9, glass=True, float=6, ph=1.7, wipe=1.1) ]
    subs = [tuple(s) for s in json.load(open(comp4k.SUBDIR+'subs.json'))]
    def boost(t):
        b = 0.
        for (t0, amp) in [(6.52,1.2),(46.03,0.9),(84.97,0.6),(113.26,0.6),(117.58,0.9),(118.78,0.8)]:
            if t0 <= t < t0+.7: b += amp*(1-(t-t0)/.7)
        if t >= 119.6: b += 0.25+0.25*math.sin((t-119.6)*4)
        return b
    fx = dict(boost=boost, streaks=[(0.05,TY,.5),(6.45,720,.45),(7.35,TY,.45),(8.95,1250,.45),(12.28,330,.45),(19.35,1195,.45),(37.68,1195,.45),
                                    (46.78,1195,.45),(50.74,330,.45),(91.22,1170,.45),(97.41,330,.45),(113.95,330,.45),(114.6,1160,.45)])
    return dict(els=E, subs=subs, fx=fx, sub_index={s[2]: s[2] for s in subs})

# 音效：(秒, 音效名, 声像 -1左~1右, 增益)。规则见 SKILL.md「音效」一节
SFX = [ (0.46,'deng',0.5,1),(1.13,'app',0,.8),(1.42,'deng',-0.5,1),(2.37,'ui',0,.9),(2.84,'app',-.6,.7),(3.08,'app',.6,.7),(3.44,'app',-.3,.7),(3.68,'app',.3,.7),
       (6.50,'ding3',0,.9),(7.51,'deng',-0.5,.85),(7.81,'deng',-0.5,.85),(8.05,'deng',0.5,.85),(8.29,'deng',0.5,.85),(8.95,'tone',-.3,1),(9.43,'xp',.2,.9),
       (12.28,'xp',0,.9),(12.35,'deng',-0.5,1),(15.0,'app',-0.5,.5),(15.55,'app',-0.5,.5),(16.15,'app',-0.5,.5),(16.69,'app',-0.5,.5),(19.36,'tone',0,1),
       (21.37,'deng',0.5,1),(25.74,'app',0.5,.5),(26.52,'app',0.5,.5),
       (30.43,'deng',0.5,1),(31.95,'app',0.5,.5),(32.79,'app',0.5,.5),(33.39,'app',0.5,.5),(34.89,'app',0.5,.5),(37.69,'tone',0,1),
       (39.59,'deng',-0.5,1),(40.45,'app',-0.5,.5),(41.17,'app',-0.5,.5),(41.83,'app',-0.5,.5),(43.03,'app',-0.5,.5),(46.03,'ding3',-0.5,.6),
       (46.79,'ui',0,.9),(46.95,'tone',0,.9),(47.41,'ding3',0,.9),(48.11,'tone',0,1),
       (50.75,'xp',0,.9),(52.43,'tone',0,1),(53.21,'deng',-0.5,1),(55.05,'deng',0.5,1),
       (57.38,'deng',-0.5,1),(59.5,'app',-0.5,.5),(60.58,'app',-0.5,.5),(61.48,'app',-0.5,.5),(62.96,'app',-0.5,.5),
       (68.40,'app',-0.5,.8),(68.94,'app',0.5,.8),(69.48,'tone',0,.9),
       (72.99,'deng',0.5,1),(76.12,'deng',-0.5,1),(78.67,'app',0.5,.5),(79.45,'app',0.5,.5),(80.95,'app',0.5,.5),
       (81.29,'deng',-0.5,1),(84.97,'ding3',-0.5,.6),(85.49,'tone',0,.9),(87.05,'app',-.4,.7),(88.07,'app',0,.7),(88.91,'app',.4,.7),
       (91.24,'tone',0,1),(93.46,'deng',0.5,1),(94.72,'tone',0,1),(96.40,'deng',-0.5,1),
       (97.42,'xp',0,.9),(98.98,'ui',0,.9),(100.92,'deng',-0.5,1),(105.43,'deng',0.5,1),
       (109.28,'app',-.4,.7),(111.38,'app',0,.7),(111.86,'app',.4,.7),(113.24,'ding3',0,1),
       (113.96,'xp',0,.9),(114.10,'deng',-.6,1),(114.62,'tone',0,1),(115.58,'ui',0,.9),(116.90,'deng',.6,1),(117.10,'ding3',.6,.8) ]
