#!/bin/sh
# hooks/qoder/evidence_guard.sh — Stop / SubagentStop adapter สำหรับ Qoder
#
# ตัวจริงอยู่ที่ hooks/claude-code/evidence_guard.sh — ไฟล์นี้ไม่ทำ policy เอง
#
# **หมายเหตุสำคัญ: event นี้ใช้ exit 2 ทั้งสองเครื่องมือ ไม่ใช่ JSON**
#   สัญญาแบบ JSON (permissionDecision) ใช้กับ `PreToolUse` เท่านั้น ·
#   reference implementation ของ Qoder เอง (renderQoderBlock ใน better-harness)
#   ใช้ exit 2 สำหรับทุก event ที่ไม่ใช่ PreToolUse ⇒ evidence_guard.sh ตัวจริง
#   ที่บล็อกด้วย exit 2 อยู่แล้วจึงพกพาได้ตรง ๆ ไม่ต้องแปลงอะไร
#   ยังตั้ง GUARD_HOST ไว้เพื่อความสม่ำเสมอ (ตัวจริงไม่ได้อ่านค่านี้)
#
# ⚠️ ใน subagent ของ Qoder เอกสารระบุว่า `Stop` ถูก remap เป็น `SubagentStop`
#    ⇒ config ต้องลงทะเบียน **ทั้งสอง event** ไม่งั้นด่านนี้เงียบเมื่องานเกิดใน subagent
#    (ตัวแปลง gen_qoder_settings.sh ทำให้แล้ว)
#
# ⚠️ เอกสาร Qoder **เงียบ** ว่า hook ระดับ settings fire ใน subagent หรือไม่
#    ⇒ ห้ามเคลมว่าครอบ subagent จนกว่าจะ probe จริง

set -uf

HERE=$(cd "$(dirname "$0")" && pwd)
GUARD_HOST=qoder
export GUARD_HOST
exec sh "$HERE/../claude-code/evidence_guard.sh"
