import json, urllib.request

TOOLS = r"C:\Users\Administrator\Desktop\git\_tools"
CODE = '#include <stdio.h>\nint main(void){ printf("hello from wandbox\\n"); return 0; }\n'

def post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "probe/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, r.read()

log = []
for compiler in ["gcc-13.2.0", "gcc-12.3.0", "gcc-head"]:
    payload = {"compiler": compiler, "code": CODE, "options": "warning", "stdin": ""}
    try:
        status, body = post("https://wandbox.org/api/compile.json", payload)
        resp = json.loads(body.decode("utf-8", "replace"))
        log.append(f"compiler={compiler} http={status} status={resp.get('status')!r} "
                   f"program_output={resp.get('program_output')!r} "
                   f"compiler_output={resp.get('compiler_output')!r} "
                   f"compiler_error={resp.get('compiler_error')!r}")
        with open(rf"{TOOLS}\wandbox_resp_{compiler}.json", "wb") as f:
            f.write(body)
        if resp.get("status") == "0" and "hello from wandbox" in (resp.get("program_output") or ""):
            log.append("SUCCESS: wandbox compiled AND ran the program end-to-end")
            break
    except Exception as e:
        log.append(f"compiler={compiler} ERROR {type(e).__name__}: {e}")
else:
    # find valid gcc compiler names
    try:
        with urllib.request.urlopen("https://wandbox.org/api/list.json", timeout=60) as r:
            lst = json.loads(r.read().decode("utf-8", "replace"))
        names = [c["name"] for c in lst if "gcc" in c["name"].lower() or "g++" in c["name"].lower()]
        log.append("AVAILABLE GCC COMPILERS: " + ", ".join(names[:40]))
    except Exception as e:
        log.append(f"list.json ERROR {type(e).__name__}: {e}")

with open(rf"{TOOLS}\wandbox_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log) + "\n")
print("\n".join(log))
