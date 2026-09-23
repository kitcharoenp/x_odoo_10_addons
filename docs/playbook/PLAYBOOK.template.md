---
project: "<Project Name>"
scope: "<ทั้ง repo | เฉพาะ subsystem <ชื่อ>>"
playbook_status: draft
extends: BASE_PLAYBOOK.md
base_version: "<X.Y.Z — pin เวอร์ชันที่ก๊อปมา ดู frontmatter ของ BASE_PLAYBOOK.md>"
last_reviewed_base_version: "<เท่ากับ base_version ตอน adopt ครั้งแรก>"
last_reviewed_date: <YYYY-MM-DD>
next_review: <YYYY-MM-DD>
owner: "<ชื่อ>"
maintainer: "<ชื่อ/ทีม>"
marker_namespace: "<prefix หรือ none>"
risk_level: <low | medium | high | critical>
---

# <Project Name> Playbook

**Inherits:** ทุก section ของ [`BASE_PLAYBOOK.md`](./BASE_PLAYBOOK.md) โดยอัตโนมัติ ยกเว้นที่ระบุ deviation ไว้ใน §0

> **วิธีใช้ไฟล์นี้:** ก๊อปไปเป็น `docs/playbook/PLAYBOOK.md` ของโปรเจกต์จริง (หรือ `PLAYBOOK.<subsystem>.md` ถ้า repo มีหลาย subsystem ที่วินัยต่างกัน — ดู base §1 หมายเหตุ 3) แล้วแทนที่ `<...>` ทุกจุดด้วยของจริง
>
> **ห้ามลบหัวข้อที่ยังไม่มีของจริง** — ทุกหัวข้อผูกกับ `R`-ID ใน base §9.0 ถ้ายังไม่มี ให้เขียนว่า *"ยังไม่มี เพราะ &lt;เหตุผล&gt; — จะทบทวนเมื่อ &lt;เงื่อนไข/วันที่&gt;"* แล้ว mark ⚠️ ในตาราง Adoption Status การลบหัวข้อทิ้งทำให้แยกไม่ออกว่า *ตัดสินใจแล้ว* หรือ *ลืมทำ* (base §9 "Adoption ครบเมื่อไหร่?")
>
> **ห้ามเขียนเลขเวอร์ชัน base ซ้ำในเนื้อเอกสาร** — แหล่งเดียวคือ frontmatter ด้านบน (base §5.10)

## ความหมายของ frontmatter

| field | ความหมาย |
|---|---|
| `scope` | ขอบเขตที่ playbook ไฟล์นี้รับผิดชอบ — ต้องชัดว่าครอบ repo ทั้งหมดหรือแค่ subsystem ไหน |
| `playbook_status` | `draft` = ยัง adopt ไม่ครบ · `active` = ผ่านเกณฑ์ base §9 แล้ว · `stale` = เลย `next_review` หรือเลย compliance deadline ของ base แล้วยังไม่ review · `deprecated` = เลิกใช้ |
| `base_version` / `last_reviewed_base_version` / `last_reviewed_date` | ความหมายและ invariant อยู่ที่ base §10 ("ความหมายของ version field") — ห้ามนิยามใหม่ที่นี่ · ทั้งสองฟิลด์แรกเก็บ **เวอร์ชัน** ไม่ใช่วันที่ |
| `next_review` | วันที่ต้องกลับมาอ่านเทียบ base อีกครั้ง (ตั้งไว้เสมอ ไม่เว้นว่าง) |
| `marker_namespace` | prefix ที่ใช้กับ `[DN-n]`/`[DEC-id]` ถ้า repo นี้ไม่ share numbering pool กับใคร ใส่ `none` |
| `risk_level` | ใช้ประกอบการตัดสิน blast radius ตาม base §2 — ไม่ใช่ตัวลด gate |

---

## Adoption Status (`R1`–`R14`)

สถานะจริงของ artifact ที่ base §9.0 บังคับ — **ทุกแถวต้องมีสถานะ ห้ามเว้นว่างและห้ามลบแถว** (ระดับ "ต้องมี" / "ประกาศได้" ของแต่ละ R ดูที่ base §9.0 อย่านิยามซ้ำที่นี่)

สถานะเขียนเป็น token ข้อความ + emoji นำหน้า (emoji เป็นของประดับ — ห้ามใช้ emoji เดี่ยว ๆ ดูเหตุผลใน base §9):

- `✅ present` = มีของจริงแล้ว ชี้ path ได้
- `⚠️ missing` = ยังไม่มี และประกาศเหตุผลไว้แล้วในหัวข้อที่เกี่ยวข้อง

คอลัมน์ "อยู่ที่ไหน" ใช้เลข section ของไฟล์นี้เอง — ไม่จำเป็นต้องตรงกับเลขใน template (base §9.0 ท้ายตาราง)

| R | Artifact | สถานะ | อยู่ที่ไหน / เหตุผลถ้ายังไม่มี |
|---|---|---|---|
| `R1` | Layer 1 (canonical + pointer) | ⚠️ missing | canonical: `<AGENTS.md>` · pointer: `<CLAUDE.md, QWEN.md, ... เท่าที่ใช้เครื่องมือนั้นจริง>` (base §9.1) |
| `R2` | Frontmatter + ตารางนี้ | ⚠️ missing | หัวไฟล์นี้ |
| `R3` | Explicit Deviations | ⚠️ missing | §0 |
| `R4` | Core Contracts registry | ⚠️ missing | `<architecture/CORE_CONTRACTS.md \| §1 ของไฟล์นี้>` |
| `R5` | Dependency DAG | ⚠️ missing | §2 |
| `R6` | Correctness Invariant | ⚠️ missing | §3 |
| `R7` | Marker Namespace | ⚠️ missing | §5 |
| `R8` | Test Template Paths | ⚠️ missing | §6 |
| `R9` | Acceptance Criteria Register | ⚠️ missing | §7 |
| `R10` | Virtual-gate Config | ⚠️ missing | §8 |
| `R11` | Evidence Artifact Locations | ⚠️ missing | §9 |
| `R12` | Known Gaps / Debt Ledger | ⚠️ missing | §10 |
| `R13` | Upgrade Log | ⚠️ missing | §11 |
| `R14` | Contacts / Ownership | ⚠️ missing | §12 |

ถือว่า adopt ครบ (`playbook_status: active`) เมื่อผ่านเงื่อนไข 5 ข้อท้าย base §9 — ไม่ใช่แค่กรอกตารางนี้เสร็จ

---

## 0. Explicit Deviations จาก Base (`R3`)

ตาม base §0 กฎ override ข้อ 3 — ถ้าโปรเจกต์นี้ **ตั้งใจ**ไม่ทำตามข้อไหนใน base (ไม่ใช่แค่ยังไม่เติม) ให้ระบุตรงนี้พร้อมเหตุผลและผู้อนุมัติ ถ้าไม่มี ให้เขียนว่า "ไม่มี — inherit ทุก gate ของ base แบบเต็ม"

| Base section ที่ deviate | เหตุผล | อนุมัติโดย/เมื่อไหร่ |
|---|---|---|
| — | — | — |

> แยกให้ชัดระหว่าง 2 อย่างนี้ อย่าปนกัน:
>
> - **deviation** = ตั้งใจไม่ทำตาม + มีคนอนุมัติ → อยู่ในตารางนี้
> - **debt** = ยังทำตามไม่ได้ตอนนี้ แต่ไม่มีใครอนุมัติให้เลิกทำ → อยู่ใน §10 Known Gaps
>
> การย้าย debt มาใส่ตารางนี้เพื่อให้ดู "ผ่าน" คือการลดความเข้มของ gate ซึ่ง base §0 ห้าม

### 0.1 Adoption Declaration — `doc_state.sh` (ผูกกับ `R3`)

ต้อง **ประกาศ** ว่าเลือกทางไหน 1 ค่าเท่านั้น **ห้ามเว้นว่าง** (ไม่มีหัวข้อนี้ = `audit_playbook.sh` fail · Phase 2) — คำนี้เป็น *adoption status ของ `R3`* ไม่ใช่ artifact ใหม่ จึง **ไม่เพิ่ม `R`-ID** (ตาราง `R1`–`R14` ต้องคง 14 แถว; ห้ามให้แถวนี้ขึ้นต้นด้วย `| R<digit>` ไม่งั้นจะโดนนับเป็น R-ID)

| Field | ค่า (เลือก 1) | เหตุผล + วันที่ |
|---|---|---|
| `doc_state_adoption` | `<adopted-gate \| convention-only \| not-adopted>` | `<เหตุผล (บังคับทุกค่าที่ไม่ใช่ adopted-gate) · YYYY-MM-DD>` |

- `adopted-gate` = adopt `doc_state.sh`/เทียบเท่าเต็มรูปแบบ (ต้องผ่าน D1–D8 จริง + `.doc-state-paths` ครอบเอกสาร state ทุกประเภท)
- `convention-only` = ใช้ 5 ฟิลด์ frontmatter เป็นธรรมเนียม ไม่ gate (ตาม base §9.9 carve-out)
- `not-adopted` = ไม่ใช้เลย (ต้องมีเหตุผล + วันที่ เหมือนแถว deviation อื่น)

---

## 1. Core Contracts ของโปรเจกต์นี้ (`R4`)

**registry อยู่ที่:** `<architecture/CORE_CONTRACTS.md | ในหัวข้อนี้>` ← เลือกอย่างเดียว แล้วลบตัวเลือกที่ไม่ใช้ (base §9.2 — ห้ามมีทั้งสองที่เพราะจะ drift)

*(ถ้า registry อยู่ไฟล์แยก ให้ที่นี่เหลือแค่สรุปย่อเพื่ออ่านเร็ว และระบุว่าไฟล์แยกคือแหล่งความจริง)*

### [FROZEN]
- <public API / schema / auth boundary ของโปรเจกต์นี้ — ระบุที่มาที่ตรวจได้ เช่น `file:line` หรือชื่อ endpoint>

### [TUNABLE]
- <config/param พร้อม bounds และ default — ระบุด้วยว่า bounds ถูก validate ที่ไหนในโค้ด หรือยังไม่ถูก validate>

### [INTERNAL-FROZEN]
- <internal constant พร้อมเหตุผล>

### [DEPRECATED]
- <contract เดิมที่กำลัง migrate ออก พร้อมวัน remove ที่ตั้งใจไว้ + ทางเลือกใหม่ที่ควรใช้แทน>

---

## 2. Dependency DAG (`R5`)

```txt
<module A> → <module B> → <module C>
```

Freeze order สำหรับ Forward-only mode (base §4): ทำตามลำดับนี้เสมอเมื่อ CROSS-MODULE

---

## 3. Correctness Invariant ต่อ module (`R6`)

| Module | Invariant หลัก |
|---|---|
| <module> | <เช่น deterministic output / no lookahead / idempotent write> |

---

## 4. Gate เพิ่มเติมของโปรเจกต์นี้ (additive only — ไม่มี R-ID)

*(หัวข้อนี้ไม่ผูกกับ `R`-ID ใด เพราะไม่ใช่ adoption artifact ที่ base บังคับ — เป็นที่ให้โปรเจกต์เพิ่ม gate ของตัวเอง ไม่มีก็ไม่กระทบ Adoption Status แต่ยังห้ามลบหัวข้อ ให้เขียนว่า "ไม่มี" ตามด้านล่าง)*

Gate ใน base §5 เป็น `final` — ห้ามลบ/ลดความเข้ม เพิ่มได้อย่างเดียว ถ้าโปรเจกต์นี้มี gate เฉพาะทาง (เช่น domain-specific correctness check) ให้ระบุที่นี่:

- <ชื่อ gate> — ใช้เมื่อ <เงื่อนไข> — วิธีตรวจ <...> — หลักฐานที่รับได้ <...>
- **Response Standards** — ใช้เมื่อโปรเจกต์ประกาศ response standards ใน `docs/playbook/RESPONSE_STANDARDS.md` — วิธีตรวจ: คำตอบ/รายงานผลที่ AI agent สร้างขึ้นควรยึดตาม standards นั้นเป็นแนวทาง (format, language, sourcing, adaptive depth, neutrality) — เป็นระดับ "ควร" ไม่ใช่ gate อัตโนมัติเหมือน Evidence Block (base §7/§8) — หลักฐานที่รับได้: ตัวอย่าง response ที่ผ่านเกณฑ์ + บันทึกการ review
- **Plan-first Gate** (เสริมจาก base ตาม §0 ข้อ 1: เข้มขึ้นได้ ผ่อนไม่ได้) — ใช้เมื่องานไม่ใช่ ATOMIC (หรือ blast radius ตาม base §2 ได้ "มาก/ยาก/ทันที" ตั้งแต่ 2 ข้อขึ้นไป) — ก่อน edit โค้ดครั้งแรกต้องเสนอแผนอย่างน้อย: objective · scope (ไฟล์/module ที่แตะ) · blast radius (คำตอบ 3 ข้อตาม base §2) · acceptance criteria (§5.5) · rollback plan — แล้วรอ go-ahead ชัดเจนจากผู้ใช้ในบทสนทนาปัจจุบัน (ความเงียบไม่ใช่ approval — เทียบเคียง base §5.11) — วิธีตรวจ: แผนอยู่ใน PR description หรือ path ที่ประกาศใน R11 · timestamp อนุมัติอยู่ก่อน edit แรก — หลักฐานที่รับได้: แผน + คำสั่งอนุมัติที่อ้างอิงได้ · เพิ่มบรรทัด "Plan/go-ahead: <ref หรือ 'ATOMIC — ไม่ต้องมีแผนตาม base §2'>" ใน Evidence Block (base §8) — กลางทางถ้า scope เลื่อนจนกระทบ blast radius หรือแตะ contract ใหม่ → หยุด อัปเดตแผน ขออนุมัติใหม่

> **หมายเหตุสำหรับ subclass ที่ต้องการความยืดหยุ่น:**
>
> - Plan-first Gate อาจแบ่งเป็น **Tier** ได้ตาม blast radius (เช่น Tier 0 = ATOMIC, Tier 1 = doc-only atomic, Tier 2 = doc-only structural, Tier 3 = code-touching, Tier 4 = contract-touching)
> - งานหลายรายการที่อยู่ใน Tier เดียวกัน + blast radius ระดับเดียวกัน อาจเสนอแผนเป็น **Batch** เดียวได้ — go-ahead ครั้งเดียวครอบคลุมทั้ง batch
> - การแบ่ง Tier/Batch เป็นการปรับ gate ที่ subclass เพิ่มเอง (§4 ของไฟล์นี้) **ไม่ใช่การลดความเข้มของ gate ใน base §5** — ทำได้ตราบใดที่ Tier สูงสุด (Tier 3/4) ยังต้องผ่าน Plan-first Gate เต็มรูป

ถ้าไม่มีเพิ่มเติม ให้เขียนว่า "ไม่มี — ใช้ §5 ของ base ทั้งหมด"

*(gate ที่เพิ่มที่นี่ต้องระบุ "ใช้เมื่อ" ให้ชัดแบบเดียวกับคอลัมน์ "บังคับเมื่อ" ใน base §7 มิฉะนั้นจะไม่มีใครรู้ว่าต้องตรวจตอนไหน)*

---

## 5. Marker Namespace (`R7`)

- ชุด marker ที่เลือกใช้: `[DN-n]` / `[DEC-id]` **หรือ** `[DECISION-n]` / `[RATIONALE-id]` — เลือกอันเดียว ใช้ทั้ง repo (base §6)
- เลขล่าสุดที่ใช้แล้ว: `DN-<n>`, `DEC-<id>`
- prefix namespace (ถ้า share numbering pool กับโปรเจกต์อื่น): `<prefix>-DN-n` — ถ้าไม่ share ให้ระบุ `none`
- marker ถูกฝังในโค้ดจริงแล้วหรือยัง: `<ฝังแล้ว | ยังเป็นบันทึกในเอกสารเท่านั้น>`

---

## 6. Test Template Paths (`R8`)

Path จริงของโปรเจกต์นี้ ต่อ 6 ประเภทที่ base §9.5 บังคับ (ชื่อไฟล์/นามสกุลปรับตามภาษาได้ ประเภทห้ามขาด):

| ประเภท | Gate | Path จริงของโปรเจกต์นี้ | มีไฟล์จริงแล้ว? |
|---|---|---|---|
| characterization | §5.1 | `<path/pattern>` | <ใช่ / ยัง> |
| determinism | §5.2 | `<path/pattern>` | <ใช่ / ยัง> |
| idempotency | §5.2 | `<path/pattern>` | <ใช่ / ยัง> |
| no-side-effect / no-lookahead | §5.3 | `<path/pattern>` | <ใช่ / ยัง> |
| regression | §5.8 | `<path/pattern>` | <ใช่ / ยัง> |
| benchmark | §5.9 | `<path/pattern>` | <ใช่ / ยัง> |

*(คอลัมน์สุดท้ายต้องตอบตามความจริง — path ที่ยังไม่มีไฟล์คือ "เป้าหมาย" ไม่ใช่ "สถานะ" การเขียนรวมกันทำให้คนอ่านเข้าใจผิดว่ามี test แล้ว)*

---

## 7. Acceptance Criteria Register (`R9`)

| ID | วันที่ register | Feature/Change | จุดที่บังคับใช้ | เกณฑ์ | วัดด้วย | Environment | อนุมัติโดย | Status |
|---|---|---|---|---|---|---|---|---|
| `AC-001` | <YYYY-MM-DD> | <feature/change> | <entry point / module ที่เกณฑ์นี้คุม> | <threshold ที่วัดได้> | <test/bench/สคริปต์> | <env ที่ผลอ้างอิง> | <name> | active |

กฎของ register นี้ (base §5.5):

- **register ก่อนเริ่ม validate เสมอ** — entry ที่ลงวันที่หลังเห็นผลถือเป็นโมฆะ
- **ห้ามแก้ entry เดิมให้ผ่าน** — ถ้าเกณฑ์ต้องเปลี่ยนจริง ให้สร้าง entry ใหม่ (ID ใหม่) พร้อมเหตุผลและผู้อนุมัติ แล้วเปลี่ยน entry เดิมเป็น `superseded by AC-xxx` — เก็บของเดิมไว้เป็น audit trail
- `Status`: `active` · `superseded by AC-xxx` · `retired <วันที่>`
- ถ้ามีหลายจุดที่ตั้งเกณฑ์ต่างกันสำหรับเรื่องเดียวกัน **ให้แยก ID ต่อจุด** และระบุว่าจุดไหนคือ path ที่ production ใช้จริง — ไม่ใช่เขียนรวมเป็นเกณฑ์เดียวที่ไม่ตรงกับโค้ดจุดใดเลย

---

## 8. Project-specific Config สำหรับ Gate ที่เป็น `virtual` ใน Base (`R10`)

ค่าพวกนี้ base ปล่อยให้ subclass กำหนดเอง (ดู base §0 ตาราง virtual method) — override ได้เฉพาะให้ "เข้มขึ้น":

| Config | ค่าของโปรเจกต์นี้ |
|---|---|
| Cyclomatic complexity budget ต่อ function (§5.7) | <เช่น 10> |
| Benchmark environment มาตรฐาน (§5.9) | <เช่น CI runner spec / เครื่อง dev รุ่นไหน, จำนวน run ขั้นต่ำ> |
| Deprecation window ก่อน remove ได้ (§3 lifecycle) | <เช่น 90 วัน> |
| **Secret deny-list — path ที่ agent/tooling ห้ามอ่าน (§5.12)** | <เช่น `.env*`, `secrets/`, `*.pem`, `*.key`, ไดเรกทอรีที่เก็บ cookie/session> — การอยู่ใน `.gitignore` ไม่นับว่ากันอ่านแล้ว · ระบุด้วยว่า path เหล่านี้**ถูกใส่เป็น deny rule จริงหรือยัง** (ดู 2 แถวล่างสุด) หรือยังเป็นเพียงการประกาศ |
| **เกณฑ์ revert ทันที (§5.13)** | <อาการระดับไหนต้อง revert ก่อนหาสาเหตุ เช่น ข้อมูลเสียหาย / ผู้ใช้เห็นผลผิด / ธุรกรรมผิด> |
| **เกณฑ์ที่ fix-forward ได้ (§5.13)** | <อาการระดับไหนแก้ไปข้างหน้าได้> |
| **ผู้มีอำนาจสั่ง revert + ช่องทางแจ้ง (§5.13)** | <ชื่อ/บทบาท + ช่องทาง> |
| **กลไกบังคับที่ติดตั้งจริง (§5.11 หมายเหตุ, §9.1)** | <`ask`: อะไร · `deny`: อะไร · อยู่ไฟล์ไหน · CI รันอะไร> — ก๊อปตั้งต้นจาก `settings.template.json` แล้วเติม secret deny-list จากแถวข้างบน · **ปรับให้ตรงกับเครื่องมือที่ทีมใช้จริง** (แม่แบบเขียนด้วย schema ของเครื่องมือหนึ่ง ทีมที่ใช้เครื่องมืออื่นต้องแปลงเป็น config ของตัวเอง — สิ่งที่ต้องคงคือ *การแบ่งประเภท* ไม่ใช่รูปแบบไฟล์) · ถ้ายังไม่ติดตั้ง ให้เขียน "ยังไม่มี" **ห้ามเว้นว่าง** |
| **เหตุผลของการแบ่ง `ask` vs `deny` (§5.11)** | <ทำไมข้อไหนอยู่ `ask` ข้อไหนอยู่ `deny`> — **ห้ามลบ `ask` ทิ้งเพื่อความสะอาด** เพราะของที่ *ทำได้เมื่อถูกสั่ง* ถ้าไปอยู่ `deny` จะขัดแกนของ §5.11 ที่ตัวบล็อกแยกไม่ออกระหว่างถูกสั่งกับไม่ถูกสั่ง · การมีทั้ง `ask: push` และ `deny: force-push` พร้อมกันไม่ขัดกัน เพราะ `deny` ชนะ `ask` เสมอ (ตรวจกับเอกสารของเครื่องมือที่ใช้) |
| **ข้อจำกัดของกลไกนั้น (§9.1)** | <เช่น deny rule เทียบ prefix ของ command string จึงเลี่ยงได้ด้วย wrapper/การเปลี่ยน cwd · เครื่องมืออื่นที่ไม่อ่าน config ไฟล์นี้ยังไม่ถูกครอบ ต้อง mirror เอง · config ที่ผูกกับไดเรกทอรีของโปรเจกต์ไม่มีผลเมื่อมีคนเปิด session จากไดเรกทอรีอื่นแล้วแก้ไฟล์ข้ามเข้ามา> — **ห้ามเว้นว่าง และห้ามเคลมว่ากันได้ 100%** มันเป็น guardrail ไม่ใช่ security boundary |
| **Plan-first Gate — กลไกบังคับ (ถ้าประกาศใช้)** | <ถ้าใช้ Plan-first Gate ใน §4: ระบุกลไกที่หนุน gate นี้ เช่น plan mode ของเครื่องมือ / ask-before-write rule / **"ACTIVE_PLAN artifact + PreToolUse hook"** (แผนที่อนุมัติแล้วถูก compile เป็นขอบเขตที่เครื่องบังคับได้ — ดู 3 แถวล่าง) · ถ้าไม่มีเครื่องมือเฉพาะ ให้เขียน "ยังไม่มี — ใช้ approval lever ที่มีอยู่แล้ว (§5.11 ask/deny) แทน"> — ถ้าไม่ใช้ Plan-first Gate ให้ลบแถวนี้ |
| **AI Pipeline — บทบาทและโมเดลที่ใช้ (§8 ข้อ 12)** | <ถ้าใช้ multi-agent หรือ multi-model pipeline: ระบุบทบาทแต่ละตัวและโมเดล/เครื่องมือที่ใช้ · ถ้าใช้ agent เดียวและยอมรับความเสี่ยง self-review ให้เขียนเหตุผล 1 บรรทัด> — ถ้าไม่ใช้ AI pipeline หลายบทบาท ให้ลบแถวนี้ |
| **AI Pipeline — ขีดจำกัดต้นทุน (§8 ข้อ 13)** | <ถ้ามี: ขีดจำกัดต่องาน/ต่อวัน/ต่อเดือน + หน่วยนับ> — ถ้าไม่ใช้ AI pipeline ให้ลบแถวนี้ |
| Agent Skills — skills ที่ติดตั้ง | `skills/registry.yaml` ใน dev-playbook (registry กลาง) · `skills/shared/` (curated skills) · `skills/adapters/` (ตัวแปลงสำหรับ Claude Code / Cursor / Qoder) · ติดตั้งด้วย `./skills/install.sh <skill-id>` · ทดสอบแล้วว่าใช้งานกับ Claude Code + Cursor + Qoder |
| **Unattended mode — Tier ที่อนุญาต** | <ถ้ารัน agent ในโหมดที่ไม่มีคนกดอนุมัติทีละครั้ง: ระบุ Tier สูงสุดที่ปล่อยให้รันได้โดยไม่ต้องมีแผน และ Tier ที่บังคับว่าต้องมีแผนอนุมัติแล้ว (ค่าตั้งต้นที่แนะนำ: ปล่อยได้ถึง Tier 2 · Tier 3 ต้องมีแผน · Tier 4 บล็อกเสมอ)> — ถ้าไม่รันแบบ unattended ให้ลบแถวนี้ |
| **Plan scope guard — กลไกที่ติดตั้งจริง + ข้อจำกัด** | <ชื่อไฟล์ hook ที่ติดตั้ง + ลงทะเบียนไว้ที่ไหน (ต้องเป็น config ของเครื่องมือแบบ always-on ไม่ใช่ที่ที่ทำงานเฉพาะเมื่อโมเดลเลือกเรียก) + **ข้อจำกัดที่รู้ตัว**> — **ห้ามเว้นว่างและห้ามเคลมว่ากันได้ 100%** · ข้อจำกัดที่ต้องเขียนอย่างน้อย: (1) hook ที่ path ผิดใน config = **gate ปิดเงียบ** ไม่ใช่ error (2) hook timeout ไม่บล็อก (3) exit code ที่ไม่ใช่ค่าที่ใช้บล็อกจะไม่บล็อก (4) การเทียบคำสั่งแบบ prefix เลี่ยงได้ด้วย wrapper script หรือการเปลี่ยน cwd (5) ช่องเขียนไฟล์ที่ไม่ผ่าน tool เขียนไฟล์ (แก้ไฟล์ในที่ตัวแก้ไขของเทอร์มินัล, สคริปต์ที่เขียนเองแล้วเรียก) ยังไม่ถูกครอบ (6) การปฏิเสธ metacharacter แบบไม่สนใจเครื่องหมายคำพูดทำให้คำสั่งอ่านอย่างเดียวที่ถูกต้องถูกบล็อกด้วย — เป็นราคาที่จ่ายเพื่อ fail-closed (7) ชื่อ permission mode ต่างกันตามเครื่องมือ/ส่วนติดต่อ (เช่น CLI เทียบ IDE extension) — โหมดที่ชื่อคล้ายกันอาจมีพฤติกรรมไม่เท่ากัน (เช่น มี safety-check ภายในซ้อนอยู่หรือไม่) ต้องยิง probe จริงแยกทีละชื่อโหมด ห้ามเหมาว่าเทียบเท่ากันโดยไม่ทดสอบ (8) **ลงทะเบียน hook ด้วย absolute path ของเครื่องคนติดตั้ง = gate ปิดเงียบทันทีที่ clone/ย้ายเครื่อง** — ต้องใช้ตัวแปรที่เครื่องมือเตรียมไว้ชี้ราก repo และครอบด้วยเครื่องหมายคำพูด · ประกาศในแถวนี้ว่าใช้รูปแบบใด และยืนยันด้วย probe แล้วเมื่อใด (9) **guard บังคับได้เฉพาะเครื่องมือที่ลงทะเบียนไว้** — config ของเครื่องมือหนึ่งไม่ถูกอ่านโดยอีกตัว ⇒ เครื่องมือที่ไม่ได้ลงทะเบียน **ไม่มีการบังคับเลย** (ไม่ใช่ "บังคับอ่อนลง") · ความต่างที่ต้องแก้มักเป็น **ชื่อโหมดสิทธิ์ · ตำแหน่งไฟล์ตั้งค่า · วิธีอ้าง path ในสตริง `command` · ฟิลด์ stdin ที่บอกโหมด** ไม่ใช่ตัวกลไก (โครง `hooks` และการบล็อกด้วย exit code มักเหมือนกัน) ⇒ ประกาศในแถวนี้ว่า **บังคับกับเครื่องมือใดบ้าง และ probe ยืนยันแล้วเมื่อใด** · เครื่องมือที่ยังไม่ probe ให้เขียนว่า "ไม่มีการบังคับ" ตรง ๆ ห้ามเว้นว่าง (10) **ตรวจว่า runtime นั้น *มี* กลไก hook อยู่จริงก่อนไล่แก้ไวยากรณ์** — IDE กับ CLI ของ **เครื่องมือเดียวกัน** อาจไม่เหมือนกัน: ตัวหนึ่งอาจไม่ implement `permissions`/hooks เลยและไม่อ่านไฟล์ตั้งค่าที่เอกสารระบุ ⇒ ทุก probe จะได้ผลลบ เหมือนกันหมดไม่ว่าจะปรับ syntax อย่างไร · ลำดับที่ถูกคือ **มี hook engine ไหม → มัน fire ไหม → สัญญาบล็อกแบบไหน → ไวยากรณ์ rule** ห้ามสลับลำดับ · และต้องมี **positive control** (ให้ hook บล็อกอะไรให้เห็นก่อน) ไม่งั้นผลลบทุกตัวตีความไม่ได้ (11) **สัญญาการบล็อกอาจต่างกันต่อ event ไม่ใช่แค่ต่อเครื่องมือ** — บางเครื่องมือให้ `PreToolUse` บล็อกด้วย JSON บน stdout + exit 0 แต่ event อื่นใช้ exit 2 · และการคืนคำว่า *allow* อาจ **ข้าม deny rules ของตัวเอง** ⇒ ทางปล่อยผ่านต้องเงียบเสมอ (12) **ประกาศระดับหลักฐานต่อชั้น** ไม่ใช่แค่ผ่าน/ไม่ผ่าน: `Configured` (มี config) → `Policy content` (อ่านโค้ดแล้ว) → `Tested` (มี unit test) → `Observed` (เห็น hook ทำงานใน session จริง) → `Backstopped` (มีชั้นอื่นซ้ำ เช่น git hook/CI) · **ห้ามเขียนว่า "บังคับได้" ถ้ายังไม่ถึง `Observed`** (13) **ชั้นที่ครอบเครื่องมือที่ไม่มี hook คือ git hook** (`pre-commit` ที่ตรวจ scope ของแผน) เพราะรันที่ git ไม่ใช่ใน agent ⇒ ครอบทุกเครื่องมือรวมคนที่พิมพ์เอง · แต่ **bypass ได้ด้วย `--no-verify` และต้องให้คนตั้ง `core.hooksPath` เอง** ⇒ ประกาศทั้งสองข้อ ห้ามเคลมว่าปิดช่อง |
| **ที่เก็บ `ACTIVE_PLAN` (ถ้าใช้ scope guard)** | <path จริงของไฟล์ที่ชี้แผนที่บังคับอยู่ เช่น `docs/playbook/ACTIVE_PLAN`> — **ไฟล์นี้เป็น *สำเนาการอนุมัติ* ไม่ใช่ *ตัวอนุมัติ*** การอนุมัติเกิดจากผู้ใช้ในบทสนทนาเท่านั้น (base §8) · path นี้ต้องอยู่ใน deny-list ของ agent เสมอ · ระบุด้วยว่า **ใครมีหน้าที่ลบไฟล์เมื่องานจบ** เพราะไฟล์ที่ค้าง = การอนุมัติที่ค้างข้าม session |
| **Skills ที่ติดตั้ง — จำนวน + ต้นทุน context** | <จำนวน skill ที่ติดตั้งจริง + ต้นทุน context ที่วัดได้จาก `/doctor` ของเครื่องมือ (หรือคำสั่งเทียบเท่า) + วันที่วัด> — รายการ skill กินงบ context ตลอดเวลา และเมื่อเกินงบ เครื่องมือจะ **ตัดคำอธิบายทิ้งเงียบ ๆ** ⇒ skill เลิกทำงานโดยไม่มี error · ทบทวนตัวเลขนี้ทุกรอบ release |
| **Retry limit สำหรับ gate ที่ fail ซ้ำ (§8 ข้อ 16)** | <ตัวเลข เช่น 3 หรือ "ใช้ default 3 — ปรับเป็น <n> เพราะ <เหตุผล>"> — ถ้าต้องการใช้ default ของ base โดยไม่ปรับค่า ให้ลบแถวนี้ |

> **แถว "กลไกบังคับที่ติดตั้งจริง" และ "เหตุผลของการแบ่ง `ask`/`deny`" ไม่มี `R`-ID ของตัวเอง** — เป็นส่วนหนึ่งของ `R10` เพราะ §5.11 เป็น gate ที่ต้องการ config ของโปรเจกต์อยู่แล้ว ไม่ใช่ artifact ใหม่ · base §9.1 บังคับให้ประกาศกลไก+ข้อจำกัดไว้ใน `PLAYBOOK.md` มาตั้งแต่ก่อนหน้านี้ ทั้งสองแถวเพียงทำให้มี *ที่ให้เติม* และอยู่ในตารางที่ scan ได้ · แถว **Plan-first Gate**, **AI Pipeline**, **Retry limit**, **Agent Skills**, **Unattended mode**, **Plan scope guard**, **ที่เก็บ `ACTIVE_PLAN`** และ **Skills ที่ติดตั้ง** ก็เช่นกัน — เป็นแถวมีเงื่อนไข ไม่มี `R`-ID ของตัวเอง ลบได้ถ้าโปรเจกต์ไม่ใช้ · ถ้าประกาศไว้ที่ §4 (Gate เพิ่มเติม) แทน จะไม่ถูกนับใน Adoption Status เพราะ §4 ไม่ผูกกับ `R`-ID ใด

---

## 9. Evidence Artifact Locations (`R11`)

base บอกว่า *อะไรนับเป็นหลักฐาน* (ตาราง §7 คอลัมน์ "หลักฐานที่รับได้") แต่ไม่กำหนด *ที่เก็บ* — ระบุที่นี่ ไม่งั้นแต่ละงานจะเก็บกันคนละที่แล้วตามกลับไม่ได้ (base §9.7)

**ห้ามลิสต์ gate ซ้ำกับตาราง §7 ของ base** — ตารางนี้ตอบแค่ "เก็บที่ไหน / ใครจด" · แถวที่โปรเจกต์ยังไม่เคยทำงานประเภทนั้นให้เขียน "ยังไม่มี เพราะ..." ห้ามลบแถว

| หลักฐาน | Gate | เก็บที่ไหนของโปรเจกต์นี้ | ใครจด / จดเมื่อไหร่ |
|---|---|---|---|
| Golden files + รายการ unstable field ที่ pre-register | §5.1 | `<path>` | <...> |
| Determinism/Idempotency log (seed, env, ผลรันซ้ำ) | §5.2 | `<path หรือ CI artifact>` | <...> |
| No-lookahead prefix test result | §5.3 | `<path>` | <...> |
| Contamination Ledger | §5.4 | `<path หรือ "ใน PR description">` | <...> |
| Root-cause note / debug log | §5.6 | `<issue / PR / path>` | <...> |
| Lint/type-check + regression fail-before/pass-after log | §5.7, §5.8 | `<CI log / path>` — ต้องเก็บ **ทั้งสองรอบ** | <...> |
| Perf Change Log | §5.9 | `<path>` | <...> |
| บันทึกการตรวจ dependency (license/CVE/maintain) + lockfile | §5.12 | `<path>` | <...> |
| Incident record + regression test ที่ปิดวง | §5.13 | `<path>` | <...> |
| AI Agent Evidence Block | §8 | `<PR description / commit body>` | AI agent |
| แผนการทำงาน (Plan-first Gate) | §4 ของไฟล์นี้ | `<PR description / path ที่ประกาศในโปรเจกต์>` | AI agent เสนอ · ผู้ใช้อนุมัติ |
| Decision Memory (`[DN-n]`/`[DEC-id]`) | §3, §6 | `<architecture/decisions/ หรือที่อื่น>` | <...> |

---

## 10. Known Gaps / Debt Ledger (`R12`)

จุดที่โค้ดจริงกับ doc/contract ที่ควรจะเป็นยังไม่ตรงกัน, gate ของ base (§5) ที่ยังไม่ผ่านจริง, หรือ decision ที่ยังไม่ได้ตัดสินใจ — บันทึกไว้ตรงนี้แทนการซ่อนหรือแก้เงียบ ๆ กลางทาง (ขัด base §8 ข้อ 3 เรื่องห้าม AI agent ขยาย scope โดยไม่บอก)

ถ้าตรวจแล้วไม่พบ ให้เขียนว่า "ยังไม่พบ ณ รอบ adoption &lt;วันที่&gt;" — **ห้ามลบตารางนี้ทิ้งเพราะไม่มีอะไรจะเขียน** ต้องระบุว่าตรวจแล้วว่างจริง

| # | Gap | Severity | Status | Owner | Target | ผลกระทบ | แนะนำ |
|---|---|---|---|---|---|---|---|
| 1 | <เช่น doc บรรยายสถาปัตยกรรมที่ไม่ตรงกับโค้ดจริง> | <low\|medium\|high> | <open\|decision-needed\|in-progress> | <name> | <date หรือ — ถ้ายังไม่ตั้ง> | <ใครเข้าใจผิดยังไง> | <sync doc หรือ PLAN AMENDMENT — ไม่ใช่ตัดสินใจเองในตารางนี้> |

ความหมายของคอลัมน์:

- `Severity` — ความแรงของผลกระทบถ้าไม่แก้ ไม่ใช่ความยากในการแก้
- `Status` — `open` (รู้ว่าต้องทำ) · `decision-needed` (ต้องตัดสินใจก่อนจะลงมือได้ อย่าให้ agent ตัดสินเอง) · `in-progress` · `closed <วันที่>` (**เก็บแถวที่ปิดแล้วไว้ ห้ามลบ** — debt ledger ที่ลบแถวปิดแล้วจะตามไม่ได้ว่าเคยมีอะไรและปิดเมื่อไหร่)
- `Owner` — ต้องเป็นคน ไม่ใช่ "ทีม" ลอย ๆ ถ้าไม่มีเจ้าภาพให้ใส่ owner ของ playbook (`R14`)
- `Target` — `—` หมายถึง **ยังไม่ได้ตั้งวัน** ไม่ใช่ "ไม่มีกำหนด" · gap ที่ Severity เป็น high ควรมีวันจริงทุกข้อ

แต่ละแถวคือ "สิ่งที่ยังไม่แก้ บันทึกไว้เฉย ๆ" — ไม่ใช่ "คำสั่งให้ agent ตัวต่อไปรีบไปแก้ทันที" ถ้าจะแก้ ให้ triage ตาม base §2 ก่อนเหมือนงานอื่น และ gap ที่ทำให้ gate ใน §5 ไม่ผ่าน **ไม่ใช่** deviation (ดูกล่องเทียบใน §0)

---

## 11. Upgrade Log (`R13`)

บันทึกทุกครั้งที่ review `BASE_PLAYBOOK.md` เวอร์ชันใหม่ (base §10) — รวมถึงครั้งที่ review แล้วสรุปว่า *ยังไม่ adopt* พร้อมเหตุผล:

```md
## <base version ที่ review> — <YYYY-MM-DD>
- ผล: <adopted ครบ | adopted บางส่วน | ยังไม่ adopt>
- เหตุผล / สิ่งที่ค้าง: <...>
- base_version ใน frontmatter หลังรอบนี้: <...>
```

---

## 12. Contacts / Ownership (`R14`)

- Playbook owner: <ชื่อ>
- ที่ปรึกษาเมื่อจะแก้ `[FROZEN]`: <ชื่อ/ทีม>
- ผู้อนุมัติ deviation (§0) และ acceptance criteria (§7): <ชื่อ/บทบาท>

*(สำหรับโปรเจกต์ที่มีหลายทีม — ถ้าโปรเจกต์มี owner เดียวให้ลบกล่องนี้ทิ้ง)*

> **Team leads ต่อ subsystem:**
>
> | Subsystem | Team Lead | หมายเหตุ |
> |---|---|---|
> | <ชื่อ> | <ชื่อ/ทีม> | <ขอบเขตที่รับผิดชอบ> |
>
> **Escalation path สำหรับ deviation/AC approval:** <ระบุลำดับ เช่น team lead → playbook owner → architecture board>
