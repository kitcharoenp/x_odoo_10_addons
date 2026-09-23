#!/bin/sh
# skills_notice.sh — SessionStart hook (ไม่มี matcher)
#
# หน้าที่เดียว: บอกว่าโปรเจกต์นี้มีชั้น skills ของ playbook อยู่ และเรียกตัวชี้ทางได้อย่างไร
# **ไม่ใช่ guard** — ไม่บล็อกอะไรเลย คืน exit 0 ทุกกรณี (ถ้าคืนค่าอื่น การเปิด session จะเสีย)
#
# ทำไมต้องเป็น hook ไม่ใช่ skill: การที่โมเดลจะ "นึกได้เอง" ว่ามี skill ให้เลือกเป็นเรื่องของ
# การตัดสินจาก description ⇒ ไม่แน่นอน · hook ทำงานทุก session โดยไม่ขึ้นกับการตัดสินนั้น
# (stdout ของ SessionStart ถูกเติมเข้า context ตามสัญญาของเครื่องมือ)
#
# ข้อจำกัดที่ยอมรับไว้อย่างรู้ตัว:
#   - งบ context: พิมพ์ **บรรทัดเดียว** · มีตัวตรวจกำหนดเพดานบรรทัดใน tests/smoke_auto_accept.sh
#     ⇒ อย่าเติมเนื้อหาที่นี่ ให้ไปอยู่ใน SKILL.md ของตัวชี้ทางแทน (โหลดตอนถูกเรียกเท่านั้น)
#   - ไม่ parse stdin (จึงไม่พึ่ง python3 เหมือน guard ตัวอื่น) ⇒ ใช้ `pwd` เป็นที่ตั้งของโปรเจกต์
#     **ถ้าเครื่องมือรัน hook จาก cwd อื่น การนับ "ติดตั้งแล้ว" จะเพี้ยน** — ยอมรับได้เพราะผลลัพธ์
#     แย่สุดคือข้อความแนะนำผิดจำนวน ไม่ใช่การบล็อกหรือการปล่อยผ่านสิ่งที่ควรบล็อก
#   - เงียบสนิทถ้าโปรเจกต์ไม่มี registry (downstream ที่ไม่ adopt ชั้น skills ต้องไม่เจอ noise)

set -uf

HERE=$(cd "$(dirname "$0")" && pwd) || exit 0
ROOT=$(cd "$HERE/../.." && pwd) || exit 0

REG="$ROOT/skills/registry.yaml"
[ -f "$REG" ] || exit 0

CWD=$(pwd)
IDS=$(sed -n 's/^[[:space:]]*-[[:space:]]*id:[[:space:]]*//p' "$REG" | sed 's/[[:space:]]*$//')
[ -n "$IDS" ] || exit 0

total=0
installed=0
router=0
for id in $IDS; do
	total=$((total + 1))
	if [ -f "$CWD/.claude/skills/$id/SKILL.md" ]; then
		installed=$((installed + 1))
		[ "$id" = "playbook-suggest" ] && router=1
	fi
done

if [ "$router" -eq 1 ]; then
	printf 'playbook skills: ติดตั้งแล้ว %s/%s · พิมพ์ /playbook-suggest เพื่อดูว่างานนี้ควรใช้ตัวไหน\n' \
		"$installed" "$total"
else
	printf 'playbook skills: ติดตั้งแล้ว %s/%s · ตัวชี้ทางยังไม่ติดตั้ง — sh skills/install.sh playbook-suggest\n' \
		"$installed" "$total"
fi

exit 0
