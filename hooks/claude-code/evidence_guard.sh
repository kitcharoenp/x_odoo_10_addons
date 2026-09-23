#!/bin/sh
# evidence_guard.sh — Stop hook
#
# DoD "ต้องแนบ Evidence Block" เป็นข้อบังคับที่ไม่เคยมีตัวตรวจ — ไฟล์นี้คือตัวตรวจนั้น
# ตรวจตอน agent กำลังจะหยุด: แผนที่บังคับอยู่ประกาศ evidence_path ไว้ที่ไหน
# แล้วไฟล์นั้นมีบรรทัดสรุป "Gate ที่ไม่ผ่าน / ความเสี่ยงที่ยังเหลือ" ที่ **มีเนื้อหาจริง** ไหม
#
# ---------------------------------------------------------------------------
# ห้ามเคลมว่ากันลืม Evidence Block ได้เด็ดขาด
#   `stop_hook_active` มีไว้กัน loop ⇒ hook นี้บล็อกได้จำกัด และเครื่องมืออาจ override
#   hook ที่บล็อกติดกันหลายครั้ง (ตัวเลขที่แน่นอนยืนยันจากเอกสารไม่ได้ จึงไม่อ้างตัวเลข)
#   ⇒ เป็น **ตัวเตือน** ไม่ใช่ตัวบังคับสมบูรณ์
# ---------------------------------------------------------------------------
#
# Failure mode ที่ทำให้ gate ปิดเงียบ (PB-04): path ผิดใน settings.json → exit 127
# ไม่บล็อก · timeout ไม่บล็อก · exit 1 ไม่บล็อก · มีแต่ exit 2 ที่บล็อก
#
# dependency: python3 · exit 0 = ปล่อยให้หยุด · exit 2 = ไม่ให้หยุด (บทสนทนาไปต่อ)

set -uf

MARKER='Gate ที่ไม่ผ่าน / ความเสี่ยงที่ยังเหลือ'

block() {
	printf '%s\n' "$1" >&2
	exit 2
}

command -v python3 >/dev/null 2>&1 || exit 0 # ไม่มี python3 = ตรวจไม่ได้ · ไม่บล็อกการหยุด

DATA=$(python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
print("1" if d.get("stop_hook_active") else "0")
print(d.get("cwd") or "")
' 2>/dev/null) || exit 0

ACTIVE_HOOK=$(printf '%s\n' "$DATA" | sed -n 1p)
CWD=$(printf '%s\n' "$DATA" | sed -n 2p)

# กัน loop: ถ้าเราบล็อกไปแล้วรอบหนึ่ง อย่าบล็อกซ้ำ
[ "$ACTIVE_HOOK" = "1" ] && exit 0

[ -n "$CWD" ] || CWD=$(pwd)
ACTIVE="$CWD/docs/playbook/ACTIVE_PLAN"
[ -f "$ACTIVE" ] || exit 0 # ไม่มีแผนบังคับอยู่ = ไม่ใช่งานที่ต้องมี Evidence Block

PLAN_REL=$(sed -n '1p' "$ACTIVE" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
[ -n "$PLAN_REL" ] || exit 0
case "$PLAN_REL" in
/*) PLAN="$PLAN_REL" ;;
*) PLAN="$CWD/$PLAN_REL" ;;
esac
[ -f "$PLAN" ] || exit 0

EV_REL=$(sed -n 's/^evidence_path:[[:space:]]*//p' "$PLAN" | sed -n 1p |
	sed 's/^"//; s/"$//; s/[[:space:]]*#.*$//; s/[[:space:]]*$//')
[ -n "$EV_REL" ] || exit 0
case "$EV_REL" in
/*) EV="$EV_REL" ;;
*) EV="$CWD/$EV_REL" ;;
esac

[ -f "$EV" ] || block "evidence_guard: แผน $PLAN_REL ประกาศ evidence_path: $EV_REL แต่ยังไม่มีไฟล์นั้น
⇒ ยังแนบ Evidence Block ไม่ครบ (ห้ามเขียน exit code ที่ไม่ได้รันจริง — เขียนเฉพาะที่รันแล้ว)"

LINE=$(grep -m1 -- "$MARKER" "$EV" 2>/dev/null) ||
	block "evidence_guard: $EV_REL ไม่มีบรรทัด \"$MARKER\" ⇒ Evidence Block ยังไม่ครบ"

# L-2: ตรวจ **เนื้อหา** ไม่ใช่แค่การมีบรรทัด — บรรทัดที่เว้นว่างหลัง colon
# เป็นสิ่งที่ base ห้ามอยู่แล้ว แต่ตัวตรวจที่ดูแค่ grep -q ปล่อยผ่าน
REST=${LINE#*:}
case "$(printf '%s' "$REST" | tr -d '[:space:]')" in
'') block "evidence_guard: บรรทัดสรุป \"$MARKER\" ใน $EV_REL ว่างเปล่า
⇒ §8 ห้ามเว้นว่าง · ถ้าไม่มี gate ที่ตก ให้เขียน \"ไม่มี\" พร้อมความเสี่ยงที่ยังเหลือตามตารางในแผน" ;;
esac

exit 0
