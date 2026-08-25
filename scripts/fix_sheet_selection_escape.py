from pathlib import Path

path = Path('backend/app/dashboard_assets/dashboard_inventory_views.js')
text = path.read_text(encoding='utf-8')

# The one-shot regex patch intentionally writes JavaScript from Python. re.sub replacement
# processing turns the intended \\n string escape into a literal line break; normalize those
# two generated join separators before JS syntax validation.
text = text.replace("text=rows.join('\n');count=cellSelectionCount()", "text=rows.join('\\\\n');count=cellSelectionCount()")
text = text.replace(".join('\n');count=indices.length", ".join('\\\\n');count=indices.length")

path.write_text(text, encoding='utf-8')
