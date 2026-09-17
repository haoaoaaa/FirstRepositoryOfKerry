# Recon report: compiling and running C on this Windows 11 box

Workspace: `C:\Users\Administrator\Desktop\git` · DSH file sandbox: **workspace-write** · approval prompts disabled.
Result: **a real local GCC is now installed inside the workspace and verified end-to-end.**

---

## 1. WSL — PRESENT ON DISK, BUT UNUSABLE IN THIS SANDBOX

| Command | Observed result |
|---|---|
| `wsl --status` | `Program 'wsl.exe' failed to run: Access is denied` + `[sandbox: file access denied under workspace-write mode]` |
| `wsl -l -v` (via `cmd /c ... > file 2>&1`) | `拒绝访问。` / `错误代码: Wsl/EnumerateDistros/Service/E_ACCESSDENIED` |
| `wsl --version` | same `Access is denied` |

`C:\Program Files\WSL` **does exist**, so WSL is installed on the machine — but the sandbox blocks
`wsl.exe` (and the LxssManager/vmcompute pipe), so **no distro could be enumerated and no `gcc` could be
tested inside one**. Not a usable option here; unknown (not proven absent) for a normal terminal.

## 2. Visual Studio / MSVC — NOT INSTALLED

| Check | Result |
|---|---|
| `C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe` | `False` (does not exist) |
| `C:\Program Files\Microsoft Visual Studio` / `... (x86)\...` | empty — no output from `Get-ChildItem` |
| `...\2022\BuildTools` (both roots) | `False`, `False` |
| `where cl.exe` | `INFO: Could not find files for the given pattern(s).` |
| recursive `-Depth 4` search for `cl.exe` in Program Files, Program Files (x86), `%LOCALAPPDATA%\Programs`, Desktop, `C:\tools`, Downloads | **0 hits** |

Only `C:\Program Files\MSBuild` / `C:\Program Files (x86)\MSBuild` exist (MSBuild ≠ a C compiler).
**MSVC is not usable.** Installing Build Tools requires admin + a multi-GB installer.

## 3. Portable / embedded compilers already on disk — NONE

Directory existence check:
```
C:\msys64 : False        C:\MinGW : False          C:\Strawberry : False
C:\mingw64 : False       C:\TDM-GCC-64 : False     C:\TDM-GCC-32 : False
C:\ProgramData\chocolatey : False                 C:\Users\Administrator\scoop : False
```
Bounded recursive search (`-Depth 4`) for `gcc.exe`, `clang.exe`, `tcc.exe`, `zig.exe`, `cl.exe` under
`C:\Program Files`, `C:\Program Files (x86)`, `%LOCALAPPDATA%\Programs`, Desktop, `C:\tools`, Downloads:
**0 hits.** The VS Code install (`C:\Users\Administrator\AppData\Local\Programs\Microsoft VS Code`) contains
**no** compiler binaries. `where gcc.exe / clang.exe / tcc.exe` → `Could not find files for the given pattern(s).`
Only baseline tooling is present: `Python 3.13.15`, `node v24.21.0`, `git 2.55.0.windows.5`,
`C:\Windows\System32\curl.exe`, `C:\Windows\System32\tar.exe`. No `7z.exe`, no `C:\Program Files\7-Zip\7z.exe`.

## 4. Package managers — none usable here

| Command | Result |
|---|---|
| `winget --version` / `winget --info` | **zero output**, `exit = -1978335231` = `0x8A150001` (APPINSTALLER_CLI_ERROR_INTERNAL_ERROR). `winget.exe` resolves to `C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\winget.exe` but is blocked in the sandbox (same failure class as `wsl.exe`). |
| `choco --version` | `CommandNotFoundException: The term 'choco' is not recognized...` |
| `scoop --version` | `CommandNotFoundException: The term 'scoop' is not recognized...` |

Even outside the sandbox, `winget` installs machine/user-wide and **cannot target a workspace-local directory**;
machine scope needs admin. `choco`/`scoop` are not installed at all.

## 5. Workspace-local portable toolchain — ✅ SUCCEEDED

WinLibs `.zip` was rejected by the task's own budget rule (261.3 MB > 200 MB) and its `.7z` needs 7-Zip
(absent). Chosen instead: **w64devkit 1.23.0** (plain `.zip`, `Expand-Archive`-compatible, self-contained).

Downloaded with Python `urllib` (see `_tools\get_toolchain.py`) after GitHub returned:
`HTTP 200 content-length=76798128 (73.2 MB)` → downloaded in **36 s**, `zip entries=6058`, extracted in 5 s.

```
FOUND ...\_tools\toolchain\w64devkit\bin\gcc.exe
FOUND ...\_tools\toolchain\w64devkit\bin\g++.exe
FOUND ...\_tools\toolchain\w64devkit\bin\make.exe
FOUND ...\_tools\toolchain\w64devkit\bin\gdb.exe
```

**Critical detail:** invoking `gcc.exe` by absolute path alone fails —
`gcc.exe: fatal error: cannot execute 'as': CreateProcess: No such file or directory` —
because w64devkit's `gcc` finds `as.exe`/`ld.exe` through `PATH`. **`...\w64devkit\bin` must be prepended to `PATH`.**

**End-to-end proof (local):**
```
PS> $env:PATH = "C:\Users\Administrator\Desktop\git\_tools\toolchain\w64devkit\bin;$env:PATH"
PS> gcc -o C:\Users\Administrator\Desktop\git\hello.exe C:\Users\Administrator\Desktop\git\hello.c
compile exit=0        (hello.exe = 70859 bytes)
PS> C:\Users\Administrator\Desktop\git\hello.exe
Hello, World!
run exit=0
```
`gcc --version` → `gcc.exe (GCC) 14.1.0`. Total on disk: **380.5 MB** (includes the 73.2 MB zip kept for re-extraction).

## 6. Online compiler APIs — WORK (fallback)

`curl.exe` **cannot do HTTPS in this sandbox**:
`curl: (35) schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030E)` for github/wandbox/godbolt,
and also with `-k` or `--ssl-no-revoke`. Plain HTTP works (`curl.exe http://example.com/` → `http_200`).
Working substitutes: **Python `urllib`** and **Node `fetch`** (both reached wandbox/github with HTTP 200).

| Service | Python POST | Result |
|---|---|---|
| Wandbox | `https://wandbox.org/api/compile.json`, `{"compiler":"gcc-13.2.0","code":"...","options":"warning","stdin":""}` | `http=200 status='0' program_output='hello from wandbox\n'` → **compiled AND ran** |
| Godbolt | `https://godbolt.org/api/compiler/cg132/compile` + `compilerOptions.executorRequest=true` | `HTTP 200`, `stdout: hello godbolt`, `code=0` → **compiled AND ran** (first attempt got a transient `WinError 10054` reset; the retry succeeded) |

Exact curl invocation (valid on a machine whose curl TLS works — **not runnable in this sandbox**):
```bat
curl.exe -sS -X POST -H "Content-Type: application/json" --data-binary "@wandbox_req.json" https://wandbox.org/api/compile.json -o wandbox_resp.json
```
Working in-sandbox equivalents: `_tools\wandbox_compile.py`, `_tools\godbolt_test.py`.

---

## RECOMMENDED APPROACH (beginner student on this machine)

Use the **workspace-local GCC** — already installed, no admin, no installer, works offline from now on.

**(a) compile `hello.c`** — copy-paste into PowerShell:
```powershell
$env:PATH = "C:\Users\Administrator\Desktop\git\_tools\toolchain\w64devkit\bin;$env:PATH"
cd C:\Users\Administrator\Desktop\git
gcc -Wall -o hello.exe hello.c
```
**(b) run it:**
```powershell
.\hello.exe
```
→ prints `Hello, World!`

Simplest of all for a beginner: double-click / run **`C:\Users\Administrator\Desktop\git\build.cmd`**
(compiles `hello.c` and runs `hello.exe` in one step — verified, `exit=0`, `Hello, World!`).
For any other C file: `.\cc.cmd -Wall -o myapp.exe myapp.c` then `.\myapp.exe` (verified, `exit=0`).

**Toolchain location:**
```
C:\Users\Administrator\Desktop\git\_tools\toolchain\w64devkit\bin\gcc.exe
C:\Users\Administrator\Desktop\git\_tools\toolchain\w64devkit\bin\   <-- prepend this to PATH
```
(rebuildable with `python C:\Users\Administrator\Desktop\git\_tools\get_toolchain.py`;
`...\w64devkit\w64devkit.exe` is an interactive shell launcher — not tested non-interactively.)

## BEST FALLBACK

1. **Wandbox web UI** — paste the program at https://wandbox.org, compiler `gcc-13.2.0`, click Run
   (proven working from this machine's network). Godbolt https://godbolt.org (`x86-64 gcc 13.2`) also works
   and can execute via "Execute the code" — proven reachable from here.
2. API-level fallback from a script: `python C:\Users\Administrator\Desktop\git\_tools\wandbox_compile.py`
   (works even though `curl.exe` HTTPS is broken in this sandbox).
3. If someone re-enables `curl.exe` TLS: the curl command in section 6.

## FACTS THAT DEPEND ON ADMIN RIGHTS / INTERNET

- **Internet required for**: the 73.2 MB w64devkit download (already done — the toolchain is now local and
  needs no network) and the Wandbox/Godbolt fallbacks.
- **Without internet and without admin**: this machine had **no** C compiler at all before this install
  (no WSL access, no MSVC, no MinGW anywhere on disk, no choco/scoop, winget blocked) → nothing would work.
  With the toolchain now extracted under the workspace, compilation works fully offline.
- **With admin** (and outside the sandbox) the cheap options become available: `winget install MSYS2.MSYS2`
  or `winget install BrechtSanders.WinLibs.POSIX.UCRT` (machine-wide, needs admin), `wsl --install` +
  `apt install gcc`, or the Visual Studio Build Tools installer. None of these were testable here:
  `winget` returns `0x8A150001` with no output, and `wsl.exe` returns `Access is denied` / `E_ACCESSDENIED`.
- **Sandbox-only quirks to remember**: `curl.exe` HTTPS fails (`SEC_E_NO_CREDENTIALS`) while HTTP works —
  use Python/Node for HTTPS; `npm install` needs `--cache "C:\Users\Administrator\Desktop\git\_tools\.npmcache"`;
  piping a native command's stdout to a PowerShell cmdlet dies with "Access is denied" — redirect to a file.
