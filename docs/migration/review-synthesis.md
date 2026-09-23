# Review Synthesis — แผน port 4 addons Odoo 10 → Odoo 19

**วันที่รวมผล:** 2026-09-22 · **ผู้รวมผล:** arbitrator (ชั้นที่ 3 — เจ้าของยืนยันแล้วว่าไม่ซ้ำ R1/R2 และไม่ซ้ำผู้ร่างแผน)
**input:** `docs/migration/odoo19_plan.md`, `docs/migration/odoo19_agent_prompt.md`, `review-R1.md` (242 บรรทัด), `review-R2.md` (102 บรรทัด) — อ่านครบทั้ง 4 ไฟล์
**สถานะ:** ข้อเสนอ merge — **ยังไม่ apply แผน** · **33 ข้อผ่านการตรวจยืนยันแล้ว** (A+B+C ครบ + D ที่ H-1 ยืนยัน 17 ข้อ — ดูหมวด G)
**คำตอบเจ้าของที่ได้รับแล้ว (2026-09-22):** มี Odoo 19 + Odoo 10 instance ✓ · จะ adopt dev-playbook จริง ✓ → ปิด E-1, E-2

> **verdict ร่วมของทั้งสองรีวิว: "ต้องแก้ก่อนใช้"** — R1 และ R2 สรุปตรงกันโดยไม่ได้เห็นผลของกันและกัน
>
> **การแบ่ง attribution ในไฟล์นี้:**
> - `มาจาก R1` / `R2` / `R1+R2` = ข้อเสนอของ reviewer — ผู้รวมผลไม่ได้เพิ่มเหตุผลใหม่
> - **`[V]`** = ผู้รวมผล**รันคำสั่งตรวจเอง**ตามคำสั่งเจ้าของ (2026-09-22) · raw output อยู่ในหมวด G
> - หมวด H (แนวทางกลุ่ม D) = ข้อเสนอเชิงกระบวนการของผู้รวมผล ไม่ใช่ finding ของ reviewer

---

### A. CONSENSUS — merge เข้าแผนได้ (R1+R2 เห็นตรงกัน)

| # | ตำแหน่งในแผน/prompt | ข้อเสนอ | มาจาก | เหตุผลรวม | ผลตรวจ `[V]` |
|---|---|---|---|---|---|
| A1 | `odoo19_plan.md:59-60` AC-2 | **เขียน AC-2 ใหม่ทั้งข้อ** — ปัจจุบันใช้เป็น gate ไม่ได้ | R1+R2 | R1: pattern `attrs=` ไม่ match ของจริงที่เขียนเป็น `<attribute name="attrs">`, ขาด pattern อีก ≥10 ชนิด, และ `! grep` เป็น **fail-open** · R2: AC-2 **ถูก guard deny** เพราะ entry ผิดไวยากรณ์ | ✅ **ยืนยัน** — `grep -rnE 'attrs=' telco_expense/views/` → exit 1 (ไม่เจอ) · `grep -rn 'name="attrs"'` → เจอ 2 จุด (`telco_expense_form_view.xml:28,36`) · guard → `deny` |
| A2 | `odoo19_plan.md:49-53` `allow_bash` | **เพิ่ม entry ให้ครบคำสั่งที่ AC ของตัวเองต้องใช้** (`find`, `xargs`, `odoo`, `python3 -c`) + **แก้ไวยากรณ์ entry `grep`** | R1+R2 | R1: AC-1/AC-3 ต้องใช้ `find`+`xargs`, AC-4 ต้องใช้ `odoo`, Step 1 ต้องใช้ `python3 -c` · R2: รัน guard จริงแล้ว AC-2/AC-4 ถูก deny | ✅ **ยืนยัน + พบมากกว่าที่รายงาน** — deny 4/5 คำสั่ง · รายละเอียดสำคัญ: entry `grep -rn * x_report...` **deny แม้แต่ `grep` ธรรมดา** เพราะ `*` อยู่กลางสตริง · `python3 -m py_compile` **allow เมื่อ argument เป็น path ตรง** แต่ **deny เมื่อใช้ `$(find ...)`** ← AC-1 ตามที่เขียนในแผนใช้ `$(find ...)` |
| A3 | `odoo19_agent_prompt.md:37-42` ตาราง "สิ่งที่ต้องขอจากเจ้าของ" | **เพิ่มแถว "Odoo 10 instance (หรือไฟล์ PDF/xlsx จริงจาก production) สำหรับ characterization baseline"** | R1+R2 | R1 (C-6/E2): ไม่ปรากฏหลักฐานว่ามี Odoo 10 ที่ยังรันได้ → gate Step 0 ผ่านไม่ได้ · R2 (B-5): ตารางระบุแค่ Odoo 19 ไม่เคยขอ Odoo 10 | ⬜ ไม่ใช่ข้อเท็จจริงเชิงเทคนิค — เจ้าของยืนยันเอง (E-1) |
| A4 | `odoo19_agent_prompt.md:26` + `odoo19_plan.md:8` | **แก้ path ที่อ้าง playbook เป็น absolute** — path สัมพัทธ์ `dev-playbook/BASE_PLAYBOOK.md` จาก cwd ไม่มีอยู่จริง | R1+R2 | ทั้งคู่ยืนยันว่า path ที่ prompt สั่งอ่านนั้นผิด → กฎเหล็กข้อ 3 (`prompt:18`) จะยิงตั้งแต่ก่อน Step 0 | ✅ **ยืนยัน** — `ls dev-playbook/BASE_PLAYBOOK.md` จาก cwd → `No such file` (exit 2) · **ตัวจริงอยู่ที่ `/home/kitcharoenp/respo/dev-playbook/`** (ดู C3) |
| A5 | `odoo19_plan.md:173` R-1 | **แก้ระดับความรุนแรงของ R-1** จาก "field ที่อ้างถึงหาย → รายงาน error/ค่าว่าง" เป็น **hard manifest dependency ที่บล็อกการติดตั้งทั้ง batch** | R1+R2 | R2 (B-4): เป็น `'depends'` ตรง ๆ → Odoo ปฏิเสธติดตั้งตั้งแต่ dependency resolution · R1 (C-5): แผนตามที่เขียนมีโอกาสสูงจบที่ Step 0 โดยไม่ส่งงาน | ✅ **ยืนยัน** — `x_report_timesheet_perdiem/__manifest__.py:10` = `'depends': ['x_hr_timesheet_sheet', 'report']` |

**หมายเหตุ A5:** เห็นตรงกันเฉพาะ *การประเมินความรุนแรง* — ส่วน *ทางออก* เป็น policy call → ดู **E-7**

---

### B. FACTUAL FIX — แก้ได้ทันที (ตรวจยืนยันครบ 8/8 แล้ว)

| # | ตำแหน่ง | ต้นฉบับบอกว่า | ความจริง | มาจาก | ผลตรวจ `[V]` |
|---|---|---|---|---|---|
| B1 | `odoo19_plan.md:112` G-11 | "`states` ออก v11" | ถูกถอดใน **v17** พร้อม `attrs` | R1+R2 | ✅ **CONFIRMED** — `ir_ui_view.py:495` (19.0): `'Since 17.0, the "attrs" and "states" attributes are no longer used.'` · odoo16 `fields.py:323` ยังมี `states = None` · `sale_order_views.xml` (16) ใช้ `states="` จริง 6 จุด |
| B2 | `odoo19_plan.md:110` G-9 | ระบุ `t-raw` ว่าเป็นของที่ "พบในโค้ด" | **ไม่มี `t-raw` เลยสักจุด** ใน 4 module | R1+R2 | ✅ **CONFIRMED** — `grep -rn 't-raw' <4 dirs>` → exit 1 (ว่าง) |
| B3 | `odoo19_plan.md:119` E-1 | "v16+ sheet รวมกลับเข้า `hr.expense`" | merge เกิดที่ **v19 เอง** (เวอร์ชันเป้าหมายของแผนนี้) | R1+R2 | ✅ **CONFIRMED** — odoo16 `hr_expense.py` อ้าง `hr.expense.sheet` 10 จุด · 19.0 `addons/hr_expense/models/` **ไม่มี `hr_expense_sheet.py`** · `hr_expense.py` (19) ไม่มี `sheet_id` มีเพียง `former_sheet_id = fields.Integer(string='Former Report')` ที่ `:283` ← ร่องรอย migration |
| B4 | `odoo19_plan.md:119` E-1 | `state` = 5 ค่า | มี **7 ค่า** — เพิ่ม `in_payment`, `paid` | R1+R2 | ✅ **CONFIRMED** — `hr_expense.py:124-136` (19.0): `draft, submitted, approved, posted, in_payment, paid, refused` |
| B5 | `odoo19_plan.md:74` | "`telco_expense` model ขาด `_description`" | **false positive** — เป็น `_inherit` ล้วน · ที่ขาดจริงคือ AbstractModel 2 ตัว | R1+R2 | ✅ **CONFIRMED** — `telco_expense/models/telco_expense.py:10` มีเพียง `_inherit = "hr.expense"` ไม่มี `_name` · `x_report_timesheet_perdiem_report_util.py:11` และ `telco_expense_qweb_by_date_report_util.py:15` มี `_name` แต่ **ไม่มี `_description`** |
| B6 | `odoo19_plan.md:109` G-8 | `product.uom`→`uom.uom` "ตั้งแต่ v14" | เกิดจริงที่ **v12** (คลาดเคลื่อน 2 เวอร์ชัน) | R2 (R1 ระบุว่าตรวจไม่ได้) | ✅ **CONFIRMED** — commit `2966d4f` = `[IMP] product: rename product.uom into uom.uom` · `addons/uom` → 12.0 HTTP **200**, 11.0 HTTP **404** · `11.0/addons/product/models/product_uom.py:16` ยังเป็น `_name = 'product.uom'` |
| B7 | `odoo19_plan.md:141` | OCA `hr-expense` "19.0 ยังรอ migration" | **branch 19.0 มีอยู่แล้ว** | R1+R2 | ✅ **CONFIRMED** — branches: 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, **19.0** |
| B8 | `odoo19_plan.md:140` | OCA l10n-thailand มี `l10n_th_withholding_tax` + `l10n_th_withholding_tax_report` รุ่น 19 | branch 19.0 มี **4 module** และ **ไม่มี** ทั้งสองตัวที่แผนอ้าง | R1+R2 (ชื่อโมดูลมาจาก R1) | ✅ **CONFIRMED** — 19.0 มีเพียง `l10n_th_account_tax`, `l10n_th_amount_to_text`, `l10n_th_base_sequence`, `l10n_th_base_utils` — **ตรงกับที่ R1 ระบุเป๊ะทั้ง 4 ชื่อ** |

> **ผลกระทบต่อเนื่องของ B3+B4:** E-1 คือฐานข้อมูลที่เจ้าของจะใช้ตัดสิน state mapping — R1 (C-8) เตือนว่า **ต้อง apply B3/B4 ให้เสร็จก่อนถามคำถาม E-4** มิฉะนั้นเจ้าของจะตัดสินบนข้อมูลผิด

---

### C. CONFLICT — R1 vs R2 ขัดกัน → **ตัดสินด้วยคำสั่งตรวจแล้วทั้ง 3 ข้อ**

| # | ตำแหน่ง | ฝั่ง R1 | ฝั่ง R2 | ผลตัดสิน `[V]` |
|---|---|---|---|---|
| C1 | `odoo19_plan.md:122` E-4 | **ผิด** — `default_code` มีทั้งสอง model · ตัวที่พังจริงคือ **`reference`** ซึ่งไม่มีบน `hr.expense` ใน 19 | **ถูกต้องแล้ว** — ระบุ E-4 ในรายการ "verify แล้วถูกต้อง" | 🟢 **R1 ถูก** — `hr_expense.py` (19.0) **ไม่มี field `reference`** (hit เดียวคือ `'references': msg_dict.get('message_id')` ที่ `:961` ซึ่งเป็น mail header คนละเรื่อง) · `default_code` มีทั้ง `product_product.py:31` และ `product_template.py:130` → **E-4 ต้องแก้: ลบคำกล่าวอ้างเรื่อง `default_code` และใส่ `reference` แทน** (ใช้ที่ `telco_expense_qweb_by_date_report_util.py:98` และ `order="... reference asc"` ที่ `:92-94`) |
| C2 | `odoo19_plan.md:104` G-3 | **ประเมินเบาไป** — addon `decimal_precision` ไม่มีทั้ง addon → **ImportError** ไม่ใช่แค่ helper เปลี่ยนชื่อ | **ถูกต้องแล้ว** — ระบุ G-3 ในรายการ "verify แล้วถูกต้อง" | 🟢 **R1 ถูก** — `ls addons/decimal_precision` → No such file ทั้งใน **odoo14 และ odoo16** → `import odoo.addons.decimal_precision as dp` (`x_withholding_tax_document.py:6`) เป็น **install blocker ไม่ใช่งาน cosmetic** |
| C3 | `dev-playbook/` มีอยู่จริงหรือไม่ | **ไม่มี** — ตรวจแล้วไม่พบทั้งใน repo และ parent dir → สรุปว่าเกณฑ์ playbook "ข้อมูลไม่พอที่จะตัดสิน" | **มีอยู่จริง** ที่ `/home/kitcharoenp/respo/dev-playbook/` และรัน `plan_scope.sh` ได้จริง | 🔵 **R2 ถูก** — `BASE_PLAYBOOK.md` (139,401 bytes, 2026-09-21) และ `scripts/plan_scope.sh` (32,823 bytes) **มีอยู่จริง** · และ **`find ~ -maxdepth 4 -iname "BASE_PLAYBOOK.md"` ซึ่งเป็นคำสั่งที่ R1 เสนอเอง กลับเจอไฟล์** → R1 น่าจะไม่ได้รันคำสั่งที่ตัวเองแนบมา<br>**ผลต่อเนื่อง:** หลักฐานรันจริงทั้งชุดของ R2 (D-2) **ใช้ได้** · ข้อสรุป D-1 ของ R1 ("ข้อมูลไม่พอที่จะตัดสิน" เรื่อง playbook) **ตกไป** · แต่ **A4 ยังยืน** — path สัมพัทธ์ที่ prompt สั่งอ่านผิดจริง |

---

### D. UNVERIFIED → **กลุ่ม H-1 ยืนยันครบแล้ว 14/14** (เจ้าของสั่งรัน 2026-09-22) · ที่เหลือดูหมวด H

> ✅ = ยืนยันด้วยคำสั่งจริงแล้ว (log อยู่ใน G-7) · ⬜ = ยังไม่ตรวจตามคำสั่งเจ้าของ
> **ไม่พบข้อใดที่ reviewer กล่าวอ้างเกินจริง** — มี 1 ข้อที่ระบุ location เกินมา (D4) และ 4 ข้อที่ **ความรุนแรงมากกว่า**ที่รายงานไว้

#### D-I · install blocker / runtime crash (R1 เดี่ยว)

| # | ตำแหน่ง | ข้อเสนอ | มาจาก | ผลตรวจ |
|---|---|---|---|---|
| D1 | `x_account_withholding_tax_document/__manifest__.py:12`, `x_report_timesheet_perdiem/__manifest__.py:10` | `'depends': [..., 'report']` — addon `report` ไม่มีใน 14/16/19 → AC-4 ตายตั้งแต่ resolve dependency · G-2 พูดถึงแต่ *model* `report` ไม่เคยพูดถึง manifest | R1 | ✅ **CONFIRMED** — WHT: `['hr_expense', 'purchase', 'report']` · perdiem: `['x_hr_timesheet_sheet', 'report']` · `addons/report` ไม่มีทั้ง odoo14 และ odoo16 |
| D2 | `__init__.py` ทั้ง 4 module (R1 ระบุ 10 ไฟล์) | implicit relative import แบบ Python 2 — prompt D-3 (`:35`) ตกข้อนี้ ทั้งที่ R1 เรียกว่าเป็น breakage อันดับ 1 ของ 10→11 · **AC-1 จับไม่ได้** | R1 | ✅ **CONFIRMED — ครบทั้ง 10 ไฟล์ตรงตามที่ R1 ระบุ** · ทุกไฟล์ใช้ `import models` / `import report` / `import <module>` แบบไม่มีจุดนำหน้า |
| D3 | 4 ไฟล์ act_window xml | `<field name="view_type">form</field>` ถูกถอดจาก `ir.actions.act_window` — ไม่อยู่ใน G-1..G-13 และไม่อยู่ใน pattern AC-2 | R1 | ✅ **CONFIRMED — 4 จุดตรงเป๊ะ** (`x_report_timesheet_perdiem_act_window.xml:6`, `x_withholding_tax_product_act_window.xml:7`, `telco_expense_qweb_by_date_act_window.xml:6`, `x_withholding_tax_document_act_window.xml:7`) |
| D4 | `x_withholding_tax_document_act_window.xml:8`, `x_withholding_tax_product_act_window.xml:8,23`, ~~`x_withholding_tax_product_form_view.xml:64`~~ | `view_mode` ที่มีคำว่า `tree` — G-12 ครอบแค่ **tag** `<tree>` ไม่ครอบ view_mode string | R1 | ⚠️ **CONFIRMED 3/4** — `:8` = `tree,form` · `:8` = `kanban,tree,form` · `:23` = `tree` ✓ แต่ **`x_withholding_tax_product_form_view.xml:64` เป็น `form` ไม่ใช่ `tree`** (อยู่ใน `ir.actions.act_window.view`) → R1 ระบุ location เกินมา 1 จุด |
| D5 | `x_withholding_tax_document_groups.xml:6,14,17` | `res.groups` เปลี่ยน schema ใน 19: `category_id` ไม่มีแล้ว (ย้ายไป `res.groups.privilege`), `users` → `user_ids` · R1 เสริมว่า `ir.rule.groups` **ยังชื่อเดิม** → `ir_rule.xml` ปลอดภัย | R1 | ✅ **CONFIRMED** — `:6` และ `:14` = `<field name="category_id" ref="base.module_category_hidden"/>` · `:17` = `<field name="users" eval="[(4, ref('base.user_root'))]"/>` |
| D6 | `telco_expense/views/telco_expense_sheet_form_view.xml:6,8` | `hr.expense.sheet` หายไปใน 19 → **ทั้งไฟล์ไม่มีเป้าให้ inherit** · Step 2 (`prompt:57-60`) สั่งแค่ "E-1..E-3 + G-1,G-7,G-11" → agent จะเจอ dead end กลางทาง | R1 | ✅ **CONFIRMED ทั้งสองปลาย** — `:6` `<field name="model">hr.expense.sheet</field>` · `:8` `ref="hr_expense.view_hr_expense_sheet_form"` (ทั้ง model และ view เป้าหายไปพร้อมกันใน 19 — ดู B3) |
| D7 | view: `telco_expense_form_view.xml:31`, `telco_expense_tree_view.xml:11`, `telco_expense_sheet_form_view.xml:11`, `hr_expense_form_view.xml:9,12` · model: `telco_expense.py:74` | xpath ยิงใส่ `analytic_account_id` — field ไม่มีใน 19 → view load error · E-2 พูดถึงแต่ onchange | R1 | ✅ **CONFIRMED + แก้จำนวน** — view มี **5 จุด ไม่ใช่ 4** (`hr_expense_form_view.xml` มีทั้ง `:9` และ `:12`) · **ในโค้ด model มีเพียง `:74` จุดเดียวที่ยังมีชีวิต** — `:45` และ `:58` อยู่ใน dead docstring (ดู D29) → อย่าเสียเวลาแก้สองจุดนั้น |
| D8 | `x_report_timesheet_perdiem_report_util.py:155` (อ่านกลับที่ `:196-197`) | `self.sum = round(_sum, 0)` บน recordset — `BaseModel.__slots__` ไม่มี `sum` → `AttributeError` · **report render พัง 100% และไม่มี AC ใดจับได้** | R1 | ✅ **CONFIRMED** — `:155` `self.sum = round(_sum, 0)` · อ่านกลับที่ `:196` `'sum': self.sum` และ `:197` `self._compute_amount_in_letter(self.sum)` |
| D9 | `x_report_timesheet_perdiem_report_util.py:173,176,180,182,183,184,195` | `hr.employee` drift: `work_location` ถูกถอด (16 = `work_location_id`, 19 = `work_location_name`); `bank_account_id` → `bank_account_ids` (M2m); `barcode` มี `groups="hr.group_hr_user"` → **ค่าว่างเงียบ**สำหรับ non-HR | R1 | ✅ **CONFIRMED ครบทุกบรรทัด** — `:173` `order="work_location asc, barcode asc"` ← **อยู่ใน `order=` จึงพังตอน search ไม่ใช่แค่อ่านค่าว่าง** · `:182` `emp.work_location` · `:183,184` `emp.bank_account_id.acc_number` / `.bank_name` · `:176,180,195` `emp.barcode` |
| D10 | `x_withholding_tax_document.py:83` | `domain="[('supplier','=',True)]"` — `res.partner.supplier` ถูกแทนด้วย `supplier_rank` | R1 | ✅ **CONFIRMED + พบเพิ่ม** — `:83` ตรงตามระบุ · **และ `x_withholding_tax_document_menu_view.xml:32` อ้าง `action="base.action_partner_supplier_form"`** ซึ่งเป็น action ยุคเดียวกับ `supplier` — ไม่มีใครรายงาน ควรตรวจว่ายังมีใน 19 |
| D11 | `telco_expense_qweb/models/telco_expense_qweb_by_date.py:106` | `datas_fname` ถูกถอดจาก `ir.attachment` → `export_excel` raise · prompt Step 3 (`:63`) เขียนลอย ๆ ว่า "base64/datas ให้ตรง API 19" ไม่เคยระบุ key นี้ | R1 | ✅ **CONFIRMED** — `:105` `'datas': base64.b64encode(xlsx_data)` (key นี้ยังใช้ได้) · `:106` `'datas_fname': 'Expense_by_date.xlsx'` (key ที่ถูกถอด) |
| D12 | `x_withholding_tax_document.py:141-142`, `product_template.py:14-15` | `@api.model def create(self, vals)` ควรเป็น `@api.model_create_multi` — **R1 ระบุเองว่า "ต้องตรวจซ้ำ"** ว่า 19 raise หรือแค่ warn | R1 (ยังไม่ conclusive) | ⬜ อยู่ใน H-2 (ต้องเทียบ 19.0 source) |
| D13 | `x_withholding_tax_document_form_view.xml:107-110` | `<div class="oe_chatter">` แบบเก่า — Odoo ใหม่ใช้ `<chatter/>` · **R1 ระบุเองว่า "ต้องตรวจซ้ำ"** | R1 (ยังไม่ conclusive) | ⬜ อยู่ใน H-2 |
| D14 | `x_account_withholding_tax_document/__manifest__.py:42` | `auto-install` ของ WHT มีค่า **`True`** — แก้สะกดตาม G-13 แล้ว module จะ **auto-install จริง** = เปลี่ยนพฤติกรรม ขัด behavior-preserving | R1 | ✅ **CONFIRMED + ยืนยันขอบเขต** — WHT `:42` `'auto-install': True` (typo, ค่า True) · perdiem `:24` `'auto-install': False` (typo แต่ไม่มีผล) · **`telco_expense:28` และ `telco_expense_qweb:30` สะกด `auto_install` ถูกอยู่แล้ว** → G-13 กระทบแค่ 2 module และมีเพียง WHT ที่เปลี่ยนพฤติกรรม |
| D15 | `x_report_timesheet_perdiem_report_util.py:181` + `templates/x_report_ts_perdiem_template.xml:119,120,138,140` | R-1 ตกไป 1 field: `x_signature_img` — R-1 (`plan:80`) ลิสต์เฉพาะ field บน `account.analytic.line` | R1 | ✅ **CONFIRMED + ขยายผล** — ไม่ใช่ 1 จุดแต่ **5 จุด**: `:181` `emp.x_signature_img` ใน report util **และอีก 4 จุดใน QWeb template** (`:119,120` manager, `:138,140` manager.parent) → ถ้า field หาย รูปลายเซ็นหายทั้งใบ ไม่ใช่แค่ค่าว่าง 1 ช่อง |

#### D-II · ช่องโหว่ของ AC / gate

| # | ตำแหน่ง | ข้อเสนอ | มาจาก | ทำไมอีกตัวอาจไม่พูดถึง |
|---|---|---|---|---|
| D16 | ทั้ง 3 โมดูลรายงาน: `x_withholding_tax_document_report.xml:20-27`, `telco_expense_qweb_by_date_report.xml:16-25`, `x_report_timesheet_perdiem_report.xml:16-24` | **`<report id=... />` shorthand tag** — `convert.py` ของ 19.0 ไม่มี handler → dispatcher `_tag_root` ทำ `if f is None: continue` = **เพิกเฉยเงียบ ไม่ error** → `ir.actions.report` ไม่ถูกสร้างเลย แต่ AC-4 จะผ่าน · ไม่อยู่ใน G-1..G-13 เลยสักข้อ · ต้องแปลงเป็น `<record model="ir.actions.report">` | R2 | R1 วิเคราะห์ report ที่ระดับ Python API (G-2) ไม่ได้ไล่ XML declaration · **R2 ระบุเองว่ายืนยันจาก source ของ `convert.py` เท่านั้น ยังไม่ได้รัน `-i` จริง** |
| D17 | `odoo19_plan.md:62-63` AC-3 | **ตรรกะ exit code กลับด้าน** — `grep -L` ให้ exit 0 เมื่อ *มี* ไฟล์ที่ขาด `_description` → รันวันนี้ได้ "ผ่าน" แต่พอแก้ครบจะ "ตก" | R1 | R2 ตรวจ AC-3 ที่ระดับ "ชี้ไฟล์ถูกหรือผิด" (ดู B5) ไม่ได้ตรวจ exit-code semantics |
| D18 | `odoo19_plan.md:56-57` AC-1 | **AC-1 เป็น gate เปล่า** — ผ่านทั้งก่อนและหลังพอร์ต จึงไม่ให้ข้อมูล | R1 | R2 รัน AC-1 ได้ exit 0 เหมือนกันแต่บันทึกเป็น `ok` โดยไม่ตีความว่าเป็นปัญหาของ gate |
| D19 | `odoo19_plan.md:21` Objective ข้อ 4 | "record rules + group manager ยังบังคับ approve/edit เท่าเดิม" **ไม่มี AC รองรับเลย** | R1 | R2 ไม่ได้ cross-check Objective กับตาราง AC |
| D20 | `odoo19_agent_prompt.md:55` | ไม่มี AC ระดับชุดสำหรับ XML/view-arch validity (parse ผ่าน ≠ Odoo validate view ผ่าน) → blocker ประเภท D3–D7 ไม่มีอะไรจับก่อนถึง AC-4 | R1 | R2 raise ปัญหาคนละชั้น (D16) แต่ชี้ไปทางเดียวกัน |
| D21 | `odoo19_plan.md:149-157` ตารางสรุป AC | ตารางสรุปขัดกับ yaml: AC-3 ในตารางเขียน "output ว่าง" แต่ yaml เขียน `expect_exit: 0` — แผนประกาศเองว่า yaml คือแหล่งความจริงเดียว | R1 | R2 ตรวจด้วย `--lint` (ระดับ syntax) ซึ่งไม่จับความขัดกันระหว่าง prose กับ yaml |
| D22 | `odoo19_plan.md:41` `deny_write` vs AC-1 | AC-1 เขียน `__pycache__/*.pyc` ลงโฟลเดอร์ที่ `deny_write` ห้ามไว้ (R1 เจอเองตอนรันทดสอบ — 22 ไฟล์) · เสนอ `PYTHONDONTWRITEBYTECODE=1` หรือ `compileall` + `sys.pycache_prefix` | R1 | R2 รัน AC ผ่าน script ของ playbook จึงอาจไม่สังเกตผลข้างเคียงนี้ |
| D23 | `odoo19_plan.md:44-45` `deny_write` | `../telco_hr_employee/**` และ `../x_hr_timesheet_sheet/**` ใช้ `../` ทั้งที่เป็น **โฟลเดอร์พี่น้องใน repo เดียวกัน** → pattern ชี้ออกนอก repo = **ไม่ได้กันอะไรเลย** | R1 | ✅ **CONFIRMED (โบนัสจาก H-1)** — `ls ../x_hr_timesheet_sheet` → No such file แต่ `ls x_hr_timesheet_sheet` → มีอยู่ · `git ls-files` ยืนยันว่า `telco_hr_employee/` และ `x_hr_timesheet_sheet/` **tracked ใน repo เดียวกัน** (repo root = cwd) → **guard ไม่ได้กันสองโฟลเดอร์นี้เลยแม้แต่น้อย** ซึ่งเป็นสิ่งที่ R-1 ประกาศว่าห้ามแตะเด็ดขาด |

#### D-III · ประเด็นอื่นที่มี reviewer เดียว raise

| # | ตำแหน่ง | ข้อเสนอ | มาจาก | ทำไมอีกตัวอาจไม่พูดถึง |
|---|---|---|---|---|
| D24 | `odoo19_plan.md:110` G-9 | "namespace `report.`→`web.`" สื่อว่าแค่ rename แต่ **`external_layout_header`/`footer` ไม่มีอยู่แล้วทั้งคู่** ไม่มี `web.` ตัวเทียบ — layout ใหม่กระจายเป็น `external_layout_standard/boxed/bold/striped` → **ต้อง rewrite ไม่ใช่ rename** (ใช้ที่ `x_report_ts_perdiem_template.xml:5,8,13,78`, `telco_expense_qweb_by_date_template.xml:5,8,13,141`) · R1 เน้นว่างานใหญ่กว่าที่ G-9/G-10 ประเมิน และ R-3 ระบุเองว่า "view-only ไม่ใช่ AC" = ไม่มี gate | R1 | R2 ตรวจ G-9 เฉพาะประเด็น `t-raw` (ดู B2) |
| D25 | `odoo19_plan.md:121` E-3 | "`accounting_date` (override field ที่มีอยู่)" — Odoo 19 `hr.expense` **ไม่มี** field นี้ · Odoo 16 มีแต่เป็น `related='sheet_id.accounting_date'` + `groups='account.group_account_invoice,...'` → **ไม่ใช่ override ทั้งสองปลาย** | R1 | ✅ **ยืนยันแล้ว `[V]`** — `grep -n "accounting_date" hr_expense.py` (19.0) → exit 1 (ไม่พบเลย) · R2 ไม่ได้ตรวจ E-3 |
| D26 | `odoo19_plan.md:104` G-4 | "`track_visibility` ถอดออก v11" — rename เป็น `tracking=True` เกิดที่ **v13** และ kwarg เก่ายังใช้ได้แบบ compat จนถูกลบจริงใน **v19 เอง** (commit `e6c4fa5`) | R2 | R1 ไม่ได้ตรวจ G-4 · **ทิศทางการแก้ไม่เปลี่ยน** เปลี่ยนแค่เลขเวอร์ชันในคำอธิบาย |
| D27 | prose ใต้ตาราง E (WHT) `odoo19_plan.md:127` | "ตรวจว่า `self.env.user.has_group(...)` แทน `user_has_groups` (deprecated)" — R2 ไม่พบหลักฐาน deprecation และระบุว่าโค้ดที่มีอยู่ (`x_withholding_tax_document.py:193,199,211,217`) **ใช้ถูกต้องอยู่แล้ว** | R2 (ระบุเองว่า "ยืนยันปานกลาง") | R1 ตรวจแล้วเช่นกันแต่สรุปว่า "ยืนยันได้แค่ว่ายังมีใน 14/16 → ต้องตรวจซ้ำ" → **ทั้งคู่ไม่มีใคร confirm สถานะใน 19** |
| D28 | `telco_expense/models/telco_expense.py:12-25` | G-11 ไม่ครบ — มี **Python field-kwarg `states={...}`** บน `accounting_date`/`payment_mode` ซึ่งเป็นคนละกลไกกับ view attribute และไม่ถูกระบุใน G-11 | R2 | ✅ **CONFIRMED + ได้ข้อมูลที่ E-4 ต้องใช้** — `accounting_date` มี `states={'reported': ..., 'done': ...}` · `payment_mode` มี `states={'done': ..., 'post': ...}` → **ค่า state ของ Odoo 10 ที่ต้อง map คือ `reported`, `done`, `post`** ซึ่งไม่มีสักตัวใน 7 ค่าของ 19 · R1 ยืนยันข้อเท็จจริงว่า field kwarg `states` ถูกถอดใน v17 ด้วย (A-1) → **สองรีวิวเสริมกันพอดี** |
| D29 | `telco_expense/models/telco_expense.py:40-68` | `@api.multi def submit_expenses(...)` ทั้งฟังก์ชันอยู่ในบล็อก docstring = **dead code** → grep ของ AC-2 จะเจอ `@api.multi` ตรงนี้ตลอดไปแม้ลบ deprecated API จริงหมดแล้ว · G-1 ไม่ได้ระบุ `telco_expense` เป็น location ของ `@api.multi` | R2 | ✅ **CONFIRMED + พบปัญหาที่ไม่มีใครรายงาน** — docstring กินบรรทัด **40–68** จากไฟล์ที่มี 74 บรรทัด (≈39% ของไฟล์) · **และโค้ดข้างในมี SyntaxError อยู่แล้ว**: `:63` เขียน `if(...)` **ไม่มี `:` ปิดท้าย** → ถ้าใคร uncomment ระหว่าง port จะพังทันที ไม่ใช่ dead code ที่ "กู้คืนได้" · ผลพลอยได้: `analytic_account_id` ที่ `:45`/`:58` ก็อยู่ในบล็อกนี้ (ดู D7) |
| D30 | `x_account_withholding_tax_document/models/product_template.py:16-18` | dead branch — `vals.update` อยู่ **หลัง** `super().create` ทำให้ `supplier_taxes_id: False` ไม่เคยถูกใช้ · behavior-preserving แปลว่าต้อง**คง bug นี้ไว้** | R1 | R2 ไม่ได้อ่านไฟล์นี้ระดับ logic |

---

### E. คำถามที่ต้องส่งต่อให้เจ้าของ

> **ปิดแล้ว 3 ข้อ:** ข้อ dev-playbook อยู่ไหน (ตัดสินด้วย C3) · **E-1** และ **E-2** (เจ้าของตอบ 2026-09-22)

1. ~~**มี Odoo 19 instance + Odoo 10 instance หรือไม่?**~~ → ✅ **ตอบแล้ว: มีทั้งสอง**
   **ผลต่อแผน:** AC-4 และ AC-5 วัดได้จริง → **ไม่ต้องใช้ทางเลือกสำรองของ R1** (golden test เฉพาะ pure function / PDF เก่า / ลด Objective ข้อ 3) · gate Step 0 "ห้ามแก้โค้ดก่อนมี baseline" ทำได้ตามที่เขียน
   **สิ่งที่ยังต้องทำ:** เติมค่า `<db19>` จริงลงใน AC-4 (ดู E-3) และเพิ่มแถว "Odoo 10 instance" เข้าตาราง "สิ่งที่ต้องขอจากเจ้าของ" ตาม **A3** เพื่อให้ agent รู้ว่ามีให้ใช้
   **ข้อเสนอเสริมที่ยังคุ้ม:** golden test ของ `_thai_unit_process`/`_thai_num2text`/`_compute_amount_in_letter` (R1 G-4 ข้อ 1) ยังควรทำ **เพิ่มเติม** ไม่ใช่แทน — เพราะเป็น pure function ที่ทดสอบเคสขอบ (`0`, `1`, `11`, `21`, `101`, `1000000`, `.05`, `.50`) ได้ถูกกว่าการ render PDF ทีละใบ

2. ~~**adopt dev-playbook จริงหรือใช้เป็นเอกสารอ้างอิง?**~~ → ✅ **ตอบแล้ว: adopt จริง**
   **ผลต่อแผน — ข้อนี้ทำให้ E-3 กลายเป็นงานบังคับ ไม่ใช่ทางเลือก:** เมื่อ guard ถูกบังคับจริง AC ที่ถูก deny (ยืนยันแล้ว 4/5 ใน G-6) จะ**รันไม่ได้จริง** ไม่ใช่แค่ผิดไวยากรณ์บนกระดาษ
   **สิ่งที่ต้อง set up (ยังไม่มีใน repo นี้):** `.claude/settings.json`, `docs/playbook/PLAYBOOK.md` หรือ `AGENTS.md` ที่ชี้ไป `/home/kitcharoenp/respo/dev-playbook/` · และแก้ path อ้างอิงใน `odoo19_agent_prompt.md:26` + `odoo19_plan.md:8` ให้เป็น absolute ตาม **A4** — ไม่งั้นกฎเหล็กข้อ 3 (`prompt:18`) จะยิงตั้งแต่ก่อน Step 0
   **หมายเหตุ:** `deny_write` ของแผนปัจจุบันห้ามเขียน `.claude/settings.json` และ `.claude/skills/**` อยู่ — การ adopt จึงต้องทำ**นอกรอบ port นี้** หรือแก้ `deny_write` พร้อมประกาศเหตุผล

3. **ต้องแก้ `allow_bash` + เติมค่า `<db19>` จริงก่อนปล่อย agent** — เหลือแค่ยืนยันรายการที่จะเพิ่ม
   *มาจาก R1+R2 (ดู A2 · ยืนยันด้วยการรัน guard จริงแล้วว่า deny 4/5 คำสั่ง)* — **คำตอบ E-2 ทำให้ข้อนี้บังคับ** · รายการที่ผลตรวจชี้ว่าต้องแก้: (ก) entry `grep -rn * x_report...` ใช้ไม่ได้เลยเพราะ `*` อยู่กลางสตริง (ข) ไม่มี entry สำหรับ `odoo` (ค) `python3 -m py_compile *` ไม่ครอบกรณี `$(find ...)` ที่ AC-1 ใช้ (ง) ไม่มี entry สำหรับ `python3 -c` ที่ Step 1 ต้องใช้ (จ) `<db19>` ดิบชน redirection-block ของ guard

4. **`hr.expense` state mapping:** `done`/`post` ของ Odoo 10 → ค่าไหนใน **7 ค่า** ของ 19 (`posted` / `in_payment` / `paid`)? และ report ควรนับสถานะใดเป็น "Posted"?
   *มาจาก R1+R2* — R1 ระบุว่า `telco_expense_qweb_by_date.py:60-64` และ filter ที่ `..._report_util.py:85` ใช้ `draft/reported/done/refused` · **ต้อง apply B3+B4 ก่อนถามข้อนี้** · R2 เสริมว่าพื้นที่นี้ของ core **ไม่นิ่งในเวอร์ชันเป้าหมายเอง** และ OCA กำลังทำ `hr_expense_sheet` แยกกลับมาสำหรับ 19.0 → ควรยกระดับ owner-decision gate ใน Step 2 ไหม?

5. **`accounting_date`:** คงเป็น custom field บน `hr.expense` ต่อ หรืออิง `account.move.date`?
   *มาจาก R1 (D25 — ยืนยันแล้วว่า field ไม่มีใน 19)* — R1 เตือนว่าถ้าไปพิงของ core ที่มี `groups='account.group_account_*'` report จะ**คืนค่าว่างเงียบ**สำหรับผู้ใช้ที่ไม่ใช่ accounting (เช่นเดียวกับ `barcode` ใน D9)

6. **`analytic_distribution`:** แปลง `employee.x_analytic_account_id` (บัญชีเดียว) → distribution dict ด้วยนโยบายอะไร (100% ไปบัญชีเดียว?)
   *มาจาก R1 (D7 — ยืนยันแล้วว่า 19 มีแต่ `analytic_distribution`)*

7. **Scope:** ขยายเป็น 6 module (+`telco_hr_employee`, `x_hr_timesheet_sheet`) หรือยอมรับ partial port?
   *มาจาก R1+R2 (ดู A5)* — ทางเลือกที่ R1 เสนอ: (ก) ขยาย scope เป็น 6 module · (ข) partial port โดยเอา WHT ก่อน · (ค) ลด field ที่อ้าง
   *ข้อเสนอเสริมของ R1 (G-1):* แยกเป็น 2 รอบ — **รอบ A "install sweep"** (blocker เชิงกลไกล้วน ไม่ต้องรอ owner decision) แล้วค่อย **รอบ B "behavior parity"** · R1 ยังเสนอสลับลำดับเป็น **WHT → perdiem → telco_expense (รอ owner) → qweb**

8. **`mode: REFACTOR` ถูกต้องไหม?**
   *มาจาก R1+R2 (policy call)* — R1: runtime target เปลี่ยนและ `hr.expense` state/analytic **ต้อง** เปลี่ยนความหมาย · R2: ถ้า YAML ยัง `REFACTOR` tooling จะไม่ trigger gate ที่ prose เองยอมรับว่าเข้าเงื่อนไข
   *trade-off:* (ก) แก้ `mode:` ให้ตรง prose = ตรงความจริงแต่ gate หนักขึ้น · (ข) คง `REFACTOR` + เขียนเหตุผล 1 บรรทัดกำกับ

9. **SemVer "MINOR—กระทบ compliance" ถูกต้องไหม หรือควรเป็น MAJOR?**
   *มาจาก R1* — R1 ระบุเองว่า **ไม่มีข้อมูล release policy ให้ยึด** → ข้อมูลไม่พอที่จะตัดสินแทน

10. **Adopt OCA รอบนี้ไหม (ทบทวน D-1)?**
    *มาจาก R1+R2* — R1 ชี้เฉพาะเจาะจงว่า **`l10n_th_amount_to_text` อยู่บน 19.0 แล้ว** (ยืนยันแล้วใน B8) และแทนโค้ดแปลงเลขไทยที่ซ้ำ **3 จุด** ได้ (`x_withholding_tax_document.py:149-185`, `x_report_timesheet_perdiem_report_util.py:50-86`, `telco_expense_qweb_by_date_report_util.py:25-61`)
    *trade-off:* (ก) คงโค้ดซ้ำ = behavior-preserving แน่นอน · (ข) adopt = ลดหนี้เทคนิค แต่ต้อง diff ผล "เอ็ด/ยี่/สตางค์" ทีละเคส
    *หมายเหตุ:* คำแนะนำเดิม "ใช้ OCA เป็นฐานคำนวณ WT" **ทำไม่ได้** — ยืนยันแล้วว่า 19.0 ไม่มี `l10n_th_withholding_tax` (B8)

11. **`digits`:** ตรึง `(16,2)` ตามที่ G-3 แนะนำ หรือคงค่า configurable?
    *มาจาก R1* — tuple ตรึง precision = **เปลี่ยนพฤติกรรม** ขัด Objective · ตัวเทียบเท่าที่คงพฤติกรรมคือ string (`digits='Account'` ฯลฯ)

12. **`auto-install` → `auto_install` ของ WHT:** ต้องการให้ auto-install จริง หรือตั้งเป็น `False`?
    *มาจาก R1 (D14)* — ค่าปัจจุบันคือ `True` แต่ typo ทำให้ไม่มีผล การแก้สะกดอย่างเดียวจะเปลี่ยนพฤติกรรม

13. **typo `for_withhoding_tax_doc` + dead branch:** คง bug ไว้ หรือแก้พร้อมประกาศว่าเปลี่ยนพฤติกรรม?
    *มาจาก R1 (D30)*

14. **`<report>` tag → `<record model="ir.actions.report">`:** ให้เป็นงานเพิ่มใน Step 1/3/4 ไหม?
    *มาจาก R2 (D16)* — เป็นบั๊กที่ AC-4 จับไม่ได้เอง (เพิกเฉยเงียบ ไม่ error)

15. **citation "`README.md` หัวข้อปล่อยเวอร์ชันใหม่ ข้อ 1–3"** (`odoo19_plan.md:6`) ยอมรับตามรูปแบบ template หรือปรับให้แม่นยำขึ้น?
    *มาจาก R2* — R2 ระบุเองว่าเป็น **ความไม่ชัดเจนของ template ไม่ใช่ความผิดของผู้เขียนแผน**

---

### F. สรุป

| กลุ่ม | จำนวน | สถานะหลังตรวจ (2026-09-22) |
|---|---|---|
| A. CONSENSUS | 5 | **4 ยืนยันแล้ว** (A3 ปิดด้วยคำตอบ E-1) → apply ได้ |
| B. FACTUAL FIX | 8 | **8/8 CONFIRMED** → apply ได้ |
| C. CONFLICT | 3 | **ตัดสินครบ** → R1 ถูก 2 (C1, C2) · R2 ถูก 1 (C3) → apply ได้ |
| D. UNVERIFIED | 30 | **ยืนยันแล้ว 17** (H-1 ครบ 14 + D1/D25 จากรอบ A-C + D23 โบนัส) · **เหลือ 13** → ดูหมวด H |
| E. คำถาม | 15 | **ปิดแล้ว 2** (E-1, E-2) · เหลือ **13** รอเจ้าของ |

- **จำนวนข้อที่ apply ได้หลังตรวจ (A+B+C+D ที่ยืนยันแล้ว): 33** — จาก 13 ข้อในร่างแรก
- **จำนวนข้อที่ยังรอ: 26** (D ที่ยังไม่ตรวจ 13 + E 13)
- **อัตราความแม่นของ reviewer จากทุกข้อที่ตรวจได้:**
  - **R1** — ถูก **16/17** ข้อที่ตรวจ · พลาด 2 จุด: **C3** (สรุปว่า playbook ไม่มีอยู่ ทั้งที่คำสั่ง `find` ที่ตัวเองแนบมากลับเจอ) และ **D4** (ระบุ location เกินมา 1 จุด) · นอกจากนั้นตรงเป๊ะทุก `file:line` — และ **4 ข้อรุนแรงกว่าที่รายงาน** (D7, D9, D10, D15)
  - **R2** — ถูกทุกข้อที่ตรวจ ยกเว้น **C1/C2** (จัด E-4 และ G-3 เป็น "verify แล้วถูกต้อง" ทั้งที่ทั้งสองข้อมีปัญหาจริง) · จุดแข็งคือ commit-level evidence และการรัน guard จริง ซึ่ง R1 ทำไม่ได้
- **สัดส่วนที่ต้องสังเกต:** งานที่ยังเหลือกระจุกอยู่ในสองกลุ่มที่ต่างกันมาก — (ก) **H-2** 4 ข้อที่ต้องเทียบ 19.0 source (ข) **H-3** 7 ข้อที่เป็นข้อบกพร่องของเอกสารแผนเอง ไม่ต้องยืนยันกับอะไรเลย · **R1 กับ R2 ตรวจคนละชั้น** (R1 ไล่โค้ด/view/security/AC semantics · R2 ไล่ Odoo 19 source commit + รัน guard) ความเห็นตรงกันจึงเกิดเฉพาะจุดที่ชั้นการตรวจทับกัน ไม่ใช่เพราะอีกฝ่ายตรวจแล้วไม่เจอ

#### blind spot ที่ทั้งคู่น่าจะพลาดร่วมกัน

> ข้อสังเกตของ**ผู้รวมผล** ไม่ใช่ finding ของ R1/R2

1. **ไม่มีใครรัน Odoo 19 จริง** — ข้อสรุปเรื่อง install/runtime **ทั้งหมด** เป็น static analysis เทียบ source · บั๊กที่โผล่เฉพาะตอน runtime (ลำดับ loading, view validation order, ผลรวมของ blocker หลายตัวพร้อมกัน) ยังไม่มีใครแตะ
2. **AC-1 วัดคนละอย่างกับที่ Objective ข้อ 1 อ้าง** — Objective (`plan:18`) เขียนว่า "compile ผ่านภายใต้ **Python ที่ Odoo 19 ใช้**" แต่ AC-1 รัน `python3` ของเครื่องที่รันคำสั่ง · R1 ชี้ว่า AC-1 เป็น gate เปล่า (D18) แต่ไม่มีใครชี้ว่า interpreter ที่ใช้วัดอาจเป็นคนละตัวกับของ target
3. **ไม่มีใครยืนยันว่ารายการ field ที่พึ่ง module นอกแผนครบแล้ว** — R1 เจอ `x_signature_img` เพิ่มมา 1 ตัวที่ R-1 ตกไป (D15) แต่ไม่ได้อ้างว่าไล่ครบ · ถ้ามีวิธีตกหล่นแบบเดียวกันอีก จะโผล่กลาง Step 4 ไม่ใช่ตอนวางแผน

---

## G. Verification log — ผลรันจริงของผู้รวมผล

**ผู้รัน:** arbitrator (ชั้นที่ 3) · **วันที่:** 2026-09-22 · **ได้รับคำสั่งจากเจ้าของให้รันแทน**
**ขอบเขต:** read-only ทั้งหมด — ไม่มีคำสั่งใดเขียนไฟล์ · **ไม่ได้รัน AC-1/`py_compile`** จึงไม่มี `__pycache__` เกิดใหม่ (หลีกเลี่ยงปัญหา D22)

### G-1 · Local repo (cwd = `/home/kitcharoenp/respo/odoo/x_odoo_10_addons`)

```
$ grep -rn 't-raw' x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb
exit=1                                          → B2 CONFIRMED (ไม่มี t-raw)

$ grep -n "_inherit\|_name\|_description" telco_expense/models/telco_expense.py
10:    _inherit = "hr.expense"                   → B5 CONFIRMED (ไม่มี _name → ไม่ต้องมี _description)

$ grep -n "_name\|_description" <report utils>
x_report_timesheet_perdiem_report_util.py:11:    _name = 'report.x_report_timesheet_perdiem.x_report_ts_perdiem_template'
telco_expense_qweb_by_date_report_util.py:15:    _name = 'report.telco_expense_qweb.telco_expense_qweb_by_date_template'
                                                → ทั้งคู่มี _name แต่ไม่มี _description = B5 CONFIRMED

$ grep -n "depends" <manifests>
x_account_withholding_tax_document/__manifest__.py:10: 'depends': ['hr_expense','purchase','report']
x_report_timesheet_perdiem/__manifest__.py:10:         'depends': ['x_hr_timesheet_sheet', 'report']
                                                → A5 + D1 CONFIRMED

$ grep -rnE 'attrs=' telco_expense/views/       → exit=1 (ไม่เจอ)
$ grep -rn 'name="attrs"' telco_expense/views/
telco_expense_form_view.xml:28:  <attribute name="attrs">{'readonly': 1}</attribute>
telco_expense_form_view.xml:36:  <attribute name="attrs">{'readonly': 1}</attribute>
                                                → A1 CONFIRMED (AC-2 pattern จับไม่ได้จริง)

$ ls dev-playbook/BASE_PLAYBOOK.md              → No such file (exit=2)   → A4 CONFIRMED
```

### G-2 · Local Odoo source (odoo14 / odoo16)

```
$ ls ~/respo/odoo/odoo16/addons/decimal_precision   → No such file (exit=2)
$ ls ~/respo/odoo/odoo14/addons/decimal_precision   → No such file (exit=2)
                                                → C2 ตัดสิน: R1 ถูก (ImportError ไม่ใช่ helper rename)

$ ls -d ~/respo/odoo/odoo16/addons/report           → No such file (exit=2)
$ ls -d ~/respo/odoo/odoo14/addons/report           → No such file (exit=2)
                                                → D1 CONFIRMED (addon 'report' ไม่มีแล้ว)

$ grep -c "hr.expense.sheet" ~/respo/odoo/odoo16/addons/hr_expense/models/hr_expense.py
10                                              → B3 CONFIRMED (v16 ยังมี sheet)

$ grep -n "default_code = fields" ~/respo/odoo/odoo16/addons/product/models/product_{product,template}.py
product_product.py:31:  default_code = fields.Char('Internal Reference', index=True)
product_template.py:130: default_code = fields.Char(
                                                → C1 ตัดสิน: R1 ถูก (มีทั้งสอง model)

$ grep -c 'states="' ~/respo/odoo/odoo16/addons/sale/views/sale_order_views.xml   → 6
$ grep -n "states = None" ~/respo/odoo/odoo16/odoo/fields.py                      → 323
                                                → B1 CONFIRMED (v16 ยังใช้ได้)
```

### G-3 · Odoo 19.0 source (GitHub)

```
$ curl -s .../19.0/odoo/addons/base/models/ir_ui_view.py | grep -n 'Since 17.0'
495: err = ValidationError(_('Since 17.0, the "attrs" and "states" attributes are no longer used....
                                                → B1 CONFIRMED (ถอดใน v17 ไม่ใช่ v11)

$ curl -s .../19.0/addons/hr_expense/models/hr_expense.py   (89,043 bytes)
  :124-136  state = fields.Selection([draft, submitted, approved, posted,
                                      in_payment, paid, refused])       → B4 CONFIRMED (7 ค่า)
  grep "reference"        → hit เดียว :961 'references': msg_dict.get('message_id')  (mail header)
                                                → C1 ตัดสิน: field `reference` ไม่มีจริง → R1 ถูก
  grep "accounting_date"  → exit=1 (ไม่พบเลย)   → D25 CONFIRMED
  grep "sheet_id"         → :283 former_sheet_id = fields.Integer(string='Former Report')
                                                → B3/D6 CONFIRMED (ร่องรอย migration, ไม่มี sheet_id จริง)
  grep "analytic_*"       → มีแต่ analytic_distribution (:746,756,816,1499,1660,1732)
                                                → D7 CONFIRMED (ไม่มี analytic_account_id)

$ curl -s api.github.com/repos/odoo/odoo/contents/addons/hr_expense/models?ref=19.0
  → __init__.py, account_move.py, account_move_line.py, account_payment.py, account_tax.py,
    analytic.py, hr_department.py, hr_employee.py, hr_employee_public.py, hr_expense.py,
    ir_actions_report.py, ir_attachment.py, product_product.py, product_template.py,
    res_company.py, res_config_settings.py
  → ไม่มี hr_expense_sheet.py                   → B3 CONFIRMED
```

### G-4 · เวอร์ชันที่ `uom` ถูก rename (B6)

```
$ curl -s api.github.com/repos/odoo/odoo/commits/2966d4fa...
  "message": "[IMP] product: rename product.uom into uom.uom\n\nAlso rename product.uom.categ
              into uom.category to give it a decent name."
$ curl -o /dev/null -w "%{http_code}" api.github.com/.../contents/addons/uom?ref=12.0   → 200
$ curl -o /dev/null -w "%{http_code}" api.github.com/.../contents/addons/uom?ref=11.0   → 404
$ curl -s raw.../11.0/addons/product/models/product_uom.py | grep "_name = 'product.uom'"
16:    _name = 'product.uom'
                                                → B6 CONFIRMED: rename เกิดที่ v12 (แผนเขียน v14 = ผิด 2 เวอร์ชัน)
```

### G-5 · OCA (B7, B8)

```
$ curl -s api.github.com/repos/OCA/hr-expense/branches?per_page=100
  → 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0    → B7 CONFIRMED (branch 19.0 มีจริง)

$ curl -s api.github.com/repos/OCA/l10n-thailand/contents/?ref=19.0
  → l10n_th_account_tax, l10n_th_amount_to_text, l10n_th_base_sequence, l10n_th_base_utils
  → ไม่มี l10n_th_withholding_tax, ไม่มี l10n_th_withholding_tax_report
                                                → B8 CONFIRMED (ตรงกับชื่อที่ R1 ระบุครบทั้ง 4)
```

### G-6 · dev-playbook + guard (C3, A2)

```
$ ls -la /home/kitcharoenp/respo/dev-playbook/BASE_PLAYBOOK.md  /home/kitcharoenp/respo/dev-playbook/scripts/plan_scope.sh
-rw-rw-r-- 139401 Sep 21 07:20 .../BASE_PLAYBOOK.md
-rw-rw-r--  32823 Sep  6 01:51 .../scripts/plan_scope.sh
$ find ~ -maxdepth 4 -iname "BASE_PLAYBOOK.md"
/home/kitcharoenp/respo/dev-playbook/BASE_PLAYBOOK.md
                                → C3 ตัดสิน: R2 ถูก · คำสั่ง find ที่ R1 เสนอเองกลับเจอไฟล์

$ sh .../plan_scope.sh --lint docs/migration/odoo19_plan.md
note  path "x_report_timesheet_perdiem" ปรากฏนอกบล็อก plan-scope 3 จุด (กฎข้อ 6)
note  path "x_account_withholding_tax_document" ... 3 จุด
note  path "telco_expense" ... 10 จุด
note  path "telco_expense_qweb" ... 6 จุด
note  path "docs/migration" ... 1 จุด
ok    บล็อก plan-scope ของ docs/migration/odoo19_plan.md ผ่านทุกกฎ
                                → R2 ถูก (lint ผ่านจริง) + พบ note 5 ข้อที่ไม่มี reviewer คนไหนรายงาน

$ sh .../plan_scope.sh --check-cmd <plan> "<cmd>"
  "! grep -rnE '@api\.(multi|one)|track_visibility' <4 dirs>"
      → deny  segment "! grep -rnE '@api\.(multi" ไม่อยู่ใน allow_bash
  "odoo -d <db19> -i ... --stop-after-init --log-level=error"
      → deny  พบ redirection (> หรือ >>) ที่ไม่ใช่ fd-dup N>&M  ← '<db19>' ถูกอ่านเป็น redirection
  "grep -rLn '_description' $(find telco_expense -name '*.py' | xargs grep -lE 'models.Model')"
      → deny  segment "grep -rLn '_description'" ไม่อยู่ใน allow_bash
  "grep -rn '@api.multi' telco_expense"
      → deny  segment ... ไม่อยู่ใน allow_bash   ← entry `grep -rn * x_report...` ใช้ไม่ได้เลย ('*' กลางสตริง)
  "python3 -m py_compile telco_expense/models/telco_expense.py"
      → allow                                    ← allow เฉพาะเมื่อ argument เป็น path ตรง
  "python3 -m py_compile $(find telco_expense -name '*.py')"
      → deny  segment "python3 -m py_compile" ไม่อยู่ใน allow_bash  ← AC-1 ตามที่เขียนในแผนใช้รูปนี้
  "git status --porcelain"
      → allow                                    ← control: guard ทำงานปกติ ไม่ใช่ artifact ของการทดสอบ
                                → A2 CONFIRMED + ละเอียดกว่าที่ R1/R2 รายงาน
```

### G-7 · H-1 sweep — ยืนยันกลุ่ม D 14 ข้อ (เจ้าของสั่งรัน 2026-09-22)

```
D2  implicit relative import — อ่าน __init__.py ครบ 10 ไฟล์
    telco_expense/__init__.py:5                     import models
    telco_expense/models/__init__.py:5              import telco_expense
    telco_expense_qweb/__init__.py:5,6              import models / import report
    telco_expense_qweb/models/__init__.py:5         import telco_expense_qweb_by_date
    telco_expense_qweb/report/__init__.py:6         import telco_expense_qweb_by_date_report_util
    x_account_withholding_tax_document/__init__.py:2          import models
    x_account_withholding_tax_document/models/__init__.py:2,3 import x_withholding_tax_document / product_template
    x_report_timesheet_perdiem/__init__.py:2,3      import models / import report
    x_report_timesheet_perdiem/models/__init__.py:2 import x_report_timesheet_perdiem
    x_report_timesheet_perdiem/report/__init__.py:2 import x_report_timesheet_perdiem_report_util
                                        → CONFIRMED 10/10 ตรงตามที่ R1 ระบุ

D3  $ grep -rn 'view_type' <4 dirs>                                        → 4 hits, ตรงเป๊ะ
D4  $ grep -rn 'view_mode' <4 dirs>
    x_withholding_tax_document_act_window.xml:8      tree,form        ✓
    x_withholding_tax_product_act_window.xml:8       kanban,tree,form ✓
    x_withholding_tax_product_act_window.xml:23      tree             ✓
    x_withholding_tax_product_form_view.xml:64       form             ✗ ← ไม่มี 'tree' (R1 ระบุเกิน)

D5  $ grep -n ... security/x_withholding_tax_document_groups.xml
    :6, :14  <field name="category_id" ref="base.module_category_hidden"/>
    :17      <field name="users" eval="[(4, ref('base.user_root'))]"/>     → CONFIRMED

D6  telco_expense/views/telco_expense_sheet_form_view.xml
    :6  <field name="model">hr.expense.sheet</field>
    :8  ref="hr_expense.view_hr_expense_sheet_form"                        → CONFIRMED (เป้าหายทั้งคู่)

D7  $ grep -rn 'analytic_account_id' telco_expense telco_expense_qweb x_report_timesheet_perdiem
    views: telco_expense_sheet_form_view.xml:11 · telco_expense_tree_view.xml:11
           telco_expense_form_view.xml:31 · hr_expense_form_view.xml:9,12   ← 5 จุด (R1 บอก 4)
    model: telco_expense.py:45, :58  ← อยู่ใน docstring 40-68 = dead
           telco_expense.py:74       ← โค้ดจริงจุดเดียว

D8  x_report_timesheet_perdiem_report_util.py
    :155  self.sum = round(_sum, 0)
    :196  'sum': self.sum          :197  self._compute_amount_in_letter(self.sum)   → CONFIRMED

D9  x_report_timesheet_perdiem_report_util.py
    :173  order="work_location asc, barcode asc"   ← อยู่ใน order= จึงพังตอน search
    :182  emp.work_location    :183 emp.bank_account_id.acc_number
    :184  emp.bank_account_id.bank_name            :176,180,195 emp.barcode     → CONFIRMED

D10 x_withholding_tax_document.py:83  domain="[('supplier','=',True)]"           → CONFIRMED
    + พบเพิ่ม: x_withholding_tax_document_menu_view.xml:32
               action="base.action_partner_supplier_form"   ← ไม่มีใครรายงาน

D11 telco_expense_qweb_by_date.py:105 'datas': base64.b64encode(xlsx_data)   (ok)
                                 :106 'datas_fname': 'Expense_by_date.xlsx'  (ถูกถอด)  → CONFIRMED

D14 $ grep -n 'auto.install' <4 manifests>
    x_account_withholding_tax_document/__manifest__.py:42   'auto-install': True    ← typo + True
    x_report_timesheet_perdiem/__manifest__.py:24           'auto-install': False   ← typo, ไม่มีผล
    telco_expense/__manifest__.py:28                        'auto_install': False   ← สะกดถูกแล้ว
    telco_expense_qweb/__manifest__.py:30                   'auto_install': False   ← สะกดถูกแล้ว
                                        → CONFIRMED · G-13 กระทบ 2 module, เปลี่ยนพฤติกรรมเฉพาะ WHT

D15 $ grep -rn 'x_signature_img' x_report_timesheet_perdiem
    report/x_report_timesheet_perdiem_report_util.py:181   emp.x_signature_img
    report/templates/x_report_ts_perdiem_template.xml:119,120   manager_id
    report/templates/x_report_ts_perdiem_template.xml:138,140   manager_id.parent_id
                                        → CONFIRMED · 5 จุด ไม่ใช่ 1

D28 telco_expense/models/telco_expense.py
    accounting_date  states={'reported': [...], 'done': [...]}
    payment_mode     states={'done': [...], 'post': [...]}
                                        → CONFIRMED · ค่า state ของ v10 ที่ต้อง map = reported/done/post

D29 $ grep -n '"""' telco_expense/models/telco_expense.py    → 40, 68  (ไฟล์มี 74 บรรทัด)
    :63  if(crossovered_budget_line.planned_amount > 0 and ... < 0)   ← ไม่มี ':' ปิดท้าย
                                        → CONFIRMED + โค้ดใน docstring มี SyntaxError อยู่แล้ว

D23 (โบนัส) $ ls ../x_hr_timesheet_sheet   → No such file
            $ ls x_hr_timesheet_sheet      → มีอยู่
            $ git ls-files -- telco_hr_employee   → telco_hr_employee/__init__.py ...
            repo root = /home/kitcharoenp/respo/odoo/x_odoo_10_addons
                                        → CONFIRMED · deny_write '../' ไม่กันอะไรเลย
```

**สรุป G:** ตรวจ 8/8 ของกลุ่ม B · 4/5 ของกลุ่ม A (A3 ปิดด้วยคำตอบ E-1) · 3/3 ของกลุ่ม C · และ **17/30 ของกลุ่ม D** (H-1 ครบ 14 + D1/D25 + D23) — **ไม่พบข้อใดที่ผลตรวจขัดกับสิ่งที่จัดไว้ในตาราง A/B/C**

**ของใหม่ที่ไม่มีรีวิวใดรายงาน (พบระหว่าง H-1):**
1. **SyntaxError ใน dead docstring** — `telco_expense.py:63` เขียน `if(...)` ไม่มี `:` → โค้ดบล็อกนั้นไม่ใช่ "ของที่กู้คืนได้" ถ้า uncomment จะพังทันที
2. **`x_signature_img` ใช้ 5 จุด ไม่ใช่ 1** — 4 จุดอยู่ใน QWeb template → field หาย = รูปลายเซ็นหายทั้งใบ
3. **`base.action_partner_supplier_form`** (`x_withholding_tax_document_menu_view.xml:32`) — action ยุคเดียวกับ `supplier` ที่ถูกแทนด้วย `supplier_rank` ควรตรวจว่ายังมีใน 19
4. **`work_location` อยู่ใน `order=`** (`:173`) ไม่ใช่แค่การอ่านค่า → พังตอน `search()` ไม่ใช่คืนค่าว่างเงียบอย่างที่ R1 ประเมิน

---

## H. แนวทางแนะนำสำหรับกลุ่ม D

> ข้อเสนอของผู้รวมผล ไม่ใช่ finding ของ R1/R2
> **หลักการ:** ไม่ทุกข้อต้องการ reviewer คนที่สาม — 30 ข้อแยกได้เป็น 4 ประเภทที่ต้นทุนการยืนยันต่างกันมาก

### H-1 · ยืนยันด้วย grep เดียว (14 ข้อ) — ✅ **รันครบแล้ว 2026-09-22** (log: G-7)

ผลรวม: **CONFIRMED 14/14** · ตรงตาม `file:line` ที่ reviewer แนบมาทุกข้อ ยกเว้น D4 ที่ระบุ location เกินมา 1 จุด
**4 ข้อรุนแรงกว่าที่รายงาน** — D7 (view 5 จุดไม่ใช่ 4) · D9 (`work_location` อยู่ใน `order=`) · D10 (มี action เก่าเพิ่ม) · D15 (`x_signature_img` 5 จุดไม่ใช่ 1)
**โบนัส:** ยืนยัน D23 ไปด้วย (`deny_write` ที่ใช้ `../` ไม่กันอะไรเลย — sibling dirs อยู่ใน repo เดียวกัน)

→ **ทั้ง 14 ข้อพร้อม apply แล้ว** ปฏิบัติเหมือนกลุ่ม B ได้ · **D8 ควรแก้ก่อนเพื่อน** (report render พัง 100% ไม่มี AC ใดจับได้)

### H-2 · ต้องเทียบกับ Odoo 19 source เพิ่ม (4 ข้อ) — ต้นทุนกลาง

| ข้อ | เหตุผลที่ต้องเทียบ source | ข้อสังเกต |
|---|---|---|
| D12 | `@api.model_create_multi` — **R1 ระบุเองว่า "ต้องตรวจซ้ำ"** ว่า 19 raise หรือแค่ warn | ผลต่างกันมาก: raise = install blocker · warn = งานทำความสะอาด |
| D13 | `<chatter/>` — **R1 ระบุเองว่า "ต้องตรวจซ้ำ"** | เช่นเดียวกัน |
| D24 | `external_layout_*` template ที่มีจริงใน 19 | ตัวนี้เปลี่ยน**ขนาดงาน** — ถ้า R1 ถูก G-9/G-10 ประเมินต่ำไปมาก และ R-3 เองระบุว่า "view-only ไม่ใช่ AC" |
| D27 | `user_has_groups` ใน 19 | **ทั้ง R1 และ R2 ไม่มีใคร confirm** — R1 บอก "ต้องตรวจซ้ำ", R2 บอก "ยืนยันปานกลาง" → ยังไม่มีใครรู้ |

**แนะนำ:** ทำพร้อมกันครั้งเดียวด้วยการ fetch `19.0` source ชุดเดียว (เหมือน G-3) — **D24 คุ้มที่สุด** เพราะเปลี่ยนการประเมินขนาดงานของทั้ง Step 1/3/4

### H-3 · เป็นการแก้ AC/แผน ไม่ใช่การตรวจโค้ด (7 ข้อ) — ไม่ต้อง cross-check เลย

D16, D17, D18, D19, D20, D21, D22 — ทุกข้อเป็น **ข้อบกพร่องของเอกสารแผนเอง** ที่อ่านแล้วตัดสินได้ทันทีโดยไม่ต้องยืนยันกับ source ภายนอก (D23 ยืนยันไปแล้วใน H-1)

**แนะนำ:** รวมเข้ากับงานแก้ AC ที่ A1/A2 ต้องทำอยู่แล้ว — เขียน AC ชุดใหม่ทีเดียวให้ปิดทั้ง D17 (ตรรกะกลับด้าน), D18 (gate เปล่า), D19 (ไม่มี AC สำหรับ record rule), D20 (ไม่มี AC สำหรับ view validity), D21 (ตารางขัด yaml), D22 (`__pycache__`) และ D23 (`../` ใน `deny_write` — **ยืนยันแล้วว่าไม่กันอะไรเลย** จึงเป็นการแก้ ไม่ใช่การพิจารณา)
**ข้อยกเว้น:** **D16 ควรยืนยันด้วยการติดตั้งจริง** ไม่ใช่อ่าน source — R2 ระบุเองว่ายังไม่ได้รัน `-i` และผลของมัน (report เงียบหาย แต่ AC-4 เขียว) ร้ายแรงพอที่จะไม่ควรเชื่อจากการอ่าน `convert.py` อย่างเดียว · **ตอนนี้ทำได้แล้วเพราะมี Odoo 19 instance** (E-1)

### H-4 · เป็น policy call ไม่ใช่ข้อเท็จจริง (2 ข้อ) — อยู่ในหมวด E อยู่แล้ว

D14 (auto_install ควรเป็น True/False) → **E-12** · D30 (คง dead branch ไว้ไหม) → **E-13**
**แนะนำ:** ไม่ต้องตรวจอะไรเพิ่ม ตอบคำถามใน E ได้เลย · **D14 ยืนยันขอบเขตแล้ว** — กระทบเฉพาะ WHT (perdiem ค่าเป็น `False` จึงไม่เปลี่ยนพฤติกรรม)

### H-5 · ลำดับที่แนะนำ (ปรับตามคำตอบ E-1/E-2 แล้ว)

1. ~~รัน H-1~~ → ✅ **เสร็จแล้ว** (14/14 CONFIRMED)
2. ~~ตอบ E-1, E-2~~ → ✅ **เสร็จแล้ว** (มีทั้งสอง instance · adopt dev-playbook จริง)
3. **set up การ adopt dev-playbook** (`.claude/settings.json` + `docs/playbook/` หรือ `AGENTS.md`) — **ต้องทำก่อน apply** เพราะ `deny_write` ปัจจุบันห้ามเขียน `.claude/**` ไว้ → ต้องทำนอกรอบ port หรือแก้ `deny_write` พร้อมประกาศเหตุผล
4. **apply กลุ่ม A + B + C + D(H-1) ลงแผน — 33 ข้อ** พร้อมเขียน AC ชุดใหม่ที่ปิด H-3 ไปในตัว และแก้ `allow_bash` + เติม `<db19>` (E-3)
5. **ตอบ E-4..E-7** (state mapping / accounting_date / analytic / scope) → ปลดล็อก Step 2 · **E-4 ตอบง่ายขึ้นแล้ว** เพราะ D28 ให้ค่า v10 ที่ต้อง map มาครบ (`reported`, `done`, `post`) และ B4 ให้ค่า 7 ตัวของ 19
6. **H-2 (4 ข้อ) และ D16** ทำระหว่าง Step 1 บน Odoo 19 instance ที่มีแล้ว

---

## หมายเหตุการ apply

- **apply ได้แล้ว 33 ข้อ:** กลุ่ม **A + B + C** (16) + **D ที่ H-1 ยืนยัน** (17) — raw output ทั้งหมดเก็บใน G-1..G-7 เพื่อไม่ต้องรันซ้ำ
- **ยังรอ 26 ข้อ:** D ที่ยังไม่ตรวจ 13 (H-2 4 ข้อ · H-3 7 ข้อ · H-4 2 ข้อ) + E 13 คำถาม
- กลุ่ม **E** รอการตัดสินของเจ้าของ — ผู้รวมผลไม่ตัดสิน policy call แทน (mode / SemVer / adopt OCA / scope / digits / auto_install / dead branch)
- **ยังไม่มีการแก้ `odoo19_plan.md` หรือ `odoo19_agent_prompt.md` ใด ๆ** — ไฟล์นี้เป็นข้อเสนอล้วน
- **ผลข้างเคียงจากการตรวจ:** ไม่มี · ทุกคำสั่งเป็น read-only · ไม่ได้รัน `py_compile` จึงไม่มี `__pycache__` เกิดใหม่ (เลี่ยงปัญหา D22 ที่ R1 เจอ) · `git status` สะอาด มีเพียงไฟล์ review ที่ยัง untracked
