# 素材示例：《WorkBuddy 还是豆包工作？》用到的全部素材（名字要和时间轴里的 sp= 对上）
# 用法（云端容器）: python3 sprites_example.py <输出目录>
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'container'))
from sprites_lib import *
S = {}
# 开场：两款产品卡（左 A 青蓝 / 右 B 紫靛）+ 标题三段 + 装饰图标
S['P_DB'] = product_panel(DB, "豆包工作", "字节 × 飞书", [("grid","飞书生态"),("doc","文档协作"),("book","知识管理"),("image","多模态创作")], "spark")
S['P_WB'] = product_panel(WB, "WorkBuddy", "腾讯 × 企业微信", [("chat","企业微信"),("doc","腾讯文档"),("meeting","腾讯会议"),("users","客户连接")], "link", en=True)
S['T_WB'] = glow_text("WorkBuddy", 124, en=True)
S['T_VS'] = f'<div class="el" style="font-family:PopBI;font-size:110px;padding:10px 24px;background:linear-gradient(90deg,{DB[0]},#fff 50%,{WB[0]});-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 3px 0 rgba(40,25,120,.9)) drop-shadow(0 0 16px rgba(170,140,255,.95))">VS</div>'
S['T_DB'] = glow_text("豆包工作", 118)
S['T_SUB'] = glow_text("企业 AI 办公工具，到底怎么选？", 50)
S['F_doc'] = float_icon(DB, "doc"); S['F_book'] = float_icon(DB, "book"); S['F_chat'] = float_icon(WB, "chat"); S['F_meet'] = float_icon(WB, "meeting")
# 四步路线图 + 第一章标题
for n, t, g in [("01","生态","grid"),("02","业务","users"),("03","模型","cpu"),("04","实测","check")]: S[f'R{n}'] = number_tile(n, t, g)
S['CH1'] = '''<div class="el" style="padding:10px 20px"><div class="cn glowtxt" style="font-size:104px;font-weight:900;line-height:1.1"><span class="skew">看生态</span></div>
  <div class="cn glowtxt" style="font-size:42px;font-weight:700;margin-top:10px">你们公司泡在哪个生态里</div></div>'''
# 章节标
for n, t, k in [("01","生态","BADGE1"),("02","业务","BADGE2"),("03","模型","BADGE3"),("04","实测","BADGE4")]: S[k] = badge(n, t)
# 第一章
S['P_FEISHU'] = list_panel(DB, "grid", "飞书重度用户", "大量工作都在飞书里", [("doc","文档"),("book","知识库"),("meeting","会议"),("users","协作")])
S['P_NATIVE'] = list_panel(DB, "lock", "原生结合", "豆包工作 × 飞书", [("card","沿用飞书身份"),("lock","沿用对象权限"),("users","原来的组织"),("book","原来的知识体系")])
S['P_WECOM']  = list_panel(WB, "chat", "企微 / 微信生态", "业务关系都沉淀在这里", [("chat","企业微信"),("doc","腾讯文档"),("meeting","腾讯会议"),("link","业务关系")], tsize=46)
S['P_WBE']    = list_panel(WB, "grid", "企业版深度整合", "WorkBuddy Enterprise", [("chat","企业微信"),("doc","腾讯文档"),("meeting","腾讯会议"),("book","乐享知识库")], footer='<span style="font-size:22px;color:#6B6596;font-weight:500">来源：腾讯云官网</span>', tsize=40)
S['V_DB'] = verdict(DB, "飞书重度用户", "豆包工作"); S['V_WB'] = verdict(WB, "企微生态", "WorkBuddy", en=True)
S['Q_STEP1'] = pill("第一步"); S['Q_NOTAI'] = dim_text("不是选 AI"); S['Q_STRIKE'] = strike(); S['Q_ECO'] = glow_text("是看你活在哪个生态")
# 第二章
S['T_INOUT'] = glow_text("一个向内 · 一个向外", 92)
S['P_IN']  = big_card(DB, "豆包工作", "向内", "组织管理", "自己人怎么协作")
S['P_OUT'] = big_card(WB, "WorkBuddy", "向外", "客户管理", "外边的人怎么管", en=True)
S['P_DBIN'] = list_panel(DB, "users", "豆包工作", "更偏内部协作", [("users","自己人怎么协作"),("doc","文档怎么沉淀"),("flow","知识怎么流转"),("target","团队怎么对齐")], footer="内部的事越多 → 越好用")
S['F_POSTER'] = icon_tile(DB, "image", "海报"); S['F_VIDEO'] = icon_tile(DB, "video", "视频")
S['T_MM'] = glow_text("内容类工作 · 完成度更高", 66)
S['P_WBOUT'] = list_panel(WB, "funnel", "WorkBuddy", "更偏客户连接", [("funnel","线索怎么跟"),("chart","商机怎么推"),("mega","客户怎么运营")], footer="通过企业微信连接客户", en=True)
S['P_WECOMLINK'] = small_card(WB, "chat", "企业微信", "连接客户")
S['P_CORDYS'] = progress_card(WB, "Cordys CRM", "专门做了 Skill 插件", "线索", "回款", source="Cordys CRM 官方")
S['F_ONE'] = chat_bar("一句话", "企业微信接入以后")
S['F_R1'] = result_tile("card","客户画像"); S['F_R2'] = result_tile("task","跟进任务"); S['F_R3'] = result_tile("mega","客户运营")
S['J1'] = judge(WB, "销售驱动 · 客户管理重", "WorkBuddy", en=True); S['J2'] = judge(DB, "内部协作 · 组织管理重", "豆包工作")
# 第三章
S['W_WARN'] = warn_chip("这点很多公司会忽略")
S['P_MDB'] = big_card(DB, "豆包工作", None, "Seed 系列", "只支持自家模型", foot="截至 2026 年 9 月 · 以官方为准", bsize=78)
S['P_MWB'] = big_card(WB, "WorkBuddy", None, "多模型", "可以自由切换", foot="截至 2026 年 9 月 · 以官方为准", en=True)
S['C_COMP'] = chip("shield","合规"); S['C_BACKUP'] = chip("db","多模型备份"); S['C_SPEC'] = chip("target","指定模型")
S['STAMP'] = stamp("硬指标")
# 第四章 + 结尾
S['LAPTOP'] = laptop("真实业务评测", "豆包工作", "生成项目方案", "WorkBuddy", "客户跟进分析", ["完成质量","操作步骤","数据连接","稳定性"])
S['RATING'] = rating_panel("评测维度", [("award","完成质量"),("steps","操作步骤"),("db","数据连接"),("cpu","模型能力"),("shield","权限与安全"),("clock","稳定性"),("coin","成本")])
S['T_EVAL'] = glow_text("真实业务评测", 112); S['T_EVALSUB'] = glow_text("别只看 Demo，用你的业务跑一遍", 46)
if __name__ == '__main__':
    render_all(S, sys.argv[1] if len(sys.argv) > 1 else './sp3')
