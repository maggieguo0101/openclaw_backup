const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');

// ===== 样式 =====
const C = {
  primary: "1A3A5C",
  accent: "2E86AB",
  green: "28A745",
  red: "DC3545",
  orange: "FD7E14",
  gray: "6C757D",
  lightGray: "F2F7FB",
  white: "FFFFFF",
  black: "222222",
};

const border = { style: BorderStyle.SINGLE, size: 1, color: "DEE2E6" };
const borders = { top: border, bottom: border, left: border, right: border };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };

function hCell(text, w) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: { fill: C.primary, type: ShadingType.CLEAR }, margins: cm,
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, font: "Arial", size: 20, color: C.white })] })]
  });
}
function dCell(text, w, opts = {}) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined, margins: cm,
    verticalAlign: opts.valign || undefined,
    children: Array.isArray(text) ? text : [new Paragraph({ alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), font: "Arial", size: 20,
        color: opts.color || C.black, bold: opts.bold || false })] })]
  });
}
function mCell(paragraphs, w, opts = {}) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined, margins: cm,
    children: paragraphs
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 },
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: C.primary })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 300, after: 160 },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: C.accent })] });
}
function h3(text) {
  return new Paragraph({ spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: C.primary })] });
}
function p(text, opts = {}) {
  return new Paragraph({ spacing: { after: opts.after || 100 }, indent: opts.indent ? { left: opts.indent } : undefined,
    children: [new TextRun({ text, font: "Arial", size: 20, color: opts.color || C.black, bold: opts.bold || false, italics: opts.italics || false })] });
}
function bullet(text, level = 0) {
  return new Paragraph({ numbering: { reference: "bullets", level }, spacing: { after: 60 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: C.black })] });
}
function numItem(text, level = 0) {
  return new Paragraph({ numbering: { reference: "numbers", level }, spacing: { after: 60 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: C.black })] });
}
function divider() {
  return new Paragraph({ spacing: { before: 100, after: 100 },
    children: [new TextRun({ text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font: "Arial", size: 16, color: C.accent })] });
}

// ===== API字段表 =====
function apiTable(fields) {
  const colW = [2200, 1400, 1000, 4760];
  const rows = [
    new TableRow({ children: [hCell("字段名", colW[0]), hCell("类型", colW[1]), hCell("必填", colW[2]), hCell("说明", colW[3])] }),
  ];
  fields.forEach((f, i) => {
    const bg = i % 2 === 1 ? C.lightGray : undefined;
    rows.push(new TableRow({ children: [
      dCell(f[0], colW[0], { bold: true, bg }),
      dCell(f[1], colW[1], { align: AlignmentType.CENTER, bg }),
      dCell(f[2], colW[2], { align: AlignmentType.CENTER, color: f[2]==="是" ? C.red : C.gray, bg }),
      dCell(f[3], colW[3], { bg }),
    ] }));
  });
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, columnWidths: colW, rows });
}

// ===== JSON示例块 =====
function jsonBlock(obj) {
  const lines = JSON.stringify(obj, null, 2).split('\n');
  return lines.map(line => new Paragraph({
    spacing: { after: 0 },
    shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
    indent: { left: 360 },
    children: [new TextRun({ text: line, font: "Courier New", size: 18, color: "333333" })]
  }));
}

// ===== 文档主体 =====
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: C.primary },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.accent },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
        ] },
      { reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.DECIMAL, text: "%2)", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
        ] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1200, right: 1200, bottom: 1200, left: 1200 }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "OpenClaw × AIBD 商家装修上单自动化 | 接口需求文档 v1.0", font: "Arial", size: 16, color: C.gray, italics: true })] })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "机密文档 — 仅限内部使用  |  Page ", font: "Arial", size: 16, color: C.gray }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: C.gray })
        ] })] })
    },
    children: [
      // ===== 封面 =====
      new Paragraph({ spacing: { before: 1200, after: 0 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "接口需求文档", font: "Arial", size: 52, bold: true, color: C.primary })] }),
      new Paragraph({ spacing: { before: 200, after: 0 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "OpenClaw × AIBD", font: "Arial", size: 36, color: C.accent })] }),
      new Paragraph({ spacing: { before: 100, after: 0 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "商家装修 & 上单自动化提交接口", font: "Arial", size: 28, color: C.gray })] }),
      divider(),

      new Table({
        width: { size: 60, type: WidthType.PERCENTAGE },
        columnWidths: [2400, 3600],
        rows: [
          new TableRow({ children: [dCell("文档版本", 2400, { bold: true, bg: C.lightGray }), dCell("v1.0", 3600)] }),
          new TableRow({ children: [dCell("编写日期", 2400, { bold: true, bg: C.lightGray }), dCell("2026-03-10", 3600)] }),
          new TableRow({ children: [dCell("产品负责人", 2400, { bold: true, bg: C.lightGray }), dCell("郭磊平", 3600)] }),
          new TableRow({ children: [dCell("需求状态", 2400, { bold: true, bg: C.lightGray }), dCell("草稿 — 待评审", 3600, { color: C.orange })] }),
          new TableRow({ children: [dCell("优先级", 2400, { bold: true, bg: C.lightGray }), dCell("P0", 3600, { color: C.red, bold: true })] }),
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 1. 背景与目标 =====
      h1("1. 背景与目标"),

      h2("1.1 项目背景"),
      p("当前商家入驻美团后，「装修」和「上单」两个环节依赖外部运营团队手工操作内部运营后台完成。存在以下问题："),
      bullet("人力成本高：外包人均处理30家/月，人力成本1.5万/月"),
      bullet("速度慢：从签约到上线平均3-5个工作日"),
      bullet("质量参差：不同操作人员出品标准不一致"),
      bullet("规模瓶颈：旺季扩团队困难，淡季资源浪费"),

      h2("1.2 解决方案"),
      p("利用OpenClaw（AI Agent）的内容生成能力，自动完成装修图制作、商品信息结构化、文案生成等工作，通过标准化API接口将结果提交至内部运营系统。"),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [hCell("现状（人工操作）", 4680), hCell("目标（AI+接口）", 4680)] }),
          new TableRow({ children: [
            mCell([
              p("1. AIBD完成签约"),
              p("2. 外部团队登录运营后台"),
              p("3. 手动上传图片/填写信息"),
              p("4. 手动录入商品/设置价格"),
              p("5. 提交审核"),
            ], 4680),
            mCell([
              p("1. AIBD完成签约 → 触发消息"),
              p("2. OpenClaw Skill自动生成内容"),
              p("3. 调用装修提交接口"),
              p("4. 调用上单提交接口"),
              p("5. 自动进入审核流程"),
            ], 4680),
          ] }),
        ]
      }),

      h2("1.3 预期收益"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [2340, 3120, 3900],
        rows: [
          new TableRow({ children: [hCell("指标", 2340), hCell("现状", 3120), hCell("目标", 3900)] }),
          new TableRow({ children: [
            dCell("单商家处理耗时", 2340, { bold: true }),
            dCell("2-4小时（人工）", 3120),
            dCell("5-10分钟（AI自动）", 3900, { color: C.green })
          ] }),
          new TableRow({ children: [
            dCell("月处理能力", 2340, { bold: true, bg: C.lightGray }),
            dCell("30家/人", 3120, { bg: C.lightGray }),
            dCell("200+家/Agent（并发）", 3900, { color: C.green, bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("月成本", 2340, { bold: true }),
            dCell("1.5万/人", 3120),
            dCell("~3000/Agent（算力+API）", 3900, { color: C.green })
          ] }),
          new TableRow({ children: [
            dCell("签约-上线周期", 2340, { bold: true, bg: C.lightGray }),
            dCell("3-5个工作日", 3120, { bg: C.lightGray }),
            dCell("当天完成", 3900, { color: C.green, bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("出品一致性", 2340, { bold: true }),
            dCell("因人而异", 3120),
            dCell("模板化标准化", 3900, { color: C.green })
          ] }),
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 2. 系统架构 =====
      h1("2. 系统架构"),

      h2("2.1 整体流程"),
      p("签约完成 → AIBD推送签约消息 → OpenClaw Agent接收 → 内容生成（Skill层）→ 调用接口提交（API层）→ 运营系统写入 → 触发审核"),

      h2("2.2 分层设计"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [1870, 2340, 2340, 2810],
        rows: [
          new TableRow({ children: [hCell("层级", 1870), hCell("负责方", 2340), hCell("能力", 2340), hCell("说明", 2810)] }),
          new TableRow({ children: [
            dCell("触发层", 1870, { bold: true }),
            dCell("AIBD", 2340, { align: AlignmentType.CENTER }),
            dCell("签约完成通知", 2340),
            dCell("签约成功后推送MQ消息/回调", 2810)
          ] }),
          new TableRow({ children: [
            dCell("生成层", 1870, { bold: true, bg: C.lightGray }),
            dCell("OpenClaw Skill", 2340, { align: AlignmentType.CENTER, bg: C.lightGray }),
            dCell("内容生成", 2340, { bg: C.lightGray }),
            dCell("装修图/商品结构化/文案生成", 2810, { bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("提交层", 1870, { bold: true }),
            dCell("研发提供API", 2340, { align: AlignmentType.CENTER }),
            dCell("数据写入", 2340),
            dCell("接收标准化JSON → 写库 → 触发审核", 2810)
          ] }),
          new TableRow({ children: [
            dCell("审核层", 1870, { bold: true, bg: C.lightGray }),
            dCell("现有系统", 2340, { align: AlignmentType.CENTER, bg: C.lightGray }),
            dCell("人工/自动审核", 2340, { bg: C.lightGray }),
            dCell("复用现有审核流程，无需改造", 2810, { bg: C.lightGray })
          ] }),
        ]
      }),

      h2("2.3 和现有AIBD的关系"),
      bullet("AIBD负责「从0到签约」—— 商家触达、意向引导、资质收集、签约"),
      bullet("OpenClaw负责「从签约到上线」—— 装修、上单、状态跟踪"),
      bullet("两者通过消息/回调对接，AIBD签约完成后触发OpenClaw装修流程"),
      bullet("不是替代关系，而是接力关系"),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 3. 接口定义 =====
      h1("3. 接口定义"),

      // === 3.1 装修提交 ===
      h2("3.1 装修信息提交接口"),
      p("将AI生成的装修内容一次性提交到运营系统。"),

      h3("基本信息"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [2340, 7020],
        rows: [
          new TableRow({ children: [dCell("接口路径", 2340, { bold: true, bg: C.lightGray }), dCell("POST /api/v1/shop/decoration/submit", 7020)] }),
          new TableRow({ children: [dCell("Content-Type", 2340, { bold: true, bg: C.lightGray }), dCell("application/json", 7020)] }),
          new TableRow({ children: [dCell("鉴权方式", 2340, { bold: true, bg: C.lightGray }), dCell("内部服务鉴权（APPKEY + Token）", 7020)] }),
          new TableRow({ children: [dCell("幂等性", 2340, { bold: true, bg: C.lightGray }), dCell("基于 request_id 做幂等，重复提交返回上次结果", 7020)] }),
        ]
      }),

      h3("请求参数"),
      apiTable([
        ["request_id", "string", "是", "幂等键，建议UUID，同一request_id重复调用返回相同结果"],
        ["shop_id", "string", "是", "商家ID（AIBD签约时分配）"],
        ["operator_id", "string", "是", "操作人ID（AI Agent标识，如 openclaw_agent_001）"],
        ["shop_name", "string", "是", "店铺名称"],
        ["logo_url", "string", "是", "店铺LOGO图片URL（已上传CDN）"],
        ["banner_url", "string", "否", "店铺头图/Banner URL"],
        ["env_photos", "array[string]", "否", "环境照片URL列表，最多6张"],
        ["description", "string", "是", "店铺简介（AI生成，≤200字）"],
        ["business_hours", "string", "是", "营业时间，格式 HH:MM-HH:MM"],
        ["phone", "string", "否", "联系电话"],
        ["delivery_range_km", "number", "否", "配送范围（公里），默认3"],
        ["category_tags", "array[string]", "是", "品类标签，如[\"烧烤\",\"夜宵\"]"],
        ["announcement", "string", "否", "店铺公告（≤100字）"],
        ["extra", "object", "否", "扩展字段，预留业务定制"],
      ]),

      h3("请求示例"),
      ...jsonBlock({
        request_id: "550e8400-e29b-41d4-a716-446655440000",
        shop_id: "SH20260310001",
        operator_id: "openclaw_agent_001",
        shop_name: "张三烧烤（望京店）",
        logo_url: "https://cdn.meituan.com/shops/logo_001.jpg",
        banner_url: "https://cdn.meituan.com/shops/banner_001.jpg",
        env_photos: [
          "https://cdn.meituan.com/shops/env_001.jpg",
          "https://cdn.meituan.com/shops/env_002.jpg"
        ],
        description: "本店主打正宗东北烧烤，15年老师傅掌勺，精选羊后腿肉现串现烤",
        business_hours: "16:00-02:00",
        phone: "010-12345678",
        delivery_range_km: 3,
        category_tags: ["烧烤", "夜宵", "东北菜"],
        announcement: "新店开业，全场8折！"
      }),

      h3("响应参数"),
      apiTable([
        ["code", "int", "是", "状态码：0=成功，非0=失败"],
        ["message", "string", "是", "状态描述"],
        ["data.task_id", "string", "是", "装修任务ID，用于后续查询状态"],
        ["data.status", "string", "是", "PENDING / REVIEWING / APPROVED / REJECTED"],
        ["data.reject_reason", "string", "否", "审核驳回原因（status=REJECTED时）"],
      ]),

      h3("响应示例"),
      ...jsonBlock({
        code: 0,
        message: "success",
        data: {
          task_id: "DEC20260310001",
          status: "PENDING"
        }
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // === 3.2 上单提交 ===
      h2("3.2 商品上单提交接口"),
      p("批量提交商品信息到运营系统。"),

      h3("基本信息"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [2340, 7020],
        rows: [
          new TableRow({ children: [dCell("接口路径", 2340, { bold: true, bg: C.lightGray }), dCell("POST /api/v1/shop/products/batch-submit", 7020)] }),
          new TableRow({ children: [dCell("Content-Type", 2340, { bold: true, bg: C.lightGray }), dCell("application/json", 7020)] }),
          new TableRow({ children: [dCell("鉴权方式", 2340, { bold: true, bg: C.lightGray }), dCell("内部服务鉴权（APPKEY + Token）", 7020)] }),
          new TableRow({ children: [dCell("幂等性", 2340, { bold: true, bg: C.lightGray }), dCell("基于 request_id 做幂等", 7020)] }),
          new TableRow({ children: [dCell("单次上限", 2340, { bold: true, bg: C.lightGray }), dCell("单次最多100个商品", 7020)] }),
        ]
      }),

      h3("请求参数"),
      apiTable([
        ["request_id", "string", "是", "幂等键UUID"],
        ["shop_id", "string", "是", "商家ID"],
        ["operator_id", "string", "是", "操作人ID（AI Agent标识）"],
        ["products", "array[object]", "是", "商品列表，单次≤100个"],
      ]),

      p("products 数组中每个元素：", { bold: true }),
      apiTable([
        ["name", "string", "是", "商品名称"],
        ["category", "string", "是", "商品分类（如\"烧烤类\"、\"饮品\"）"],
        ["price", "number", "是", "售价（元），精确到分"],
        ["original_price", "number", "否", "原价（划线价）"],
        ["unit", "string", "否", "单位（如\"份\"、\"串\"、\"杯\"），默认\"份\""],
        ["description", "string", "否", "商品描述（AI生成，≤100字）"],
        ["image_url", "string", "否", "商品图片URL（已上传CDN）"],
        ["specs", "array[object]", "否", "规格列表：[{name:\"大份\",price:38},{name:\"小份\",price:22}]"],
        ["tags", "array[string]", "否", "标签：[\"招牌\",\"必点\",\"新品\"]"],
        ["sort_order", "int", "否", "排序权重，数字越小越靠前"],
        ["is_recommend", "boolean", "否", "是否推荐菜品，默认false"],
        ["extra", "object", "否", "扩展字段"],
      ]),

      h3("请求示例"),
      ...jsonBlock({
        request_id: "660e8400-e29b-41d4-a716-446655440001",
        shop_id: "SH20260310001",
        operator_id: "openclaw_agent_001",
        products: [
          {
            name: "羊肉串",
            category: "烧烤类",
            price: 5.00,
            unit: "串",
            description: "精选羊后腿肉，现串现烤，外焦里嫩",
            image_url: "https://cdn.meituan.com/products/yangrou.jpg",
            tags: ["招牌", "必点"],
            sort_order: 1,
            is_recommend: true
          },
          {
            name: "烤鸡翅",
            category: "烧烤类",
            price: 8.00,
            unit: "个",
            description: "蜜汁腌制，炭火慢烤",
            image_url: "https://cdn.meituan.com/products/jichi.jpg",
            sort_order: 2
          },
          {
            name: "冰镇啤酒",
            category: "饮品",
            price: 8.00,
            original_price: 12.00,
            unit: "瓶",
            specs: [
              { name: "青岛经典", price: 8.00 },
              { name: "百威", price: 12.00 }
            ],
            sort_order: 10
          }
        ]
      }),

      h3("响应参数"),
      apiTable([
        ["code", "int", "是", "状态码：0=成功"],
        ["message", "string", "是", "状态描述"],
        ["data.task_id", "string", "是", "上单任务ID"],
        ["data.total", "int", "是", "提交商品总数"],
        ["data.success_count", "int", "是", "成功数"],
        ["data.fail_count", "int", "是", "失败数"],
        ["data.fail_details", "array[object]", "否", "失败明细：[{name,reason}]"],
        ["data.status", "string", "是", "PENDING / REVIEWING / APPROVED / PARTIAL_REJECTED"],
      ]),

      new Paragraph({ children: [new PageBreak()] }),

      // === 3.3 状态查询 ===
      h2("3.3 任务状态查询接口"),
      p("查询装修/上单任务的审核状态，供OpenClaw轮询跟踪。"),

      h3("基本信息"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [2340, 7020],
        rows: [
          new TableRow({ children: [dCell("接口路径", 2340, { bold: true, bg: C.lightGray }), dCell("GET /api/v1/shop/task/status?task_id={task_id}", 7020)] }),
          new TableRow({ children: [dCell("鉴权方式", 2340, { bold: true, bg: C.lightGray }), dCell("内部服务鉴权", 7020)] }),
        ]
      }),

      h3("响应参数"),
      apiTable([
        ["code", "int", "是", "状态码"],
        ["data.task_id", "string", "是", "任务ID"],
        ["data.task_type", "string", "是", "DECORATION / PRODUCT_UPLOAD"],
        ["data.status", "string", "是", "PENDING / REVIEWING / APPROVED / REJECTED / PARTIAL_REJECTED"],
        ["data.created_at", "string", "是", "创建时间 ISO 8601"],
        ["data.updated_at", "string", "是", "最后更新时间"],
        ["data.reject_reason", "string", "否", "驳回原因"],
        ["data.reject_fields", "array[string]", "否", "驳回字段列表（便于AI自动修正）"],
      ]),

      p("说明：reject_fields 返回具体哪些字段不合规，OpenClaw可据此自动修正后重新提交。", { italics: true, color: C.gray }),

      // === 3.4 回调 ===
      h2("3.4 审核结果回调（可选）"),
      p("除轮询外，支持审核完成后主动回调通知，减少轮询频率。"),

      h3("回调请求（由运营系统发出）"),
      apiTable([
        ["task_id", "string", "是", "任务ID"],
        ["task_type", "string", "是", "DECORATION / PRODUCT_UPLOAD"],
        ["status", "string", "是", "APPROVED / REJECTED / PARTIAL_REJECTED"],
        ["reject_reason", "string", "否", "驳回原因"],
        ["reject_fields", "array[string]", "否", "驳回字段"],
        ["timestamp", "string", "是", "回调时间 ISO 8601"],
      ]),

      p("回调地址由OpenClaw侧提供，需支持重试机制（3次，间隔1s/5s/30s）。", { italics: true, color: C.gray }),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 4. 错误码 =====
      h1("4. 错误码规范"),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [1400, 3900, 4060],
        rows: [
          new TableRow({ children: [hCell("错误码", 1400), hCell("含义", 3900), hCell("处理建议", 4060)] }),
          new TableRow({ children: [dCell("0", 1400, { bold: true, color: C.green }), dCell("成功", 3900), dCell("—", 4060)] }),
          new TableRow({ children: [dCell("1001", 1400, { bold: true, color: C.red, bg: C.lightGray }), dCell("参数校验失败", 3900, { bg: C.lightGray }), dCell("检查必填字段、格式是否正确", 4060, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("1002", 1400, { bold: true, color: C.red }), dCell("shop_id不存在或未签约", 3900), dCell("确认AIBD签约是否完成", 4060)] }),
          new TableRow({ children: [dCell("1003", 1400, { bold: true, color: C.red, bg: C.lightGray }), dCell("重复提交（幂等命中）", 3900, { bg: C.lightGray }), dCell("返回上次结果，无需处理", 4060, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("1004", 1400, { bold: true, color: C.red }), dCell("图片URL无法访问", 3900), dCell("检查CDN链接是否有效", 4060)] }),
          new TableRow({ children: [dCell("1005", 1400, { bold: true, color: C.red, bg: C.lightGray }), dCell("商品数量超限（>100）", 3900, { bg: C.lightGray }), dCell("分批提交", 4060, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("2001", 1400, { bold: true, color: C.red }), dCell("装修任务已存在（该店铺已装修）", 3900), dCell("查询现有装修状态，决定是否覆盖", 4060)] }),
          new TableRow({ children: [dCell("5000", 1400, { bold: true, color: C.red, bg: C.lightGray }), dCell("系统内部错误", 3900, { bg: C.lightGray }), dCell("重试3次，仍失败则告警", 4060, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("5001", 1400, { bold: true, color: C.red }), dCell("服务限流", 3900), dCell("退避重试（1s→5s→30s）", 4060)] }),
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 5. 数据流 =====
      h1("5. 完整数据流"),

      h2("5.1 装修流程"),
      numItem("AIBD签约成功 → 推送签约完成消息（含shop_id、商家基础信息）"),
      numItem("OpenClaw接收消息 → 在企微群和商家确认装修需求"),
      numItem("OpenClaw Skill层：生成装修图（门头照裁剪/AI生图）→ 上传CDN → 获取URL"),
      numItem("OpenClaw Skill层：基于商家品类+位置，AI生成店铺简介、公告"),
      numItem("OpenClaw组装JSON → 调用装修提交接口 POST /api/v1/shop/decoration/submit"),
      numItem("运营系统写入数据 → 触发审核流程"),
      numItem("OpenClaw轮询状态 / 收到回调"),
      numItem("审核通过 → 企微群通知商家\"装修已完成\" → 进入上单流程"),
      numItem("审核驳回 → OpenClaw读取reject_fields → 自动修正 → 重新提交"),

      h2("5.2 上单流程"),
      numItem("装修审核通过后自动触发"),
      numItem("OpenClaw在企微群请求商家提供菜单（支持：图片OCR/Excel/语音/文字）"),
      numItem("OpenClaw Skill层：OCR识别 → 结构化提取（品名/价格/规格）→ AI补充描述"),
      numItem("OpenClaw在群里发确认清单 → 商家确认/修改"),
      numItem("OpenClaw组装JSON → 调用上单接口 POST /api/v1/shop/products/batch-submit"),
      numItem("运营系统写入 → 审核"),
      numItem("审核通过 → 商品上架 → 商家正式营业"),

      h2("5.3 异常处理"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [3120, 3120, 3120],
        rows: [
          new TableRow({ children: [hCell("异常场景", 3120), hCell("处理策略", 3120), hCell("责任方", 3120)] }),
          new TableRow({ children: [dCell("接口超时", 3120), dCell("重试3次 → 告警 → 人工介入", 3120), dCell("OpenClaw", 3120)] }),
          new TableRow({ children: [dCell("图片上传失败", 3120, { bg: C.lightGray }), dCell("重新上传CDN → 重新提交", 3120, { bg: C.lightGray }), dCell("OpenClaw", 3120, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("审核驳回", 3120), dCell("读取reject_fields → AI修正 → 重提", 3120), dCell("OpenClaw", 3120)] }),
          new TableRow({ children: [dCell("商家不响应（>24h）", 3120, { bg: C.lightGray }), dCell("企微群提醒 → 超72h转人工BD", 3120, { bg: C.lightGray }), dCell("OpenClaw+BD", 3120, { bg: C.lightGray })] }),
          new TableRow({ children: [dCell("接口限流", 3120), dCell("退避重试（指数退避）", 3120), dCell("OpenClaw", 3120)] }),
          new TableRow({ children: [dCell("数据格式不合规", 3120, { bg: C.lightGray }), dCell("错误码1001 → 修正字段 → 重提", 3120, { bg: C.lightGray }), dCell("OpenClaw", 3120, { bg: C.lightGray })] }),
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 6. 非功能要求 =====
      h1("6. 非功能性要求"),

      h2("6.1 性能"),
      bullet("接口响应时间：P99 < 500ms"),
      bullet("单店装修提交：< 2s（含图片URL校验）"),
      bullet("批量上单（100商品）：< 5s"),
      bullet("并发支持：QPS ≥ 50（满足多Agent并行）"),

      h2("6.2 安全"),
      bullet("鉴权：APPKEY + Token方式，每个AI Agent分配独立APPKEY"),
      bullet("日志：完整记录每次调用的operator_id、request_id、操作内容"),
      bullet("审计：所有AI提交的内容标记为\"AI生成\"，审核界面可区分"),

      h2("6.3 监控"),
      bullet("接口调用量/成功率/响应时间 — 接入公司监控（CAT/Raptor）"),
      bullet("审核通过率按AI vs 人工分别统计"),
      bullet("异常告警：连续3次提交失败 → 通知运维"),

      h2("6.4 灰度策略"),
      bullet("第一阶段：10家商家试点，仅开放装修接口，人工复核100%"),
      bullet("第二阶段：100家商家，开放上单接口，人工抽检50%"),
      bullet("第三阶段：全量上线，人工抽检10%"),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 7. 排期建议 =====
      h1("7. 排期建议"),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [780, 2340, 2340, 1560, 2340],
        rows: [
          new TableRow({ children: [hCell("阶段", 780), hCell("任务", 2340), hCell("负责方", 2340), hCell("工期", 1560), hCell("产出", 2340)] }),
          new TableRow({ children: [
            dCell("1", 780, { align: AlignmentType.CENTER, bold: true }),
            dCell("接口方案评审", 2340), dCell("产品+研发", 2340),
            dCell("1天", 1560, { align: AlignmentType.CENTER }),
            dCell("确认接口规范", 2340)
          ] }),
          new TableRow({ children: [
            dCell("2", 780, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("装修提交接口开发", 2340, { bg: C.lightGray }), dCell("后端研发", 2340, { bg: C.lightGray }),
            dCell("3-5天", 1560, { align: AlignmentType.CENTER, bg: C.lightGray }),
            dCell("接口上线（测试环境）", 2340, { bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("3", 780, { align: AlignmentType.CENTER, bold: true }),
            dCell("上单提交接口开发", 2340), dCell("后端研发", 2340),
            dCell("3-5天", 1560, { align: AlignmentType.CENTER }),
            dCell("接口上线（测试环境）", 2340)
          ] }),
          new TableRow({ children: [
            dCell("4", 780, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("OpenClaw Skill开发", 2340, { bg: C.lightGray }), dCell("AI团队（产品侧）", 2340, { bg: C.lightGray }),
            dCell("5-7天", 1560, { align: AlignmentType.CENTER, bg: C.lightGray }),
            dCell("装修+上单Skill", 2340, { bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("5", 780, { align: AlignmentType.CENTER, bold: true }),
            dCell("联调测试", 2340), dCell("产品+研发+AI", 2340),
            dCell("3天", 1560, { align: AlignmentType.CENTER }),
            dCell("端到端跑通", 2340)
          ] }),
          new TableRow({ children: [
            dCell("6", 780, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("灰度试点（10家）", 2340, { bg: C.lightGray }), dCell("全员", 2340, { bg: C.lightGray }),
            dCell("7天", 1560, { align: AlignmentType.CENTER, bg: C.lightGray }),
            dCell("验证效果、收集反馈", 2340, { bg: C.lightGray })
          ] }),
        ]
      }),

      p("总计预估：3-4周可完成灰度验证。", { bold: true, color: C.primary }),

      // ===== 8. 开放问题 =====
      h1("8. 待确认事项"),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        columnWidths: [600, 4680, 4080],
        rows: [
          new TableRow({ children: [hCell("#", 600), hCell("问题", 4680), hCell("建议", 4080)] }),
          new TableRow({ children: [
            dCell("1", 600, { align: AlignmentType.CENTER, bold: true }),
            dCell("图片上传走哪个CDN？现有CDN是否支持外部上传？", 4680),
            dCell("建议复用现有商家图片CDN，提供上传Token", 4080)
          ] }),
          new TableRow({ children: [
            dCell("2", 600, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("装修和上单是否有品类差异化模板？", 4680, { bg: C.lightGray }),
            dCell("第一期先做通用模板，后续按品类扩展", 4080, { bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("3", 600, { align: AlignmentType.CENTER, bold: true }),
            dCell("AIBD签约完成后，推送消息的格式和通道是什么？", 4680),
            dCell("建议MQ消息，包含shop_id和商家基础信息", 4080)
          ] }),
          new TableRow({ children: [
            dCell("4", 600, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("审核流程是否需要改造？AI提交的是否走不同审核通道？", 4680, { bg: C.lightGray }),
            dCell("建议复用现有审核流程，仅打\"AI提交\"标签", 4080, { bg: C.lightGray })
          ] }),
          new TableRow({ children: [
            dCell("5", 600, { align: AlignmentType.CENTER, bold: true }),
            dCell("已有装修的商家是否支持覆盖提交？", 4680),
            dCell("建议支持，新提交覆盖旧数据", 4080)
          ] }),
          new TableRow({ children: [
            dCell("6", 600, { align: AlignmentType.CENTER, bold: true, bg: C.lightGray }),
            dCell("OpenClaw Agent的权限如何管理？一个Agent对应多少商家？", 4680, { bg: C.lightGray }),
            dCell("建议一个APPKEY对应一个Agent实例，不做商家绑定", 4080, { bg: C.lightGray })
          ] }),
        ]
      }),

      new Paragraph({ spacing: { before: 400, after: 100 },
        children: [new TextRun({ text: "— END —", font: "Arial", size: 24, bold: true, color: C.gray })] }),
    ]
  }]
});

// 生成
Packer.toBuffer(doc).then(buffer => {
  const path = '/root/.openclaw/workspace/OpenClaw_AIBD_装修上单接口需求文档_v1.0.docx';
  fs.writeFileSync(path, buffer);
  console.log('PRD saved to: ' + path);
});
