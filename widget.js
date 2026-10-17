// what2wear: today's Outfit as a small Home Screen widget.
// Paste into Scriptable, set these two, and see the README.
const HOST = "https://<user>.pythonanywhere.com";
const TOKEN = "<the token>";

const BACKGROUND = Color.dynamic(new Color("#ffffff"), new Color("#1c1c1e"));
const LABEL = Color.dynamic(Color.black(), Color.white());
const SECONDARY = Color.dynamic(new Color("#8e8e93"), new Color("#98989d"));
const WARNING = Color.dynamic(new Color("#ff9500"), new Color("#ff9f0a"));
const IF_COLD_OPACITY = 0.4;
// The art's and the label's size for each number of rows, so a short
// Outfit fills the tile. An Outfit is 3 Garments, or 4 with Outerwear.
const ART_SIZES = { 3: 34, 4: 27 };
const LABEL_SIZES = { 3: 17, 4: 16 };
const ART_BOX = 76;

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
  if (answer?.error) return "⚠︎ Can't load your data";
  return "⚠︎ Renew PythonAnywhere?";
}

function getWidget(answer, message) {
  const widget = new ListWidget();
  widget.backgroundColor = BACKGROUND;
  widget.url = dayUrl;
  widget.setPadding(11, 16, 11, 16);
  const header = widget.addStack();
  if (message) {
    addText(header, message, Font.semiboldRoundedSystemFont(13), WARNING);
  } else if (answer) {
    const isStale = answer.date !== today;
    const shortDate = getFormatter("EEE d").string(
      getFormatter("yyyy-MM-dd").date(answer.date),
    );
    addText(
      header,
      answer.day === "office" ? "Office" : "Home",
      Font.boldRoundedSystemFont(13),
      LABEL,
    );
    addText(
      header,
      ` · ${isStale ? "⚠︎ " : ""}${shortDate}`,
      Font.semiboldRoundedSystemFont(13),
      isStale ? WARNING : SECONDARY,
    );
  }
  const outfit = answer?.outfit ?? [];
  const artSize = ART_SIZES[outfit.length] ?? ART_SIZES[3];
  const labelSize = LABEL_SIZES[outfit.length] ?? LABEL_SIZES[3];
  outfit.forEach((item) => {
    widget.addSpacer();
    addRow(widget, item, artSize, labelSize);
  });
  widget.addSpacer();
  return widget;
}

function addText(stack, text, font, color) {
  const widgetText = stack.addText(text);
  widgetText.font = font;
  widgetText.textColor = color;
  widgetText.lineLimit = 1;
  widgetText.minimumScaleFactor = 0.7;
  return widgetText;
}

// One Garment: its art and Label, dimmed and marked if worn only if
// cold. The art sits in a fixed-size stack and the gap is a fixed
// spacer, so the Labels line up: stacks ignore text alignment.
function addRow(widget, item, artSize, labelSize) {
  const row = widget.addStack();
  row.centerAlignContent();
  const opacity = item.if_cold ? IF_COLD_OPACITY : 1;
  const artStack = row.addStack();
  artStack.size = new Size(artSize, artSize);
  const image = artStack.addImage(drawArt(item.art));
  image.imageSize = new Size(artSize, artSize);
  image.imageOpacity = opacity;
  row.addSpacer(7);
  addText(
    row,
    item.label,
    Font.semiboldRoundedSystemFont(labelSize),
    LABEL,
  ).textOpacity = opacity;
  if (item.if_cold) {
    row.addSpacer();
    addText(row, "if cold", Font.semiboldRoundedSystemFont(11), SECONDARY);
  }
}

// Drawn in the art's own 76-unit box and scaled down whole, so stroke
// widths scale with it.
function drawArt(layers) {
  const context = new DrawContext();
  context.size = new Size(ART_BOX, ART_BOX);
  context.opaque = false;
  context.respectScreenScale = true;
  layers.forEach((layer) => {
    context.addPath(parsePath(layer.d));
    const color = new Color(layer.fill ?? layer.stroke, layer.alpha ?? 1);
    if (layer.fill) {
      context.setFillColor(color);
      context.fillPath();
    } else {
      context.setStrokeColor(color);
      context.setLineWidth(layer.width);
      context.strokePath();
    }
  });
  return context.getImage();
}

// An SVG path of only M, L, Q, C and Z, as the server's art is drawn.
function parsePath(text) {
  const path = new Path();
  text.match(/[MLQCZ][^MLQCZ]*/g).forEach((segment) => {
    const numbers = (segment.match(/-?[\d.]+/g) ?? []).map(Number);
    const points = numbers
      .filter((_, at) => at % 2 === 0)
      .map((x, at) => new Point(x, numbers[at * 2 + 1]));
    if (segment[0] === "M") path.move(points[0]);
    else if (segment[0] === "L") path.addLine(points[0]);
    else if (segment[0] === "Q") path.addQuadCurve(points[1], points[0]);
    else if (segment[0] === "C")
      path.addCurve(points[2], points[0], points[1]);
    else path.closeSubpath();
  });
  return path;
}
