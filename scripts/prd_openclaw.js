const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');

const C = { primary:"1A3A5C", accent:"2E86AB", green:"28A745", red:"DC3545", orange:"FD7E14", gray:"6C757D", light:"F2F7FB", white:"FFFFFF", black:"222222" };
const bd = { style:BorderStyle.SINGLE, size:1, color:"DEE2E6" };
const bs = { top:bd, bottom:bd, left:bd, right:bd };
const mg = { top:60, bottom:60, left:100, right:100 };

function hC(t,w){ return new TableCell({ borders:bs, width:{size:w,type:WidthType.DXA}, shading:{fill:C.primary,type:ShadingType.CLEAR}, margins:mg, children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:t,bold:true,font:"Arial",size:20,color:C.white})]})] }); }
function dC(t,w,o={}){ return new TableCell({ borders:bs, width:{size:w,type:WidthType.DXA}, shading:o.bg?{fill:o.bg,type:ShadingType.CLEAR}:undefined, margins:mg, children:Array.isArray(t)?t:[new Paragraph({alignment:o.align||AlignmentType.LEFT, children:[new TextRun({text:String(t),font:"Arial",size:20,color:o.color||C.black,bold:o.bold||false})]})] }); }

function h1(t){ return new Paragraph({heading:HeadingLevel.HEADING_1, spacing:{before:400,after:200}, children:[new TextRun({text:t,font:"Arial",size:32,bold:true,color:C.primary})]}); }
function h2(t){ return new Paragraph({heading:HeadingLevel.HEADING_2, spacing:{before:300,after:160}, children:[new TextRun({text:t,font:"Arial",size:26,bold:true,color:C.accent})]}); }
function h3(t){ return new Paragraph({spacing:{before:240,after:120}, children:[new TextRun({text:t,font:"Arial",size:22,bold:true,color:C.primary})]}); }
function p(t,o={}){ return new Paragraph({spacing:{after:o.after||100}, indent:o.indent?{left:o.indent}:undefined, children:[new TextRun({text:t,font:"Arial",size:20,color:o.color||C.black,bold:o.bold||false,italics:o.it||false})]}); }
function bl(t,l=0){ return new Paragraph({numbering:{reference:"bullets",level:l},spacing:{after:60}, children:[new TextRun({text:t,font:"Arial",size:20,color:C.black})]}); }
function nl(t,l=0){ return new Paragraph({numbering:{reference:"numbers",level:l},spacing:{after:60}, children:[new TextRun({text:t,font:"Arial",size:20,color:C.black})]}); }
function code(lines){ return lines.map(l=>new Paragraph({spacing:{after:0},shading:{fill:"F5F5F5",type:ShadingType.CLEAR},indent:{left:360}, children:[new TextRun({text:l,font:"Courier New",size:17,color:"333333"})]})); }
function apiT(fields){ const cw=[2200,1400,1000,4760]; const rows=[new TableRow({children:[hC("字段名",cw[0]),hC("类型",cw[1]),hC("必填",cw[2]),hC("说明",cw[3])]})]; fields.forEach((f,i)=>{const bg=i%2===1?C.light:undefined; rows.push(new TableRow({children:[dC(f[0],cw[0],{bold:true,bg}),dC(f[1],cw[1],{align:AlignmentType.CENTER,bg}),dC(f[2],cw[2],{align:AlignmentType.CENTER,color:f[2]==="是"?C.red:C.gray,bg}),dC(f[3],cw[3],{bg})]}));}); return new Table({width:{size:100,type:WidthType.PERCENTAGE},columnWidths:cw,rows}); }

const doc = new Document({
  styles:{ default:{document:{run:{font:"Arial",size:22}}}, paragraphStyles:[
    {id:"Heading1",name:"Heading 1",basedOn:"Normal",next:"Normal",quickFormat:true, run:{size:32,bold:true,font:"Arial",color:C.primary}, paragraph:{spacing:{before:400,after:200},outlineLevel:0}},
    {id:"Heading2",name:"Heading 2",basedOn:"Normal",next:"Normal",quickFormat:true, run:{size:26,bold:true,font:"Arial",color:C.accent}, paragraph:{spacing:{before:300,after:160},outlineLevel:1}},
  ]},
  numbering:{config:[
    {reference:"bullets",levels:[{level:0,format:LevelFormat.BULLET,text:"•",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}},{level:1,format:LevelFormat.BULLET,text:"◦",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:1080,hanging:360}}}}]},
    {reference:"numbers",levels:[{level:0,format:LevelFormat.DECIMAL,text:"%1.",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}},{level:1,format:LevelFormat.DECIMAL,text:"%2)",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:1080,hanging:360}}}}]},
  ]},
  sections:[{
    properties:{ page:{ size:{width:12240,height:15840}, margin:{top:1200,right:1200,bottom:1200,left:1200} }},
    headers:{ default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT, children:[new TextRun({text:"AIBD新店冷启动 — OpenClaw架构方案 v1.0",font:"Arial",size:16,color:C.gray,italics:true})]})]}) },
    footers:{ default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:"机密文档 — 仅限内部使用  |  Page ",font:"Arial",size:16,color:C.gray}), new TextRun({children:[PageNumber.CURRENT],font:"Arial",size:16,color:C.gray})]})]}) },
    children:[
      // ===== 封面 =====
      new Paragraph({spacing:{before:1000,after:0},alignment:AlignmentType.CENTER, children:[new TextRun({text:"AIBD新店冷启动",font:"Arial",size:52,bold:true,color:C.primary})]}),
      new Paragraph({spacing:{before:100,after:0},alignment:AlignmentType.CENTER, children:[new TextRun({text:"OpenClaw架构方案",font:"Arial",size:36,color:C.accent})]}),
      new Paragraph({spacing:{before:80,after:200},alignment:AlignmentType.CENTER, children:[new TextRun({text:"基于OpenClaw Agent框架的多Skill协同冷启动方案",font:"Arial",size:22,color:C.gray})]}),

      new Table({ width:{size:60,type:WidthType.PERCENTAGE}, columnWidths:[2400,3600], rows:[
        new TableRow({children:[dC("文档版本",2400,{bold:true,bg:C.light}),dC("v1.0",3600)]}),
        new TableRow({children:[dC("编写日期",2400,{bold:true,bg:C.light}),dC("2026-03-10",3600)]}),
        new TableRow({children:[dC("产品负责人",2400,{bold:true,bg:C.light}),dC("郭磊平",3600)]}),
        new TableRow({children:[dC("状态",2400,{bold:true,bg:C.light}),dC("草稿 — 待评审",3600,{color:C.orange})]}),
        new TableRow({children:[dC("优先级",2400,{bold:true,bg:C.light}),dC("P0",3600,{color:C.red,bold:true})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 1. 背景 =====
      h1("1. 背景与目标"),
      h2("1.1 现状痛点"),
      p("AIBD已支持「意向嗅探→企微添加→建群→群内签约」全流程。但签约完成后，新店冷启动（装修/上单/活动报名）仍依赖外部运营团队手工操作，存在："),
      bl("人力瓶颈：外包人员处理能力有限，旺季扩张困难"),
      bl("效率低下：签约到上线平均3-5个工作日"),
      bl("质量不稳：不同操作人员出品差异大"),
      bl("信息断层：AIBD签约信息无法自动流转到冷启环节"),

      h2("1.2 为什么用OpenClaw"),
      p("OpenClaw是公司内部AI Agent框架，核心能力与冷启动场景高度匹配："),

      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2340,3120,3900], rows:[
        new TableRow({children:[hC("OpenClaw能力",2340),hC("冷启动场景映射",3120),hC("替代现状",3900)]}),
        new TableRow({children:[dC("Skill体系",2340,{bold:true}),dC("每个冷启子项 = 一个独立Skill",3120),dC("替代外部团队各岗位",3900)]}),
        new TableRow({children:[dC("Session管理",2340,{bold:true,bg:C.light}),dC("每个商家 = 一个独立Session",3120,{bg:C.light}),dC("替代人工跟踪表",3900,{bg:C.light})]}),
        new TableRow({children:[dC("企微消息通道",2340,{bold:true}),dC("企微群内对话交互",3120),dC("替代人工群内沟通",3900)]}),
        new TableRow({children:[dC("浏览器自动化",2340,{bold:true,bg:C.light}),dC("操作商家后台（兜底方案）",3120,{bg:C.light}),dC("替代手工操作页面",3900,{bg:C.light})]}),
        new TableRow({children:[dC("定时任务/Cron",2340,{bold:true}),dC("超时提醒/状态轮询",3120),dC("替代人工跟催",3900)]}),
        new TableRow({children:[dC("图片处理",2340,{bold:true,bg:C.light}),dC("门头图裁剪/AI生图/OCR识别",3120,{bg:C.light}),dC("替代外部图片处理",3900,{bg:C.light})]}),
      ]}),

      h2("1.3 目标"),
      bl("AIBD签约完成后，OpenClaw自动接管冷启动全流程"),
      bl("签约到上线周期：3-5天 → 当天完成"),
      bl("覆盖三大子项：门店装修 + 上团单 + 活动报名"),
      bl("第一期聚焦：门店装修（门头图+入口图）+ 上团单"),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 2. 架构设计 =====
      h1("2. 系统架构"),

      h2("2.1 整体架构"),
      p("采用「AIBD主控 + OpenClaw Skill执行」的A2A架构。AIBD负责商机管理和路由决策，OpenClaw负责具体冷启子项的执行。",{bold:true}),

      ...code([
        "┌─────────────────────────────────────────────────────────┐",
        "│                     AIBD 主控 Agent                      │",
        "│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │",
        "│  │ 商机管理  │  │ 意向路由  │  │ 状态聚合  │               │",
        "│  └──────────┘  └──────────┘  └──────────┘               │",
        "│         │              │              │                   │",
        "│         ▼              ▼              ▼                   │",
        "│  ┌─────────────── MQ / 回调 ─────────────────┐          │",
        "└──┤                                            ├──────────┘",
        "   │                                            │",
        "   ▼                                            ▼",
        "┌──────────────── OpenClaw Agent ──────────────────┐",
        "│                                                   │",
        "│  ┌──────────────┐  ┌──────────┐  ┌────────────┐ │",
        "│  │ 装修 Skill    │  │上单 Skill │  │活动报名Skill│ │",
        "│  │ (门头图/入口图)│  │(团单录入) │  │ (神券报名)  │ │",
        "│  └──────┬───────┘  └────┬─────┘  └──────┬─────┘ │",
        "│         │               │               │        │",
        "│         ▼               ▼               ▼        │",
        "│  ┌─────────────── 提交接口层 ─────────────────┐  │",
        "│  │ 装修API  │  团购API  │  活动API  │  查询API │  │",
        "│  └──────────────────────────────────────────────┘ │",
        "│                        │                          │",
        "│                        ▼                          │",
        "│               ┌──────────────┐                    │",
        "│               │  企微群消息   │                    │",
        "│               │ (商家交互)    │                    │",
        "│               └──────────────┘                    │",
        "└───────────────────────────────────────────────────┘",
      ]),

      h2("2.2 A2A协议设计"),
      p("AIBD与OpenClaw之间通过标准化消息协议通信："),

      h3("2.2.1 AIBD → OpenClaw（任务下发）"),
      apiT([
        ["task_id","string","是","全局唯一任务ID"],
        ["task_type","enum","是","COLD_START_DECORATION / COLD_START_PRODUCT / COLD_START_ACTIVITY"],
        ["shop_id","string","是","门店ID"],
        ["dp_shop_id","string","是","点评门店ID"],
        ["shop_name","string","是","门店名称"],
        ["shop_category","string","是","品类（如：烧烤、美容美发）"],
        ["wechat_group_id","string","是","企微群ID（AIBD已建好的群）"],
        ["signed_info","object","否","签约时采集的信息（商家提供的照片/菜单等）"],
        ["cold_start_items","array","是","待完成冷启子项列表（见下方状态表）"],
        ["priority","enum","否","HIGH / NORMAL / LOW，默认NORMAL"],
        ["timeout_hours","int","否","超时时间，默认72小时"],
      ]),

      h3("2.2.2 OpenClaw → AIBD（状态回报）"),
      apiT([
        ["task_id","string","是","任务ID"],
        ["task_type","enum","是","任务类型"],
        ["shop_id","string","是","门店ID"],
        ["status","enum","是","IN_PROGRESS / COMPLETED / FAILED / TIMEOUT / NEED_HUMAN"],
        ["sub_items","array","是","每个子项的完成状态（见下方状态表）"],
        ["message","string","否","状态描述/失败原因"],
        ["completed_at","string","否","完成时间 ISO 8601"],
      ]),

      h3("2.2.3 冷启子项状态表"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2200,1600,1600,2200,1760], rows:[
        new TableRow({children:[hC("子项",2200),hC("字段名",1600),hC("达标条件",1600),hC("查询方式",2200),hC("状态枚举",1760)]}),
        new TableRow({children:[dC("门头图",2200,{bold:true}),dC("header_photo",1600),dC("≥3张",1600),dC("商家侧接口查询",2200),dC("NOT_DONE/SUBMITTED/APPROVED/REJECTED",1760,{color:C.gray})]}),
        new TableRow({children:[dC("入口图",2200,{bold:true,bg:C.light}),dC("entrance_photo",1600,{bg:C.light}),dC("=1张",1600,{bg:C.light}),dC("商家侧接口查询",2200,{bg:C.light}),dC("同上",1760,{bg:C.light})]}),
        new TableRow({children:[dC("门店电话",2200,{bold:true}),dC("phone",1600),dC("有值",1600),dC("商家侧接口查询",2200),dC("NOT_DONE/DONE",1760,{color:C.gray})]}),
        new TableRow({children:[dC("营业时间",2200,{bold:true,bg:C.light}),dC("business_hours",1600,{bg:C.light}),dC("有值",1600,{bg:C.light}),dC("商家侧接口查询",2200,{bg:C.light}),dC("NOT_DONE/DONE",1760,{bg:C.light})]}),
        new TableRow({children:[dC("经营范围",2200,{bold:true}),dC("biz_scope",1600),dC("有值",1600),dC("商家侧接口查询",2200),dC("NOT_DONE/DONE",1760,{color:C.gray})]}),
        new TableRow({children:[dC("银行卡绑定",2200,{bold:true,bg:C.light}),dC("bank_bindingbind",1600,{bg:C.light}),dC("已绑定",1600,{bg:C.light}),dC("支付侧接口查询",2200,{bg:C.light}),dC("NOT_DONE/DONE",1760,{bg:C.light})]}),
        new TableRow({children:[dC("上团单",2200,{bold:true}),dC("products",1600),dC("≥3个",1600),dC("团购侧接口查询",2200),dC("NOT_DONE/SUBMITTED/APPROVED/REJECTED",1760,{color:C.gray})]}),
        new TableRow({children:[dC("神券报名",2200,{bold:true,bg:C.light}),dC("activity",1600,{bg:C.light}),dC("已报名",1600,{bg:C.light}),dC("活动侧接口查询",2200,{bg:C.light}),dC("NOT_DONE/SUBMITTED/ACTIVE",1760,{bg:C.light})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 3. Skill详细设计 =====
      h1("3. Skill详细设计"),

      h2("3.1 装修Skill（decoration-skill）"),
      h3("3.1.1 职责"),
      bl("采集商家门头图、入口图（企微群内对话）"),
      bl("图片质量校验（分辨率≥1080p、非模糊、非截图）"),
      bl("图片裁剪/比例调整（门头图16:9、入口图1:1）"),
      bl("AI文生图（可选：商家无合适照片时，基于品类生成）"),
      bl("调用装修提交接口 → 送审"),
      bl("监听审核结果 → 通过则通知商家 → 驳回则解析原因重新采集"),

      h3("3.1.2 交互流程（企微群内）"),
      nl("OpenClaw在企微群发送开场白：「您好！签约已完成🎉 接下来帮您完成门店装修，需要您提供几张照片...」"),
      nl("引导商家发送门头照片（至少3张）"),
      nl("收到图片 → Skill自动校验（分辨率/清晰度/内容识别）"),
      nl("校验通过 → 自动裁剪+预览 → 群内发预览图让商家确认"),
      nl("商家确认 → 调用提交接口送审"),
      nl("审核通过 → 群内通知「装修已完成✅」"),
      nl("审核驳回 → 群内发送驳回原因 + 指引重新拍照"),

      h3("3.1.3 所需外部接口"),
      apiT([
        ["POST /api/decoration/photo/submit","—","是","提交门头图/入口图，入参：shop_id, photo_type(HEADER/ENTRANCE), photo_urls[], operator_id"],
        ["GET /api/decoration/photo/status","—","是","查询审核状态，入参：shop_id, submission_id"],
        ["GET /api/shop/info","—","是","查询门店当前装修状态（电话/营业时间/经营范围是否有值）"],
        ["POST /api/decoration/photo/crop","—","否","图片裁剪服务（如商家侧有），否则OpenClaw内部处理"],
      ]),

      h3("3.1.4 状态机"),
      ...code([
        "IDLE → COLLECTING → VALIDATING → PREVIEWING → SUBMITTED → REVIEWING",
        "  │                      │              │                      │",
        "  │                      ▼              ▼                      ▼",
        "  │                VALIDATION_FAILED  MERCHANT_REJECTED    REVIEW_REJECTED",
        "  │                      │              │                      │",
        "  │                      └──── COLLECTING ◄────────────────────┘",
        "  │                                                           │",
        "  └───────── TIMEOUT (72h) ───────────────────────────────────┤",
        "                                                              ▼",
        "                                              REVIEW_APPROVED → DONE",
      ]),

      h2("3.2 上单Skill（product-skill）"),
      h3("3.2.1 职责"),
      bl("前置校验：银行卡是否已绑定（阻塞项）"),
      bl("采集团单信息（企微群内：图片OCR/文字/Excel）"),
      bl("结构化提取：品名、价格、规格、图片"),
      bl("AI补充：自动生成商品描述、推荐定价"),
      bl("群内发确认清单 → 商家确认/修改"),
      bl("调用团购提交接口 → 送审"),
      bl("审核结果处理"),

      h3("3.2.2 前置检查"),
      p("上团单前必须完成以下前置项，否则Skill自动阻塞并引导商家完成：",{bold:true}),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[3120,3120,3120], rows:[
        new TableRow({children:[hC("前置项",3120),hC("检查方式",3120),hC("未完成处理",3120)]}),
        new TableRow({children:[dC("银行卡绑定",3120,{bold:true}),dC("调用支付侧接口查询",3120),dC("群内发绑卡操作指引图",3120)]}),
        new TableRow({children:[dC("门店装修(基础信息)",3120,{bold:true,bg:C.light}),dC("调用商家侧接口查询",3120,{bg:C.light}),dC("先触发装修Skill完成",3120,{bg:C.light})]}),
      ]}),

      h3("3.2.3 所需外部接口"),
      apiT([
        ["POST /api/product/batch-create","—","是","批量创建团单，入参：shop_id, products[{name,price,specs,image_url,...}]"],
        ["POST /api/product/submit-review","—","是","提交送审，入参：shop_id, product_ids[]"],
        ["GET /api/product/review-status","—","是","查询审核状态，入参：shop_id, submission_id"],
        ["GET /api/product/list","—","是","查询门店现有团单列表"],
        ["GET /api/payment/bindcard-status","—","是","查询银行卡绑定状态，入参：shop_id"],
        ["GET /api/shop/recommend-products","—","否","基于品类/商圈推荐团单模板"],
      ]),

      h2("3.3 活动报名Skill（activity-skill）"),
      h3("3.3.1 职责"),
      bl("查询门店可报名活动列表（当前聚焦神券活动）"),
      bl("向商家介绍活动利益点（流量/曝光/ROI预估）"),
      bl("收集报名意向 → 调用报名接口"),
      bl("跟踪报名状态 → 通知结果"),

      h3("3.3.2 所需外部接口"),
      apiT([
        ["GET /api/activity/available","—","是","查询门店可报名活动，入参：shop_id"],
        ["POST /api/activity/enroll","—","是","提交报名，入参：shop_id, activity_id, params"],
        ["GET /api/activity/enroll-status","—","是","查询报名状态"],
      ]),

      p("注：活动报名是否纳入一期需再确认。如果销售签约时能直接搞定，可延后到二期。",{it:true,color:C.gray}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 4. 核心流程 =====
      h1("4. 核心流程时序"),

      h2("4.1 完整冷启动时序"),
      ...code([
        "AIBD          MQ/回调        OpenClaw        装修API       团购API       企微群",
        " │               │              │              │             │             │",
        " │─签约完成──────>│              │              │             │             │",
        " │               │─任务下发────>│              │             │             │",
        " │               │              │──查询门店状态─>│             │             │",
        " │               │              │<──返回缺项────│             │             │",
        " │               │              │              │             │             │",
        " │               │              │──发开场白────────────────────────────────>│",
        " │               │              │              │             │  商家发照片  │",
        " │               │              │<──────────────────────────────收到图片───│",
        " │               │              │──校验+裁剪──>│             │             │",
        " │               │              │──提交装修────>│             │             │",
        " │               │              │<──审核结果────│             │             │",
        " │               │              │──通知装修完成──────────────────────────>│",
        " │               │              │              │             │             │",
        " │               │              │──检查银行卡──────────────>│             │",
        " │               │              │──采集团单────────────────────────────>│",
        " │               │              │<──────────────────────────商家发菜单──│",
        " │               │              │──OCR+结构化  │             │             │",
        " │               │              │──发确认清单──────────────────────────>│",
        " │               │              │<──────────────────────────商家确认────│",
        " │               │              │──提交团单─────────────────>│             │",
        " │               │              │<──审核结果──────────────── │             │",
        " │               │              │──通知上单完成──────────────────────────>│",
        " │               │              │              │             │             │",
        " │               │<─状态回报────│              │             │             │",
        " │<──更新商机状态─│              │              │             │             │",
      ]),

      h2("4.2 异常处理流程"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2340,3900,3120], rows:[
        new TableRow({children:[hC("异常场景",2340),hC("OpenClaw处理策略",3900),hC("兜底",3120)]}),
        new TableRow({children:[dC("图片审核驳回",2340,{bold:true}),dC("解析reject_reason → 群内告知商家具体原因 → 引导重新拍照 → 重新提交",3900),dC("3次驳回 → 转人工",3120)]}),
        new TableRow({children:[dC("商家72h未回复",2340,{bold:true,bg:C.light}),dC("间隔8h/24h/48h发3次提醒 → 第3次未回复则结束",3900,{bg:C.light}),dC("通知销售接管",3120,{bg:C.light})]}),
        new TableRow({children:[dC("银行卡未绑定",2340,{bold:true}),dC("群内发操作指引图 → 等待绑定 → 轮询检查",3900),dC("引导联系客服",3120)]}),
        new TableRow({children:[dC("接口超时",2340,{bold:true,bg:C.light}),dC("指数退避重试3次（1s→5s→30s）",3900,{bg:C.light}),dC("告警 → 人工排查",3120,{bg:C.light})]}),
        new TableRow({children:[dC("群内≥2个商家微信",2340,{bold:true}),dC("检测到多商家 → 暂停冷启 → 通知销售",3900),dC("发送接管通知模板",3120)]}),
        new TableRow({children:[dC("审核中商家要求修改",2340,{bold:true,bg:C.light}),dC("告知商家\"审核中，通过/驳回后再修改\" → 不做撤销",3900,{bg:C.light}),dC("—",3120,{bg:C.light})]}),
      ]}),

      h2("4.3 超时提醒策略（复用AIBD新签）"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1560,3900,3900], rows:[
        new TableRow({children:[hC("次数",1560),hC("时间",3900),hC("内容",3900)]}),
        new TableRow({children:[dC("第1次",1560,{bold:true}),dC("8小时未回复",3900),dC("温馨提醒：还差X步就能上线营业啦～",3900)]}),
        new TableRow({children:[dC("第2次",1560,{bold:true,bg:C.light}),dC("24小时未回复",3900,{bg:C.light}),dC("再次提醒：完成冷启后即可开始接单",3900,{bg:C.light})]}),
        new TableRow({children:[dC("第3次",1560,{bold:true}),dC("48小时未回复",3900),dC("最后提醒：如需帮助可随时回复",3900)]}),
        new TableRow({children:[dC("结束",1560,{bold:true,bg:C.light}),dC("72小时",3900,{bg:C.light}),dC("任务结束，通知销售人工跟进",3900,{bg:C.light})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 5. 接口清单 =====
      h1("5. 需要各方提供的接口清单"),

      h2("5.1 商家侧（门店装修）"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[600,2800,2400,1560,2000], rows:[
        new TableRow({children:[hC("#",600),hC("接口",2800),hC("用途",2400),hC("优先级",1560),hC("状态",2000)]}),
        new TableRow({children:[dC("1",600,{align:AlignmentType.CENTER}),dC("门头图/入口图提交",2800),dC("上传照片送审",2400),dC("P0",1560,{color:C.red,bold:true}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("2",600,{align:AlignmentType.CENTER,bg:C.light}),dC("照片审核状态查询",2800,{bg:C.light}),dC("轮询/回调审核结果",2400,{bg:C.light}),dC("P0",1560,{color:C.red,bold:true,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("3",600,{align:AlignmentType.CENTER}),dC("门店基础信息查询",2800),dC("查电话/营业时间/经营范围",2400),dC("P0",1560,{color:C.red,bold:true}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("4",600,{align:AlignmentType.CENTER,bg:C.light}),dC("图片裁剪服务",2800,{bg:C.light}),dC("自动裁剪到指定比例",2400,{bg:C.light}),dC("P1",1560,{color:C.orange,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("5",600,{align:AlignmentType.CENTER}),dC("审核结果回调",2800),dC("主动推送审核结果",2400),dC("P1",1560,{color:C.orange}),dC("待确认",2000,{color:C.orange})]}),
      ]}),

      h2("5.2 团购侧（上单）"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[600,2800,2400,1560,2000], rows:[
        new TableRow({children:[hC("#",600),hC("接口",2800),hC("用途",2400),hC("优先级",1560),hC("状态",2000)]}),
        new TableRow({children:[dC("1",600,{align:AlignmentType.CENTER}),dC("团单批量创建",2800),dC("AI生成的团单写入系统",2400),dC("P0",1560,{color:C.red,bold:true}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("2",600,{align:AlignmentType.CENTER,bg:C.light}),dC("团单送审",2800,{bg:C.light}),dC("提交审核",2400,{bg:C.light}),dC("P0",1560,{color:C.red,bold:true,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("3",600,{align:AlignmentType.CENTER}),dC("审核状态查询",2800),dC("轮询审核结果",2400),dC("P0",1560,{color:C.red,bold:true}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("4",600,{align:AlignmentType.CENTER,bg:C.light}),dC("门店团单列表查询",2800,{bg:C.light}),dC("检查已有团单数",2400,{bg:C.light}),dC("P0",1560,{color:C.red,bold:true,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("5",600,{align:AlignmentType.CENTER}),dC("银行卡绑定状态查询",2800),dC("上单前置检查",2400),dC("P0",1560,{color:C.red,bold:true}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("6",600,{align:AlignmentType.CENTER,bg:C.light}),dC("品类推荐团单模板",2800,{bg:C.light}),dC("AI参考生成团单",2400,{bg:C.light}),dC("P2",1560,{color:C.gray,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
      ]}),

      h2("5.3 活动侧"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[600,2800,2400,1560,2000], rows:[
        new TableRow({children:[hC("#",600),hC("接口",2800),hC("用途",2400),hC("优先级",1560),hC("状态",2000)]}),
        new TableRow({children:[dC("1",600,{align:AlignmentType.CENTER}),dC("可报名活动查询",2800),dC("查门店可参与的活动",2400),dC("P1",1560,{color:C.orange}),dC("待确认",2000,{color:C.orange})]}),
        new TableRow({children:[dC("2",600,{align:AlignmentType.CENTER,bg:C.light}),dC("活动报名提交",2800,{bg:C.light}),dC("提交报名",2400,{bg:C.light}),dC("P1",1560,{color:C.orange,bg:C.light}),dC("待确认",2000,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("3",600,{align:AlignmentType.CENTER}),dC("报名状态查询",2800),dC("跟踪报名结果",2400),dC("P1",1560,{color:C.orange}),dC("待确认",2000,{color:C.orange})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 6. OpenClaw配置 =====
      h1("6. OpenClaw技术配置"),

      h2("6.1 Session管理"),
      bl("每个商家的冷启动任务 = 一个独立的OpenClaw Session"),
      bl("Session label格式：cold-start:{shop_id}"),
      bl("Session超时：72小时无交互自动关闭"),
      bl("Session内可包含多个Skill的执行（装修→上单→活动顺序执行）"),

      h2("6.2 Skill注册"),
      ...code([
        "// decoration-skill",
        "{",
        "  name: \"decoration-skill\",",
        "  description: \"门店装修自动化：图片采集、校验、裁剪、提交送审\",",
        "  triggers: [\"COLD_START_DECORATION\"],",
        "  required_apis: [\"decoration/photo/submit\", \"shop/info\"],",
        "  timeout: 48h",
        "}",
        "",
        "// product-skill",
        "{",
        "  name: \"product-skill\",",
        "  description: \"团单上架自动化：信息采集、OCR、结构化、提交送审\",",
        "  triggers: [\"COLD_START_PRODUCT\"],",
        "  required_apis: [\"product/batch-create\", \"payment/bindcard-status\"],",
        "  timeout: 48h",
        "}",
      ]),

      h2("6.3 企微消息通道配置"),
      bl("OpenClaw通过企微Bot SDK接入企微群"),
      bl("消息监听：绑定wechat_group_id，监听商家消息"),
      bl("消息发送：支持文字、图片、小程序卡片"),
      bl("复用AIBD已有的企微Bot（王晓慧）身份"),

      h2("6.4 Cron任务"),
      bl("审核状态轮询：每30分钟查一次提交中的任务审核状态"),
      bl("超时提醒：每小时检查是否有商家超时未回复"),
      bl("每日汇总：每天18:00汇总当日冷启完成情况推送给BD"),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 7. 排期 =====
      h1("7. 分期规划与排期"),

      h2("7.1 分期"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1200,4380,3780], rows:[
        new TableRow({children:[hC("期次",1200),hC("范围",4380),hC("目标",3780)]}),
        new TableRow({children:[dC("一期",1200,{bold:true,color:C.red}),dC("门店装修（门头图+入口图）+ 上团单",4380),dC("10家试点 → 验证全流程",3780)]}),
        new TableRow({children:[dC("二期",1200,{bold:true,color:C.orange,bg:C.light}),dC("一期+活动报名+门店电话/营业时间",4380,{bg:C.light}),dC("100家扩量",3780,{bg:C.light})]}),
        new TableRow({children:[dC("三期",1200,{bold:true,color:C.green}),dC("全量冷启子项+AI生图+智能定价",4380),dC("全量上线",3780)]}),
      ]}),

      h2("7.2 一期排期（预估）"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[780,2800,2000,1560,2220], rows:[
        new TableRow({children:[hC("阶段",780),hC("任务",2800),hC("负责方",2000),hC("工期",1560),hC("产出",2220)]}),
        new TableRow({children:[dC("1",780,{align:AlignmentType.CENTER,bold:true}),dC("接口方案评审",2800),dC("产品+各业务方研发",2000),dC("2天",1560,{align:AlignmentType.CENTER}),dC("接口规范确认",2220)]}),
        new TableRow({children:[dC("2",780,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("商家侧装修接口开发",2800,{bg:C.light}),dC("商家侧研发",2000,{bg:C.light}),dC("5天",1560,{align:AlignmentType.CENTER,bg:C.light}),dC("装修API上线",2220,{bg:C.light})]}),
        new TableRow({children:[dC("3",780,{align:AlignmentType.CENTER,bold:true}),dC("团购侧上单接口开发",2800),dC("团购侧研发",2000),dC("5天",1560,{align:AlignmentType.CENTER}),dC("上单API上线",2220)]}),
        new TableRow({children:[dC("4",780,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("OpenClaw Skill开发",2800,{bg:C.light}),dC("AI产品+AIBD研发",2000,{bg:C.light}),dC("7天",1560,{align:AlignmentType.CENTER,bg:C.light}),dC("装修+上单Skill",2220,{bg:C.light})]}),
        new TableRow({children:[dC("5",780,{align:AlignmentType.CENTER,bold:true}),dC("AIBD→OpenClaw对接",2800),dC("AIBD研发",2000),dC("3天",1560,{align:AlignmentType.CENTER}),dC("A2A链路打通",2220)]}),
        new TableRow({children:[dC("6",780,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("联调+测试",2800,{bg:C.light}),dC("全员",2000,{bg:C.light}),dC("5天",1560,{align:AlignmentType.CENTER,bg:C.light}),dC("端到端验证",2220,{bg:C.light})]}),
        new TableRow({children:[dC("7",780,{align:AlignmentType.CENTER,bold:true}),dC("灰度试点",2800),dC("全员",2000),dC("7天",1560,{align:AlignmentType.CENTER}),dC("10家验证",2220)]}),
      ]}),
      p("总计预估：5-6周（含灰度验证）。阶段2/3可并行。",{bold:true,color:C.primary}),

      // ===== 8. 待确认 =====
      h1("8. 待确认事项"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[600,4080,2340,2340], rows:[
        new TableRow({children:[hC("#",600),hC("问题",4080),hC("建议",2340),hC("对接方",2340)]}),
        new TableRow({children:[dC("1",600,{align:AlignmentType.CENTER,bold:true}),dC("冷启事项来源：商家侧新手任务 or 销售侧考核？",4080),dC("优先对齐商家侧",2340),dC("业务方+商家侧",2340)]}),
        new TableRow({children:[dC("2",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("冷启状态是父子结构还是打平？",4080,{bg:C.light}),dC("建议父子（总状态+子项）",2340,{bg:C.light}),dC("商机侧",2340,{bg:C.light})]}),
        new TableRow({children:[dC("3",600,{align:AlignmentType.CENTER,bold:true}),dC("图片尺寸校验和裁剪谁做？",4080),dC("OpenClaw做裁剪，商家侧做合规审核",2340),dC("商家侧",2340)]}),
        new TableRow({children:[dC("4",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("OpenClaw复用王晓慧Bot还是新建Bot？",4080,{bg:C.light}),dC("复用，减少商家认知负担",2340,{bg:C.light}),dC("企微团队",2340,{bg:C.light})]}),
        new TableRow({children:[dC("5",600,{align:AlignmentType.CENTER,bold:true}),dC("活动报名是否纳入一期？",4080),dC("一期先不做，二期上",2340),dC("业务方",2340)]}),
        new TableRow({children:[dC("6",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("图片CDN上传Token获取方式？",4080,{bg:C.light}),dC("OpenClaw需要CDN上传权限",2340,{bg:C.light}),dC("基础架构",2340,{bg:C.light})]}),
        new TableRow({children:[dC("7",600,{align:AlignmentType.CENTER,bold:true}),dC("新签和冷启是同一场景还是拆分？",4080),dC("建议拆分，AIBD签约结束后交棒",2340),dC("AIBD+规划",2340)]}),
      ]}),

      new Paragraph({spacing:{before:400,after:100}, children:[new TextRun({text:"— END —",font:"Arial",size:24,bold:true,color:C.gray})]}),
    ]
  }]
});

Packer.toBuffer(doc).then(b=>{ const p='/root/.openclaw/workspace/AIBD冷启动_OpenClaw架构方案_v1.0.docx'; fs.writeFileSync(p,b); console.log('Saved: '+p); });
