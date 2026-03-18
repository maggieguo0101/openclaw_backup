const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType, PageBreak } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

// ====== 原文 ======
const originalText = `Lesson 21 of the free Engage course invites you to question the idea that personal time must be earned through work. Explore how limiting work hours and choosing abundant personal time can lead to greater clarity, motivation, and a more satisfying life.

You'll find the rest of the Engage course videos in the Video section.

Join the Engage notification list to get an email whenever a new Engage lesson is published. I also encourage you to subscribe to my YouTube channel to follow the course there.

Enjoy!`;

// ====== 三个模型翻译 ======
const translations = {
  "Claude Opus 4.6": {
    title: `别再用工作去"换取"你的个人生活`,
    body: `免费课程"Engage"第21课邀请你重新审视一个根深蒂固的观念——个人时间必须通过工作来换取。探索如何通过限制工作时长、主动选择充裕的个人时间，来获得更清晰的思路、更强的内驱力，以及更令人满意的生活。

你可以在"视频"板块找到 Engage 课程的其余视频。

加入 Engage 通知列表，每当有新课程发布时，你都会收到邮件提醒。同时也欢迎订阅我的 YouTube 频道，在那里同步跟进课程内容。

祝学习愉快！`,
    color: "1F4E79"
  },
  "Gemini 3.0 Pro": {
    title: `别再用工作来"换取"你的私人生活`,
    body: `免费课程《投入》的第21课，邀请你重新审视一个根深蒂固的观念——私人时间必须靠工作来换取。探索如何通过限制工作时长、主动选择充裕的个人时间，来获得更清晰的思路、更强的动力，以及更令人满意的生活。

其余《投入》课程视频可在"视频"板块找到。

加入《投入》课程的通知列表，每当新课程发布时，你将收到邮件提醒。我也建议你订阅我的YouTube频道，在那里同步跟进课程。

祝学习愉快！`,
    color: "0B5394"
  },
  "DeepSeek R1": {
    title: `别再用工作去"换取"你的个人生活`,
    body: `免费课程"Engage"的第21课，邀请你重新审视一个根深蒂固的观念——个人时间必须靠工作来换取。探索如何通过限制工作时长、主动选择充裕的个人时间，从而获得更清晰的头脑、更强的内驱力，以及更令人满意的生活。

其余的 Engage 课程视频可在"视频"板块中找到。

加入 Engage 通知列表，每当有新课程发布时，你将第一时间收到邮件提醒。同时也欢迎订阅我的 YouTube 频道，在那里同步跟进课程内容。

祝学习愉快！`,
    color: "38761D"
  }
};

// ====== 差异分析 ======
const diffAnalysis = [
  {
    dimension: "标题翻译",
    claude: `"别再用工作去'换取'你的个人生活"`,
    gemini: `"别再用工作来'换取'你的私人生活"`,
    deepseek: `"别再用工作去'换取'你的个人生活"`,
    comment: "Gemini 将 Personal Life 译为「私人生活」，Claude 和 DeepSeek 译为「个人生活」。Gemini 将 Engage 意译为《投入》。"
  },
  {
    dimension: "课程名处理",
    claude: `保留英文 "Engage"`,
    gemini: `意译为《投入》`,
    deepseek: `保留英文 "Engage"`,
    comment: "Gemini 选择意译课程名，更利于中文读者理解；Claude 和 DeepSeek 保留原名，避免误译。"
  },
  {
    dimension: "\"clarity\" 译法",
    claude: "更清晰的思路",
    gemini: "更清晰的思路",
    deepseek: "更清晰的头脑",
    comment: "DeepSeek 用「头脑」替代「思路」，更口语化。"
  },
  {
    dimension: "\"motivation\" 译法",
    claude: "更强的内驱力",
    gemini: "更强的动力",
    deepseek: "更强的内驱力",
    comment: "Gemini 用「动力」更通俗；Claude 和 DeepSeek 用「内驱力」更精准。"
  },
  {
    dimension: "整体风格",
    claude: "流畅自然，用词精准",
    gemini: "本土化程度最高，意译较多",
    deepseek: "忠实原文，表达稳健",
    comment: "Claude 平衡度最佳；Gemini 最大胆（意译课程名）；DeepSeek 最保守稳妥。"
  }
];

function makeHeaderCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: "2C3E50", type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })
    ]})]
  });
}

function makeCell(text, width, fill) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: [
      new TextRun({ text, font: "Arial", size: 20 })
    ]})]
  });
}

// ====== 构建文档 ======
const children = [];

// 封面标题
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 100 },
  children: [new TextRun({ text: "多模型翻译对比报告", bold: true, font: "Arial", size: 40, color: "2C3E50" })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 100 },
  children: [new TextRun({ text: "Stop Earning Your Personal Life — Steve Pavlina", font: "Arial", size: 24, color: "7F8C8D", italics: true })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 400 },
  children: [new TextRun({ text: "翻译模型：Claude Opus 4.6 | Gemini 3.0 Pro | DeepSeek R1", font: "Arial", size: 20, color: "95A5A6" })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 400 },
  children: [new TextRun({ text: "生成日期：2026年3月9日", font: "Arial", size: 20, color: "95A5A6" })]
}));

// 原文
children.push(new Paragraph({ spacing: { before: 300, after: 200 }, children: [
  new TextRun({ text: "一、原文（英文）", bold: true, font: "Arial", size: 28, color: "2C3E50" })
]}));
children.push(new Paragraph({ spacing: { after: 100 }, children: [
  new TextRun({ text: "Stop Earning Your Personal Life", bold: true, font: "Arial", size: 24 })
]}));
for (const para of originalText.split('\n\n')) {
  children.push(new Paragraph({ spacing: { after: 120 }, children: [
    new TextRun({ text: para, font: "Arial", size: 20, color: "333333" })
  ]}));
}

// 各模型翻译
children.push(new Paragraph({ children: [new PageBreak()] }));

let modelIdx = 0;
for (const [model, data] of Object.entries(translations)) {
  modelIdx++;
  children.push(new Paragraph({ spacing: { before: 300, after: 200 }, children: [
    new TextRun({ text: `二-${modelIdx}. ${model} 翻译`, bold: true, font: "Arial", size: 28, color: data.color })
  ]}));
  children.push(new Paragraph({ spacing: { after: 100 }, children: [
    new TextRun({ text: data.title, bold: true, font: "Arial", size: 24, color: data.color })
  ]}));
  for (const para of data.body.split('\n\n')) {
    children.push(new Paragraph({ spacing: { after: 120 }, children: [
      new TextRun({ text: para, font: "Arial", size: 20, color: "333333" })
    ]}));
  }
}

// 差异对比表
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(new Paragraph({ spacing: { before: 300, after: 200 }, children: [
  new TextRun({ text: "三、翻译差异对比", bold: true, font: "Arial", size: 28, color: "2C3E50" })
]}));

const colWidths = [1400, 1800, 1800, 1800, 2560];
const tableRows = [];
tableRows.push(new TableRow({
  children: [
    makeHeaderCell("维度", colWidths[0]),
    makeHeaderCell("Claude Opus 4.6", colWidths[1]),
    makeHeaderCell("Gemini 3.0 Pro", colWidths[2]),
    makeHeaderCell("DeepSeek R1", colWidths[3]),
    makeHeaderCell("点评", colWidths[4]),
  ]
}));
for (let i = 0; i < diffAnalysis.length; i++) {
  const d = diffAnalysis[i];
  const fill = i % 2 === 0 ? "F8F9FA" : undefined;
  tableRows.push(new TableRow({
    children: [
      makeCell(d.dimension, colWidths[0], fill),
      makeCell(d.claude, colWidths[1], fill),
      makeCell(d.gemini, colWidths[2], fill),
      makeCell(d.deepseek, colWidths[3], fill),
      makeCell(d.comment, colWidths[4], fill),
    ]
  }));
}

children.push(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  columnWidths: colWidths,
  rows: tableRows
}));

// 总结
children.push(new Paragraph({ spacing: { before: 400, after: 200 }, children: [
  new TextRun({ text: "四、总结", bold: true, font: "Arial", size: 28, color: "2C3E50" })
]}));

const summaryPoints = [
  "Claude Opus 4.6：翻译流畅自然，用词精准，保留原文课程名不做意译，整体平衡度最佳。",
  "Gemini 3.0 Pro：本土化程度最高，大胆将 Engage 意译为《投入》，更贴近中文读者习惯，但可能引起歧义。",
  "DeepSeek R1：忠实原文，表达稳健，与 Claude 结果高度接近，个别用词略有不同（如「头脑」vs「思路」）。",
  "三个模型在这篇短文上的翻译质量差异不大，主要体现在课程名处理策略和个别词汇选择上。建议在长文测试中进一步对比。"
];

for (const point of summaryPoints) {
  children.push(new Paragraph({ spacing: { after: 100 }, children: [
    new TextRun({ text: "▸ " + point, font: "Arial", size: 20, color: "333333" })
  ]}));
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1080, bottom: 1440, left: 1080 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/root/.openclaw/workspace/翻译对比_Stop_Earning_Your_Personal_Life.docx", buffer);
  console.log("Done!");
});
