const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');

// ===== 颜色定义 =====
const COLORS = {
  primary: "1A3A5C",    // 深蓝
  accent: "2E86AB",     // 浅蓝
  green: "28A745",
  red: "DC3545",
  orange: "FD7E14",
  gray: "6C757D",
  lightGray: "F8F9FA",
  headerBg: "1A3A5C",
  headerText: "FFFFFF",
  rowAlt: "F2F7FB",
};

const border = { style: BorderStyle.SINGLE, size: 1, color: "DEE2E6" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: COLORS.headerBg, type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, font: "Arial", size: 20, color: COLORS.headerText })] })]
  });
}

function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), font: "Arial", size: 20,
        color: opts.color || "333333", bold: opts.bold || false })] })]
  });
}

function sectionTitle(text) {
  return new Paragraph({
    spacing: { before: 360, after: 200 },
    children: [
      new TextRun({ text: "▎", font: "Arial", size: 28, color: COLORS.accent }),
      new TextRun({ text: " " + text, font: "Arial", size: 28, bold: true, color: COLORS.primary })
    ]
  });
}

function bulletItem(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: "333333" })]
  });
}

function riskItem(label, desc, color) {
  return new Paragraph({
    spacing: { after: 80 },
    indent: { left: 360 },
    children: [
      new TextRun({ text: "⚠ " + label + "：", font: "Arial", size: 20, bold: true, color }),
      new TextRun({ text: desc, font: "Arial", size: 20, color: "555555" })
    ]
  });
}

// ===== 文档结构 =====
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: COLORS.primary },
        paragraph: { spacing: { before: 0, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: COLORS.primary },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
      ]
    }]
  },
  sections: [
    // ========== 第一部分：思源电气 ==========
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1200, right: 1200, bottom: 1200, left: 1200 }
        }
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "Catclaw 深度研究 | 2026.03.10", font: "Arial", size: 16, color: COLORS.gray, italics: true })]
        })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "以上不构成投资建议，仅供研究参考  |  Page ", font: "Arial", size: 16, color: COLORS.gray }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: COLORS.gray })
          ]
        })] })
      },
      children: [
        // 封面标题
        new Paragraph({ spacing: { before: 600, after: 0 }, alignment: AlignmentType.LEFT,
          children: [new TextRun({ text: "深度个股分析报告", font: "Arial", size: 44, bold: true, color: COLORS.primary })] }),
        new Paragraph({ spacing: { before: 100, after: 60 },
          children: [new TextRun({ text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font: "Arial", size: 20, color: COLORS.accent })] }),

        // ===== 思源电气 标题 =====
        new Paragraph({ spacing: { before: 300, after: 100 },
          children: [
            new TextRun({ text: "思源电气 ", font: "Arial", size: 40, bold: true, color: COLORS.primary }),
            new TextRun({ text: "(002028.SZ)", font: "Arial", size: 28, color: COLORS.gray }),
          ] }),
        new Paragraph({ spacing: { after: 100 },
          children: [
            new TextRun({ text: "最新价：¥69.74  |  总市值：~542亿  |  行业：输配电设备", font: "Arial", size: 20, color: COLORS.gray }),
          ] }),

        // 综合评级
        new Paragraph({ spacing: { before: 100, after: 200 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: COLORS.accent } },
          children: [
            new TextRun({ text: "综合评级：", font: "Arial", size: 22, bold: true, color: COLORS.primary }),
            new TextRun({ text: "⭐⭐⭐⭐☆  🟢 偏多", font: "Arial", size: 22, bold: true, color: COLORS.green }),
          ] }),

        // 一、赛道分析
        sectionTitle("一、赛道分析 — 电力设备黄金赛道"),
        new Paragraph({ spacing: { after: 120 },
          children: [new TextRun({ text: "输配电设备行业位于电力产业链中游，2024年中国市场规模约1.2万亿元，2025-2027年年均复合增速约8.5%。全球市场约2500亿美元，年增6%。", font: "Arial", size: 20, color: "333333" })] }),

        bulletItem("国内驱动：新型电力系统建设 + 特高压 + 新能源并网 + 储能配储"),
        bulletItem("海外驱动：北美/欧洲电网老化换新 + AI算力中心用电暴增"),
        bulletItem("细分高增赛道：储能变流器、构网型SVG、超容储能年增速>30%"),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({ children: [
              headerCell("维度", 2340), headerCell("国内", 2340), headerCell("海外", 2340), headerCell("评价", 2340)
            ] }),
            new TableRow({ children: [
              dataCell("市场规模", 2340, { bold: true }),
              dataCell("1.2万亿元/年", 2340, { align: AlignmentType.CENTER }),
              dataCell("2500亿美元/年", 2340, { align: AlignmentType.CENTER }),
              dataCell("超大赛道", 2340, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("增速", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("8.5% CAGR", 2340, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("6% CAGR", 2340, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("稳健增长", 2340, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("竞争格局", 2340, { bold: true }),
              dataCell("国企+民企并存", 2340, { align: AlignmentType.CENTER }),
              dataCell("ABB/西门子主导", 2340, { align: AlignmentType.CENTER }),
              dataCell("中国份额提升", 2340, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
          ]
        }),

        // 二、护城河
        sectionTitle("二、护城河分析 — 技术+出海双重壁垒"),
        bulletItem("技术全覆盖：交流1000kV、直流±800kV全系列通过型式试验，国内电压等级覆盖最全"),
        bulletItem("成本优势：同规格GIS成本较外资低15-20%，交付周期4个月（外资8-10个月）"),
        bulletItem("出海领先：海外收入占比33.68%（2025H1），远超国电南瑞<10%"),
        bulletItem("专利壁垒：授权专利948项（发明342项），牵头IEC/IEEE/国标63项"),
        bulletItem("产能规模：全国7大基地 + 海外20余家子公司，24h响应全球"),
        bulletItem("外资认可：摩根大通等机构持股，外资持股比例高达22.02%（A股第二）"),

        new Paragraph({ spacing: { before: 160, after: 120 },
          children: [
            new TextRun({ text: "护城河评级：", font: "Arial", size: 20, bold: true, color: COLORS.primary }),
            new TextRun({ text: "★★★★☆ — 技术壁垒+海外先发优势+交付能力构成强护城河", font: "Arial", size: 20, color: COLORS.green }),
          ] }),

        // 三、财报分析
        sectionTitle("三、财报分析 — 高增长、高质量"),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [2600, 1690, 1690, 1690, 1690],
          rows: [
            new TableRow({ children: [
              headerCell("指标", 2600), headerCell("2024Q3", 1690), headerCell("2025Q3", 1690), headerCell("变化", 1690), headerCell("评价", 1690)
            ] }),
            new TableRow({ children: [
              dataCell("营业总收入", 2600, { bold: true }),
              dataCell("104.07亿", 1690, { align: AlignmentType.CENTER }),
              dataCell("138.27亿", 1690, { align: AlignmentType.CENTER }),
              dataCell("+32.86%", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bold: true }),
              dataCell("优秀", 1690, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("归母净利润", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("14.91亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("21.91亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+46.94%", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bold: true, bg: COLORS.lightGray }),
              dataCell("优秀", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("毛利率", 2600, { bold: true }),
              dataCell("31.42%", 1690, { align: AlignmentType.CENTER }),
              dataCell("32.32%", 1690, { align: AlignmentType.CENTER }),
              dataCell("+0.90pct", 1690, { color: COLORS.green, align: AlignmentType.CENTER }),
              dataCell("稳定提升", 1690, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("ROE", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("13.28%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("16.11%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+2.83pct", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("资本效率提升", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("净利润现金含量", 2600, { bold: true }),
              dataCell("52.30%", 1690, { align: AlignmentType.CENTER }),
              dataCell("19.69%", 1690, { align: AlignmentType.CENTER }),
              dataCell("-32.61pct", 1690, { color: COLORS.red, align: AlignmentType.CENTER, bold: true }),
              dataCell("⚠ 需关注", 1690, { color: COLORS.red, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("资产负债率", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("44.35%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("45.94%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+1.59pct", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("合理范围", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 160, after: 60 },
          children: [new TextRun({ text: "⚠ 关键风险信号：净利润现金含量从52%骤降至20%，应收账款70.86亿（同比大增），存货50.27亿。扩张期回款压力加大，需持续跟踪。", font: "Arial", size: 20, color: COLORS.orange, bold: true })] }),

        // 四、管理层
        sectionTitle("四、管理层与治理"),
        bulletItem("公司历史：1993年成立，2004年深交所上市，30+年行业积淀"),
        bulletItem("战略清晰：2018年低价收购常州东芝变压器 → 打开海外市场，战略眼光一流"),
        bulletItem("执行力强：2020-2024年订单完成率接近或超过100%，2025年计划268亿订单"),
        bulletItem("研发投入：2025H1研发5.60亿（占收入6.6%），高于行业均值4%"),
        bulletItem("机构认可：17家机构覆盖，16家买入/1家增持"),

        // 五、估值
        sectionTitle("五、估值分析"),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [1870, 1870, 1870, 1870, 1870],
          rows: [
            new TableRow({ children: [
              headerCell("机构/方法", 1870), headerCell("2025E净利", 1870), headerCell("给予PE", 1870), headerCell("目标价", 1870), headerCell("评级", 1870)
            ] }),
            new TableRow({ children: [
              dataCell("国泰海通", 1870, { bold: true }),
              dataCell("26.38亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("28x", 1870, { align: AlignmentType.CENTER }),
              dataCell("¥94.92", 1870, { align: AlignmentType.CENTER, bold: true }),
              dataCell("增持", 1870, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("东吴证券", 1870, { bold: true, bg: COLORS.lightGray }),
              dataCell("28.2亿", 1870, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("25x", 1870, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("¥90.7→130.2", 1870, { align: AlignmentType.CENTER, bold: true, bg: COLORS.lightGray }),
              dataCell("买入", 1870, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("亚思维(DCF)", 1870, { bold: true }),
              dataCell("22.5亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("25.6-46.4x", 1870, { align: AlignmentType.CENTER }),
              dataCell("—", 1870, { align: AlignmentType.CENTER }),
              dataCell("观望/持有", 1870, { color: COLORS.orange, align: AlignmentType.CENTER })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 160, after: 60 },
          children: [
            new TextRun({ text: "当前估值：", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "静态PE 46.71x / 动态PE 32.76x / 最新价 ¥69.74（腾讯行情不准确，以实盘为准）", font: "Arial", size: 20, color: "555555" }),
          ] }),
        new Paragraph({ spacing: { after: 60 },
          children: [
            new TextRun({ text: "2025-2027年预测CAGR：", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "~21.7%（净利润）/ ~29%（乐观估计）", font: "Arial", size: 20, color: "555555" }),
          ] }),

        // Bear Case
        sectionTitle("六、看空理由 — 不买的理由"),
        riskItem("现金流恶化", "净利润现金含量从52%骤降至20%，应收账款暴增，扩张期可能'赚了利润没赚到钱'", COLORS.red),
        riskItem("估值偏高", "动态PE 32x，已price-in大部分增长预期，下跌空间大于上涨空间", COLORS.red),
        riskItem("海外政策风险", "美国/欧洲可能对中国电力设备加征关税，海外收入占比33%直接受冲击", COLORS.red),
        riskItem("原材料波动", "铜、铝、硅钢等上游价格波动直接影响毛利率", COLORS.orange),
        riskItem("竞争加剧", "国内平高/许继/国电南瑞+国际ABB/西门子双重竞争", COLORS.orange),
        riskItem("订单转化不确定", "268亿订单目标虽有历史支撑，但海外地缘风险可能导致延迟", COLORS.orange),

        // 综合结论
        sectionTitle("七、综合结论"),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({
            text: "思源电气是A股电力设备赛道中出海最成功的标的，技术壁垒+海外先发优势构成强护城河。业绩高增确定性强（21-29% CAGR），但当前估值偏高（动态PE 32x），且现金流质量下降是核心风险。建议等待回调至25x PE以下（约¥55-60）再介入，或持有不加仓。",
            font: "Arial", size: 20, color: "333333"
          })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // ========== 第二部分：金盘科技 ==========
        new Paragraph({ spacing: { before: 300, after: 100 },
          children: [
            new TextRun({ text: "金盘科技 ", font: "Arial", size: 40, bold: true, color: COLORS.primary }),
            new TextRun({ text: "(688676.SH)", font: "Arial", size: 28, color: COLORS.gray }),
          ] }),
        new Paragraph({ spacing: { after: 100 },
          children: [
            new TextRun({ text: "最新价：¥46.50  |  总市值：~130亿  |  行业：干式变压器/电力设备", font: "Arial", size: 20, color: COLORS.gray }),
          ] }),

        new Paragraph({ spacing: { before: 100, after: 200 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: COLORS.accent } },
          children: [
            new TextRun({ text: "综合评级：", font: "Arial", size: 22, bold: true, color: COLORS.primary }),
            new TextRun({ text: "⭐⭐⭐⭐  🟡 中性偏多", font: "Arial", size: 22, bold: true, color: COLORS.orange }),
          ] }),

        // 一、赛道
        sectionTitle("一、赛道分析 — 干式变压器+AIDC双轮驱动"),
        bulletItem("干式变压器：环保型、防火型变压器，在数据中心、轨交、新能源等领域替代油变趋势明确"),
        bulletItem("AIDC（AI数据中心）：用电量暴增驱动配电设备需求，数据中心领域2022-2024 CAGR达79.22%"),
        bulletItem("海外市场：全球电网老化+新兴市场电力基建，海外在手订单28.02亿元"),
        bulletItem("技术迭代：HVDC（高压直流）+ SST（固态变压器）是下一代数据中心供电方向"),

        // 二、护城河
        sectionTitle("二、护城河分析 — 数字化+AIDC先发"),
        bulletItem("数字化工厂：国内首家实现干式变压器全流程数字化制造的企业"),
        bulletItem("AIDC全栈方案：从HVDC到SST，10kV/2.4MW SST样机已完成"),
        bulletItem("客户结构优化：数据中心客户（云厂商/互联网巨头）占比快速提升，25H1同比+460%"),
        bulletItem("海外布局：产能覆盖东南亚、欧洲市场，海外收入占比稳步提升"),

        new Paragraph({ spacing: { before: 160, after: 120 },
          children: [
            new TextRun({ text: "护城河评级：", font: "Arial", size: 20, bold: true, color: COLORS.primary }),
            new TextRun({ text: "★★★☆☆ — 数字化制造+AIDC布局有特色，但干式变压器竞争壁垒不算高", font: "Arial", size: 20, color: COLORS.orange }),
          ] }),

        // 三、财报
        sectionTitle("三、财报分析 — 增速分化，结构优化"),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [2600, 1690, 1690, 1690, 1690],
          rows: [
            new TableRow({ children: [
              headerCell("指标", 2600), headerCell("2024H1", 1690), headerCell("2025H1", 1690), headerCell("变化", 1690), headerCell("评价", 1690)
            ] }),
            new TableRow({ children: [
              dataCell("营业收入", 2600, { bold: true }),
              dataCell("29.17亿", 1690, { align: AlignmentType.CENTER }),
              dataCell("31.54亿", 1690, { align: AlignmentType.CENTER }),
              dataCell("+8.16%", 1690, { color: COLORS.orange, align: AlignmentType.CENTER }),
              dataCell("增速偏低", 1690, { color: COLORS.orange, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("归母净利润", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("2.22亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("2.65亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+19.10%", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("利润增速>收入", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("毛利率", 2600, { bold: true }),
              dataCell("23.07%", 1690, { align: AlignmentType.CENTER }),
              dataCell("25.87%", 1690, { align: AlignmentType.CENTER }),
              dataCell("+2.80pct", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bold: true }),
              dataCell("显著改善", 1690, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("净利率", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("7.55%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("8.34%", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+0.79pct", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("盈利能力提升", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("数据中心收入", 2600, { bold: true }),
              dataCell("~0.9亿", 1690, { align: AlignmentType.CENTER }),
              dataCell(">5亿", 1690, { align: AlignmentType.CENTER }),
              dataCell("+460.51%", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bold: true }),
              dataCell("爆发式增长", 1690, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("在手订单", 2600, { bold: true, bg: COLORS.lightGray }),
              dataCell("65.63亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("75.40亿", 1690, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+14.89%", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("订单充足", 1690, { color: COLORS.green, align: AlignmentType.CENTER, bg: COLORS.lightGray })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 160, after: 60 },
          children: [new TextRun({ text: "亮点：数据中心收入同比+460%是核心驱动。风电+77%、发电供电+58%也表现强劲。国内订单同比+30%支撑后续增长。", font: "Arial", size: 20, color: COLORS.green })] }),

        // 四、管理层
        sectionTitle("四、管理层与治理"),
        bulletItem("海南本土企业，扎根干式变压器30+年"),
        bulletItem("数字化转型决心大：国内首家数字化干式变压器工厂"),
        bulletItem("AIDC战略前瞻：SST样机完成，布局HVDC800V架构"),
        bulletItem("海外扩张稳健：不激进，先打好东南亚/欧洲根据地"),

        // 五、估值
        sectionTitle("五、估值分析"),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [1870, 1870, 1870, 1870, 1870],
          rows: [
            new TableRow({ children: [
              headerCell("年份", 1870), headerCell("预测营收", 1870), headerCell("预测净利", 1870), headerCell("对应PE", 1870), headerCell("增速", 1870)
            ] }),
            new TableRow({ children: [
              dataCell("2025E", 1870, { bold: true }),
              dataCell("91.84亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("7.32亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("38x", 1870, { align: AlignmentType.CENTER }),
              dataCell("+27.3%", 1870, { color: COLORS.green, align: AlignmentType.CENTER })
            ] }),
            new TableRow({ children: [
              dataCell("2026E", 1870, { bold: true, bg: COLORS.lightGray }),
              dataCell("110.01亿", 1870, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("10.46亿", 1870, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("26x", 1870, { align: AlignmentType.CENTER, bg: COLORS.lightGray }),
              dataCell("+43.0%", 1870, { color: COLORS.green, align: AlignmentType.CENTER, bold: true, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("2027E", 1870, { bold: true }),
              dataCell("134.45亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("15.49亿", 1870, { align: AlignmentType.CENTER }),
              dataCell("18x", 1870, { align: AlignmentType.CENTER }),
              dataCell("+48.1%", 1870, { color: COLORS.green, align: AlignmentType.CENTER, bold: true })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 160, after: 60 },
          children: [
            new TextRun({ text: "研报评级：", font: "Arial", size: 20, bold: true }),
            new TextRun({ text: "民生证券维持\"推荐\"评级。2025-2027年净利润CAGR约39%，当前PE 38x对应PEG≈1x。", font: "Arial", size: 20, color: "555555" }),
          ] }),

        // Bear Case
        sectionTitle("六、看空理由 — 不买的理由"),
        riskItem("整体收入增速偏低", "25H1收入仅+8.16%，远低于市场预期的30%+增速，说明传统业务增长乏力", COLORS.red),
        riskItem("PE偏高", "当前38x PE，需要净利润连续高增2年才能消化估值，容错率低", COLORS.red),
        riskItem("干式变压器壁垒有限", "顺特电气等竞争对手也在发力数据中心市场，护城河不深", COLORS.red),
        riskItem("AIDC依赖度上升", "数据中心收入占比快速提升，一旦AI投资周期回落，业绩波动大", COLORS.orange),
        riskItem("海外汇率风险", "海外订单28亿，人民币升值将直接侵蚀利润", COLORS.orange),
        riskItem("上游原材料", "铜铝价格波动对毛利率影响显著", COLORS.orange),

        // 综合结论
        sectionTitle("七、综合结论"),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({
            text: "金盘科技是AIDC供电设备的稀缺标的，数据中心业务爆发式增长（+460%）是核心亮点。但整体收入增速偏低（仅+8%），说明传统业务拖后腿。当前PE 38x偏贵，如果AIDC增长持续（2026E净利+43%），估值会快速消化至26x。建议等回调至30x PE以下（约¥40-42）再考虑介入，或小仓位跟踪AIDC业务进展。",
            font: "Arial", size: 20, color: "333333"
          })] }),

        // 对比总结页
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ spacing: { before: 300, after: 200 },
          children: [new TextRun({ text: "两只股票对比总结", font: "Arial", size: 36, bold: true, color: COLORS.primary })] }),
        new Paragraph({ spacing: { after: 100 },
          children: [new TextRun({ text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font: "Arial", size: 20, color: COLORS.accent })] }),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          columnWidths: [2340, 3510, 3510],
          rows: [
            new TableRow({ children: [
              headerCell("对比维度", 2340), headerCell("思源电气 002028", 3510), headerCell("金盘科技 688676", 3510)
            ] }),
            new TableRow({ children: [
              dataCell("核心逻辑", 2340, { bold: true }),
              dataCell("电力出海龙头", 3510), dataCell("AIDC供电稀缺标的", 3510)
            ] }),
            new TableRow({ children: [
              dataCell("收入增速", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("32.86% ✅", 3510, { color: COLORS.green, bg: COLORS.lightGray }),
              dataCell("8.16% ⚠", 3510, { color: COLORS.orange, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("净利润增速", 2340, { bold: true }),
              dataCell("46.94% ✅", 3510, { color: COLORS.green }),
              dataCell("19.10% ✅", 3510, { color: COLORS.green })
            ] }),
            new TableRow({ children: [
              dataCell("毛利率", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("32.32% ✅ 领先", 3510, { color: COLORS.green, bg: COLORS.lightGray }),
              dataCell("25.87% 一般", 3510, { bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("核心增长点", 2340, { bold: true }),
              dataCell("海外EPC+储能+超容", 3510), dataCell("数据中心(+460%)+SST", 3510)
            ] }),
            new TableRow({ children: [
              dataCell("当前PE", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("动态32x — 偏高", 3510, { color: COLORS.orange, bg: COLORS.lightGray }),
              dataCell("38x — 偏高", 3510, { color: COLORS.orange, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("护城河", 2340, { bold: true }),
              dataCell("★★★★☆ 强", 3510, { color: COLORS.green }),
              dataCell("★★★☆☆ 中", 3510, { color: COLORS.orange })
            ] }),
            new TableRow({ children: [
              dataCell("核心风险", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("现金流恶化+关税风险", 3510, { color: COLORS.red, bg: COLORS.lightGray }),
              dataCell("收入增速慢+估值高", 3510, { color: COLORS.red, bg: COLORS.lightGray })
            ] }),
            new TableRow({ children: [
              dataCell("综合评级", 2340, { bold: true }),
              dataCell("⭐⭐⭐⭐☆ 偏多", 3510, { color: COLORS.green, bold: true }),
              dataCell("⭐⭐⭐⭐ 中性偏多", 3510, { color: COLORS.orange, bold: true })
            ] }),
            new TableRow({ children: [
              dataCell("建议操作", 2340, { bold: true, bg: COLORS.lightGray }),
              dataCell("等回调至25x PE(¥55-60)介入", 3510, { bg: COLORS.lightGray, bold: true }),
              dataCell("等回调至30x PE(¥40-42)或跟踪AIDC", 3510, { bg: COLORS.lightGray, bold: true })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 300, after: 100 },
          children: [new TextRun({ text: "📌 如果只能选一只：", font: "Arial", size: 24, bold: true, color: COLORS.primary })] }),
        new Paragraph({ spacing: { after: 80 },
          children: [new TextRun({ text: "追求确定性 → 思源电气（业绩增速快、护城河深、出海逻辑已兑现）", font: "Arial", size: 20, color: "333333" })] }),
        new Paragraph({ spacing: { after: 80 },
          children: [new TextRun({ text: "追求爆发力 → 金盘科技（AIDC增速460%、SST新技术想象空间大）", font: "Arial", size: 20, color: "333333" })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "两只都偏贵，建议耐心等回调。", font: "Arial", size: 20, bold: true, color: COLORS.red })] }),
      ]
    }
  ]
});

// 生成文件
Packer.toBuffer(doc).then(buffer => {
  const path = '/root/.openclaw/workspace/思源电气_金盘科技_深度分析报告_20260310.docx';
  fs.writeFileSync(path, buffer);
  console.log('Report saved to: ' + path);
});
