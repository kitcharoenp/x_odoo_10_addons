#!/bin/sh
# gen_qoder_settings.sh — แปลง .claude/settings.json (canonical) → .qoder/settings.json
#
# ทำไมต้องมี: .claude/settings.json บังคับ allow/ask/deny + hooks ได้เฉพาะ Claude Code —
# เซสชัน Qoder ใน repo เดียวกันไม่อ่านไฟล์นั้น ⇒ guard ทั้งหมดเป็นโมฆะบน Qoder
# สคริปต์นี้แปลง canonical source เป็นฟอร์มของ Qoder เพื่อให้ guard ชุดเดียวกันทำงาน
# ทั้งสองเครื่องมือ โดย .claude/settings.json คงสถานะแหล่งความจริงเดียว (ห้ามแก้ฝั่ง Qoder
# ด้วยมือ — จะ drift)
#
# การแปลง (แผน review/proposal-p6-qoder-adapter/plan.md ภาคผนวก A):
#  - ถอด $schema (คนละ schema)
#  - permissions.allow/ask/deny + additionalDirectories: โครงสร้างเดิม
#  - Bash(x*) trailing * → Bash(x:*)  (prefix form ของ Qoder) · Bash(x *) glob คงเดิม
#  - Read/Edit/Write path: ./X → /X (rooted ที่ project root) · //abs/** และ ~/ คงเดิม
#  - Write(path) → Edit(path) — docs Qoder: rule Edit(...) ครอบการตรวจทั้ง Edit/Write/
#    NotebookEdit · ⚠️ พฤติกรรมเปลี่ยน: .claude มี Write deny + Edit ask บน BASE_PLAYBOOK.md
#    → หลังแปลง deny ชนะ (deny > ask) ซึ่งตรงปรัชญา repo แต่ต้องรู้ตัว
#  - WebFetch(domain:X): คงเดิม + WARN (syntax นอก docs — probe ยืนยันก่อนพึ่ง)
#  - hooks: ปลายทาง hooks/claude-code/ → hooks/qoder/ (wrapper ที่ตั้ง GUARD_HOST)
#           · matcher เพิ่มชื่อ tool จริงของ Qoder (SearchReplace/run_in_terminal/…)
#           · **ไม่แปลง** ${CLAUDE_PROJECT_DIR} — Qoder รับเป็น alias อยู่แล้ว
#
# พฤติกรรม: stdout เป็น default (POSIX sh ส่งออก binary ไม่ได้จึงต้องผ่าน python3)
#  -i <path>   input (default .claude/settings.json)
#  -o <path>   เขียนลงไฟล์ (สร้างไดเรกทอรีให้)
#  --check <p> แปลงแล้วเทียบกับ p · exit 0 = เหมือน · 1 = drift
#
# fail loud: rule ที่ parse ไม่ได้ / tool ไม่รู้จัก / `*` อยู่กลาง command → stderr + exit 3
# (ไม่เดา ไม่ปล่อยผ่านเงียบ ๆ — สอดคล้อง fail-closed ของ repo)
#
# dependency: python3 (parse JSON — ห้าม grep JSON เพราะพังกับ escaped char)
# exit 0 = สำเร็จ · 1 = ใช้ผิด/ไฟล์ขาด/drift · 3 = พบ pattern ที่ยังไม่รองรับ

set -uf

usage() {
	cat >&2 <<'USAGE'
usage: gen_qoder_settings.sh [-i <input>] [-o <output>] [--check <existing>]

  -i <path>    ไฟล์ input (default: .claude/settings.json)
  -o <path>    เขียนผลลัพธ์ลงไฟล์ (default: stdout)
  --check <p>  แปลงแล้วเทียบกับไฟล์ที่มีอยู่ — exit 0 = เหมือน · 1 = drift
USAGE
	exit 1
}

command -v python3 >/dev/null 2>&1 || {
	echo "gen_qoder_settings: ไม่มี python3 — convert ไม่ได้" >&2
	exit 1
}

INPUT=".claude/settings.json"
OUTPUT=""
CHECK=""

while [ $# -gt 0 ]; do
	case "$1" in
		-i) [ $# -ge 2 ] || usage; INPUT="$2"; shift 2 ;;
		-o) [ $# -ge 2 ] || usage; OUTPUT="$2"; shift 2 ;;
		--check) [ $# -ge 2 ] || usage; CHECK="$2"; shift 2 ;;
		*) usage ;;
	esac
done

if [ -n "$OUTPUT" ] && [ -n "$CHECK" ]; then
	echo "gen_qoder_settings: ใช้ -o ร่วมกับ --check ไม่ได้" >&2
	exit 1
fi
[ -f "$INPUT" ] || { echo "gen_qoder_settings: ไม่พบ $INPUT" >&2; exit 1; }
if [ -n "$CHECK" ] && [ ! -f "$CHECK" ]; then
	echo "gen_qoder_settings: ไม่พบไฟล์ --check: $CHECK" >&2
	exit 1
fi

# ส่ง INPUT/OUTPUT/CHECK ผ่าน env — ไม่ต้องกังวล quoting ข้ามชั้น shell
GEN_INPUT="$INPUT" GEN_OUTPUT="$OUTPUT" GEN_CHECK="$CHECK" python3 - <<'PYEOF'
import json, os, sys

src = os.environ["GEN_INPUT"]
out_path = os.environ["GEN_OUTPUT"]
check_path = os.environ["GEN_CHECK"]

KNOWN_TOOLS = {"Read", "Edit", "Write", "Bash", "WebFetch", "WebSearch",
               "Agent", "Grep", "Glob"}
warns = []
errors = []


def warn(msg):
    warns.append(msg)
    print(f"gen_qoder_settings: WARN {msg}", file=sys.stderr)


def die(msg):
    errors.append(msg)
    print(f"gen_qoder_settings: ERROR {msg}", file=sys.stderr)


def split_rule(rule):
    """แยก 'Tool(content)' — content อาจมี escaped parens (docs Qoder)"""
    if "(" in rule and rule.endswith(")"):
        return rule[:rule.index("(")], rule[rule.index("(") + 1:-1]
    if "(" in rule or rule.endswith(")"):
        die(f"rule ผิดรูป (วงเล็บไม่ครบ): {rule!r}")
        return None, None
    return rule, None


def conv_bash(content, rule):
    if "*" not in content:
        return content                      # exact match — ทั้งสองเครื่องมือตรงกัน
    if content.endswith(" *"):
        return content                      # glob form — docs Qoder รองรับ
    if content.endswith("*"):
        return content[:-1] + ":*"          # trailing * → prefix form ของ Qoder
    die(f"Bash rule มี '*' กลาง command — ยังไม่รองรับ: {rule!r}")
    return None


def conv_path(content):
    if content.startswith("//"):            # absolute (double-slash) — คงเดิม
        return content
    if content.startswith("~/"):            # home-based — คงเดิม
        return content
    if content.startswith("./"):            # Claude relative → rooted ของ Qoder
        return "/" + content[2:]
    if content.startswith("/"):             # rooted อยู่แล้ว
        return content
    return content                          # rootless pattern (*.secret) — คงเดิม


def conv_rule(rule):
    tool, content = split_rule(rule)
    if tool is None:
        return None
    if tool not in KNOWN_TOOLS:
        die(f"tool ไม่รู้จัก: {rule!r}")
        return None
    if content is None:
        return rule                         # tool-level rule
    if tool == "Bash":
        c = conv_bash(content, rule)
        return None if c is None else f"Bash({c})"
    if tool == "WebFetch" and content.startswith("domain:"):
        warn(f"WebFetch(domain:) ไม่ใช่ syntax ใน docs ของ Qoder — คงเดิมแต่"
             f"อย่าพึ่งจนกว่า probe ยืนยัน: {rule!r}")
        return rule
    if tool in ("Read", "Edit", "Write"):
        if tool == "Write":
            warn(f"Write(...) → Edit(...) — Qoder ตรวจ Write ผ่าน rule Edit(...): {rule!r}")
            tool = "Edit"
        return f"{tool}({conv_path(content)})"
    return rule                             # WebSearch/Agent/Grep/Glob — คงเดิม


def dedupe(items):
    seen = []
    for x in items:
        if x not in seen:
            seen.append(x)
    return seen


with open(src) as f:
    doc = json.load(f)

out = {}

perm = doc.get("permissions") or {}
perms_out = {}
for key in ("allow", "ask", "deny"):
    conv = [r for r in map(conv_rule, perm.get(key) or []) if r is not None]
    if conv:
        perms_out[key] = dedupe(conv)
for key in ("additionalDirectories",):      # โครงสร้างตรงกันทั้งสองเครื่องมือ
    if key in perm:
        perms_out[key] = perm[key]
if perms_out:
    out["permissions"] = perms_out

# hooks — สองอย่างที่ต้องเปลี่ยน และหนึ่งอย่างที่ **ไม่ต้อง** เปลี่ยน
#
# ไม่ต้องเปลี่ยน: `${CLAUDE_PROJECT_DIR}` — Qoder รับชื่อนี้เป็น alias อยู่แล้ว
#   (replacePlaceholders() ใน qodercli map ทั้ง ${QODER_PROJECT_DIR} และ
#   ${CLAUDE_PROJECT_DIR} ไปที่ cwd เดียวกัน และ export ทั้งสองชื่อเป็น env var
#   ให้ hook subprocess) ⇒ การแปลงชื่อเป็นโค้ดที่ต้องดูแลโดยไม่ได้ผลอะไร
#
# ต้องเปลี่ยน:
#   1. ปลายทางสคริปต์ → hooks/qoder/*.sh (wrapper ที่ตั้ง GUARD_HOST=qoder เพื่อให้
#      block() render สัญญาของ Qoder: JSON บน stdout + exit 0 ไม่ใช่ exit 2)
#   2. matcher → เพิ่มชื่อ tool จริงของ Qoder ต่อจากชื่อ canonical เพราะ IDE เรียก
#      ตัวแก้ไฟล์ว่า SearchReplace/search_replace/create_file และเรียกตัวรันคำสั่งว่า
#      run_in_terminal ⇒ matcher ที่มีแต่ "Edit|Write" จะไม่ชนอะไรเลย
HOOK_DIR_MAP = ("/hooks/claude-code/", "/hooks/qoder/")
MATCHER_EXTRA = {
    "Edit|Write|NotebookEdit": "Edit|Write|NotebookEdit|SearchReplace|search_replace|create_file|apply_patch",
    "Bash": "Bash|run_in_terminal",
}

hooks = doc.get("hooks") or {}
hooks_out = {}
for event, groups in hooks.items():
    gs = []
    for g in groups:
        g2 = dict(g)
        if "matcher" in g2 and g2["matcher"] in MATCHER_EXTRA:
            g2["matcher"] = MATCHER_EXTRA[g2["matcher"]]
        hs = []
        for h in g.get("hooks") or []:
            h2 = dict(h)
            cmd = h2.get("command")
            if cmd:
                if HOOK_DIR_MAP[0] not in cmd:
                    warn(f"hook command ไม่ได้ชี้ {HOOK_DIR_MAP[0]} — ปล่อยผ่านตามเดิม: {cmd!r}")
                h2["command"] = cmd.replace(*HOOK_DIR_MAP)
            hs.append(h2)
        g2["hooks"] = hs
        gs.append(g2)
    hooks_out[event] = gs

# ใน subagent ของ Qoder เอกสารระบุว่า `Stop` ถูก remap เป็น `SubagentStop`
# ⇒ ถ้าลงทะเบียนแค่ Stop ด่านนี้จะเงียบเมื่องานจบใน subagent · ลงทะเบียนทั้งคู่
# (ข้อจำกัดที่ยังไม่ยืนยัน: เอกสารเงียบว่า hook ระดับ settings fire ใน subagent ไหม)
if "Stop" in hooks_out and "SubagentStop" not in hooks_out:
    hooks_out["SubagentStop"] = [dict(g) for g in hooks_out["Stop"]]

if hooks_out:
    out["hooks"] = hooks_out

# $schema ของ Claude Code ไม่ใช้กับ Qoder — ถอดออกโดยเจตนา

if errors:
    sys.exit(3)

if check_path:
    with open(check_path) as f:
        existing = json.load(f)
    if existing == out:
        print("gen_qoder_settings: no drift")
        sys.exit(0)
    print("gen_qoder_settings: DRIFT — ไฟล์ที่มีอยู่ต่างจากผลแปลง", file=sys.stderr)
    sys.exit(1)

rendered = json.dumps(out, indent=2, ensure_ascii=False)
if out_path:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write(rendered + "\n")
else:
    print(rendered)
PYEOF
