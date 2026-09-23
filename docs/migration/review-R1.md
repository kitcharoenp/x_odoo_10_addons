# Independent Review R1 — แผน port 4 addons Odoo 10 → Odoo 19

**Reviewer:** R1 (independent) · **วันที่:** 2026-09-22
**สถานะ:** single pass · read-only review
**ไฟล์ที่รีวิว:** `docs/migration/odoo19_plan.md`, `docs/migration/odoo19_agent_prompt.md`, และโค้ดต้นทาง 4 module
**สถานะรวม:** ต้องแก้ก่อนใช้

> R1 ไม่ได้เห็นผลของ R2 ระหว่างทำงานนี้ (ไฟล์ `review-R2.md` ยังไม่มีในดิสก์ ณ เวลาที่เขียน)

---

## 0. วิธีหาหลักฐาน + ข้อจำกัด

ตรวจจากต้นทาง 3 ทาง ไม่เชื่อคำเคลมของแผน:

1. **โค้ดจริง** ใน 4 module (`grep`/อ่านทั้งไฟล์)
2. **Odoo source tree บนเครื่องนี้** — `~/respo/odoo/odoo14` (14.0.0) และ `~/respo/odoo/odoo16` (16.0.0) ใช้เป็นจุดอ้างอิงกลางทางเพื่อ bracket ว่า API หายไปช่วงไหน
3. **`odoo/odoo` branch 19.0** ผ่าน raw.githubusercontent / GitHub tree

**รันจริงเพื่อทดสอบ AC:** AC-1, AC-2, AC-3 ถูกรันตามที่แผนเขียนทุกตัวอักษร ผลอยู่ในหัวข้อ A-11, B-17, B-18

> **ผลข้างเคียงที่ต้องแจ้ง:** การรัน AC-1 (`python3 -m py_compile ...`) เขียน `__pycache__/*.pyc` ลงใน 4 โฟลเดอร์ module (22 ไฟล์ · gitignored · `git status` ยังสะอาด · ไม่มีไฟล์ที่ git ติดตามถูกแก้) นี่เป็นผลข้างเคียงของ AC-1 เอง และชนกับ `deny_write` ของแผน — ดู D-4

**สิ่งที่ยืนยันไม่ได้จากเครื่องนี้ (ไม่เดา):**

| เรื่อง | เหตุผล |
|---|---|
| AC-4, AC-5 ทั้งหมด | ไม่มี Odoo 19 binary/DB และไม่มีหลักฐานว่ามี Odoo 10 instance ที่ยังรันได้ (มีแค่ source tree 14/16) → **AC-4/AC-5 วัดไม่ได้ ณ ตอนนี้** |
| เกณฑ์ข้อ 6 (playbook alignment) | `dev-playbook/` ไม่มีอยู่จริง → **ข้อมูลไม่พอที่จะตัดสิน** (ดู D-1) |
| B-12 `@api.model_create_multi` เป็น hard error หรือ warn ใน 19 | fetch `odoo/orm/models.py` ถูกตัดกลางคัน → **ต้องตรวจซ้ำ** |
| B-13 `<chatter/>` บังคับหรือยังใน 19 | ไม่ได้ verify → **ต้องตรวจซ้ำ** |
| สถานะ `user_has_groups` ใน 19 | ยืนยันได้แค่ว่ายังมีใน 14/16 → **ต้องตรวจซ้ำ** |
| A-12 `uom.uom` เปลี่ยนที่ v12 หรือ v14 | บนเครื่องมีแค่ 14/16 → **ต้องตรวจซ้ำ** (ผลกระทบเชิงปฏิบัติ = ศูนย์) |
| รายชื่อโมดูลบน branch OCA/hr-expense 19.0 | GitHub tree listing ที่ fetch มาไม่สมบูรณ์ → **ต้องตรวจซ้ำรายโมดูล** |

---

## A. FACTUAL_ERROR

| # | ตำแหน่ง | แผนบอกว่า | ความจริง | หลักฐาน | วิธีตรวจยืนยัน |
|---|---|---|---|---|---|
| A-1 | `odoo19_plan.md:112` G-11 | "`states` ออก v11" | ถูกถอดใน **17.0** ทั้ง view attribute และ field kwarg | Odoo 16 ยังมี `states = None` ใน Field; Odoo 19 raise `'Since 17.0, the "attrs" and "states" attributes are no longer used.'` | `grep -n "states = None" ~/respo/odoo/odoo16/odoo/fields.py`<br>`curl -s https://raw.githubusercontent.com/odoo/odoo/19.0/odoo/addons/base/models/ir_ui_view.py \| grep -n 'Since 17.0'` |
| A-2 | `odoo19_plan.md:110` G-9 | ระบุ `t-raw` ว่า "พบในโค้ด" | **ไม่มี `t-raw` เลย** ใน 4 module | grep = 0 hit | `grep -rn 't-raw' x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb` |
| A-3 | `odoo19_plan.md:110` G-9 | "namespace `report.` → `web.` (v12+)" — สื่อว่าแค่ rename | `external_layout_header`/`external_layout_footer` **ไม่มีอยู่แล้วทั้งคู่** ไม่มี `web.` ตัวเทียบให้ rename; layout ใหม่กระจายเป็น `external_layout_standard/boxed/bold/striped` → ต้อง **rewrite** | `x_report_ts_perdiem_template.xml:5,8,13,78`<br>`telco_expense_qweb_by_date_template.xml:5,8,13,141` | `grep -rn "external_layout_header" ~/respo/odoo/odoo16/addons/` → ว่าง<br>`grep -n 'template id="external_layout' ~/respo/odoo/odoo16/addons/web/views/report_templates.xml` |
| A-4 | `odoo19_plan.md:119` E-1 | "v16+ sheet รวมกลับเข้า `hr.expense`, state = `draft/submitted/approved/posted/refused`" | (ก) Odoo 16 **ยังมี** `hr.expense.sheet` — การรวมเกิดที่ **19.0**; (ข) state ของ 19 มี **7 ค่า**: `draft, submitted, approved, posted, in_payment, paid, refused` (แผนตก `in_payment`, `paid`) | odoo16 `hr_expense.py:903` ยังนิยาม state ของ sheet; 19.0 ไม่มีทั้ง `hr.expense.sheet` และ `sheet_id` | `grep -n "hr.expense.sheet" ~/respo/odoo/odoo16/addons/hr_expense/models/hr_expense.py`<br>`curl -s https://raw.githubusercontent.com/odoo/odoo/19.0/addons/hr_expense/models/hr_expense.py \| grep -n "in_payment\|sheet_id"` |
| A-5 | `odoo19_plan.md:121` E-3 | "`accounting_date` (override field ที่มีอยู่)" | Odoo 19 hr.expense **ไม่มี** `accounting_date` เลย · Odoo 16 มีแต่เป็น `related='sheet_id.accounting_date', store=True, groups='account.group_account_invoice,...'` → ไม่ใช่ override ทั้งสองปลาย | `telco_expense/models/telco_expense.py:12` สร้างเป็น field ใหม่ | `curl -s .../19.0/addons/hr_expense/models/hr_expense.py \| grep -n accounting_date`<br>`grep -n "accounting_date = fields" ~/respo/odoo/odoo16/addons/hr_expense/models/hr_expense.py` |
| A-6 | `odoo19_plan.md:122` E-4 | "`default_code` ย้ายไป `product.template`" | มีอยู่ **ทั้งสอง** model → `exp.product_id.default_code` ใช้ได้ปกติ · ตัวที่พังจริงคือ **`reference`** ซึ่ง **ไม่มี** บน hr.expense ใน 19 | `telco_expense_qweb/report/telco_expense_qweb_by_date_report_util.py:98` และ `order="... reference asc"` ที่ `:92-94` | `grep -n "default_code = fields" ~/respo/odoo/odoo16/addons/product/models/product_{product,template}.py`<br>`curl -s .../19.0/addons/hr_expense/models/hr_expense.py \| grep -n "reference"` |
| A-7 | `odoo19_plan.md:104` G-3 | "`get_precision` ย้าย/เลิกใช้แบบตรง" | **addon `decimal_precision` ไม่มีอยู่แล้วทั้งหมด** → `import odoo.addons.decimal_precision as dp` เป็น ImportError ไม่ใช่แค่ helper เปลี่ยนชื่อ | `x_account_withholding_tax_document/models/x_withholding_tax_document.py:6` | `ls ~/respo/odoo/odoo16/addons/decimal_precision` → No such file |
| A-8 | `odoo19_plan.md:140` | OCA l10n-thailand มี `l10n_th_withholding_tax`, `l10n_th_account_tax`, `l10n_th_withholding_tax_report` รุ่น 19 | branch **19.0 มีเฉพาะ** `l10n_th_account_tax`, `l10n_th_amount_to_text`, `l10n_th_base_sequence`, `l10n_th_base_utils` — **ไม่มี** `l10n_th_withholding_tax` และ `l10n_th_withholding_tax_report` | — | https://github.com/OCA/l10n-thailand/tree/19.0 |
| A-9 | `odoo19_plan.md:141` | hr-expense "ตอนนี้ 18.0.x — 19.0 ยังรอ migration" | **มี branch 19.0 แล้ว** (อัปเดต 13 ส.ค. 2026) · โมดูลไหน landed **ต้องตรวจซ้ำรายตัว** | — | https://github.com/OCA/hr-expense/branches/all |
| A-10 | `odoo19_plan.md:74` | "`telco_expense` model ขาด `_description`" | `telco_expense/models/telco_expense.py` เป็น `_inherit` ล้วน — **ต้องไม่มี** `_description` · ที่ขาดจริงคือ AbstractModel 2 ตัว: `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report_util.py:11` และ `telco_expense_qweb/report/telco_expense_qweb_by_date_report_util.py:15` | ผลรัน AC-3 จริง | รัน AC-3 ตามแผนแล้วดู output |
| A-11 | `odoo19_plan.md:62-63` AC-3 | `expect_exit: 0` = ผ่าน | **ตรรกะกลับด้าน** — `grep -L` exit 0 แปลว่า *มี* ไฟล์ที่ขาด `_description` · รันวันนี้บนโค้ดที่ยังไม่พอร์ต → **exit 0 = "ผ่าน"** · พอแก้ครบจะ exit 1 = "ตก" · ยังขัดกับตารางสรุป `:155` ที่เขียน "output ว่าง" | รันจริงได้ 4 ไฟล์ + `exit=0` | `grep -rLn '_description' $(find <4 dirs> -name '*.py' \| xargs grep -lE 'models.(Model\|TransientModel\|AbstractModel)'); echo $?` |
| A-12 | `odoo19_plan.md:109` G-8 | `product.uom`→`uom.uom` "ตั้งแต่ v14" | ยืนยันได้ว่า **ใน 14 เป็น `uom.uom` แล้วและไม่มี `product.uom`** — การแยก addon `uom` เกิดก่อนหน้านั้น แต่ **ข้อมูลบนเครื่องนี้ไม่พอยืนยัน v12 → ต้องตรวจซ้ำ** ผลกระทบเชิงปฏิบัติ = ศูนย์ | `grep -rn "_name = 'uom.uom'" ~/respo/odoo/odoo14/addons/uom/models/uom_uom.py` | เทียบ odoo/odoo tree 12.0 |

---

## B. MISSING

| # | หมวด | ประเด็นที่ขาด | หลักฐาน (file:line) | ผลต่อแผน/AC |
|---|---|---|---|---|
| B-1 | **install blocker** | `'depends': [..., 'report']` — addon `report` ไม่มีใน 14/16/19 · G-2 พูดถึงแต่ *model* `report` ไม่เคยพูดถึง manifest | `x_account_withholding_tax_document/__manifest__.py:12`<br>`x_report_timesheet_perdiem/__manifest__.py:10` | AC-4 ตายตั้งแต่ resolve dependency ก่อนโหลดอะไรเลย |
| B-2 | **install blocker** | **implicit relative import แบบ Python 2** ใน `__init__.py` ทั้ง 4 module — prompt D-3 (`:35`) ลิสต์ `u''`/`has_key`/print แต่ตกข้อนี้ ทั้งที่เป็น breakage อันดับ 1 ของ 10→11 | `telco_expense/__init__.py:5` · `telco_expense/models/__init__.py:5`<br>`telco_expense_qweb/__init__.py:5-6` · `models/__init__.py:5` · `report/__init__.py:6`<br>`x_account_withholding_tax_document/__init__.py:2` · `models/__init__.py:2-3`<br>`x_report_timesheet_perdiem/__init__.py:2-3` · `models/__init__.py:2` · `report/__init__.py:2` | **AC-1 จับไม่ได้** (พิสูจน์แล้ว: `py_compile` exit 0 บนโค้ดปัจจุบัน) |
| B-3 | **install blocker** | `<field name="view_type">form</field>` — field ถูกถอดจาก `ir.actions.act_window` | `x_report_timesheet_perdiem/actions/x_report_timesheet_perdiem_act_window.xml:6`<br>`x_account_withholding_tax_document/actions/x_withholding_tax_document_act_window.xml:7`<br>`x_account_withholding_tax_document/actions/x_withholding_tax_product_act_window.xml:7`<br>`telco_expense_qweb/actions/telco_expense_qweb_by_date_act_window.xml:6` | ไม่อยู่ใน G-1..G-13 และไม่อยู่ใน pattern AC-2 |
| B-4 | **install blocker** | `view_mode` ที่มีคำว่า `tree` — Odoo 19 `ir.ui.view.type` มีแค่ `list,form,graph,pivot,calendar,kanban,search,qweb` · G-12 ครอบแค่ **tag** `<tree>` ไม่ครอบ view_mode string | `x_withholding_tax_document_act_window.xml:8`<br>`x_withholding_tax_product_act_window.xml:8,23`<br>`views/x_withholding_tax_product_form_view.xml:64` | เช่นกัน |
| B-5 | **install blocker** | `res.groups` เปลี่ยน schema ใน 19: `category_id` **ไม่มีแล้ว** (ย้ายไป `res.groups.privilege`), `users` → **`user_ids`** | `x_account_withholding_tax_document/security/x_withholding_tax_document_groups.xml:6,14,17` | ไม่อยู่ในแผนเลย · หมายเหตุ: `ir.rule.groups` **ยังชื่อเดิม** ใน 19 → `security/ir_rule.xml` ปลอดภัย |
| B-6 | **install blocker** | `hr.expense.sheet` หายไปใน 19 → ทั้งไฟล์ไม่มีเป้าให้ inherit · แผนไม่เคยเอ่ยชื่อไฟล์นี้ และ Step 2 (`:57-60`) สั่งแค่ "E-1..E-3 + G-1,G-7,G-11" | `telco_expense/views/telco_expense_sheet_form_view.xml:6,8` | agent จะเจอ dead end กลาง Step 2 |
| B-7 | **install blocker** | xpath ยิงใส่ `analytic_account_id` 4 จุด — field ไม่มีใน 19 → view load error · E-2 พูดถึงแต่ onchange | `telco_expense/views/telco_expense_form_view.xml:31`<br>`telco_expense/views/telco_expense_tree_view.xml:11`<br>`telco_expense/views/telco_expense_sheet_form_view.xml:11`<br>`telco_expense_qweb/views/hr_expense_form_view.xml:9` | — |
| B-8 | **runtime crash** | `self.sum = round(_sum, 0)` บน recordset — `BaseModel.__slots__ = ['env','_ids','_prefetch_ids']` → `AttributeError` | `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report_util.py:155` (อ่านกลับที่ `:196-197`) | report render พัง 100% · ไม่มี AC ใดจับได้ |
| B-9 | **runtime crash** | `hr.employee` drift: `work_location` (char) ถูกถอด (16 = `work_location_id`, 19 = `work_location_name`); `bank_account_id` → **`bank_account_ids`** (M2m) ใน 19; `barcode` มี `groups="hr.group_hr_user"` → ค่าว่างเงียบสำหรับ non-HR | `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report_util.py:173,182` (`order="work_location asc"`), `:183-184`, `:176,180,195` | ไม่อยู่ในแผน · R-1 ระบุแค่ field ของ `account.analytic.line` |
| B-10 | compat | `domain="[('supplier','=',True)]"` — `res.partner.supplier` ถูกแทนด้วย `supplier_rank` | `x_account_withholding_tax_document/models/x_withholding_tax_document.py:83` | ไม่อยู่ในแผน |
| B-11 | compat | `datas_fname` ถูกถอดจาก `ir.attachment` · prompt Step 3 (`:63`) เขียนลอย ๆ ว่า "base64/datas ให้ตรง API 19" ไม่เคยระบุ key นี้ | `telco_expense_qweb/models/telco_expense_qweb_by_date.py:106` | `export_excel` raise |
| B-12 | compat | `@api.model def create(self, vals)` ต้องเป็น `@api.model_create_multi def create(self, vals_list)` | `x_account_withholding_tax_document/models/x_withholding_tax_document.py:141-142`<br>`x_account_withholding_tax_document/models/product_template.py:14-15` | **ต้องตรวจซ้ำ** ว่า 19 raise หรือแค่ warn |
| B-13 | compat | `<div class="oe_chatter">` แบบเก่า — Odoo ใหม่ใช้ `<chatter/>` | `x_account_withholding_tax_document/views/x_withholding_tax_document_form_view.xml:107-110` | **ต้องตรวจซ้ำ** กับ 19 |
| B-14 | compat / behavior | `auto-install` ของ WHT มีค่า **`True`** — แก้สะกดเป็น `auto_install` แล้วโมดูลจะ **auto-install จริง** (ตอนนี้ typo ทำให้เฉย ๆ) = เปลี่ยนพฤติกรรม · G-13 (`:114`) บอกแค่ "แก้สะกด" | `x_account_withholding_tax_document/__manifest__.py:42` (perdiem เป็น `False` จึงไม่มีผล) | ขัดเป้าหมาย behavior-preserving |
| B-15 | R-1 | dependency นอกแผนตกไป 1 field: `x_signature_img` นิยามที่ `x_hr_timesheet_sheet/models/hr_employee.py:9` | ใช้ที่ `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report_util.py:181` | R-1 (`:80`) ลิสต์แต่ field บน `account.analytic.line` |
| B-16 | **AC** | Objective ข้อ 4 ("record rules + group manager ยังบังคับ approve/edit เท่าเดิม") **ไม่มี AC รองรับเลย** | `odoo19_plan.md:21` | เป้าหมายที่ประกาศไว้วัดไม่ได้ |
| B-17 | **AC** | **AC-1 เป็น gate เปล่า** — รันวันนี้บนโค้ด Odoo 10 ที่ยังไม่แตะ ได้ exit 0 | `odoo19_plan.md:56-57` | ผ่านทั้งก่อนและหลังพอร์ต = ไม่ให้ข้อมูล |
| B-18 | **AC** | **AC-2 pattern มีรู 3 แบบ** — (ก) `attrs=` **ไม่ match** ของจริงซึ่งเขียนเป็น `<attribute name="attrs">` ที่ `telco_expense/views/telco_expense_form_view.xml:28,36` (ยืนยัน: `grep -rnE 'attrs=' telco_expense/views/` ได้ 0 บรรทัด); (ข) ไม่มี pattern ให้ `view_type`, `datas_fname`, `'supplier'`, `user_has_groups`, `^import models`, `depends.*'report'`, `@api.model def create`, `hr.expense.sheet`, `analytic_account_id`, `work_location`, `bank_account_id`; (ค) **fail-open** — `! grep …` คืน 0 เมื่อ grep error (exit 2) เช่นพิมพ์ path ผิด | `odoo19_plan.md:59-60` | AC-2 เขียวได้ทั้งที่ยังมี `attrs` และ blocker อีก ≥10 ข้อค้างอยู่ → ขัดกับ Objective ข้อ 1 (`:18`) โดยตรง |
| B-19 | **AC** | ไม่มี AC ระดับชุดสำหรับ XML/view-arch validity (มีแต่ `xml.etree` ad-hoc ใน Step 1 — และ parse ผ่าน ≠ Odoo validate view ผ่าน) | `odoo19_agent_prompt.md:55` | blocker ประเภท B-3..B-7 ไม่มีอะไรจับก่อนถึง AC-4 |

---

## C. CONFLICT / JUDGEMENT (ส่งต่อเจ้าของตัดสิน)

| # | ประเด็น | มุมมองผู้รีวิว | ทางเลือก + trade-off |
|---|---|---|---|
| C-1 | `mode: REFACTOR` | งานนี้ไม่ใช่ refactor — runtime target เปลี่ยน และ `hr.expense` state/analytic **ต้อง** เปลี่ยนความหมาย (behavior-preserving 100% ทำไม่ได้) | (ก) ตั้ง mode migration/CONTRACT-TOUCHING ตั้งแต่แรก — ตรงความจริง gate หนักกว่า · (ข) คง REFACTOR + escalate ตาม `:13` แต่เสี่ยง agent ไม่ escalate |
| C-2 | SemVer "MINOR—กระทบ compliance" | port ที่เปลี่ยน runtime และทำให้ field หาย/เปลี่ยนชื่อ เถียงได้ว่าเป็น MAJOR | เจ้าของตัดสิน — ไม่มีข้อมูล release policy ให้ยึด |
| C-3 | adopt OCA สำหรับ WHT | จาก A-8 คำแนะนำ "ใช้ OCA เป็นฐานคำนวณ WT" **ทำไม่ได้ตอนนี้** · แต่ `l10n_th_amount_to_text` **อยู่บน 19.0** และแทนโค้ดแปลงเลขไทยที่ซ้ำ **3 จุด** ได้ (`x_withholding_tax_document.py:149-185`, `x_report_timesheet_perdiem_report_util.py:50-86`, `telco_expense_qweb_by_date_report_util.py:25-61`) — แผนไม่เห็นตัวนี้ | (ก) คงโค้ดซ้ำ = behavior-preserving แน่นอน · (ข) adopt = ลดหนี้เทคนิค แต่ต้อง diff ผล "เอ็ด/ยี่/สตางค์" ทีละเคส (นอก non-goal ปัจจุบัน) |
| C-4 | G-3 แนะนำ `digits=(16,2)` | tuple ตรึง precision = **เปลี่ยนพฤติกรรม** ขัด Objective · ตัวเทียบเท่าคือ `digits='Product Price'` / `'Product Unit of Measure'` / `'Account'` | (ก) string = คงพฤติกรรม · (ข) tuple = ง่ายกว่าแต่ผู้ใช้ตั้งค่าไม่ได้อีก |
| C-5 | Step 0 กับ R-1 | `x_hr_timesheet_sheet` และ `telco_hr_employee` ยังเป็น Odoo 10 ทั้งคู่ → Step 0 (`:49`) สั่ง "หยุด emit PLAN AMENDMENT" **ทันที** → แผนตามที่เขียนมีโอกาสสูงมากที่จะจบที่ Step 0 โดยไม่ส่งงานอะไรเลย | (ก) ขยาย scope เป็น 6 module · (ข) partial port (WHT ก่อน — ตัวเดียวที่ไม่พึ่ง module นอกแผน) · (ค) ลด field ที่อ้าง |
| C-6 | AC-5 / characterization baseline | ต้องมี Odoo 10 instance ที่ยังรันได้ ซึ่งไม่ปรากฏหลักฐานบนเครื่องนี้ · ถ้าไม่มี → gate "ห้ามแก้โค้ดก่อนมี baseline" ผ่านไม่ได้ | เจ้าของยืนยันมี/ไม่มี ก่อนสั่ง go-ahead (ดูข้อเสนอ G-4) |
| C-7 | D-2 คง typo `for_withhoding_tax_doc` | เห็นด้วยกับ D-2 · เพิ่มข้อสังเกต: `product_template.py:16-18` มี dead branch (`vals.update` **หลัง** `super().create` → `supplier_taxes_id: False` ไม่เคยถูกใช้) — behavior-preserving แปลว่าต้องคง bug นี้ | ตัดสินชัดว่า "คง bug" หรือ "แก้พร้อมประกาศว่าเปลี่ยนพฤติกรรม" |
| C-8 | state mapping ของ report | `telco_expense_qweb_by_date.py:60-64` และ filter `..._report_util.py:85` ใช้ `draft/reported/done/refused` เทียบกับ 7 ค่าของ 19 · prompt ส่งเรื่องนี้ให้เจ้าของแล้ว ✓ แต่ตาราง E-1 ที่ผิด (A-4) จะทำให้เจ้าของตัดสินบนข้อมูลผิด | ต้องแก้ A-4 ก่อนถามเจ้าของ |

---

## D. PLAYBOOK_GAP

| # | ข้อกำหนด base | แผน/prompt ทำอะไร | ควรแก้เป็น |
|---|---|---|---|
| D-1 | §2/§5/§7/§8/§10, `PLAN.template.md`, `PROMPT.template.md`, `dev-playbook/review/` | **ไฟล์เหล่านี้ไม่มีอยู่จริง** — `dev-playbook/`, `docs/playbook/`, `.claude/`, `AGENTS.md`, `CLAUDE.md` ไม่มีทั้งใน repo และ parent dir · ผล: **เกณฑ์ข้อ 6 ข้อมูลไม่พอที่จะตัดสิน** · และ prompt `:26` สั่ง agent อ่าน `dev-playbook/BASE_PLAYBOOK.md` ซึ่งอ่านไม่ได้ → กฎเหล็กข้อ 3 (`:18`) จะยิงตั้งแต่ก่อน Step 0 | ระบุ path จริงของ playbook หรือ vendor เข้ามา — ตรวจ: `find ~ -maxdepth 4 -iname "BASE_PLAYBOOK.md"` |
| D-2 | plan-scope grammar | `deny_write` ใช้ `../telco_hr_employee/**` และ `../x_hr_timesheet_sheet/**` (`:44-45`) แต่ทั้งคู่เป็น **โฟลเดอร์พี่น้องใน repo เดียวกัน** → pattern ชี้ออกนอก repo = **ไม่ได้กันอะไรเลย** (ตอบเกณฑ์ข้อ 4: ไม่พอ) | `telco_hr_employee/**`, `x_hr_timesheet_sheet/**` (ไม่มี `../`) |
| D-3 | allow_bash vs AC | allow_bash (`:49-53`) ไม่มี `find`, `xargs`, `odoo`, `python3 -c` แต่ AC-1/AC-3 ต้องใช้ `find`+`xargs`, AC-4 ต้องใช้ `odoo`, Step 1 (`:55`) ต้องใช้ `python3 -c` → **AC รันไม่ได้ภายใน allowlist ของตัวเอง** | เพิ่มเข้า allow_bash หรือเขียน AC ใหม่ให้อยู่ในวงที่อนุญาต |
| D-4 | deny_write vs AC | AC-1 เขียน `__pycache__/*.pyc` ลงโฟลเดอร์ module ซึ่ง `deny_write` (`:41`) ห้ามไว้ (R1 เจอเองตอนรันทดสอบ) | ตั้ง `PYTHONDONTWRITEBYTECODE=1` หรือใช้ `compileall` + `sys.pycache_prefix` |
| D-5 | §8 ข้อ 1 (ห้ามเคลมผลที่ไม่ได้รัน) | **ทำได้ดี ไม่มี gap** — R-4 (`:176`), หมายเหตุ AC-4 (`:73`), Evidence Block (`:102`) สอดคล้องกันทั้งสามที่ | — |
| D-6 | plan-scope = แหล่งความจริงเดียว | `go_ahead` placeholder ✓ · `require_go_ahead: true` ✓ · `evidence_path` อยู่ใน `allow_write` ✓ · แต่ตารางสรุป AC (`:149-157`) **ขัดกับ** yaml ที่ AC-3 (ตาราง = "ว่าง", yaml = `expect_exit: 0`) | ลบ/แก้ตารางสรุปให้ตรง หรือแก้ yaml |

---

## E. คำถามที่ต้องส่งต่อให้เจ้าของ

1. **Odoo 19 instance + `<db19>`** มีหรือยัง? ถ้าไม่มี AC-4 วัดไม่ได้ และ blocker B-1..B-7 จะไม่มีอะไรจับเลย
2. **Odoo 10 instance ที่ยังรันได้** สำหรับ baseline (AC-5 / Step 0) มีไหม? ถ้าไม่มี → gate "ห้ามแก้โค้ดก่อนมี baseline" ผ่านไม่ได้ แผนติดตั้งแต่ก้าวแรก
3. **`dev-playbook` อยู่ที่ไหน?** (ดู D-1) — ถ้าไม่มี path จริง ทั้งผู้รีวิวและ agent ตรวจ §2/§5/§8/§10 ไม่ได้
4. **ขยาย scope เป็น 6 module** (+`telco_hr_employee`, `x_hr_timesheet_sheet`) หรือยอมรับ partial port (WHT ก่อน)? — ดู C-5
5. **hr.expense state mapping**: `done`/`post` ของ Odoo 10 → ค่าไหนใน 7 ค่าของ 19 (`posted` / `in_payment` / `paid`)? และ report ควรนับสถานะใดเป็น "Posted"?
6. **`accounting_date`**: คงเป็น custom field บน hr.expense ต่อ หรืออิง `account.move.date`? (field หายจาก 19 — A-5)
7. **`analytic_distribution`**: แปลง `employee.x_analytic_account_id` (บัญชีเดียว) → distribution dict ด้วยนโยบายอะไร (100% ไปบัญชีเดียว?)
8. **`digits`**: ตรึง `(16,2)` หรือคงค่า configurable ด้วย `digits='Account'`? (C-4)
9. **`auto-install` → `auto_install` ของ WHT** ค่าเป็น `True` — ต้องการให้ auto-install จริง หรือให้ตั้งเป็น `False`? (B-14)
10. **`l10n_th_amount_to_text` (OCA 19.0)** — adopt แทนโค้ดแปลงเลขไทยที่ซ้ำ 3 จุด หรือคงของเดิมไว้ในรอบนี้?

---

## F. สรุป verdict — R1

**สถานะรวม: ต้องแก้ก่อนใช้**

เหตุผลสั้น: โครงแผนใช้ได้ (scope block, rollback, R-1..R-4, §8 discipline ดี) แต่ **สามเสาหลักพัง**

1. ตาราง G/E มีเวอร์ชันผิดในจุดที่ agent จะเอาไปตัดสินใจจริง (A-1, A-4, A-5)
2. ตกรายการที่เป็น install blocker อย่างน้อย 7 ข้อ (B-1..B-7) ซึ่งจะทำให้ AC-4 ตายก่อนเจอปัญหาที่แผนเตรียมไว้เสียอีก
3. **AC-1/AC-2/AC-3 ใช้เป็น gate ไม่ได้** — AC-1 ผ่านอยู่แล้ววันนี้, AC-2 พลาด `attrs` ตัวจริงและ blocker อีก ≥10 ข้อ พร้อม fail-open, AC-3 ตรรกะกลับด้าน สรุปคือ agent สามารถรายงาน "AC เขียวครบ" ได้โดยที่โค้ดยังติดตั้งไม่ขึ้นเลย

**นับข้อ:** A = 12 · B = 19 · C = 8 · D = 6 · E = 10 คำถาม

**ความเสี่ยงที่ยังเหลือหลังอ่านจบ:**

- แผนมีโอกาสสูงที่จะ **หยุดที่ Step 0** (R-1: dependency 2 ตัวยังเป็น Odoo 10) และไม่ส่งงานใด ๆ — เจ้าของควรตัดสิน C-5 ก่อนปล่อย agent
- **ความเพี้ยนเงียบทางตัวเลข** ยังไม่มีอะไรกัน: ถ้า state mapping ผิด รายงาน expense-by-date จะได้ชุดข้อมูลผิดโดยไม่ error (ตรงกับที่ Blast Radius `:90` ระบุไว้เอง) และ AC-5 ที่เป็นตัวเดียวที่จับได้ ขึ้นกับ environment ที่ยังไม่ยืนยันว่ามี
- **`accounting_date` + `groups=`**: ถ้าพอร์ตแล้วไปพิงของ core ที่มี `groups='account.group_account_*'` report จะคืนค่าว่างเงียบสำหรับผู้ใช้ที่ไม่ใช่ accounting — เช่นเดียวกับ `barcode` (B-9)
- **Layout report ต้อง rewrite จริง ไม่ใช่ rename** (A-3) — งานใหญ่กว่าที่ G-9/G-10 ประเมิน และ R-3 ระบุเองว่า "view-only ไม่ใช่ AC" → ไม่มี gate
- **playbook ตรวจไม่ได้** (D-1) → กฎที่ทั้งแผนและ prompt อ้างเป็นฐานอำนาจ อาจไม่ตรงกับของจริง

**สิ่งที่ไม่สามารถยืนยันได้จากเครื่องนี้:** ดูตารางในหัวข้อ 0

---

## G. ข้อเสนอแนะเพิ่มเติม (นอกกรอบ 4 กลุ่ม — ไม่ใช่คำตัดสิน)

> ส่วนนี้เป็นความเห็นเชิงสร้างสรรค์ตามที่เจ้าของขอ · ไม่ใช่ finding และไม่ผูกมัด · ทุกข้อยังอยู่ในขอบเขต 4 module

### G-1 แยกแผนเป็น 2 รอบ: "ติดตั้งขึ้น" ก่อน "พฤติกรรมตรง"

ตอนนี้แผนพยายามทำ *install compatibility* กับ *behavior parity* พร้อมกันในรอบเดียว ซึ่งทำให้ AC ปนกันและ gate วัดไม่ได้ ข้อเสนอ:

- **รอบ A — Install sweep (ไม่มี business decision เลย):** B-1..B-7, B-10..B-14, G-1/G-4/G-5/G-6/G-8/G-12/G-13 · ทั้งหมดเป็นการแก้เชิงกลไก ตรวจได้ด้วย AC-4 อย่างเดียว · **ไม่ต้องรอ owner decision** จึงไม่ติด C-5
- **รอบ B — Behavior parity:** E-1..E-4, report layout (A-3), state mapping, analytic_distribution · ต้องมี baseline + owner decision

ข้อดี: รอบ A ส่งของได้จริงแม้ dependency นอกแผนยังไม่พอร์ต และทำให้ AC-4 เริ่มมีความหมาย (จาก "ตายที่ depends" → "ตายที่ field จริง ๆ")

### G-2 AC-2 ที่ fail-closed และครอบของจริง

ปัญหาหลักคือ regex ชุดเดียวไม่พอและ `!` ทำให้ fail-open ข้อเสนอ: เก็บ pattern เป็นไฟล์ แล้วให้ exit code มาจากจำนวน match ไม่ใช่จาก `!`

```bash
# ตัวอย่างแนวทาง — เจ้าของปรับรายการเองได้
PATTERNS='@api\.(multi|one)|track_visibility|ir\.needaction_mixin
|decimal_precision|self\.env\[.report.\]|env\.user\.company_id
|<tree|</tree>|states=|name="attrs"|attrs=|t-raw
|report\.external_layout|product\.uom|user_has_groups
|view_type|datas_fname|\bsupplier\b.*=.*True
|^\s*import\s+(models|report)\b|analytic_account_id
|work_location\b|bank_account_id\b|hr\.expense\.sheet
|@api\.model\s*$'
n=$(grep -rnE "$(echo "$PATTERNS" | tr -d '\n')" \
      x_report_timesheet_perdiem x_account_withholding_tax_document \
      telco_expense telco_expense_qweb \
      --include='*.py' --include='*.xml' --include='*.csv' | tee /dev/stderr | wc -l)
test "$n" -eq 0
```

จุดสำคัญ 3 อย่าง: (ก) `--include` กัน `.pyc` ปนเข้ามา · (ข) `name="attrs"` ต้องอยู่ใน pattern (ดู B-18ก) · (ค) `test -eq 0` ทำให้ grep error ไม่กลายเป็น pass

### G-3 AC-3 เขียนใหม่ให้ตรวจเฉพาะ model ที่ประกาศ `_name`

AC-3 ปัจจุบันจับ `_inherit`-only มาด้วยจึงให้ผลลวง (A-10) เกณฑ์ที่ถูกคือ *"ไฟล์ที่มี `_name =` ต้องมี `_description`"*

```bash
miss=$(grep -rl "_name\s*=" <4 dirs> --include='*.py' | xargs grep -L "_description")
test -z "$miss"
```

รันตอนนี้จะได้ 2 ไฟล์ (report util ทั้งสองตัว) ซึ่งตรงกับความจริง

### G-4 characterization test ที่ทำได้แม้ไม่มี Odoo 10 instance

C-6 / E ข้อ 2 อาจตอบว่า "ไม่มี Odoo 10 แล้ว" ซึ่งจะทำให้ Step 0 ค้างถาวร ทางออกที่ยังให้ค่า:

1. **Pure function golden test** — `_thai_unit_process` / `_thai_num2text` / `_compute_amount_in_letter` ไม่พึ่ง ORM เลย (ดู `x_withholding_tax_document.py:149-185`) ดึงออกมารันด้วย `python3` เปล่า ๆ บนโค้ด Odoo 10 ปัจจุบัน แล้ว freeze ผลลัพธ์เป็นตาราง input→output (รวมเคสขอบ: `0`, `1`, `11`, `21`, `101`, `1000000`, `.05`, `.50`) — นี่คือ baseline ที่ **ตรวจได้บนเครื่องนี้วันนี้** และคุ้มที่สุดเพราะ "ตัวเลขภาษาไทย" คือสิ่งที่ Objective ข้อ 3 ระบุชัด
2. **PDF/xlsx เก่าที่ผู้ใช้เคยออก** — ถ้ามีไฟล์จริงจากระบบ production เก็บไว้ ใช้เป็น golden แทนการรัน Odoo 10 ใหม่
3. ถ้าทั้งสองทางไม่มี → **ประกาศตรง ๆ ว่า AC-5 วัดไม่ได้** และลด Objective ข้อ 3 ลงเป็น "ไม่ raise" แทน "ค่าตรง baseline" อย่าปล่อยให้ AC ค้างเป็นเป้าลอย

### G-5 เพิ่ม AC สำหรับ record rule / ACL (ปิดช่อง B-16)

Objective ข้อ 4 ต้องมีตัววัด ข้อเสนอที่ถูกที่สุดคือ smoke test หลัง install บน db19:

```
odoo shell -d <db19> --no-http  # แล้วรันสคริปต์ที่:
#  1. สร้าง user ที่อยู่ใน group officer อย่างเดียว
#  2. สร้าง WHT doc, submit
#  3. ยืนยันว่า approve_withholding_tax() raise UserError
#  4. ยืนยันว่า write() บน record state != draft raise UserError
#  5. ยืนยันว่า officer search เห็นเฉพาะ doc ของตัวเอง (ir_rule.xml:17)
```

อยู่ในกลุ่ม "ต้องมี env" เหมือน AC-4 — ควรเขียนไว้ใน AC ให้ชัดว่าเป็น AC-6 ที่รอ environment ไม่ใช่ปล่อยหาย

### G-6 `.gitignore` ยังไม่ครอบ `__pycache__/`

ตอนนี้มีแค่ `*.pyc` (บรรทัดเดียวใน `.gitignore`) ซึ่งพอสำหรับไฟล์ แต่โฟลเดอร์ `__pycache__/` เปล่า ๆ ยังโผล่ใน `git status` ได้ในบางสถานการณ์ · เพิ่ม `__pycache__/` จะลด noise ตอนรัน AC-1 (เกี่ยวกับ D-4)

### G-7 ลำดับ Step ที่เสี่ยงน้อยกว่า

Step ปัจจุบันคือ WHT → telco_expense → qweb → perdiem ซึ่งดีอยู่แล้วตรงที่เอา WHT ขึ้นก่อน แต่ข้อเสนอเล็ก ๆ: **ย้าย perdiem ขึ้นเป็น Step 2** แทน `telco_expense`

เหตุผล: `telco_expense` เป็นตัวเดียวที่ **บล็อกรอ owner decision** (state mapping + analytic) ถ้าวางไว้กลางทาง Step 3/4 จะค้างตามไปด้วยทั้งที่ไม่จำเป็น · perdiem ติด R-1 ก็จริง แต่ blocker ของมัน (B-8, B-9, B-1, B-3) แก้ได้โดยไม่ต้องถามใคร

ลำดับที่เสนอ: **WHT → perdiem → telco_expense (รอ owner) → qweb** โดย qweb ยังต้องอยู่หลัง telco_expense เพราะพึ่ง `x_project_id`/`x_require_po`/`accounting_date` จริง

### G-8 จุดที่แผนทำได้ดีและควรคงไว้

เพื่อความเป็นธรรม — สามอย่างนี้ทำได้ดีกว่าแผน migration ทั่วไปและไม่ควรรื้อ:

- **§8 discipline** สอดคล้องกัน 3 ที่ (R-4, หมายเหตุ AC-4, Evidence Block) ไม่มีช่องให้เคลมผลลอย ๆ — ดู D-5
- **`plan-scope` ประกาศตัวเองเป็นแหล่งความจริงเดียว** และ prose ไม่มีผลบังคับ ทำให้รีวิวชี้จุดขัดกันได้ชัด (D-6)
- **R-1/R-2 ระบุ dependency นอกขอบเขตและสั่งห้ามพอร์ตเงียบ ๆ** — เป็นข้อที่แผนส่วนใหญ่มักตกหล่น

---

*จบรายงาน R1 · ถัดไป: นำไฟล์นี้ + `review-R2.md` + แผนต้นฉบับ เข้า `odoo19_synthesis_prompt.md`*
