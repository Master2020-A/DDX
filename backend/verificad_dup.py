from collections import defaultdict
from fastapi.routing import APIRoute


def print_duplicates(app: FastAPI):
    seen = defaultdict(list)

    for r in app.routes:
        if isinstance(r, APIRoute):
            for m in sorted(r.methods or []):
                key = (m, r.path)
                seen[key].append(r)

    dups = {k: v for k, v in seen.items() if len(v) > 1}
    if not dups:
        print("✅ No hay endpoints duplicados")
        return

    print("⚠️ Endpoints duplicados:")
    for (m, path), routes in sorted(dups.items()):
        print(f"  {m:6} {path}")
        for rr in routes:
            print(f"    - {rr.endpoint.__module__}.{rr.name}")


print_duplicates(app)
