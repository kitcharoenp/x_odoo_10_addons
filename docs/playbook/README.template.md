# Playbook System — วิธีใช้โฟลเดอร์นี้

> **วิธีใช้ไฟล์นี้:** ก๊อปเป็น `README.md` ในโฟลเดอร์ `docs/playbook/` ของโปรเจกต์ใหม่ แล้วแทนที่ `<...>` ทุกจุด — จากนั้น**ลบกล่องนี้ทิ้ง** (เก็บไฟล์ `README.template.md` ไว้เฉย ๆ ถ้าคาดว่าจะ adopt subsystem/โปรเจกต์เพิ่ม)
>
> ไฟล์นี้เป็นเอกสาร "ทางเข้า" ของ repo — เขียนให้คนที่เพิ่งเข้ามาอ่าน 2 นาทีแล้วรู้ว่าต้องไปอ่านอะไรต่อ ไม่ใช่ที่สำหรับคัดลอกกฎจาก `BASE_PLAYBOOK.md` มาไว้ซ้ำ (base §5.10)

โฟลเดอร์นี้เก็บระบบ playbook แบบ **abstract base class / concrete subclass**: กฎกลางอยู่ไฟล์เดียวที่ก๊อปข้ามโปรเจกต์ได้ ส่วนแต่ละโปรเจกต์เขียนเฉพาะของตัวเอง

| ไฟล์ | บทบาท | แก้บ่อยแค่ไหน |
|---|---|---|
| [`BASE_PLAYBOOK.md`](./BASE_PLAYBOOK.md) | กฎ/gate ที่ใช้ได้กับทุกโปรเจกต์ (triage, contract marker, non-negotiable gates, AI-agent discipline) — versioned ด้วย SemVer | **ห้ามแก้เพื่อโปรเจกต์นี้** — อัปเดตด้วยการก๊อปเวอร์ชันใหม่จากต้นทางเท่านั้น (base §0 กฎ portability) |
| [`PLAYBOOK.md`](./PLAYBOOK.md) | subclass ของโปรเจกต์นี้ — Core Contracts, DAG, invariant, acceptance criteria, debt ledger | บ่อยที่สุด — ทีมอ่าน/แก้ไฟล์นี้เป็นหลัก |
| [`PLAYBOOK.template.md`](./PLAYBOOK.template.md) | แม่แบบสำหรับสร้าง `PLAYBOOK.md` ตัวใหม่ | ก๊อปตอนตั้งโปรเจกต์/subsystem ใหม่ |
| [`AGENTS.template.md`](./AGENTS.template.md) | แม่แบบ Layer 1 **canonical** (`R1`) — ก๊อปไปที่ราก repo | ก๊อปตอนตั้งโปรเจกต์ใหม่ · แก้เมื่อ trigger list เปลี่ยน |
| [`POINTER.template.md`](./POINTER.template.md) | แม่แบบ **pointer** ต่อเครื่องมือ (`CLAUDE.md`, `QWEN.md`, …) ที่ชี้มา canonical | ก๊อปตอนเพิ่มเครื่องมือใหม่ในทีม |
| [`RESPONSE.template.md`](./RESPONSE.template.md) | แม่แบบ **response standards** สำหรับ AI agent (optional) | ก๊อปเป็น `RESPONSE_STANDARDS.md` ถ้าโปรเจกต์ประกาศ standards · **ถ้าไม่ adopt ให้ลบแถวนี้** |
| [`settings.template.json`](./settings.template.json) | แม่แบบ **ตัวบังคับ** — `ask`/`deny` ตาม base §5.11 + deny การอ่านไฟล์ secret ตาม §5.12 | ก๊อปไป `.claude/settings.json` แล้วเติม deny-list ของโปรเจกต์ |
| [`scripts/audit_playbook.sh`](./scripts/audit_playbook.sh) | ตัวตรวจ compliance ทั้งหมดในคำสั่งเดียว (base §9.8) | แทบไม่แก้ — มาจากต้นทางพร้อม base |
| [`MANIFEST.sha256`](./MANIFEST.sha256) | `version → checksum` ของ `BASE_PLAYBOOK.md` ทุกเวอร์ชัน ใช้ตรวจว่า base ไม่ถูกแก้ | มาจากต้นทาง — **ห้ามแก้เอง** |
| [`README.template.md`](./README.template.md) | แม่แบบของไฟล์ที่คุณกำลังอ่าน | เก็บไว้เผื่อ adopt เพิ่ม |

**สถานะ adoption ของ repo นี้อยู่ที่ไหน:** ตาราง `Adoption Status` ในหัวไฟล์ [`PLAYBOOK.md`](./PLAYBOOK.md) พร้อม `playbook_status` ใน frontmatter — ตั้งใจไม่บันทึกสถานะไว้ใน README นี้ เพราะจะมี 2 ที่ที่พูดเรื่องเดียวกันแล้ว drift (base §5.10)

## Quickstart — adopt ในโปรเจกต์/subsystem ใหม่

1. ก๊อป `BASE_PLAYBOOK.md` **พร้อมกับ `scripts/audit_playbook.sh` และ `MANIFEST.sha256`** ไปวางที่ `docs/playbook/` **โดยไม่แก้เนื้อหา** — 2 ไฟล์หลังเป็นตัวตรวจและตัวพิสูจน์ว่าสำเนา base ไม่ถูกแก้ ถ้าไม่ก๊อปมาด้วย การตรวจ integrity จะถูกข้ามแบบเงียบ ๆ (สคริปต์จะรายงานเป็น note ไม่ใช่ fail)
2. ก๊อป `PLAYBOOK.template.md` เป็น `docs/playbook/PLAYBOOK.md` แล้วเติม frontmatter (pin `base_version`, `scope`, `owner`, `next_review`)
3. เติม artifact `R1`–`R14` ตาม `BASE_PLAYBOOK.md` §9.0 แล้วกรอกตาราง `Adoption Status` **ตามความจริง** — ข้อไหนยังไม่มีให้ประกาศเหตุผล ห้ามลบหัวข้อ
4. สร้าง Layer 1 ที่ราก repo — ก๊อป `AGENTS.template.md` → `AGENTS.md` (canonical) + `POINTER.template.md` → ไฟล์ตามเครื่องมือที่ทีมใช้จริง (`CLAUDE.md`, `QWEN.md`, ...) ทั้งหมดชี้ไป `PLAYBOOK.md` **ไม่ใช่** ชี้มา `BASE_PLAYBOOK.md` ตรง ๆ (base §9.1) · ระวังงบบรรทัด core ≤30 / ช่องกับดัก ≤6 (base §1)
5. ติดตั้งตัวบังคับ — ก๊อป `settings.template.json` → `.claude/settings.json` เติม secret deny-list ของโปรเจกต์ แล้ว **ประกาศกลไก + ข้อจำกัดของมันใน `PLAYBOOK.md` `R10`** (base §9.1 — Layer 1 ไม่ใช่ตัวบังคับด้วยตัวเอง)
6. ตรวจเงื่อนไข 5 ข้อท้าย base §9 ("Adoption ครบเมื่อไหร่?") แล้วตั้ง `playbook_status` — `draft` จนกว่าจะครบ

ตรวจข้อ 3–5 ด้วยคำสั่งเดียว — ห้ามนับด้วยมือ (base §9.8):

```bash
docs/playbook/scripts/audit_playbook.sh --downstream
```

## ทำไมแยกไฟล์ base ออกจาก playbook ของโปรเจกต์

- แก้กฎกลาง (เช่นเพิ่ม gate ใหม่) ที่ `BASE_PLAYBOOK.md` ที่เดียว แล้วแต่ละโปรเจกต์ pull ไป review ตามจังหวะของตัวเอง — ไม่ต้องแก้ทุก repo พร้อมกัน (เหมือนอัป dependency version)
- `PLAYBOOK.md` ของแต่ละโปรเจกต์สั้น อ่านง่าย เพราะมีแต่ของที่เป็นของโปรเจกต์นั้นจริง ๆ ไม่ต้องแบก boilerplate ซ้ำทุก repo
- ตรงกับ §5.10 (Single-source Layout) ของ playbook เอง — ไม่มีกฎซ้ำที่ควร dedupe

## เมื่อ base ออกเวอร์ชันใหม่

ตรวจ base §10 (Versioning Policy) ว่าเป็น PATCH / MINOR-ไม่กระทบ-compliance / MINOR-กระทบ-compliance / MAJOR แล้ว:

- ทำตาม migration note + **compliance deadline** ที่ระบุใน changelog ของ base
- บันทึกผลใน Upgrade Log (`R13`) ของ `PLAYBOOK.md` — **รวมถึงกรณีที่ review แล้วสรุปว่ายังไม่ adopt**
- อัปเดต `base_version` / `last_reviewed_base_version` ใน frontmatter (ความหมายต่างกัน — ดู base §10)

subclass ที่ pin เวอร์ชันเก่าไว้ยังถือว่า compliant กับเวอร์ชันที่ตัวเอง pin จนถึง deadline ไม่ได้กลายเป็น non-compliant ทันทีที่ base ออกเวอร์ชันใหม่ (base §10 กฎข้อ 3)

## การตัดสินใจระดับ repo ที่ควรบันทึกไว้ตรงนี้

เรื่องที่ base เปิดทางไว้หลายแบบ — เขียนให้ชัดว่า repo นี้เลือกแบบไหน เพื่อไม่ให้คนถัดไป (หรือ AI agent) เลือกแบบอื่นเงียบ ๆ

**ตอบเป็นตารางหรือเป็นย่อหน้าก็ได้ แต่ต้องตอบให้ครบทุกข้อ** — ประสบการณ์จากการ adopt จริงคือคนมักตอบเรื่องที่ตัวเองตัดสินใจไปแล้วเป็นย่อหน้าที่มีเหตุผลกำกับ แล้วปล่อยแถวที่เหลือค้างเป็น `<...>` · ถ้าเลือกเขียนเป็นย่อหน้า ให้เก็บชื่อหัวข้อของแต่ละเรื่องไว้เพื่อให้ยังค้นหาได้:

| เรื่อง | ตัวเลือกที่ base อนุญาต | repo นี้เลือก |
|---|---|---|
| จำนวน playbook ต่อ repo | ไฟล์เดียวคุมทั้ง repo **หรือ** `PLAYBOOK.<subsystem>.md` หลายไฟล์ (base §1 หมายเหตุ 3) | `<...>` |
| ที่เก็บ Core Contracts registry (`R4`) | `architecture/CORE_CONTRACTS.md` **หรือ** inline ใน `PLAYBOOK.md` (base §9.2) | `<...>` |
| ชุด marker (`R7`) | `[DN-n]`/`[DEC-id]` **หรือ** `[DECISION-n]`/`[RATIONALE-id]` (base §6) | `<...>` |
| Layer 1 canonical + pointer ที่มีจริง (`R1`) | canonical 1 ไฟล์ (แนะนำ `AGENTS.md`) + pointer เท่าที่ทีมใช้เครื่องมือนั้นจริง (base §9.1) | `<canonical: … · pointer: …>` |
| กลไกบังคับที่ติดตั้ง (§5.11/§9.1) | permission `ask`/`deny` · git hook · CI — อย่างน้อยหนึ่งอย่าง | `<…>` — **รายละเอียดและข้อจำกัดอยู่ที่ `PLAYBOOK.md` `R10` ที่เดียว** ที่นี่เขียนแค่ว่ามีอะไร |

## ประวัติของแม่แบบชุดนี้

`<ก๊อปแม่แบบมาจากที่ไหน (repo/URL) เวอร์ชัน/tag ไหน เมื่อไหร่ — เพื่อให้รู้ว่าต้องไปดูต้นทางที่ไหนเมื่อ base ออกเวอร์ชันใหม่>`

ตรวจว่าสำเนา `BASE_PLAYBOOK.md` ในโปรเจกต์นี้ยังตรงกับเวอร์ชันที่ pin ไว้จริง (base §9.8):

```bash
docs/playbook/scripts/audit_playbook.sh --downstream
```

## Doc-state index (generated — ห้ามแก้มือใน marker)

ถ้าโปรเจกต์นี้ adopt `doc_state.sh` หัวข้อล่าง marker จะถูก generate ใหม่ด้วย `sh scripts/doc_state.sh --gen-index` — เขียนภายนอก marker ได้ตามปกติ แต่ **ห้ามแก้มือระหว่าง BEGIN/END** (จะถูกทับ) · ถ้ายังไม่ adopt ก็ปล่อยว่างไว้ได้ ไม่กระทบอะไร (ดู `PLAYBOOK.md` §0 Adoption Declaration)

<!-- BEGIN GENERATED: doc_state -->
<!-- END GENERATED: doc_state -->
