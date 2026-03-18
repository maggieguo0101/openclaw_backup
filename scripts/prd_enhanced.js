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
    headers:{ default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT, children:[new TextRun({text:"PRD | AIBD新签场景-新店冷启动 技术详版 v2.0",font:"Arial",size:16,color:C.gray,italics:true})]})]}) },
    footers:{ default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:"机密文档 — 仅限内部使用  |  Page ",font:"Arial",size:16,color:C.gray}), new TextRun({children:[PageNumber.CURRENT],font:"Arial",size:16,color:C.gray})]})]}) },
    children:[
      // ===== 封面 =====
      new Paragraph({spacing:{before:1000,after:0},alignment:AlignmentType.CENTER, children:[new TextRun({text:"PRD | AIBD新签场景",font:"Arial",size:44,bold:true,color:C.primary})]}),
      new Paragraph({spacing:{before:80,after:0},alignment:AlignmentType.CENTER, children:[new TextRun({text:"新店冷启动（技术详版）",font:"Arial",size:36,color:C.accent})]}),
      new Paragraph({spacing:{before:80,after:200},alignment:AlignmentType.CENTER, children:[new TextRun({text:"在原PRD基础上补充技术实现细节，供研发评审",font:"Arial",size:22,color:C.gray})]}),

      new Table({ width:{size:60,type:WidthType.PERCENTAGE}, columnWidths:[2400,3600], rows:[
        new TableRow({children:[dC("文档版本",2400,{bold:true,bg:C.light}),dC("v2.0（技术增强版）",3600)]}),
        new TableRow({children:[dC("基线文档",2400,{bold:true,bg:C.light}),dC("KM collabpage/2748832550",3600)]}),
        new TableRow({children:[dC("编写日期",2400,{bold:true,bg:C.light}),dC("2026-03-10",3600)]}),
        new TableRow({children:[dC("产品负责人",2400,{bold:true,bg:C.light}),dC("郭磊平",3600)]}),
        new TableRow({children:[dC("状态",2400,{bold:true,bg:C.light}),dC("草稿 — 待评审",3600,{color:C.orange})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 1. 背景 =====
      h1("1. 背景（补充技术上下文）"),
      p("原PRD已详细描述业务背景，本节补充技术侧需要了解的上下文。"),

      h2("1.1 AIBD现有技术栈"),
      bl("规划-执行框架：基于LLM的意向识别 + 规则引擎的流程编排"),
      bl("触点：企微Bot（王晓慧身份），通过企微Open API收发消息"),
      bl("商机管理：salesmind平台，维护门店签约状态"),
      bl("场景下发：memdirectsign场景，规划侧控制门店是否进入AIBD作业"),

      h2("1.2 冷启动涉及的外部系统"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1870,2340,2340,2810], rows:[
        new TableRow({children:[hC("系统",1870),hC("负责方",2340),hC("冷启相关能力",2340),hC("对接方式",2810)]}),
        new TableRow({children:[dC("商家中心",1870,{bold:true}),dC("商家侧",2340),dC("门店装修（图片/信息）",2340),dC("需提供API（目前仅后台操作）",2810,{color:C.orange})]}),
        new TableRow({children:[dC("团购系统",1870,{bold:true,bg:C.light}),dC("供给侧",2340,{bg:C.light}),dC("团单CRUD+送审",2340,{bg:C.light}),dC("需提供API",2810,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("活动系统",1870,{bold:true}),dC("营销侧",2340),dC("神券活动报名",2340),dC("需提供API",2810,{color:C.orange})]}),
        new TableRow({children:[dC("支付系统",1870,{bold:true,bg:C.light}),dC("支付侧",2340,{bg:C.light}),dC("银行卡绑定状态",2340,{bg:C.light}),dC("需提供查询API",2810,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("企微Open API",1870,{bold:true}),dC("企微团队",2340),dC("群消息收发",2340),dC("已有，可复用",2810,{color:C.green})]}),
        new TableRow({children:[dC("salesmind",1870,{bold:true,bg:C.light}),dC("AIBD",2340,{bg:C.light}),dC("商机管理/状态展示",2340,{bg:C.light}),dC("已有，需扩展",2810,{color:C.green,bg:C.light})]}),
      ]}),

      h2("1.3 关键技术决策：A2A vs Agent+Tool"),
      p("原PRD提出两种方案。从技术实现角度补充分析：",{bold:true}),

      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2340,3510,3510], rows:[
        new TableRow({children:[hC("技术维度",2340),hC("A2A（推荐）",3510),hC("Agent+Tool",3510)]}),
        new TableRow({children:[dC("Context消耗",2340,{bold:true}),dC("每个子Skill独立Context，互不影响。AIBD仅维护路由逻辑~2K tokens",3510,{color:C.green}),dC("装修+上单+活动知识全塞一个Context，保守估计30K+ tokens，容易溢出",3510,{color:C.red})]}),
        new TableRow({children:[dC("Prompt工程",2340,{bold:true,bg:C.light}),dC("各Skill独立优化Prompt，互不干扰",3510,{color:C.green,bg:C.light}),dC("一个超长Prompt管所有场景，调一个影响全部",3510,{color:C.red,bg:C.light})]}),
        new TableRow({children:[dC("错误隔离",2340,{bold:true}),dC("装修Skill挂了不影响上单Skill",3510,{color:C.green}),dC("一个接口报错可能导致整个对话Context被污染",3510,{color:C.red})]}),
        new TableRow({children:[dC("可观测性",2340,{bold:true,bg:C.light}),dC("每个Skill独立日志链路，易排查",3510,{color:C.green,bg:C.light}),dC("日志混在一起，难区分哪个环节出问题",3510,{color:C.red,bg:C.light})]}),
        new TableRow({children:[dC("版本迭代",2340,{bold:true}),dC("各Skill独立发版，商家侧改接口只影响对应Skill",3510,{color:C.green}),dC("任何接口变更都需要AIBD整体发版",3510,{color:C.red})]}),
        new TableRow({children:[dC("Latency",2340,{bold:true,bg:C.light}),dC("多一次Agent调度~500ms",3510,{color:C.orange,bg:C.light}),dC("直接调API，少一跳",3510,{color:C.green,bg:C.light})]}),
      ]}),

      p("结论：A2A在可维护性、可扩展性、错误隔离上显著优于Agent+Tool。Latency增加的500ms对企微群异步交互场景可忽略。推荐A2A。",{bold:true,color:C.primary}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 2. 方案详情：门店装修 =====
      h1("2. 门店装修 — 技术方案详述"),

      h2("2.1 一期范围"),
      p("一期聚焦门头图+入口图的采集和提交。门店电话、营业时间等简单字段AI暂不涉及（商家自助完成或销售操作）。",{bold:true}),

      h2("2.2 Agent to API方案（一期推荐）"),
      h3("2.2.1 完整流程"),
      nl("AIBD签约完成 → 推送冷启任务消息（含shop_id、企微群ID）"),
      nl("冷启Agent查询门店当前装修状态 → 确定缺项"),
      nl("企微群发开场白（基于缺项定制化生成）"),
      nl("商家在企微群发送图片"),
      nl("Agent接收图片 → 调用图片分类模型（门头图 or 入口图 or 其他）"),
      nl("图片质量校验："),
      bl("分辨率检查（≥720×540）",1),
      bl("模糊检测（拉普拉斯方差阈值）",1),
      bl("内容检测（是否为门头/店面，排除截图/表情包）",1),
      nl("校验通过 → 图片裁剪（门头图16:9 / 入口图1:1）"),
      nl("上传CDN → 获取URL"),
      nl("调用商家侧提交接口 → 送审"),
      nl("轮询审核状态（每30分钟）或等回调"),
      nl("审核通过 → 群内通知商家"),
      nl("审核驳回 → 解析reject_reason → 群内发具体修改指引 → 回到步骤4"),

      h3("2.2.2 商家侧需提供的接口"),
      p("接口1：门头图/入口图提交",{bold:true,color:C.accent}),
      ...code(["POST /api/v1/shop/decoration/photo/submit"]),
      apiT([
        ["shop_id","string","是","门店ID"],
        ["photo_type","enum","是","HEADER_PHOTO / ENTRANCE_PHOTO"],
        ["photo_urls","array[string]","是","图片CDN URL列表。门头图1-6张，入口图1张"],
        ["operator_type","enum","是","HUMAN / AI（标记来源，审核可区分）"],
        ["operator_id","string","是","操作人标识"],
        ["request_id","string","是","幂等键"],
      ]),
      p("响应：",{bold:true}),
      apiT([
        ["code","int","是","0=成功"],
        ["data.submission_id","string","是","提交ID，用于查询审核状态"],
        ["data.status","enum","是","PENDING / REJECTED（即时校验失败时）"],
        ["data.reject_reason","string","否","即时驳回原因（如格式不对）"],
      ]),

      p("接口2：审核状态查询",{bold:true,color:C.accent}),
      ...code(["GET /api/v1/shop/decoration/photo/status?submission_id={id}"]),
      apiT([
        ["code","int","是","0=成功"],
        ["data.status","enum","是","PENDING / REVIEWING / APPROVED / REJECTED"],
        ["data.reject_reason","string","否","驳回原因"],
        ["data.reject_details","array","否","[{photo_url, reason}] 具体哪张图被驳回及原因"],
        ["data.updated_at","string","是","最后更新时间"],
      ]),

      p("接口3：门店装修信息查询",{bold:true,color:C.accent}),
      ...code(["GET /api/v1/shop/info?shop_id={id}&fields=phone,hours,photos,scope"]),
      apiT([
        ["code","int","是","0=成功"],
        ["data.header_photo_count","int","是","当前门头图数量"],
        ["data.entrance_photo_count","int","是","当前入口图数量"],
        ["data.phone","string","否","门店电话（空=未设置）"],
        ["data.business_hours","string","否","营业时间（空=未设置）"],
        ["data.biz_scope","string","否","经营范围（空=未设置）"],
        ["data.bank_bindingbind","bool","是","银行卡是否已绑定"],
      ]),

      h3("2.2.3 图片处理技术方案"),
      p("图片处理由AIBD侧/AI Agent侧完成，不依赖商家侧："),

      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2340,3510,3510], rows:[
        new TableRow({children:[hC("处理环节",2340),hC("技术方案",3510),hC("说明",3510)]}),
        new TableRow({children:[dC("图片分类",2340,{bold:true}),dC("多模态LLM识别（门头图/入口图/其他）",3510),dC("Prompt：判断图片是否为店铺门头/入口",3510)]}),
        new TableRow({children:[dC("质量校验",2340,{bold:true,bg:C.light}),dC("OpenCV: 分辨率检查 + 拉普拉斯模糊检测",3510,{bg:C.light}),dC("threshold=100，低于100判定为模糊",3510,{bg:C.light})]}),
        new TableRow({children:[dC("裁剪",2340,{bold:true}),dC("Pillow/OpenCV: 智能裁剪到目标比例",3510),dC("门头图16:9，入口图1:1，中心裁剪",3510)]}),
        new TableRow({children:[dC("CDN上传",2340,{bold:true,bg:C.light}),dC("调用公司CDN上传接口",3510,{bg:C.light}),dC("需获取上传Token（待确认接入方式）",3510,{bg:C.light})]}),
        new TableRow({children:[dC("AI生图（P2）",2340,{bold:true}),dC("文生图API（商家无合适照片时）",3510),dC("基于品类+地址生成虚拟门头图",3510)]}),
      ]}),

      h3("2.2.4 边界情况处理"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[3120,3120,3120], rows:[
        new TableRow({children:[hC("边界情况",3120),hC("处理策略",3120),hC("技术实现",3120)]}),
        new TableRow({children:[dC("商家发了非图片消息",3120),dC("友好提示需要发送图片",3120),dC("企微消息类型判断",3120)]}),
        new TableRow({children:[dC("图片太小/模糊",3120,{bg:C.light}),dC("提示重新拍摄，给拍照建议",3120,{bg:C.light}),dC("分辨率+拉普拉斯检测",3120,{bg:C.light})]}),
        new TableRow({children:[dC("图片不是门店（风景/自拍等）",3120),dC("提示需要店铺照片",3120),dC("多模态LLM内容识别",3120)]}),
        new TableRow({children:[dC("审核中商家要求换图",3120,{bg:C.light}),dC("告知审核中，审核完再操作",3120,{bg:C.light}),dC("状态机控制，REVIEWING状态不接受新图",3120,{bg:C.light})]}),
        new TableRow({children:[dC("审核驳回3次",3120),dC("通知销售人工介入",3120),dC("驳回计数器，>=3触发转人工",3120)]}),
        new TableRow({children:[dC("商家发了多张图混在一起",3120,{bg:C.light}),dC("逐张处理+分类",3120,{bg:C.light}),dC("遍历消息中所有图片附件",3120,{bg:C.light})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 3. 上单 =====
      h1("3. 门店上团单 — 技术方案详述"),

      h2("3.1 前置依赖"),
      p("上团单前必须满足以下条件，Agent需先检查：",{bold:true}),
      nl("银行卡已绑定（调用支付侧接口查询）—— 阻塞项，未绑定则引导绑卡"),
      nl("门店基础信息已完善（电话/营业时间）—— 非阻塞，但影响审核通过率"),

      h2("3.2 Agent to API方案"),
      h3("3.2.1 流程"),
      nl("检查前置条件（银行卡绑定+基础信息）"),
      nl("企微群询问商家提供菜单/团单信息（支持多种输入）"),
      bl("图片：菜单照片 → OCR识别 → 结构化提取",1),
      bl("文字：商家直接发\"羊肉串5块一串\" → NLU提取",1),
      bl("Excel/文件：解析表格数据",1),
      nl("AI结构化处理：提取品名、价格、规格、分类"),
      nl("AI补充：自动生成商品描述、推荐分类标签"),
      nl("企微群发确认清单（表格形式）→ 商家确认/修改"),
      nl("调用团购侧批量创建接口"),
      nl("调用送审接口"),
      nl("轮询审核/等回调"),
      nl("审核通过 → 商品上架 → 通知商家"),
      nl("审核驳回 → 解析原因 → 修正 → 重提"),

      h3("3.2.2 团购侧需提供的接口"),
      p("接口1：团单批量创建",{bold:true,color:C.accent}),
      ...code(["POST /api/v1/product/batch-create"]),
      apiT([
        ["shop_id","string","是","门店ID"],
        ["operator_type","enum","是","HUMAN / AI"],
        ["operator_id","string","是","操作人标识"],
        ["request_id","string","是","幂等键"],
        ["products","array[object]","是","团单列表，单次≤50个"],
      ]),
      p("products数组每个元素：",{bold:true}),
      apiT([
        ["name","string","是","团单名称（≤30字）"],
        ["category_id","string","是","团单分类ID（商家中心分类体系）"],
        ["price","number","是","售价（分），整数"],
        ["original_price","number","否","原价（分）"],
        ["description","string","否","描述（≤200字）"],
        ["image_urls","array[string]","否","图片URL列表"],
        ["specs","array[object]","否","规格列表：[{spec_name,spec_price,spec_desc}]"],
        ["use_rules","object","否","使用规则：{valid_days, use_time, need_appointment, max_per_order}"],
        ["tags","array[string]","否","标签：[\"招牌\",\"必点\"]"],
      ]),

      p("接口2：团单送审",{bold:true,color:C.accent}),
      ...code(["POST /api/v1/product/submit-review"]),
      apiT([
        ["shop_id","string","是","门店ID"],
        ["product_ids","array[string]","是","要送审的团单ID列表"],
        ["request_id","string","是","幂等键"],
      ]),

      p("接口3：审核状态查询",{bold:true,color:C.accent}),
      ...code(["GET /api/v1/product/review-status?shop_id={id}&submission_id={id}"]),
      apiT([
        ["code","int","是","0=成功"],
        ["data.status","enum","是","PENDING/REVIEWING/APPROVED/PARTIAL_REJECTED/ALL_REJECTED"],
        ["data.details","array","是","每个团单审核结果：[{product_id, name, status, reject_reason}]"],
      ]),

      p("接口4：门店已有团单查询",{bold:true,color:C.accent}),
      ...code(["GET /api/v1/product/list?shop_id={id}"]),
      apiT([
        ["code","int","是","0=成功"],
        ["data.total","int","是","团单总数"],
        ["data.products","array","是","[{product_id, name, price, status}]"],
      ]),

      p("接口5：银行卡绑定状态",{bold:true,color:C.accent}),
      ...code(["GET /api/v1/payment/bindcard-status?shop_id={id}"]),
      apiT([
        ["code","int","是","0=成功"],
        ["data.bindingbound","bool","是","是否已绑定"],
        ["data.bindingbound_at","string","否","绑定时间"],
      ]),

      h3("3.2.3 OCR与信息提取技术方案"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[2340,3900,3120], rows:[
        new TableRow({children:[hC("输入类型",2340),hC("处理方案",3900),hC("输出",3120)]}),
        new TableRow({children:[dC("菜单照片",2340,{bold:true}),dC("多模态LLM: 发送图片+Prompt\"从菜单中提取菜品名称、价格、描述\"",3900),dC("JSON数组[{name,price,desc}]",3120)]}),
        new TableRow({children:[dC("文字消息",2340,{bold:true,bg:C.light}),dC("LLM NLU: \"羊肉串5块串\" → 结构化提取",3900,{bg:C.light}),dC("JSON数组",3120,{bg:C.light})]}),
        new TableRow({children:[dC("Excel/CSV",2340,{bold:true}),dC("pandas读取 → 列名映射 → JSON转换",3900),dC("JSON数组",3120)]}),
        new TableRow({children:[dC("语音消息",2340,{bold:true,bg:C.light}),dC("Whisper STT → LLM NLU",3900,{bg:C.light}),dC("JSON数组",3120,{bg:C.light})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 4. 活动报名 =====
      h1("4. 活动报名 — 技术方案概要"),
      p("一期建议暂不纳入，原因：",{bold:true}),
      bl("活动报名相对简单（查询可报名活动 → 介绍 → 报名），销售签约时可直接搞定"),
      bl("涉及营销侧系统对接，增加一期复杂度"),
      bl("建议二期上线，一期优先保障装修+上单的质量"),

      p("如需一期纳入，所需接口见下表：",{it:true,color:C.gray}),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[3120,3120,3120], rows:[
        new TableRow({children:[hC("接口",3120),hC("用途",3120),hC("入参核心字段",3120)]}),
        new TableRow({children:[dC("GET /activity/available",3120),dC("查询可报名活动",3120),dC("shop_id → 活动列表",3120)]}),
        new TableRow({children:[dC("POST /activity/enroll",3120,{bg:C.light}),dC("提交报名",3120,{bg:C.light}),dC("shop_id, activity_id",3120,{bg:C.light})]}),
        new TableRow({children:[dC("GET /activity/enroll-status",3120),dC("查报名结果",3120),dC("enrollment_id → 状态",3120)]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 5. 场景下发与规划 =====
      h1("5. 场景下发与规划侧调整"),

      h2("5.1 下发规则调整"),
      p("原规则：仅支持免费开店宝门店通过memdirectsign场景下发",{bold:true}),
      p("新规则：免费开店宝 + 付费商户通 均可通过memdirectsign下发",{bold:true,color:C.green}),
      bl("去掉\"门店仅支持开店宝\"的限制校验"),
      bl("付费商户通门店前置条件：企微群已建立 + 王晓慧为群主"),

      h2("5.2 规划侧调整"),
      p("原规则：门店已签约 → 任务结束",{bold:true}),
      p("新规则：门店冷启完成 → 任务结束",{bold:true,color:C.green}),
      bl("规划侧新增阶段：SIGNED → COLD_STARTING → COLD_START_DONE"),
      bl("规划只判断冷启是否完成（父状态），不拆解到子项粒度"),
      bl("子项粒度由冷启Agent内部管理，向规划回报父状态"),

      h2("5.3 salesmind页面调整"),
      bl("批次列表新增冷启列：显示冷启状态（已完成/进行中/超时）"),
      bl("点击可展开子项状态（门头图✅ / 入口图⏳ / 上单❌ / 活动—）"),
      bl("需确认：子项是显示到最细粒度（门头图/入口图），还是聚合为\"门店装修\""),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 6. 兜底策略 =====
      h1("6. 兜底策略 — 技术实现"),

      h2("6.1 多商家检测"),
      p("若企微群内有≥2个商家个人微信（非王晓慧、非AIBD），则暂停冷启，通知销售接管。",{bold:true}),

      h3("检测方式"),
      bl("调用企微API获取群成员列表"),
      bl("排除：Bot账号（王晓慧）、内部员工（销售mis标识）"),
      bl("剩余成员数≥2 → 判定为多商家群"),

      h3("接管通知模板"),
      ...code([
        "【接管通知】",
        "商家名称：{shop_name}（点评ID：{dp_shop_id}）",
        "当前企微群内商户人数已超过2人，王晓慧无法进行新店冷启。",
        "请搜索商户名称至企微群内完成后续沟通。",
        "",
        "商户签约信息：",
        "- 意向分数：{intent_score}",
        "- 意向分层：{intent_degree}",
        "- 接触意愿：{contact_willingness}",
        "- 营业执照：{has_license}",
      ]),

      h2("6.2 超时策略"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1560,1560,3120,3120], rows:[
        new TableRow({children:[hC("提醒次数",1560),hC("触发时间",1560),hC("消息内容",3120),hC("技术实现",3120)]}),
        new TableRow({children:[dC("第1次",1560,{bold:true}),dC("8h未回复",1560),dC("温馨提醒 + 剩余待完成项",3120),dC("Cron定时检查last_reply_at",3120)]}),
        new TableRow({children:[dC("第2次",1560,{bold:true,bg:C.light}),dC("24h",1560,{bg:C.light}),dC("再次提醒 + 操作指引",3120,{bg:C.light}),dC("同上",3120,{bg:C.light})]}),
        new TableRow({children:[dC("第3次",1560,{bold:true}),dC("48h",1560),dC("最后提醒",3120),dC("同上",3120)]}),
        new TableRow({children:[dC("结束",1560,{bold:true,bg:C.light}),dC("72h",1560,{bg:C.light}),dC("任务关闭，通知销售",3120,{bg:C.light}),dC("更新商机状态TIMEOUT",3120,{bg:C.light})]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 7. 冷启状态模型 =====
      h1("7. 冷启动状态模型"),

      h2("7.1 状态层级设计（推荐：父子结构）"),
      p("采用两级状态：父状态（冷启整体）+ 子状态（每个子项）。规划侧只看父状态，冷启Agent管理子状态。",{bold:true}),

      h3("父状态流转"),
      ...code([
        "NOT_STARTED → IN_PROGRESS → COMPLETED",
        "                   │",
        "                   ├── TIMEOUT (72h无交互)",
        "                   └── NEED_HUMAN (多商家/3次驳回)",
      ]),

      h3("子状态流转"),
      ...code([
        "NOT_DONE → COLLECTING → SUBMITTED → REVIEWING → APPROVED",
        "              │                          │",
        "              └── VALIDATION_FAILED       └── REJECTED",
        "                     │                          │",
        "                     └───── COLLECTING ◄─────────┘",
      ]),

      h3("父状态判定规则"),
      bl("COMPLETED：所有必选子项状态=APPROVED/DONE"),
      bl("IN_PROGRESS：至少一个子项状态!=NOT_DONE 且 未全部完成"),
      bl("TIMEOUT：最后交互时间距今>72h"),
      bl("NEED_HUMAN：触发兜底策略（多商家/3次驳回）"),

      h2("7.2 子项达标条件"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1870,1870,2340,1560,1720], rows:[
        new TableRow({children:[hC("子项",1870),hC("达标条件",1870),hC("查询方式",2340),hC("一期",1560),hC("判定方",1720)]}),
        new TableRow({children:[dC("门头图",1870,{bold:true}),dC("≥3张已审核通过",1870),dC("商家侧/photo/status",2340),dC("✅ 做",1560,{color:C.green}),dC("外部接口",1720)]}),
        new TableRow({children:[dC("入口图",1870,{bold:true,bg:C.light}),dC("=1张已审核通过",1870,{bg:C.light}),dC("商家侧/photo/status",2340,{bg:C.light}),dC("✅ 做",1560,{color:C.green,bg:C.light}),dC("外部接口",1720,{bg:C.light})]}),
        new TableRow({children:[dC("门店电话",1870,{bold:true}),dC("有值",1870),dC("商家侧/shop/info",2340),dC("❌ 不做",1560,{color:C.gray}),dC("外部接口",1720)]}),
        new TableRow({children:[dC("营业时间",1870,{bold:true,bg:C.light}),dC("有值",1870,{bg:C.light}),dC("商家侧/shop/info",2340,{bg:C.light}),dC("❌ 不做",1560,{color:C.gray,bg:C.light}),dC("外部接口",1720,{bg:C.light})]}),
        new TableRow({children:[dC("银行卡",1870,{bold:true}),dC("已绑定",1870),dC("支付侧/bindcard-status",2340),dC("✅ 检查",1560,{color:C.green}),dC("外部接口",1720)]}),
        new TableRow({children:[dC("上团单",1870,{bold:true,bg:C.light}),dC("≥3个已审核通过",1870,{bg:C.light}),dC("团购侧/product/list",2340,{bg:C.light}),dC("✅ 做",1560,{color:C.green,bg:C.light}),dC("外部接口",1720,{bg:C.light})]}),
        new TableRow({children:[dC("神券报名",1870,{bold:true}),dC("已报名生效",1870),dC("活动侧/enroll-status",2340),dC("❌ 二期",1560,{color:C.gray}),dC("外部接口",1720)]}),
      ]}),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 8. 错误码与监控 =====
      h1("8. 错误码规范与监控"),

      h2("8.1 统一错误码"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[1200,3600,4560], rows:[
        new TableRow({children:[hC("错误码",1200),hC("含义",3600),hC("AIBD/Agent处理",4560)]}),
        new TableRow({children:[dC("0",1200,{bold:true,color:C.green}),dC("成功",3600),dC("—",4560)]}),
        new TableRow({children:[dC("1001",1200,{bold:true,color:C.red,bg:C.light}),dC("参数校验失败",3600,{bg:C.light}),dC("检查必填字段 → 修正 → 重试",4560,{bg:C.light})]}),
        new TableRow({children:[dC("1002",1200,{bold:true,color:C.red}),dC("shop_id不存在/未签约",3600),dC("确认AIBD签约状态",4560)]}),
        new TableRow({children:[dC("1003",1200,{bold:true,color:C.red,bg:C.light}),dC("幂等命中（重复提交）",3600,{bg:C.light}),dC("返回上次结果",4560,{bg:C.light})]}),
        new TableRow({children:[dC("1004",1200,{bold:true,color:C.red}),dC("图片URL不可访问",3600),dC("检查CDN链接 → 重新上传",4560)]}),
        new TableRow({children:[dC("1005",1200,{bold:true,color:C.red,bg:C.light}),dC("超出数量限制",3600,{bg:C.light}),dC("分批提交",4560,{bg:C.light})]}),
        new TableRow({children:[dC("2001",1200,{bold:true,color:C.red}),dC("银行卡未绑定",3600),dC("引导商家绑卡",4560)]}),
        new TableRow({children:[dC("5000",1200,{bold:true,color:C.red,bg:C.light}),dC("系统内部错误",3600,{bg:C.light}),dC("指数退避重试3次 → 告警",4560,{bg:C.light})]}),
        new TableRow({children:[dC("5001",1200,{bold:true,color:C.red}),dC("限流",3600),dC("退避重试",4560)]}),
      ]}),

      h2("8.2 监控指标"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[3120,3120,3120], rows:[
        new TableRow({children:[hC("指标",3120),hC("目标值",3120),hC("告警阈值",3120)]}),
        new TableRow({children:[dC("接口成功率",3120,{bold:true}),dC("≥99%",3120),dC("<95%触发告警",3120,{color:C.red})]}),
        new TableRow({children:[dC("P99响应时间",3120,{bold:true,bg:C.light}),dC("<500ms",3120,{bg:C.light}),dC(">2s触发告警",3120,{color:C.red,bg:C.light})]}),
        new TableRow({children:[dC("审核通过率（AI提交）",3120,{bold:true}),dC("≥80%",3120),dC("<60%需排查Prompt/校验逻辑",3120,{color:C.orange})]}),
        new TableRow({children:[dC("冷启完成率（72h内）",3120,{bold:true,bg:C.light}),dC("≥70%",3120,{bg:C.light}),dC("<50%需分析流失环节",3120,{color:C.orange,bg:C.light})]}),
        new TableRow({children:[dC("平均冷启耗时",3120,{bold:true}),dC("<24h",3120),dC(">48h需优化流程",3120,{color:C.orange})]}),
      ]}),

      h2("8.3 日志规范"),
      bl("每次API调用记录：request_id, shop_id, operator_id, operator_type(AI/HUMAN), 请求参数, 响应结果, 耗时"),
      bl("AI提交的所有内容打标\"AI_GENERATED\"，审核界面可筛选"),
      bl("企微对话日志保留（脱敏后），用于Prompt优化分析"),

      new Paragraph({children:[new PageBreak()]}),

      // ===== 9. 排期 =====
      h1("9. 一期排期建议"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[780,3200,2200,1200,2000], rows:[
        new TableRow({children:[hC("周",780),hC("任务",3200),hC("负责方",2200),hC("人日",1200),hC("产出",2000)]}),
        new TableRow({children:[dC("W1",780,{bold:true}),dC("接口规范评审+确认",3200),dC("产品+各方研发",2200),dC("2",1200,{align:AlignmentType.CENTER}),dC("接口Contract",2000)]}),
        new TableRow({children:[dC("W1-W2",780,{bold:true,bg:C.light}),dC("商家侧装修API开发",3200,{bg:C.light}),dC("商家侧",2200,{bg:C.light}),dC("5",1200,{align:AlignmentType.CENTER,bg:C.light}),dC("装修API",2000,{bg:C.light})]}),
        new TableRow({children:[dC("W1-W2",780,{bold:true}),dC("团购侧上单API开发（并行）",3200),dC("团购侧",2200),dC("5",1200,{align:AlignmentType.CENTER}),dC("上单API",2000)]}),
        new TableRow({children:[dC("W2-W3",780,{bold:true,bg:C.light}),dC("AIBD冷启场景+A2A对接",3200,{bg:C.light}),dC("AIBD研发",2200,{bg:C.light}),dC("5",1200,{align:AlignmentType.CENTER,bg:C.light}),dC("A2A链路",2000,{bg:C.light})]}),
        new TableRow({children:[dC("W2-W3",780,{bold:true}),dC("冷启Agent/Skill开发（并行）",3200),dC("AI产品+研发",2200),dC("7",1200,{align:AlignmentType.CENTER}),dC("装修+上单Skill",2000)]}),
        new TableRow({children:[dC("W3",780,{bold:true,bg:C.light}),dC("salesmind页面+规划调整",3200,{bg:C.light}),dC("前端+规划",2200,{bg:C.light}),dC("3",1200,{align:AlignmentType.CENTER,bg:C.light}),dC("页面+规则",2000,{bg:C.light})]}),
        new TableRow({children:[dC("W4",780,{bold:true}),dC("联调+测试",3200),dC("全员",2200),dC("5",1200,{align:AlignmentType.CENTER}),dC("端到端验证",2000)]}),
        new TableRow({children:[dC("W5",780,{bold:true,bg:C.light}),dC("灰度试点（10家）",3200,{bg:C.light}),dC("全员",2200,{bg:C.light}),dC("5",1200,{align:AlignmentType.CENTER,bg:C.light}),dC("效果验证",2000,{bg:C.light})]}),
      ]}),
      p("总计：5周，关键路径在商家侧+团购侧API开发。W1-W2并行可压缩至4周。",{bold:true,color:C.primary}),

      // ===== 10. 待确认 =====
      h1("10. 待确认事项汇总"),
      new Table({ width:{size:100,type:WidthType.PERCENTAGE}, columnWidths:[600,3600,2400,2760], rows:[
        new TableRow({children:[hC("#",600),hC("问题",3600),hC("建议",2400),hC("Owner",2760)]}),
        new TableRow({children:[dC("1",600,{align:AlignmentType.CENTER,bold:true}),dC("冷启事项来源（商家新手任务 vs 销售考核）及变动频次",3600),dC("对齐商家侧为主",2400),dC("业务方+商家侧",2760)]}),
        new TableRow({children:[dC("2",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("商家侧各接口是否已有或需新建",3600,{bg:C.light}),dC("需商家侧排查确认",2400,{bg:C.light}),dC("商家侧研发",2760,{bg:C.light})]}),
        new TableRow({children:[dC("3",600,{align:AlignmentType.CENTER,bold:true}),dC("团购侧批量创建+送审接口是否已有",3600),dC("需团购侧确认",2400),dC("团购侧研发",2760)]}),
        new TableRow({children:[dC("4",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("图片CDN上传权限获取方式",3600,{bg:C.light}),dC("申请上传Token",2400,{bg:C.light}),dC("基础架构",2760,{bg:C.light})]}),
        new TableRow({children:[dC("5",600,{align:AlignmentType.CENTER,bold:true}),dC("图片裁剪能力：商家侧提供 or Agent侧处理",3600),dC("Agent做裁剪，商家侧做审核",2400),dC("商家侧",2760)]}),
        new TableRow({children:[dC("6",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("审核接口是否支持回调（减少轮询）",3600,{bg:C.light}),dC("优先回调，fallback轮询",2400,{bg:C.light}),dC("各方研发",2760,{bg:C.light})]}),
        new TableRow({children:[dC("7",600,{align:AlignmentType.CENTER,bold:true}),dC("salesmind冷启子项展示粒度（门头图/入口图 vs 门店装修）",3600),dC("建议展示到最细粒度",2400),dC("AIBD前端",2760)]}),
        new TableRow({children:[dC("8",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("活动报名是否纳入一期",3600,{bg:C.light}),dC("建议二期",2400,{bg:C.light}),dC("业务方",2760,{bg:C.light})]}),
        new TableRow({children:[dC("9",600,{align:AlignmentType.CENTER,bold:true}),dC("王晓慧Bot复用还是新建冷启专用Bot",3600),dC("复用，减少商家认知切换",2400),dC("企微团队",2760)]}),
        new TableRow({children:[dC("10",600,{align:AlignmentType.CENTER,bold:true,bg:C.light}),dC("付费商户通门店冷启是否和免费开店宝走同一套流程",3600,{bg:C.light}),dC("统一流程，按门店类型差异化配置",2400,{bg:C.light}),dC("业务方",2760,{bg:C.light})]}),
      ]}),

      new Paragraph({spacing:{before:400,after:100}, children:[new TextRun({text:"— END —",font:"Arial",size:24,bold:true,color:C.gray})]}),
    ]
  }]
});

Packer.toBuffer(doc).then(b=>{ const path='/root/.openclaw/workspace/AIBD冷启动_技术详版PRD_v2.0.docx'; fs.writeFileSync(path,b); console.log('Saved: '+path); });
