import os, time, urllib.request, zipfile, ssl

BASE = r"C:\Users\Administrator\Desktop\git\_tools\toolchain"
ZIP = os.path.join(BASE, "w64devkit-1.23.0.zip")
URL = "https://github.com/skeeto/w64devkit/releases/download/v1.23.0/w64devkit-1.23.0.zip"
LOG = os.path.join(BASE, "download_log.txt")
DEADLINE = 300  # seconds

os.makedirs(BASE, exist_ok=True)
log = open(LOG, "w", encoding="utf-8", buffering=1)

def say(msg):
    log.write(msg + "\n")
    try:
        print(msg)
    except Exception:
        pass

start = time.time()
say(f"START {time.strftime('%H:%M:%S')} url={URL}")
try:
    req = urllib.request.Request(URL, headers={"User-Agent": "probe/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(ZIP, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        say(f"HTTP {r.status} content-length={total} ({total/1048576:.1f} MB)")
        done = 0
        last = 0
        while True:
            if time.time() - start > DEADLINE:
                say(f"TIMEOUT after {time.time()-start:.0f}s at {done/1048576:.1f} MB")
                raise SystemExit(2)
            chunk = r.read(262144)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if done - last >= 8 * 1048576:
                last = done
                say(f"  downloaded {done/1048576:.1f} MB in {time.time()-start:.0f}s")
    say(f"DOWNLOAD OK size={os.path.getsize(ZIP)} bytes in {time.time()-start:.0f}s")
except SystemExit:
    raise
except Exception as e:
    say(f"DOWNLOAD FAILED {type(e).__name__}: {e}")
    raise SystemExit(1)

try:
    t0 = time.time()
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        say(f"zip entries={len(names)} first={names[0]}")
        z.extractall(BASE)
    say(f"EXTRACT OK in {time.time()-t0:.0f}s -> {BASE}")
except Exception as e:
    say(f"EXTRACT FAILED {type(e).__name__}: {e}")

for root, dirs, files in os.walk(BASE):
    for fn in files:
        if fn.lower() in ("gcc.exe", "g++.exe", "make.exe", "gdb.exe"):
            say("FOUND " + os.path.join(root, fn))
say(f"DONE total={time.time()-start:.0f}s")
