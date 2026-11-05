"""Bundle the static site into one shareable HTML file."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
CSS = ROOT / "styles.css"
DATA = ROOT / "data.js"
ECHARTS = ROOT / "vendor" / "echarts.min.js"
GLOBAL_DATA = ROOT / "global_data.js"
APP = ROOT / "app.js"
OUTPUT = ROOT / "IC-Compare-单文件版.html"


def safe_script(source: str) -> str:
    return source.replace("</script", "<\\/script")


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    data = safe_script(DATA.read_text(encoding="utf-8"))
    echarts = safe_script(ECHARTS.read_text(encoding="utf-8"))
    global_data = safe_script(GLOBAL_DATA.read_text(encoding="utf-8"))
    app = safe_script(APP.read_text(encoding="utf-8"))

    html = html.replace(
        '<link rel="stylesheet" href="styles.css" />',
        f"<style>\n{css}\n</style>",
    )
    html = html.replace(
        '<script src="data.js"></script>',
        f"<script>\n{data}\n</script>",
    )
    html = html.replace(
        '<script src="vendor/echarts.min.js"></script>',
        f"<script>\n{echarts}\n</script>",
    )
    html = html.replace(
        '<script src="global_data.js"></script>',
        f"<script>\n{global_data}\n</script>",
    )
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>\n{app}\n</script>",
    )
    html = html.replace(
        "<title>比芯 · 芯片公司的照妖镜</title>",
        "<title>比芯 · 芯片公司的照妖镜（单文件版）</title>",
    )

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
