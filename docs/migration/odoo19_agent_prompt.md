> **วิธีใช้:** วางเนื้อหาใต้เส้นคั่นเป็นข้อความสั่งงานในบทสนทนากับ coding agent แล้วแทน/ตรวจ `<...>` — จับคู่กับ `docs/migration/odoo19_plan.md` (บล็อก `plan-scope`)
>
> - prompt **ไม่ใช่ที่เก็บกฎ** — กฎจริงอยู่ที่ `dev-playbook/BASE_PLAYBOOK.md` + `PLAYBOOK.md`/`AGENTS.md` ของ repo · ไฟล์นี้แค่ *ชี้* + ย้ำข้อที่แพงที่สุด
> - Owner Verification Checklist ท้ายไฟล์ = ของเจ้าของ repo ใช้ตรวจหลัง agent รายงาน — อย่าให้ agent ตรวจตัวเอง

---

## งาน: Port 4 custom addons Odoo 10 → Odoo 19 (MINOR—กระทบ compliance)

### กฎเหล็ก — อ่านก่อนทำทุกอย่าง

**cwd = `/home/kitcharoenp/respo/odoo/x_odoo_10_addons`** · แผนรอบนี้ที่ `docs/migration/odoo19_plan.md` · ทุก path เขียนจากราก
**Mode: REFACTOR (escalate เป็น CROSS-MODULE/CONTRACT-TOUCHING ตาม self-check base §2) · Tier: 3 · `plan_id: port-4-addons-odoo10-to-odoo19`** (ใช้ค่านี้ใน Evidence Block)

1. **ห้ามเริ่มแก้ไฟล์ใด ๆ** จนกว่าจะอ่าน `docs/migration/odoo19_plan.md` ครบ (โดยเฉพาะบล็อก `plan-scope` + ตาราง G-1..G-13, E-1..E-4) และยืนยันฉบับล่าสุดด้วย:
   `grep -c 'port-4-addons-odoo10-to-odoo19' docs/migration/odoo19_plan.md` (ต้อง ≥1)
2. **มีข้อสงสัยที่กฎไม่ครอบคลุม → ถามเจ้าของ repo ก่อน ห้ามเดา** (โดยเฉพาะ `hr.expense` state mapping และ analytic change)
3. **ถ้าข้อเท็จจริงไม่ตรงกับแผน** (เวอร์ชัน Odoo ไม่ตรง 19 · dependency `telco_hr_employee`/`x_hr_timesheet_sheet` ยังไม่เป็น 19 · working tree ไม่สะอาด) **หยุดแล้วรายงาน ห้ามแก้เอง**
4. **ห้ามทำเกิน scope ในบล็อก `plan-scope`** — พบปัญหาอื่น (module อื่นใน repo, i18n) ให้บันทึกแจ้ง ไม่ใช่แก้แซมเงียบ ๆ
5. **ก่อนรายงานว่าเสร็จ ต้องแนบ Evidence Block** — **ห้ามเขียน exit code/output ที่ไม่ได้รันจริง** (base §8 ข้อ 1) ถ้าไม่มี Odoo 19 environment ให้บอกตรง ๆ ว่า AC-4/AC-5 ยังไม่ verify
6. **ห้าม commit / push / merge / tag** โดยไม่มีคำสั่งชัดเจนจากเจ้าของ
7. **ถ้าถูก guard บล็อก** → รายงานหรือ emit `PLAN AMENDMENT` ห้ามหาทางเลี่ยงด้วย `sed -i`/`python3 -c`/เปลี่ยน cwd

### อ่านก่อนเริ่ม
- `docs/migration/odoo19_plan.md` — scope, blast radius, AC, ความเสี่ยง R-1..R-4
- `dev-playbook/BASE_PLAYBOOK.md` §2 (modes/self-check), §5.1 (characterization test), §5.6 (root-cause), §8 (enforcement)
- โค้ดต้นทาง 4 module: ไฟล์ `models/*.py`, `report*/*.py`, `views/*.xml`, `report/templates/*.xml`, `__manifest__.py`
- **อ้างอิง API 19.0 จริง** จาก `github.com/mirror/odoo/tree/19.0` — อย่าจำจากเวอร์ชันเก่า

### คำตัดสินที่มีแล้ว — ห้ามถามซ้ำ ห้ามเปิดใหม่
| # | ประเด็น | คำตัดสิน |
|---|---|---|
| D-1 | จะใช้ OCA `l10n-thailand` แทน WHT เลยไหม | **ไม่ใช่รอบนี้** — รอบนี้ port `x_account_withholding_tax_document` ให้เดินบน 19 ก่อน; การ adopt OCA เป็น round แยก (Non-goal) |
| D-2 | `for_withhoding_tax_doc` (typo) | คง typo ไว้เพื่อ compat กับ view/domain เดิม เว้นแต่เจ้าของสั่ง rename พร้อม data migration |
| D-3 | python style | Odoo 19 = Python 3 เท่านั้น — ลบ `u''` prefix, `dict.has_key`, print-statement (ถ้าเจอ) |

### สิ่งที่ต้องขอจากเจ้าของ (agent ทำแทนไม่ได้)
| เมื่อไหร่ | เจ้าของต้องทำ | ทำไม |
|---|---|---|
| ก่อน AC-4 | จัดหา Odoo 19 instance + DB ทดสอบ `<db19>` | ต้องรัน install จริงจึงวัด AC-4 ได้ |
| ก่อน Step "hr.expense" | ยืนยัน state mapping (`done`/`post` → ค่า 19) และนโยบาย `analytic_distribution` | เป็นการตัดสินใจทางธุรกิจ/บัญชี |
| หลัง agent รายงาน | อนุมัติ `git add`/commit (ห้ามก่อนตรวจ Owner Checklist) | การ commit = เจ้าของสั่งเท่านั้น |

### ขั้นตอน (ทำทีละ Step · รัน verify ของ Step ให้ผ่านก่อนไป Step ถัดไป · ห้ามข้าม)

**Step 0 — Preflight / characterization baseline**
- `git status --porcelain` ต้องสะอาด · ยืนยัน Odoo 19 target จริง
- เก็บ characterization baseline: เก็บ PDF/xlsx/ค่ารวมปัจจุบันของ report แต่ละตัว (perdiem, expense-by-date, WHT certificate) ไว้เทียบหลัง port — base §5.1 **ห้ามแก้โค้ดก่อนมี baseline**
- ตรวจ dependency: `telco_hr_employee`, `x_hr_timesheet_sheet`พอร์ตหรือยัง → ถ้ายังไม่ → **หยุด emit `PLAN AMENDMENT` (R-1)**
- verify: baseline ไฟล์เทียบมีครบ + dependency ชัด

**Step 1 — `x_account_withholding_tax_document` (standalone-ish, ไม่มี shared field กับ module อื่น)**
- แก้ G-1,G-3,G-4,G-5,G-6,G-7,G-8,G-11,G-12,G-13 + `compute_all` signature + `has_group`
- rewrite report เป็น `ir.actions.report` / `_get_report_values` (G-2), template `report.external_layout`→`web.external_layout`, Bootstrap grid (G-9,G-10)
- verify: AC-1 (py_compile), AC-2 (grep clean) เฉพาะโฟลเดอร์นี้, `xml` parse ผ่าน (`python3 -c "import xml.etree.ElementTree as E,sys; [E.parse(f) for f in sys.argv[1:]]" $(find x_account_withholding_tax_document -name '*.xml')`)

**Step 2 — `telco_expense` (core hr.expense extension — อันตรายสุด ต้องมี owner decision)**
- จัดการ E-1..E-3 + G-1,G-7,G-11
- ถ้า owner ยังไม่ยืนยัน state/analytic mapping → **หยุดรอ** ห้ามเดา
- verify: AC-1, AC-2 (โฟลเดอร์นี้), model load syntax

**Step 3 — `telco_expense_qweb` (พึ่ง `telco_expense` จาก Step 2)**
- rewrite old report API (G-2), `export_excel` base64/datas ให้ตรง API 19, template G-9/G-10, view G-11/G-12
- ตรวจ field ที่ query จาก Step 2 (E-4) ว่ายังชื่อเดิม/คำนวณตรง
- verify: AC-1, AC-2, AC-3 (เพิ่ม `_description` ให้ `telco_expense` model ถ้าขาด)

**Step 4 — `x_report_timesheet_perdiem` (พึ่ง `x_hr_timesheet_sheet` — ดู R-1)**
- rewrite old report API (G-2), date defaults (G-7), `account.analytic.line` custom fields (R-1), view G-11/G-12
- verify: AC-1, AC-2, AC-3

**Step 5 — Whole-set gate**
- รัน AC-1, AC-2, AC-3 ครบทุกโฟลเดอร์
- ถ้ามี Odoo 19 env: รัน AC-4 + เทียบ baseline (AC-5) → แก้ layout/ตัวเลขจนตรง
- verify: ตาราง AC ทุกแถวผ่านหรือระบุ "รอ environment" ตามจริง

**Step 6 — รายงาน + Evidence Block** (อย่า commit)

### จุดที่ต้องหยุดรอ (ห้ามข้าม)
- หลัง Step 0 ถ้า dependency ไม่พร้อม → หยุด
- ก่อน Step 2 mapping → รอ owner
- หลัง Step ใดถ้า verify ไม่เขียว → หยุดรายงาน ห้ามแก้ต่อ
- ก่อน `git add`/commit → รอ go-ahead

### เมื่อพบว่าต้องแตะของนอกแผน
emit บล็อกนี้แล้วหยุดรอ (base §4):
```text
PLAN AMENDMENT
Reason:
Affected contract:
Proposed change:
Alternatives:
Requested decision:
```

### รูปแบบ Evidence Block (แนบท้ายรายงาน)
```text
Evidence — plan_id: port-4-addons-odoo10-to-odoo19
Approval ref: <ข้อความ/เวลา go-ahead ของเจ้าของ — ต้องเกิดก่อนแก้ไฟล์ครั้งแรก>
AC-1 cmd: <คำสั่ง>            exit: <จริง>
AC-2 cmd: <คำสั่ง>            exit: <จริง>  (grep ต้องไม่เจอ match)
AC-3 cmd: <คำสั่ง>            output: <ว่าง>
AC-4 cmd: <คำสั่ง odoo -i>    exit: <จริง หรือ "รอ environment">
AC-5 baseline diff: <สรุปเทียบค่าต่อ report + ว่าตรง/ต่าง>
Files touched: <list>
Gate ที่ไม่ผ่าน / ความเสี่ยงที่ยังเหลือ: <ต้องเขียน — ถ้าไม่มีให้เขียน "ไม่มี" พร้อมสิ่งที่ยังไม่ได้ทดสอบ>
```

---

## Owner Verification Checklist (เจ้าของใช้หลัง agent รายงาน)

- [ ] `git diff --name-only HEAD` → มีแต่ 4 โฟลเดอร์ + `docs/migration/**`, ไม่มี `telco_hr_employee`/`x_hr_timesheet_sheet`/`i18n`
- [ ] สุ่มรัน AC-2 ใหม่ → grep ไม่เจอ `@api.multi|track_visibility|states=|attrs=|<tree|report.external_layout|product.uom|self.env['report']`
- [ ] AC-4 รันจริงใน Odoo 19 แล้ว install ผ่าน (ถ้าไม่มี env ต้องระบุชัดว่ายังไม่ verify)
- [ ] report PDF/xlsx เทียบ baseline แล้วค่ารวม + ตัวเลขภาษาไทยตรง
- [ ] Evidence Block มีบรรทัด "Gate ไม่ผ่าน/ความเสี่ยง" เนื้อหาจริง ไม่เว้นว่าง
- [ ] ผ่านครบ → จึงให้ go-ahead commit
