import ast

# --- CONFIG ---
source_path = r"/home/msutt/hal/eyes/eye_frame_composer.py"
output_path = r"/home/msutt/hal/eyes/code_outline.txt"
# ---------------

with open(source_path, "r") as f:
    tree = ast.parse(f.read())

lines = []

for node in tree.body:
    if isinstance(node, ast.ClassDef):
        lines.append(f"Class: {node.name}")
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(f"  - {item.name}")
        lines.append("")

with open(output_path, "w") as out:
    out.write("\n".join(lines))

print(f"[✓] Outline written to: {output_path}")
