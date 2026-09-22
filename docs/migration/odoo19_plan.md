# Plan: Port 4 custom addons จาก Odoo 10 → Odoo 19 (behavior-preserving)

**วันที่:** 2026-09-22
**สถานะ:** เสนอเพื่ออนุมัติ
**ระดับเวอร์ชัน:** MINOR—กระทบ compliance (เปลี่ยน runtime target ทั้งชุด + แตะ contract ของ `hr.expense` / report API)
**เข้าเกณฑ์ independent review:** เข้า — แตะ ≥2 module ที่ coupled กัน (`telco_expense` ↔ `telco_expense_qweb`) และเปลี่ยน public contract (report action API, view semantics) → ต้องผ่านรอบ review อิสระตาม `dev-playbook/README.md` "ปล่อยเวอร์ชันใหม่" ข้อ 1–3

> ไฟล์นี้อ้างโครงสร้างจาก `dev-playbook/PLAN.template.md` · กฎ/โหมด/-tier อ้าง `dev-playbook/BASE_PLAYBOOK.md` §2, §5, §7, §10
> บล็อก `plan-scope` ด้านล่างคือ **แหล่งความจริงเดียวของ scope** — prose รอบ ๆ ไม่มีผลบังคับ

---

## Objective

ย้าย addon 4 ตัว (`x_report_timesheet_perdiem`, `x_account_withholding_tax_document`, `telco_expense`, `telco_expense_qweb`) ที่เขียนบน Odoo 10 ให้ติดตั้งและทำงานได้บน **Odoo 19 (Ubuntu)** โดย **คงพฤติกรรมธุรกิจเดิม** (รายงาน/เอกสารรูปแบบไทย, การคิดเงินเป็นตัวอักษรภาษาไทย, workflow draft→submit→approve) — ไม่ใช่การ rewrite ฟีเจอร์

ผลลัพธ์ที่วัดได้:
1. ทุกไฟล์ `.py` compile ผ่านภายใต้ Python ที่ Odoo 19 ใช้ และไม่มี API ที่ถูกถอดออกแล้วหลงเหลือ (ตรวจด้วย grep — ดู AC)
2. `ir.module.module` install ทั้ง 4 ตัวโดยไม่ raise ตอน load view/report
3. เปิด report แต่ละตัวแล้ว render ได้ (qweb-pdf / qweb-html / xlsx) โดยค่ารวม/ตัวเลขตัวอักษรตรงกับ baseline Odoo 10
4. record rules + group manager ของ WHT ยังบังคับ approve/edit ได้เท่าเดิม

**ทำไม:** Odoo 10 EOL นานแล้ว · API เดิม (`@api.multi`, old `report` model, `states=`, `track_visibility`, `product.uom`, Bootstrap-3 layout) ถูกถอดออกในสาย 11→19 ทำให้โค้ดปัจจุบันโหลดไม่ขึ้นบน 19

---

## Scope — บล็อก `plan-scope` (แหล่งความจริงเดียว)

```yaml plan-scope
plan_id: port-4-addons-odoo10-to-odoo19
tier: 3
mode: REFACTOR
blast_radius: [มาก, ยาก, ทันที]
allow_write:
  - x_report_timesheet_perdiem/**
  - x_account_withholding_tax_document/**
  - telco_expense/**
  - telco_expense_qweb/**
  - docs/migration/**
deny_write:
  - "**/__pycache__/**"
  - "*/i18n/*.po"
  - "*/static/libs/**"
  - "../telco_hr_employee/**"
  - "../x_hr_timesheet_sheet/**"
  - "docs/playbook/ACTIVE_PLAN"
  - ".claude/settings.json"
  - ".claude/skills/**"
allow_bash:
  - "git status --porcelain"
  - "git diff *"
  - "python3 -m py_compile *"
  - "grep -rn * x_report_timesheet_perdiem telco_expense telco_expense_qweb x_account_withholding_tax_document"
acceptance_criteria:
  - id: AC-1
    cmd: "python3 -m py_compile $(find x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb -name '*.py')"
    expect_exit: 0
  - id: AC-2
    cmd: "! grep -rnE '@api\\.(multi|one)|track_visibility|ir\\.needaction_mixin|decimal_precision as dp|self\\.env\\[.report.\\]|env\\.user\\.company_id|<tree|states=|attrs=|t-raw|report\\.external_layout|product\\.uom' x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb"
    expect_exit: 0
  - id: AC-3
    cmd: "grep -rLn '_description' $(find x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb -name '*.py' | xargs grep -lE 'models.(Model|TransientModel|AbstractModel)')"
    expect_exit: 0
  - id: AC-4
    cmd: "odoo -d <db19> -i x_account_withholding_tax_document,telco_expense_qweb,x_report_timesheet_perdiem --stop-after-init --log-level=error"
    expect_exit: 0
require_go_ahead: true
go_ahead: "<ยังไม่ได้ — รอ go-ahead ในบทสนทนา>"
evidence_path: docs/migration/evidence-odoo10-to-odoo19.md
```

### หมายเหตุไวยากรณ์
- **AC-4 ต้องรันในสภาพ Odoo 19 จริง** (มี `<db19>` + binary) — ถ้าไม่มีสภาพแวดล้อม ให้ mark AC-4 ว่า "รอ environment" และห้ามเคลมว่าผ่าน (§8 ข้อ 1)
- AC-3 ยังเป็นเป้าหมาย (ทุก model ต้องมี `_description` ตาม Odoo 19) — ตอนนี้ WHT/perdiem มีแล้ว แต่ `telco_expense` model ขาด ให้เพิ่มในรอบแก้

---

## Scope — ไฟล์ที่ไม่แตะ (ห้ามเด็ดขาด)

- **Dependency นอกแผน 2 ตัว:** `telco_hr_employee` (ที่ `telco_expense` พึ่ง `employee_id.x_analytic_account_id`) และ `x_hr_timesheet_sheet` (ที่ perdiem report พึ่ง field `x_start_date`/`x_end_date`/`x_is_per_diem`/`x_overnight`/`x_notes`/`x_vehicle_id`/`x_state_id` บน `account.analytic.line`) — ทั้งคู่เป็น Odoo 10 และ **ไม่อยู่ใน 4 ตัวเป้าหมาย** ถ้าสองตัวนี้ยังไม่พอร์ต field ที่อ้างถึงจะหาย → ดูความเสี่ยง R-1 ต้อง emit `PLAN AMENDMENT` ไม่ใช่พอร์ตเงียบ ๆ
- `i18n/*.po`, `static/libs/**` — ของ third-party/แปล ไม่ต้องแตะในรอบ port

---

## Blast Radius (base §2)

| คำถาม | คำตอบ |
|---|---|
| มี caller/consumer กี่จุดที่พึ่ง? | มาก — `telco_expense_qweb` เรียก method/helper ใน `telco_expense` โดยตรง (shared field `x_project_id`, `x_require_po`, `accounting_date`); perdiem/WHT ผูกกับ field custom ของ module อื่น |
| ถ้าผิดพลาด ย้อนกลับง่ายแค่ไหน? | ยาก — เป็นการแก้ทั้ง view+model+report พร้อมกัน, ผิดแล้ว report เงียบ (numeric ผิดแต่ไม่มี error) |
| ผู้ใช้/ระบบอื่นเห็นผลกระทบทันทีหรือไม่? | ทันที — document/report เป็น user-facing |

→ blast radius = **สูง** (3 ข้อ "มาก/ยาก/ทันที") · Tier 3 · **ต้อง**ผ่าน Plan-first Gate เต็มรูป + characterization test (base §5.1, §2 โหมด REFACTOR)

---

## รายการปัญหา compatibility ที่พบ (ต่อ module)

### ทุก module (Odoo 10 → 19 API ที่ถูกถอด)
| # | ที่พบในโค้ด | สถานะ 19 | ต้องแก้ |
|---|---|---|---|
| G-1 | `@api.multi` (`telco_expense_qweb_by_date.print_report/export_excel`, perdiem `print_report`, WHT `submit_/approve_/cancel_/reset_/write`) | ถอดออกตั้งแต่ v13 | ลบ decorator, ใช้ `self.ensure_one()` ตามเดิม |
| G-2 | Old reporting API: `self.env['report'].get_action(...)`, `Report._get_report_from_name`, `def render_html(self, docids, data)` (`report_util.py` ทุกตัว, `models/*.print_report`) | model `report` ถูกแทนด้วย `ir.actions.report` ตั้งแต่ v11–12 | เปลี่ยนเป็น AbstractModel ชื่อ `report.<module>.<template>` + override `_get_report_values(self, docids, data)` + เรียกผ่าน `self.env['ir.actions.report']._render_qweb_pdf/_html` หรือ `report_action` |
| G-3 | `import odoo.addons.decimal_precision as dp` + `digits=dp.get_precision(...)` (WHT) | `get_precision` ย้าย/เลิกใช้แบบตรง | ใช้ `digits=(16,2)` tuple หรืออ้าง precision ผ่าน helper ใหม่ |
| G-4 | `track_visibility='onchange'` (WHT `state`) | ถอดออก v11 | ใช้ `tracking=True` |
| G-5 | `_inherit = [..., 'ir.needaction_mixin']` (WHT) | mixin ถอดออก v11 | ลบออก, ใช้ `mail.thread` + `activity` ถ้าต้องการ |
| G-6 | `self.env.user.company_id` (WHT `company_id`/`currency_id` default) | deprecated | `self.env.company` |
| G-7 | `fields.date.context_today(self)` (perdiem/qweb โดย `fields.date` ตัวเล็ก) | ตัวสะกดถูกต้องคือ `fields.Date` |แก้ case + ทดสอบว่า default ยังทำงาน (Odoo 19 ไม่รับ `self` แบบเดิมในบาง call site) |
| G-8 | model `product.uom` (WHT `product_uom_id`) | เปลี่ยนเป็น `uom.uom` ตั้งแต่ v14 | เปลี่ยน reference ทั้ง field + search |
| G-9 | QWeb: `inherit_id="report.external_layout"`, `report.external_layout_header/footer`, `t-raw` | namespace `report.` → `web.` (v12+), `t-raw` ออก | ใช้ `web.external_layout`, `t-out` |
| G-10 | Layout CSS `col-xs-12` / Bootstrap 3 (templates) | v16+ ใช้ Bootstrap 5 | แปลง grid (`col-xs-12`→`col-12`) ตรวจ margin/pagination |
| G-11 | view `states=` (WHT buttons), `attrs=` (telco_expense form) | `states` ออก v11; `attrs` ออก v17 | ใช้ `invisible="state != 'draft'"` / `readonly="..."` แบบ inline expression |
| G-12 | `<tree>` in tree views | v18+ rename เป็น `<list>` | ใช้ `<list>` (ตรวจ alias) |
| G-13 | `__manifest__.py` key `'auto-install'` (perdiem/WHT สะผิด) | key ถูกคือ `auto_install` | แก้สะกด |

### `telco_expense` / `telco_expense_qweb` (hr.expense model drift — อันตรายที่สุด)
| # | ประเด็น | หมายเหตุ 19 |
|---|---|---|
| E-1 | override `payment_mode` ด้วย `states={'done':..., 'post':...}` | `hr.expense` v10 field/`state` value เปลี่ยนไปมาก (v16+ sheet รวมกลับเข้า `hr.expense`, state เป็น `draft/submitted/approved/posted/refused`) — ต้อง map ใหม่ |
| E-2 | `analytic_account_id` + `_onchange_employee_id` ตั้ง analytic | v16+ ใช้ `analytic_distribution` — onchange เดิมใช้ไม่ได้ตรง ๆ |
| E-3 | `accounting_date` (override field ที่มีอยู่) | ตรวจว่า 19 มี field นี้จริงหรือต้องเก็บเป็น custom `x_` |
| E-4 | perdiem/qweb query `hr.expense` search ด้วย field เดิม (`reference`, `total_amount`, `date`, `product_id.default_code`, `description`) | ตรวจชื่อ/พฤติกรรมทีละ field; `default_code` ย้ายไป `product.template` ในบางเวอร์ชัน |

### `x_account_withholding_tax_document`
- `product_template.py` เพิ่ม field `for_withhoding_tax_doc` (สะกด typo ติดใน domain) — คง typo ไว้ถ้าต้องเข้ากันได้กับข้อมูลเดิม หรือ rename ทั้ง model+view พร้อม migration
- `compute_all(...)` signature ของ `account.tax` เปลี่ยน (v11+) — ต้องอัปเดตพารามิเตอร์
- `ir_rule.xml` + group manager — พฤติกรรม `_check()` override `write` ใช้ได้ต่อ แต่ตรวจว่า `self.env.user.has_group(...)` แทน `user_has_groups` (deprecated)

### `x_report_timesheet_perdiem`
- ผูกกับ `account.analytic.line` field custom จาก `x_hr_timesheet_sheet` (ดู R-1) — ถ้า module นั้นยังไม่พอร์ต รายงานจะ error/ค่าว่าง

---

## External module research (งานที่ 2) — สรุปว่า "ใช้แทน" หรือ "พอร์ตเอง"

ค้นจาก Odoo Apps Marketplace (filter Free), nightly 19.0, และ GitHub 19.0/OCA ณ 2026-09:

| Module เป้า | ทางเลือกฟรีที่เจอ | สถานะ 19.0 | คำแนะนำ |
|---|---|---|---|
| `x_account_withholding_tax_document` | OCA **`l10n-thailand`**: `l10n_th_withholding_tax`, `l10n_th_account_tax`, `l10n_th_withholding_tax_report` (AGPL, ฟรี); + Odoo 19 core มี withholding tax (retention) ในตัว | PR "[19.0][MIG] l10n_th_account_tax_multi" กำลัง migrate → OCA apps store มีรุ่น 19 | **ใช้ OCA เป็นฐานคำนวณ/ทะเบียน WT** แล้วคงเฉพาะ PDF certificate แบบฟอร์มไทย (ภ.ง.3/53) ที่ custom layout จำเป็น — ลดโค้ดที่ต้องดูแล |
| `telco_expense` | OCA **`hr-expense`**: `hr_expense_invoice`, `hr_expense_payment`, `hr_expense_vendor_receipt`, `hr_expense_sequence` (AGPL, ฟรี) | ตอนนี้ 18.0.x — 19.0 ยังรอ migration | **ยังไม่แทนได้ทันที** — port ตัวเองก่อน, monitor OCA 19.0 แล้วค่อยแทนฟีเจอร์ที่ overlap |
| `telco_expense_qweb` (expense-by-date + xlsx report) | ไม่มี free module ตรงฟังก์ชัน (รายงานเฉพาะองค์กร/ภาษาไทย) | — | **port เอง** (ยกระดับ report API ตาม G-2) |
| `x_report_timesheet_perdiem` (perdiem จาก timesheet, ตัวเลขไทย) | ไม่มี free module ที่คิด per-diem แบบระบุ | — | **port เอง** |

> ข้อสรุป: ตัวที่มี free alternative ชัดคือ **WHT → OCA l10n-thailand** (แนะนำให้ adopt บางส่วน) ส่วนอีก 3 ตัวเป็น report/field เฉพาะ-org ที่ **ต้อง port เอง** — ไม่มีทางเลือกฟรีที่ดีกว่าที่พิสูจน์แล้ว

---

## Acceptance Criteria (สรุป — เต็มรูปแบบอยู่ในบล็อก)

| # | เกณฑ์ | วัดด้วย | ผลที่คาด |
|---|---|---|---|
| AC-1 | Python compile ผ่าน | `py_compile` ทุก `.py` | exit 0 |
| AC-2 | ไม่มี API/view attribute ที่ถอดแล้วหลงเหลือ | `grep -rE '@api\.multi|track_visibility|...'` | ไม่เจอ (exit 0) |
| AC-3 | ทุก model มี `_description` | `grep -L '_description'` | ว่าง |
| AC-4 | ติดตั้งใน Odoo 19 ได้ | `odoo -i ... --stop-after-init` | exit 0 |
| AC-5 (manual) | baseline ตรงกับ Odoo 10 | เทียบ PDF/xlsx 1 เคสต่อ report กับ environment เดิม | ค่าตรง |

---

## Rollback Plan

- ทำงานบน branch `port/odoo19-addons` — `git revert <sha>` ทีละ module ได้ (module แยกโฟลเดอร์กัน ไม่มี shared file)
- ยังไม่ tag/deploy จนกว่า AC-4 + AC-5 ผ่าน
- ถ้า Adopt OCA `l10n-thailand` ทำเป็น round แยก (`docs/migration/wht-to-oca.md`) เพื่อย้อนง่าย

---

## ความเสี่ยงที่ต้องประกาศ ห้ามซ่อน

| ID | ความเสี่ยง | การจัดการ |
|---|---|---|
| R-1 | dependency นอกขอบเขต (`telco_hr_employee`, `x_hr_timesheet_sheet`) ยังเป็น Odoo 10 → perdiem/expense อาจพอร์ตไม่ได้ถ้า field อ้างถึงหาย | ก่อนแตะ module ที่พึ่ง 2 ตัวนี้ ให้ตรวจว่าพอร์ตแล้ว; ถ้ายังไม่ → emit `PLAN AMENDMENT` ขยาย scope หรือ reduce field ที่อ้าง (ห้ามแก้ module เจ้าของคนอื่นเงียบ ๆ) |
| R-2 | `hr.expense` model drift (E-1..E-4) เปลี่ยนความหมายทางบัญชี | ต้องมี characterization test เทียบก่อน/หลัง; ห้ามเดา state mapping — ถ้าไม่ชัดถาม owner |
| R-3 | Bootstrap 3→5 + external_layout ทำ layout report เพี้ยน | ตรวจด้วยตา (AC-5) ทุก template; view-only ไม่ใช่ AC |
| R-4 | สภาพแวดล้อม Odoo 19 สำหรับ AC-4 อาจไม่มีในเครื่องนี้ | ถ้าไม่มี → รายงาน "ยังไม่ verify" ห้ามเคลมผ่าน (§8 ข้อ 1) |

---

## Non-goals

- ไม่ rewrite ฟีเจอร์/เปลี่ยน UI เกินจำเป็นเพื่อ port — ถ้าจะ adopt OCA WHT เป็นอีก round แยก
- ไม่พอร์ต module อื่นใน repo ที่ไม่ใช่ 4 ตัวเป้าหมาย
- ไม่แตะ `i18n/*.po` (ปล่อย round ถัดไป)

---

## Plan/go-ahead

`<ยังไม่ได้ — รอ go-ahead ในบทสนทนาปัจจุบัน>`
