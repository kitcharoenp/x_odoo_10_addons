#!/bin/sh
# hooks/qoder/plan_scope_guard.sh — PreToolUse adapter สำหรับ Qoder
#
# ตัว guard จริงอยู่ที่ hooks/claude-code/plan_scope_guard.sh — ไฟล์นี้ไม่ทำ policy เอง
# หน้าที่เดียวคือบอกตัวจริงว่า "ปลายทางเป็น Qoder" ผ่าน GUARD_HOST เพื่อให้ block()
# render สัญญาให้ถูก (JSON บน stdout + exit 0 ไม่ใช่ exit 2)
#
# ทำไมต้องเป็น wrapper ไม่ใช่ if ในตัวจริง: การเดา host จาก env ตอน runtime เชื่อไม่ได้ —
# Qoder export **ทั้ง** QODER_PROJECT_DIR และ CLAUDE_PROJECT_DIR ให้ hook subprocess
# (ยืนยันจาก replacePlaceholders() ใน qodercli binary) ⇒ แยกสองเครื่องมือจาก env ไม่ได้
# จึงให้ไฟล์ตั้งค่าของแต่ละเครื่องมือ **ประกาศ host เอง** ด้วยการเลือก wrapper ที่ชี้มา
#
# ผลพลอยได้ที่สำคัญ: .claude/settings.json ไม่ต้องแก้เลย (อยู่ใน deny_write ของแผน)
#
# matcher ที่ควรใช้ฝั่ง Qoder ต้องครอบ **ชื่อ tool จริงของ IDE** ไม่ใช่แค่ชื่อ canonical
# (probe เจอว่า IDE เรียกตัวแก้ไฟล์ว่า SearchReplace / search_replace ไม่ใช่ Edit)
#   "Edit|Write|NotebookEdit|SearchReplace|search_replace|create_file|apply_patch"
#
# stdin ส่งต่อโดย exec ⇒ ตัวจริงอ่านได้เหมือนถูกเรียกตรง

set -uf

HERE=$(cd "$(dirname "$0")" && pwd)
GUARD_HOST=qoder
export GUARD_HOST
exec sh "$HERE/../claude-code/plan_scope_guard.sh"
