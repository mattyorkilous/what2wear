// what2wear: today's Outfit as a small Home Screen widget.
// Paste into Scriptable, set these two, and see the README.
const HOST = "https://<user>.pythonanywhere.com";
const TOKEN = "<the token>";

const BACKGROUND = new Color("#1c1c1e");
const DETAIL = new Color("#ffffff", 0.67);
const WARNING = new Color("#ff9f0a");
const HEADER = new Color("#aaaaaa");
const IF_COLD_OPACITY = 0.4;

const today = getFormatter("yyyy-MM-dd").string(new Date());
const dayUrl = `${HOST}/${TOKEN}/day/${today}`;
const files = FileManager.local();
const cachePath = files.joinPath(files.documentsDirectory(), "what2wear.json");

const reply = await fetchReply();
const answer = reply === null ? null : parseJson(reply);
if (answer?.outfit) files.writeString(cachePath, reply);
const shown =
  answer?.outfit || !files.fileExists(cachePath)
    ? answer
    : parseJson(files.readString(cachePath));
const widget = getWidget(
  shown?.outfit ? shown : null,
  getMessage(reply, answer, shown?.outfit),
);
if (config.runsInWidget) Script.setWidget(widget);
else await widget.presentSmall();
Script.complete();

function getFormatter(format) {
  const formatter = new DateFormatter();
  formatter.dateFormat = format;
  return formatter;
}

// The server's answer as text, or null with no network. A short
// timeout, so a slow server falls back to the cache before iOS
// gives up on the widget.
async function fetchReply() {
  const request = new Request(`${dayUrl}.json`);
  request.timeoutInterval = 10;
  try {
    return await request.loadString();
  } catch {
    return null;
  }
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// What the header says instead of the day, if anything. With no
// network a cached Outfit needs no words: its date says how old it is.
function getMessage(reply, answer, hasOutfit) {
  if (reply === null) return hasOutfit ? null : "⚠︎ Can't reach server";
  if (answer?.outfit) return null;
  if (answer?.error) return "⚠︎ State won't read";
  return "⚠︎ Renew PythonAnywhere?";
}

function getWidget(answer, message) {
  const widget = new ListWidget();
  widget.backgroundColor = BACKGROUND;
  widget.url = dayUrl;
  widget.setPadding(11, 12, 11, 12);
  const header = widget.addStack();
  if (message) {
    addText(header, message, 12, WARNING);
  } else if (answer) {
    const isStale = answer.date !== today;
    const shortDate = getFormatter("EEE d").string(
      getFormatter("yyyy-MM-dd").date(answer.date),
    );
    addText(
      header,
      answer.day === "office" ? "🏢 Office " : "🏠 Home ",
      12,
      HEADER,
    );
    addText(
      header,
      (isStale ? "⚠︎ " : "") + shortDate,
      12,
      isStale ? WARNING : HEADER,
    );
  }
  widget.addSpacer(6);
  (answer?.outfit ?? []).forEach((item) => addRow(widget, item));
  widget.addSpacer();
  return widget;
}

function addText(stack, text, size, color) {
  const widgetText = stack.addText(text);
  widgetText.font = Font.systemFont(size);
  widgetText.textColor = color;
  widgetText.lineLimit = 1;
  widgetText.minimumScaleFactor = 0.7;
  return widgetText;
}

// One Garment: its icon and full name, dimmed if worn only if cold.
function addRow(widget, item) {
  const row = widget.addStack();
  row.centerAlignContent();
  const opacity = item.if_cold ? IF_COLD_OPACITY : 1;
  const image = row.addImage(drawIcon(item.icon));
  image.imageSize = new Size(20, 20);
  image.imageOpacity = opacity;
  row.addSpacer(6);
  const kind = item.garment[0].toUpperCase() + item.garment.slice(1);
  addText(row, `${item.label} ${kind}`, 13, Color.white()).textOpacity =
    opacity;
  widget.addSpacer(3);
}

// Drawn in the icon's own 32×32 box; the widget scales it down.
function drawIcon(icon) {
  const context = new DrawContext();
  context.size = new Size(32, 32);
  context.opaque = false;
  context.respectScreenScale = true;
  fillPath(context, icon.shape, icon.fill);
  if (icon.pattern) fillPath(context, icon.pattern, icon.pattern_fill);
  context.addPath(parsePath(icon.detail));
  context.setStrokeColor(DETAIL);
  context.setLineWidth(1.2);
  context.strokePath();
  return context.getImage();
}

function fillPath(context, path, color) {
  context.addPath(parsePath(path));
  context.setFillColor(new Color(color));
  context.fillPath();
}

// An SVG path of only M, L, Q and Z, as the server's icons are drawn.
function parsePath(text) {
  const path = new Path();
  text.match(/[MLQZ][^MLQZ]*/g).forEach((segment) => {
    const numbers = (segment.match(/-?[\d.]+/g) ?? []).map(Number);
    const points = numbers
      .filter((_, at) => at % 2 === 0)
      .map((x, at) => new Point(x, numbers[at * 2 + 1]));
    if (segment[0] === "M") path.move(points[0]);
    else if (segment[0] === "L") path.addLine(points[0]);
    else if (segment[0] === "Q") path.addQuadCurve(points[1], points[0]);
    else path.closeSubpath();
  });
  return path;
}
