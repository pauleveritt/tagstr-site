import json
import pathlib
import argparse

p = argparse.ArgumentParser()
p.add_argument("json_path")
p.add_argument("--whl-url", required=True)
args = p.parse_args()

path = pathlib.Path(args.json_path)
data = json.loads(path.read_text())

kernel_key = "@jupyterlite/pyodide-kernel-extension:kernel"
plugin = data.setdefault("jupyter-config-data", {}) \
             .setdefault("litePluginSettings", {}) \
             .setdefault(kernel_key, {})

plugin["pyodideUrl"] = (
    "https://koxudaxi.github.io/pyodide/tstrings/pyodide.js"
)

opt = plugin.setdefault("loadPyodideOptions", {})
opt["indexURL"] = "https://koxudaxi.github.io/pyodide/tstrings/"
opt["packages"] = [args.whl_url]

path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
