#!/bin/sh
# bash_scope_guard.sh — PreToolUse hook (matcher: Bash)
#
# เทียบคำสั่งที่จะรันกับ allow_bash ของแผนที่อนุมัติแล้ว · ปิดช่องที่ agent เขียนไฟล์
# นอกแผนผ่าน shell แทนที่จะผ่าน tool Write/Edit (ซึ่ง plan_scope_guard ดูอยู่)
#
# ข้อจำกัดที่รู้ตัว — guardrail ไม่ใช่ security boundary (PLAYBOOK แถว R10 ห้ามเว้นว่าง
# และห้ามเคลมว่ากันได้ 100%):
#  - prefix matching: เลี่ยงได้ด้วย wrapper script หรือการเปลี่ยน cwd
#  - ยังไม่ครอบ: sed -i · python3 -c ที่เปิดไฟล์เขียน · editor ใน terminal
#               · script ที่ agent เขียนไว้ก่อนแล้วเรียกทีหลัง
#  - ครอบแล้ว: > >> tee dd (L-1b) · command chaining && || ; | ` $( และ newline (L-1)
#  - ค่าที่ตามหลัง -m/-F/--message/--file ที่พิสูจน์ได้ว่าเป็น quoted value จะไม่ถูกสแกน
#    metacharacter (ROADMAP P3) — เงื่อนไขการพิสูจน์อยู่ที่ mask_msg_args() ใน plan_scope.sh
#
# Failure mode ที่ทำให้ gate ปิดเงียบ (PB-04): เหมือน plan_scope_guard ทุกข้อ —
#  path ผิดใน settings.json → exit 127 ไม่บล็อก · timeout ไม่บล็อก · exit 1 ไม่บล็อก
#  · permission_mode **ไม่รู้จัก** → บล็อก (fail closed) · **ไม่มีฟิลด์เลย** → ถือว่า
#  unattended (บังคับให้ต้องมีแผน) ไม่ใช่บล็อกทุกอย่าง
#
# dependency: python3 · exit 0 = ผ่าน · exit 2 = บล็อก

set -uf

HERE=$(cd "$(dirname "$0")" && pwd)
PLAN_SCOPE="$HERE/../../scripts/plan_scope.sh"

# block <message> — ปฏิเสธ tool call · สัญญาต่างกันตามเครื่องมือ (ดูหมายเหตุยาวใน
# plan_scope_guard.sh): claude = stderr + exit 2 · qoder = JSON บน stdout + exit 0
# โดย `hookEventName` เป็นฟิลด์บังคับ · และห้าม emit "allow" เด็ดขาด
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
	block "bash_scope_guard: ไม่มี python3 — parse stdin ไม่ได้ ⇒ fail closed"

# command ต้องถูกส่งต่อ **ทั้งก้อนพร้อม newline** — ห้ามยุบ newline เป็น space:
#   newline เป็นตัวคั่นคำสั่งของ shell เท่ากับ `;` ⇒ ถ้ายุบ `git status<NL>rm -rf /` จะกลายเป็น
#   segment เดียวที่ขึ้นต้นด้วย `git status ` แล้ว **ผ่าน** allow_bash (fail-open ที่วัดได้จริง)
#   และ idiom `git commit -m "$(cat <<'EOF' … EOF)"` ของ Claude Code จะพังเป็นบรรทัดเดียวที่
#   plan_scope.sh พิสูจน์ไม่ได้ว่าเป็น heredoc ⇒ ถูกบล็อกทุกครั้ง (ROADMAP P3)
# ⇒ command เป็นฟิลด์ **สุดท้าย** เสมอ แล้วอ่านด้วย `sed -n '3,$p'` (บรรทัด 3 ถึงท้าย)
#   ห้ามสลับลำดับ print ทั้งสามบรรทัดนี้
DATA=$(python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
ti = d.get("tool_input") or {}
print(d.get("permission_mode") or "")
print(d.get("cwd") or "")
print(ti.get("command") or "")
' 2>/dev/null) || block "bash_scope_guard: parse stdin JSON ไม่สำเร็จ ⇒ fail closed"

MODE=$(printf '%s\n' "$DATA" | sed -n 1p)
CWD=$(printf '%s\n' "$DATA" | sed -n 2p)
CMD=$(printf '%s\n' "$DATA" | sed -n '3,$p')

[ -n "$CWD" ] || CWD=$(pwd)
ACTIVE="$CWD/docs/playbook/ACTIVE_PLAN"

# normalize: lowercase + ตัด `_` ⇒ ครอบทั้ง camelCase (Claude Code) และ snake_case
# (Qoder · เอกสารระบุว่า case-insensitive · alias yolo = bypass_permissions)
MODE_N=$(printf '%s' "$MODE" | tr 'A-Z' 'a-z' | tr -d '_')
case "$MODE_N" in
default | plan) UNATTENDED=0 ;;
acceptedits | auto | dontask | bypasspermissions | yolo) UNATTENDED=1 ;;
'')
	# ทางถอยเดียวกับ plan_scope_guard: ไม่มีฟิลด์ = ถือว่า unattended (เข้มกว่า)
	# ไม่ใช่บล็อกทุกอย่าง ซึ่งจะทำให้ guard ใช้กับเครื่องมือที่ไม่ส่งฟิลด์นี้ไม่ได้เลย
	UNATTENDED=1
	;;
*) block "bash_scope_guard: permission_mode ไม่รู้จัก ('$MODE') ⇒ fail closed" ;;
esac

if [ ! -f "$ACTIVE" ]; then
	[ "$UNATTENDED" -eq 0 ] && exit 0
	block "bash_scope_guard: บล็อกคำสั่ง \"$CMD\" — โหมด $MODE แต่ไม่มี docs/playbook/ACTIVE_PLAN ⇒ ไม่มีแผนให้ยึด"
fi

PLAN_REL=$(sed -n '1p' "$ACTIVE" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
[ -n "$PLAN_REL" ] || block "bash_scope_guard: docs/playbook/ACTIVE_PLAN ว่าง ⇒ fail closed"

case "$PLAN_REL" in
/*) PLAN="$PLAN_REL" ;;
*) PLAN="$CWD/$PLAN_REL" ;;
esac
[ -f "$PLAN" ] || block "bash_scope_guard: ACTIVE_PLAN ชี้ไปที่ '$PLAN_REL' ซึ่งไม่มีไฟล์อยู่ ⇒ fail closed"

# แผนที่ยังไม่ถูกเติม go_ahead = ยังไม่อนุมัติ ⇒ ยังไม่เริ่มงาน — เกณฑ์เดียวกับ plan_scope_guard
# (ถ้าด่านนี้อยู่แต่ฝั่ง Write/Edit จะเกิดสภาพ "แผนยังไม่อนุมัติแต่รันคำสั่งได้" ซึ่งไม่สมมาตร)
if ! sh "$PLAN_SCOPE" --go-ahead "$PLAN" >/dev/null 2>&1; then
	block "bash_scope_guard: แผน $PLAN_REL ยังไม่มี go_ahead จริง (ยังเป็น placeholder) ⇒ ยังไม่อนุมัติให้เริ่มงาน"
fi

REASON=$(PLAN_SCOPE_CWD="$CWD" sh "$PLAN_SCOPE" --check-cmd "$PLAN" "$CMD" 2>&1) && exit 0

block "$(
	cat <<EOF
bash_scope_guard: บล็อกคำสั่ง "$CMD"

แผนที่บังคับอยู่: $PLAN_REL
permission_mode ตอนถูกบล็อก: $MODE
เหตุผล: $REASON

ถ้าคำสั่งนี้จำเป็นต่องานในแผนจริง ให้ขอเพิ่มใน allow_bash ผ่าน PLAN AMENDMENT (base §4)
ห้ามหาทางเลี่ยงด้วย wrapper script, การเปลี่ยน cwd หรือ redirection
EOF
)"
