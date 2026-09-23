#!/bin/sh
# hooks/qoder/bash_scope_guard.sh — PreToolUse adapter สำหรับ Qoder (ฝั่งคำสั่ง)
#
# เหตุผลของการเป็น wrapper และข้อจำกัดทั้งหมด ดูหมายเหตุยาวใน
# hooks/qoder/plan_scope_guard.sh — ไฟล์นี้ต่างกันแค่ตัว guard ที่ exec ไปหา
#
# matcher ที่ควรใช้ฝั่ง Qoder: "Bash|run_in_terminal"
# (IDE เรียก tool รันคำสั่งว่า run_in_terminal ไม่ใช่ Bash)

set -uf

HERE=$(cd "$(dirname "$0")" && pwd)
GUARD_HOST=qoder
export GUARD_HOST
exec sh "$HERE/../claude-code/bash_scope_guard.sh"
