#!/bin/sh
# plan_scope_guard.sh — PreToolUse hook (matcher: Edit|Write|NotebookEdit)
#
# บังคับ scope ของแผนที่อนุมัติแล้วในระดับเครื่องมือ — prose ในไฟล์ playbook เพิ่มโอกาส
# ที่ agent จะทำตาม แต่ไม่รับประกัน · ตัวบังคับจริงคือ permission rule หรือ hook แบบนี้
#
# ลงทะเบียนที่ .claude/settings.json เท่านั้น (canonical) — ห้ามลงทะเบียนผ่าน frontmatter
# `hooks:` ของ SKILL.md เพราะ hook ที่ผูกกับการเรียก skill = ขึ้นกับดุลพินิจของโมเดล
# ⇒ ไม่ใช่ตัวบังคับ · และ hook entries merge ข้ามแหล่ง ไม่ใช่ replace ⇒ เสี่ยง double-run
#
# ---------------------------------------------------------------------------
# docs/playbook/ACTIVE_PLAN คือ **สำเนาการอนุมัติ ไม่ใช่ตัวอนุมัติ**
#   การอนุมัติเกิดจากผู้ใช้ในบทสนทนาปัจจุบันเท่านั้น (base §8 ข้อ 10)
#   ไฟล์นี้เป็นจุดยึดให้ hook รู้ว่า "แผนไหนกำลังบังคับอยู่" — การมีไฟล์ไม่ได้แปลว่า
#   agent ได้รับอนุญาตให้ทำอะไรก็ได้ และ agent ห้ามเขียนไฟล์นี้เอง (อยู่ใน deny_write)
# ---------------------------------------------------------------------------
#
# Failure mode ที่ทำให้ gate ปิดเงียบ — ต้องรู้ก่อนติดตั้ง (PB-04):
#   1. path ของ hook ผิดใน settings.json → shell exit 127 = **ไม่บล็อก**
#      เอกสารทางการ: "a mistyped path in settings.json leaves the gate silently disabled"
#   2. hook timeout → **ไม่บล็อก** tool call
#   3. exit 1 → **ไม่บล็อก** (non-blocking error) · มีแต่ exit 2 เท่านั้นที่บล็อก
#   4. permission_mode **เป็นค่าที่ไม่รู้จัก** → บล็อก (fail closed) — กฎของเราเอง
#      แต่ถ้า **ไม่มีฟิลด์นี้เลย** → ถือว่า unattended (บังคับให้ต้องมีแผนทุกครั้ง)
#      ไม่ใช่บล็อกทุกอย่าง เพราะเครื่องมือบางตัวไม่ส่งฟิลด์นี้มา ⇒ ดู case ด้านล่าง
#
# dependency: python3 (parse JSON) — ประกาศตรง ๆ ห้าม grep JSON เพราะพังกับ escaped char
# ข้อจำกัด: ชื่อไฟล์ที่มี newline ไม่รองรับ · เป็น guardrail ไม่ใช่ security boundary
#
# exit 0 = ปล่อยผ่านไปตาม permission flow ปกติ · exit 2 = บล็อก (stderr ส่งให้ Claude อ่าน)

set -uf

HERE=$(cd "$(dirname "$0")" && pwd)
PLAN_SCOPE="$HERE/../../scripts/plan_scope.sh"

# block <message> — ปฏิเสธ tool call · **สองเครื่องมือใช้สัญญาไม่เหมือนกัน**
#   claude (default) : stderr + exit 2
#   qoder            : PreToolUse ต้องเป็น JSON บน stdout + exit 0
#                      · `hookEventName` เป็นฟิลด์บังคับ ถ้าขาด Qoder ทิ้ง JSON ทั้งก้อน
#                        แล้วกลายเป็น "ไม่บล็อก" แบบเงียบ
# ห้าม emit permissionDecision "allow" เด็ดขาด — เอกสาร Qoder ระบุว่า allow จะ
# short-circuit ข้าม permission pipeline ทั้งชุด **รวม deny rules ของเราเอง**
# ⇒ ทางปล่อยผ่านมีทางเดียวคือ exit 0 เงียบ ๆ โดยไม่พิมพ์อะไร
block() {
	case "$(printf '%s' "${GUARD_HOST:-claude}" | tr 'A-Z' 'a-z')" in
	qoder)
		printf '%s' "$1" | python3 -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": sys.stdin.read(),
}}))
'
		exit 0
		;;
	*)
		printf '%s\n' "$1" >&2
		exit 2
		;;
	esac
}

command -v python3 >/dev/null 2>&1 ||
	block "plan_scope_guard: ไม่มี python3 — parse stdin ไม่ได้ ⇒ fail closed (บล็อกไว้ก่อน)"

DATA=$(python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
ti = d.get("tool_input") or {}
print(d.get("permission_mode") or "")
print(d.get("cwd") or "")
print(ti.get("file_path") or ti.get("notebook_path") or "")
' 2>/dev/null) || block "plan_scope_guard: parse stdin JSON ไม่สำเร็จ ⇒ fail closed"

MODE=$(printf '%s\n' "$DATA" | sed -n 1p)
CWD=$(printf '%s\n' "$DATA" | sed -n 2p)
FILE=$(printf '%s\n' "$DATA" | sed -n 3p)

[ -n "$CWD" ] || CWD=$(pwd)
ACTIVE="$CWD/docs/playbook/ACTIVE_PLAN"

# permission_mode: ค่านี้มาจากตัวเครื่องมือ ไม่ใช่ output ของโมเดล ⇒ โมเดลปลอมไม่ได้
#
# normalize ก่อนเทียบ: lowercase + ตัด `_` ⇒ รองรับทั้ง camelCase ของ Claude Code
# และ snake_case ของ Qoder ด้วยรายการเดียว (accept_edits = acceptEdits = ACCEPT_EDITS)
# เอกสาร Qoder ระบุว่าชื่อโหมด **case-insensitive** และมี alias yolo = bypass_permissions
MODE_N=$(printf '%s' "$MODE" | tr 'A-Z' 'a-z' | tr -d '_')
case "$MODE_N" in
default | plan) UNATTENDED=0 ;;
acceptedits | auto | dontask | bypasspermissions | yolo) UNATTENDED=1 ;;
'')
	# ทางถอย (ADOPTING.md §7): เครื่องมือบางตัวไม่ส่งฟิลด์นี้มาเลย — ถ้า fail closed
	# ตรงนี้ guard จะบล็อก **ทุก** tool call จนใช้งานไม่ได้ ⇒ ถือว่า unattended แทน
	# ซึ่งเป็นทิศทางที่เข้มกว่า ไม่ใช่หลวมกว่า: บังคับให้ต้องมีแผนที่อนุมัติแล้วทุกครั้ง
	UNATTENDED=1
	;;
*) block "plan_scope_guard: permission_mode ไม่รู้จัก ('$MODE') ⇒ fail closed" ;;
esac

if [ ! -f "$ACTIVE" ]; then
	# ไม่มีแผน + โหมดที่มีคนดูอยู่ = งาน ATOMIC ตาม base §2 ไม่ต้องมีแผน
	[ "$UNATTENDED" -eq 0 ] && exit 0
	block "$(
		cat <<EOF
plan_scope_guard: บล็อกการเขียน "$FILE"

โหมดปัจจุบันคือ $MODE (ไม่มีคนกดอนุมัติทีละครั้ง) แต่ไม่มีไฟล์ docs/playbook/ACTIVE_PLAN
⇒ ไม่มีแผนที่ถูกอนุมัติให้ยึด จึงไม่มีขอบเขตให้บังคับ

ทางออก (เจ้าของ repo เป็นคนทำ ไม่ใช่ agent):
  1. ขอ go-ahead ในบทสนทนา — การอนุมัติเกิดที่นั่น ไม่ใช่ในไฟล์
  2. เจ้าของเขียน docs/playbook/ACTIVE_PLAN บรรทัดเดียวชี้ path ของแผนที่อนุมัติแล้ว
     (ไฟล์นี้เป็นสำเนาการอนุมัติ ไม่ใช่ตัวอนุมัติ — agent เขียนเองไม่ได้)
EOF
	)"
fi

PLAN_REL=$(sed -n '1p' "$ACTIVE" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
[ -n "$PLAN_REL" ] || block "plan_scope_guard: docs/playbook/ACTIVE_PLAN ว่าง ⇒ fail closed"

case "$PLAN_REL" in
/*) PLAN="$PLAN_REL" ;;
*) PLAN="$CWD/$PLAN_REL" ;;
esac
[ -f "$PLAN" ] || block "plan_scope_guard: ACTIVE_PLAN ชี้ไปที่ '$PLAN_REL' ซึ่งไม่มีไฟล์อยู่ ⇒ fail closed"

# แผนที่ยังไม่ถูกเติม go_ahead = ยังไม่อนุมัติ — hook ไม่เติมให้เอง (อยู่ใน deny_write)
if ! sh "$PLAN_SCOPE" --go-ahead "$PLAN" >/dev/null 2>&1; then
	block "plan_scope_guard: แผน $PLAN_REL ยังไม่มี go_ahead จริง (ยังเป็น placeholder) ⇒ ยังไม่อนุมัติ"
fi

REASON=$(PLAN_SCOPE_CWD="$CWD" sh "$PLAN_SCOPE" --check-path "$PLAN" "$FILE" 2>&1) && exit 0

block "$(
	cat <<EOF
plan_scope_guard: บล็อกการเขียน "$FILE"

แผนที่บังคับอยู่: $PLAN_REL
permission_mode ตอนถูกบล็อก: $MODE
เหตุผล: $REASON

ห้ามหาทางเลี่ยง (redirection, sed -i, wrapper script) — ถ้างานนี้จำเป็นจริง
ให้ emit บล็อกนี้แล้วหยุดรอเจ้าของ repo ตัดสิน (base §4):

PLAN AMENDMENT
Reason: <ทำไมต้องแตะไฟล์นอกแผน>
Affected contract: <สัญญา/ไฟล์ที่กระทบ>
Proposed change: <สิ่งที่ขอแก้ในแผน>
Alternatives: <ทางเลือกที่พิจารณาแล้ว>
Requested decision: <คำถามที่ต้องการคำตอบ>
EOF
)"
