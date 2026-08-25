from pathlib import Path

path = Path('backend/app/dashboard_assets/dashboard_inventory_views.js')
text = path.read_text(encoding='utf-8')

# re.sub replacement processing turns the intended JavaScript backslash-n escape
# into a literal line break. Normalize the two generated join separators to a
# single JavaScript \n escape so copied TSV contains real row breaks.
text = text.replace("text=rows.join('\n');count=cellSelectionCount()", "text=rows.join('\\n');count=cellSelectionCount()")
text = text.replace(".join('\n');count=indices.length", ".join('\\n');count=indices.length")

path.write_text(text, encoding='utf-8')
