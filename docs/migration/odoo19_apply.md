# Apply Plan: Port 4 addons Odoo 10 → 19 (decision-complete, ผู้ลงมือ = โมเดลต้นทุนต่ำ)

> ไฟล์นี้คือ "ไฟล์ apply ของรอบนี้" ที่ `odoo19_agent_prompt.md` / `odoo19_plan.md` อ้างถึง
> แปลง synthesis ที่อนุมัติแล้ว → ขั้นตอนย่อยที่ **โมเดลระดับกลาง/พื้นฐานทำตามได้เป๊ะ** โดยเดาให้น้อยที่สุด
> ทุก Step ต้อง **เล็ก · self-contained · วัดด้วยคำสั่ง deterministic · มี golden example · มี stop-condition**

## หลักออกแบบสำหรับโมเดลต้นทุนต่ำ (บังคับใช้ทุก Step)
1. **1 Step = 1 กลุ่มไฟล์เล็ก** (ไม่เกิน ~1 ไฟล์ .py + XML ที่ผูกกัน) — ห้ามรวมหลาย module ใน step เดียว
2. **Write-set ปิด** — ทำได้เฉพาะ `allow_write` ใน `plan-scope` ของ `odoo19_plan.md`; เจอสิ่งที่ต้องแตะนอกนั้น → `PLAN AMENDMENT` ห้ามแก้
3. **ก่อน/หลัง เป็น pattern ที่จับคู่ได้จริง** — ทุก transformation เขียน `MATCH → REPLACE` ไม่ใช่ "ทำให้มันเข้ากันได้"
4. **golden example ทุก step** — มี snippet input→output จริงให้ลอกสูตร (โมเดลถูกทำถูกเมื่อมีตัวอย่าง ไม่ใช่เมื่อถูกอธิบาย)
5. **verify เป็นคำสั่งรันได้** — end-of-step มีคำสั่ง + ผลที่คาด; **รันไม่ผ่าน = ห้ามไป stepถัดไป** (ห้าม soften)
6. **deterministic ก่อน LLM เสมอ** (gap-analysis A4): build/grep/py_compile/pytest เขียวก่อน ค่อยส่งให้ verifier
7. **loop cap ≤2 รอบ/step** (gap A3): แก้ไม่ผ่านใน 2 รอบ → หยุด + รายงานพร้อมสิ่งที่ลองไปแล้ว ห้าม retry ต่อเงียบ ๆ
8. **ไม่ commit/push** — ทำตามแผนเท่านั้น การ commit = เจ้าของสั่งในบทสนทนา

## ลำดับ module (เรียงตาม dependency — ทำทีละตัวจนจบค่อยไปตัวถัดไป)
`x_account_withholding_tax_document` (independent) → `telco_expense` → `telco_expense_qweb` → `x_report_timesheet_perdiem`
เหตุผล: qwebพึ่ง telco_expense, perdiemพึ่ง x_hr_timesheet_sheet (dependency ต่าง module)

---

## Step 0 — Preflight + characterization baseline (KILL-POINT)
- **ทำ:** `git status --porcelain` ต้องว่าง · ยืนยัน target = Odoo 19 จริง · สร้าง golden baseline: เก็บ PDF/xlsx/ค่ารวมปัจจุบันของ report 3 ตัว + WHT certificate 1 ฉบับ (จาก env Odoo 10) ไว้ใน `docs/migration/baseline/`
- **ตรวจ dependency ต่าง module:** `telco_hr_employee`, `x_hr_timesheet_sheet` มีรุ่น 19 หรือยัง
- **STOP:** ถ้า dependency ข้างต้นยังไม่ 19 → emit `PLAN AMENDMENT` (R-1) ห้าม port ต่อแบบ field หาย
- **verify:** `ls docs/migration/baseline/` มีไฟล์เทียบครบ + dependency state บันทึกแล้ว

---

## Pattern Sheet — transformation ที่ใช้ซ้ำ (ลอกสูตรตามนี้)
| ID | MATCH (Odoo 10) | REPLACE (Odoo 19) | หมายเหตุ |
|---|---|---|---|
| P-1 | `@api.multi` + newline + `def ...` | ลบ `@api.multi` บรรทัดนั้นทิ้ง | method ยัง `self.ensure_one()` ถ้าต้องการ |
| P-2 | `self.env['report'].get_action(rec, '<module>.<tpl>', data=datas)` | `rec._render_qweb_pdf(...)` / `self.env['ir.actions.report'].get_action(...)` (ดู golden) | report model ถูกถอด v11 |
| P-3 | `class X(models.AbstractModel): _name='report.<mod>.<tpl>' ... def render_html(self, docids, data=None)` | override `_get_report_values(self, docids, data=None)` คืน dict + `@api.model` | ดู golden G-REPORT |
| P-4 | `import odoo.addons.decimal_precision as dp` ... `digits=dp.get_precision('Account')` | ลบ import · `digits=(16,2)` หรือ `dp.get_precision` แบบ new-API | WHT |
| P-5 | `track_visibility='onchange'` | `tracking=True` | WHT state |
| P-6 | `_inherit = ['mail.thread', 'ir.needaction_mixin']` | `_inherit = ['mail.thread']` | mixin ถอด v11 |
| P-7 | `self.env.user.company_id` / `self.env.uid` | `self.env.company` / `self.env.uid`(ได้) หรือ `self.env.user.id` | |
| P-8 | `fields.date.context_today(self)` | `fields.Date.context_today(self)` | ตัวสะกด case |
| P-9 | `'product.uom'` (Many2one/comodel/search) | `'uom.uom'` | v14 |
| P-10 | `<button ... states="draft" ...>` | `<button ... invisible="state != 'draft'" ...>` | states ออก v11 |
| P-11 | `attrs="{'readonly': 1}"` / `{'invisible': ...}` | `readonly="1"` / `invisible="<expr>"` inline | attrs ออก v17 |
| P-12 | `<tree ...>...</tree>` (view) | `<list ...>...</list>` | v18 rename |
| P-13 | template `inherit_id="report.external_layout"` / `t-call="report.external_layout_header"` | `web.external_layout` / `web.external_layout_header` | v12 namespace |
| P-14 | `t-raw="..."` | `t-out="..."` | |
| P-15 | `col-xs-12` / Bootstrap3 grid | `col-12` (BS5) · ตรวจ offset/spacing | v16 |
| P-16 | manifest `'auto-install': True` | `'auto_install': True` | สะผิด |

---

## Module A — `x_account_withholding_tax_document`

### A-1 · manifest
- **write-set:** `x_account_withholding_tax_document/__manifest__.py`
- **ใช้ pattern:** P-16 · ตรวจ `'depends'` ไม่มี `'report'` module (ถูกรวมเข้า core แล้ว) → ลบ `'report'` ออกจาก depends ถ้ามี
- **verify:** `python3 -c "import ast;ast.literal_eval(open('x_account_withholding_tax_document/__manifest__.py').read().split('{',1)[1].rsplit('}',1)[0].join('{}'))"` exit 0 (หรือ `grep -q "'auto_install'" && ! grep -q "auto-install"`)

### A-2 · model `x_withholding_tax_document.py`
- **write-set:** ไฟล์เดียว
- **ใช้ pattern:** P-1 (submit/approve/cancel/reset/write), P-4, P-5, P-6, P-7, P-8(no), P-9(`product.uom`→`uom.uom` ทั้ง Many2one comodel + default search) · เพิ่ม `_description` (มีแล้ว) · `user_has_groups(...)` → `self.env.user.has_group(...)` · ตรวจ `compute_all()` signature ของ `account.tax` ตาม 19 source
- **golden:** see G-UOM, G-REPORT below
- **verify:** `python3 -m py_compile x_account_withholding_tax_document/models/x_withholding_tax_document.py` exit 0 + `! grep -nE "@api\.multi|track_visibility|needaction|product\.uom|user_has_groups|dp\.get_precision" <file>`

### A-3 · `product_template.py`
- **write-set:** ไฟล์เดียว · คง typo `for_withhoding_tax_doc` ตาม D-2 (ห้าม rename ถ้าไม่มี amendment)
- **verify:** py_compile + model field เดิมยังอยู่

### A-4 · views
- **write-set:** `views/x_withholding_tax_document_form_view.xml`, `_tree_view.xml`
- **ใช้ pattern:** P-10 (buttons), P-12 (`<tree>`→`<list>`), ตรวจ `widget="monetary"` + `currency_field` option ยังใช้ได้
- **verify:** `python3 -c "import xml.etree.ElementTree as E,glob;[E.parse(f) for f in glob.glob('x_account_withholding_tax_document/views/*.xml')]"` exit 0

### A-5 · report + templates
- **write-set:** `reports/x_withholding_tax_document_report.xml`, `reports/templates/*.xml`
- **ใช้ pattern:** P-3 (report util), P-13, P-14, P-15
- **golden:** G-REPORT
- **verify:** XML parse ทุกไฟล์ + `! grep -rn "report.external_layout\|t-raw" x_account_withholding_tax_document/reports/`

---

## Module B — `telco_expense` ⚠️ (แตะ hr.expense — ต้องมี owner decision)

### B-0 · OWNER GATE (หยุดรอ)
- ยืนยัน 3 เรื่องก่อนแก้: (1) `payment_mode` state mapping 10→19 (`done`/`post` → ?) (2) นโยบาย analytic (`analytic_account_id` → `analytic_distribution`) (3) `accounting_date` มีใน 19 หรือเก็บเป็น `x_`
- **STOP:** ไม่ได้คำตอบ → ห้ามเดา (แผน R-2)

### B-1 · model `telco_expense.py`
- **ใช้ pattern:** P-1(onchange ไม่ต้อง decorator), P-8 + ตัดสินใจ B-0
- เพิ่ม `_description` ให้ model (AC-3 ตอนนี้ขาด)
- **verify:** py_compile + grep clean ตาม AC-2 เฉพาะโฟลเดอร์

### B-2 · views
- **ใช้ pattern:** P-11 (`attrs`→inline readonly), ตรวจ xpath `//field[@name='tax_ids']` ยัง match view 19 (view ref `hr_expense.hr_expense_form_view` อาจเปลี่ยน)
- **verify:** XML parse + xpath anchor มีอยู่จริงใน parent view (ตรวจกับ 19 source ไม่ใช่เดา)

---

## Module C — `telco_expense_qweb` (พึ่ง B เสร็จแล้ว)

### C-1 · model `telco_expense_qweb_by_date.py`
- **ใช้ pattern:** P-1 (print_report/export_excel), P-2 (`env['report'].get_action`), P-8
- `export_excel`: ตรวจ `ir.attachment` `datas` ต้องเป็น base64 bytes ใน 19 · `build_xlsx` import path คงได้
- **verify:** py_compile + `! grep -nE "@api\.multi|env\['report'\]" <file>`

### C-2 · report util `telco_expense_qweb_by_date_report_util.py`
- **ใช้ pattern:** P-3 (render_html → `_get_report_values` + `@api.model`)
- **golden:** G-REPORT
- **verify:** py_compile + `_get_report_values` มีอยู่, ไม่มี `self.env['report']`

### C-3 · views + templates
- **ใช้ pattern:** P-10/P-11/P-12 (views), P-13/P-14/P-15 (templates), P-2 (report xml model name)
- **verify:** XML parse ทุกไฟล์

---

## Module D — `x_report_timesheet_perdiem` (พึ่ง x_hr_timesheet_sheet — R-1)

### D-0 · dependency check (ซ้ำจาก Step 0 แต่ confirm อีกรอบ)
- **STOP:** `account.analytic.line` custom fields (`x_start_date` ฯลฯ) ไม่มีใน env 19 → amendment

### D-1 · model `x_report_timesheet_perdiem.py`
- **ใช้ pattern:** P-1, P-2, P-8 · เพิ่ม `_description` (มีแล้ว)
- **verify:** py_compile + grep clean

### D-2 · report util `x_report_timesheet_perdiem_report_util.py`
- **ใช้ pattern:** P-3 (render_html→_get_report_values) · `self.sum` เก็บ state บน record = ไม่ปลอดภัยใน 19 (cache/multi) → เก็บเป็นตัวแปร local/ส่งกลับผ่าน dict ไม่ใช่ instance attr (flag ให้ verifier ตรวจ)
- **verify:** py_compile

### D-3 · views + report xml + template
- **ใช้ pattern:** P-10/P-12, P-2 (report model), P-13/P-14/P-15
- **verify:** XML parse

---

## Final Gate (ทุก module จบแล้ว)
- รัน AC-1 (py_compile ทั่ว), AC-2 (grep ทั่ว — ห้าม match), AC-3 (`_description` ครบ) ตาม `plan-scope`
- ถ้ามี env 19: AC-4 (`odoo -i ... --stop-after-init` exit 0) + AC-5 เทียบ `baseline/`
- **รายงาน:** Evidence Block ทุก step + ตาราง "step ที่ข้าม/ต้อง amendment" + **ห้ามเคลมผ่านถ้าไม่รัน**

---

## Golden Examples (ลอกสูตรได้)

### G-REPORT (P-2 + P-3) — old report API → 19
```python
# BEFORE (Odoo 10)
class XReportUtil(models.AbstractModel):
    _name = 'report.mod.tpl'
    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        rep = Report._get_report_from_name('mod.tpl')
        docs = self.env['hr.expense'].browse(docids)
        return Report.render('mod.tpl', {'docs': docs, ...})
# AFTER (Odoo 19)
class XReportUtil(models.AbstractModel):
    _name = 'report.mod.tpl'
    _description = 'Mod Tpl Report'
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.expense'].browse(docids)
        return {'docs': docs, ...}
# caller (print_report) ->
#   return self.env['ir.actions.report']._action_report / report_action(...)
```

### G-UOM (P-9)
```python
# BEFORE
product_uom_id = fields.Many2one('product.uom', ..., default=lambda self: self.env['product.uom'].search([], limit=1, order='id'))
# AFTER
product_uom_id = fields.Many2one('uom.uom', ..., default=lambda self: self.env['uom.uom'].search([], limit=1, order='id'))
```
