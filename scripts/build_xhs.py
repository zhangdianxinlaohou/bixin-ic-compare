"""Build the Xiaohongshu/mobile shell and its single-file version."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
XHS_CSS = ROOT / "xiaohongshu.css"
DATA = ROOT / "data.js"
GLOBAL_DATA = ROOT / "global_data.js"
ECHARTS = ROOT / "vendor" / "echarts.min.js"
APP = ROOT / "app.js"
MOBILE_HTML = ROOT / "xiaohongshu.html"
STANDALONE = ROOT / "IC-Compare-小红书版.html"


BOTTOM_NAV = """
    <nav class="xhs-bottom-nav" aria-label="快速导航">
      <a href="#compare" data-nav="compare" class="is-active">对比</a>
      <a href="#metrics" data-nav="metrics">指标</a>
      <a href="#history" data-nav="history">近年</a>
    </nav>
"""


def safe_script(source: str) -> str:
    return source.replace("</script", "<\\/script")


def transform() -> str:
    html = INDEX.read_text(encoding="utf-8")
    html = html.replace(
        '<html lang="zh-CN">',
        '<html lang="zh-CN" class="xhs-document">',
        1,
    )
    html = html.replace("<body>", '<body class="xhs-mode">', 1)
    html = html.replace(
        'content="width=device-width, initial-scale=1.0"',
        'content="width=device-width, initial-scale=1.0, viewport-fit=cover"',
        1,
    )
    html = html.replace(
        "<title>比芯 · 芯片公司的照妖镜</title>",
        "<title>比芯 · 小红书版</title>",
        1,
    )
    html = html.replace(
        '<link rel="stylesheet" href="styles.css" />',
        '<link rel="stylesheet" href="styles.css" />\n'
        '    <link rel="stylesheet" href="xiaohongshu.css" />',
        1,
    )
    html = html.replace(
        '    <div class="toast" id="toast" role="status" aria-live="polite"></div>',
        BOTTOM_NAV
        + '\n    <div class="toast" id="toast" role="status" aria-live="polite"></div>',
        1,
    )
    return html


def standalone(html: str) -> str:
    css = CSS.read_text(encoding="utf-8")
    xhs_css = XHS_CSS.read_text(encoding="utf-8")
    data = safe_script(DATA.read_text(encoding="utf-8"))
    global_data = safe_script(GLOBAL_DATA.read_text(encoding="utf-8"))
    echarts = safe_script(ECHARTS.read_text(encoding="utf-8"))
    app = safe_script(APP.read_text(encoding="utf-8"))

    html = html.replace(
        '<link rel="stylesheet" href="styles.css" />\n'
        '    <link rel="stylesheet" href="xiaohongshu.css" />',
        f"<style>\n{css}\n</style>\n<style>\n{xhs_css}\n</style>",
        1,
    )
    html = html.replace(
        '<script src="data.js"></script>',
        f"<script>\n{data}\n</script>",
        1,
    )
    html = html.replace(
        '<script src="global_data.js"></script>',
        f"<script>\n{global_data}\n</script>",
        1,
    )
    html = html.replace(
        '<script src="vendor/echarts.min.js"></script>',
        f"<script>\n{echarts}\n</script>",
        1,
    )
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>\n{app}\n</script>",
        1,
    )
    return html


def main() -> None:
    mobile = transform()
    MOBILE_HTML.write_text(mobile, encoding="utf-8")
    bundle = standalone(mobile)
    STANDALONE.write_text(bundle, encoding="utf-8")
    print(f"Wrote {MOBILE_HTML.name}")
    print(f"Wrote {STANDALONE.name} ({STANDALONE.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
