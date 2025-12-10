import os
import sys
import runpy

BASE_DIR = os.path.dirname(__file__)     
indexes_dir = os.path.join(BASE_DIR, "indexes") 


action = sys.argv[1] if len(sys.argv) > 1 else "create"

print(f"\n Running ES index ops: {action.upper()}\n")

for file in os.listdir(indexes_dir):
    if not file.endswith(".py") or file.startswith("__"):
        continue

    module_name = f"es.indexes.{file[:-3]}"  # remove .py
    print(f" Running: {module_name} -> {action}")

    runpy.run_module(module_name, run_name="__main__", alter_sys=True, init_globals={"__action__": action})

print("\nDONE\n")
