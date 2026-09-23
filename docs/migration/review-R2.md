# Review R2 — Independent Review: Plan/Prompt Port 4 Odoo Addons (10→19)

**Reviewer:** R2 (independent, read-only — ไม่แก้ไฟล์ใด ๆ ระหว่างรีวิว)
**วันที่รีวิว:** 2026-09-22
**ไฟล์ที่รีวิว:** `docs/migration/odoo19_plan.md`, `docs/migration/odoo19_agent_prompt.md` + โค้ดต้นทาง 4 โมดูล (`x_report_timesheet_perdiem`, `x_account_withholding_tax_document`, `telco_expense`, `telco_expense_qweb`)
**วิธีตรวจ:** verify ทุกข้อกับโค้ดจริงในโมดูล (grep/read), กับ Odoo 19 source จริง (branch `19.0` บน `github.com/odoo/odoo`, ยืนยันด้วย commit hash), และรัน `dev-playbook/scripts/plan_scope.sh` จริง (จาก `/home/kitcharoenp/respo/dev-playbook/`) เพื่อทดสอบ AC/guard แทนการอ่านแล้วเดา

---

## A. FACTUAL_ERROR

| # | ตำแหน่ง | แผนบอกว่า | ความจริง (Odoo 19 source) | หลักฐาน | วิธีตรวจยืนยัน |
|---|---|---|---|---|---|
| 1 | `odoo19_plan.md:104` (G-4) | `track_visibility='onchange'` "ถอดออก v11" | Rename เป็น `tracking=True` เกิด **v13** (kwarg เก่ายังใช้ได้แบบ compat จนถูกลบจริงใน **v19** เอง — commit `e6c4fa5`, 2024-12-05 "Bye Bye remains of track_visibility") | commit `09ad56b` (rename, contained ใน 13.0 ไม่ใช่ 12.0) | `git log --oneline --all -- odoo/addons/mail/models/mail_thread.py` เทียบ branch 12.0 vs 13.0 ของ odoo/odoo |
| 2 | `odoo19_plan.md:109` (G-8) | `product.uom`→`uom.uom` "ตั้งแต่ v14" | เกิดจริง **v12** (2 เวอร์ชันคลาดเคลื่อน) — commit `2966d4f` "[IMP] product: rename product.uom into uom.uom" | https://github.com/odoo/odoo/commit/2966d4faedb2817039ed608dff48acfda418109e | branch-compare 11.0 vs 12.0 ที่ path `addons/uom/` |
| 3 | `odoo19_plan.md:112` (G-11) | `states=` (WHT buttons) "ออก v11" | ยัง **ทำงานจริง** ใน core จนถึง v16 (verify: `addons/sale/views/sale_order_views.xml` ของ branch 16.0 ยังมี `states="draft"` ใช้งานจริง) ถูกถอดพร้อม `attrs=` ใน **v17** เดียวกัน (ValidationError "Since 17.0, the attrs and states attributes are no longer used" ใน `ir_ui_view.py`) | https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/models/ir_ui_view.py | `grep -n "states=" https://raw.githubusercontent.com/odoo/odoo/16.0/addons/sale/views/sale_order_views.xml` → เจอจริง |
| 4 | `odoo19_plan.md:119` (E-1) | `hr.expense.sheet` "v16+ sheet รวมกลับเข้า hr.expense" | Merge เกิด **v19 เอง** (target version ของแผนนี้) — commit `704a5a1` (2024-12-05) "[IMP] *expense*: Bye Bye reports — the model hr.expense.sheet is removed" ก่อนหน้านั้น (v10-v18) `hr.expense.sheet` เป็น model แยกต่างหากเสมอ | https://github.com/odoo/odoo/commit/704a5a19499469e5a14461bb81d33c832ce00d70 ; ไม่มี `hr_expense_sheet.py` ใน `addons/hr_expense/models/` ของ branch 19.0 (404) | `curl -s https://api.github.com/repos/odoo/odoo/contents/addons/hr_expense/models?ref=19.0` |
| 5 | `odoo19_plan.md:119` (E-1) | `state` field ของ hr.expense = `draft/submitted/approved/posted/refused` | 19.0 มี **7 ค่า** ไม่ใช่ 5: เพิ่ม `in_payment`, `paid` | `addons/hr_expense/models/hr_expense.py` บรรทัด 124-137 ของ branch 19.0 | `curl -s https://raw.githubusercontent.com/odoo/odoo/19.0/addons/hr_expense/models/hr_expense.py \| grep -A15 "state = fields.Selection"` |
| 6 | `odoo19_plan.md:110` (G-9) | อ้างว่าพบ `t-raw` ในโค้ด | ไม่มี `t-raw` อยู่จริงในทั้ง 4 โมดูลเลยแม้แต่จุดเดียว | — | `grep -rn "t-raw" x_report_timesheet_perdiem x_account_withholding_tax_document telco_expense telco_expense_qweb` → exit 1 (ว่าง) |
| 7 | `odoo19_plan.md:74` | "telco_expense model ขาด [_description] ให้เพิ่มในรอบแก้" | Odoo ไม่ warn/บังคับ `_description` กับ class ที่มีแค่ `_inherit` (ไม่ประกาศ `_name` ใหม่) — เงื่อนไขจริงใน `_init_model_class_attributes`: warn เฉพาะ class ที่ introduce model ใหม่ `telco_expense.py:9-10` (`_inherit = "hr.expense"` ล้วน) ไม่เข้าเงื่อนไขนี้ — false positive | `odoo/orm/model_classes.py` (`_init_model_class_attributes`) branch 19.0 | อ่าน source + เทียบกับ `telco_expense/models/telco_expense.py:9-10` |
| 8 | prose ใต้ตาราง E (x_account_withholding_tax_document) | "ตรวจว่า `self.env.user.has_group(...)` แทน `user_has_groups` (deprecated)" | ไม่พบหลักฐานว่า `user_has_groups` ถูก deprecate — คนละ method กับ `has_group` โค้ดที่มีอยู่ (`x_withholding_tax_document.py:193,199,211,217`) ใช้ถูกต้องอยู่แล้ว ไม่ต้องเปลี่ยน | ไม่พบ deprecation notice ใน Odoo forum/GitHub ที่ค้นได้ (ยืนยันปานกลาง ไม่ใช่ primary commit) | `grep -n "has_group\|user_has_groups" x_account_withholding_tax_document/models/x_withholding_tax_document.py` + web search ไม่พบ deprecation |
| 9 | `odoo19_plan.md:141` | OCA hr-expense "ตอนนี้ 18.0.x — 19.0 ยังรอ migration" | branch `19.0` มีอยู่จริงแล้ว (scaffold ว่าง + PR ค้าง 15 ใบ) ไม่ใช่ "ยังไม่มี 19.0" — ใจความถูก แต่ technical description ไม่ตรง | https://github.com/OCA/hr-expense/branches | `curl -s https://api.github.com/repos/OCA/hr-expense/branches` |

---

## B. MISSING

| # | หมวด | ประเด็นที่ยังขาด | หลักฐาน (file:line) | ผลต่อแผน/AC |
|---|---|---|---|---|
| 1 | Report action XML | `<report id="..." model="..." report_type="qweb-pdf" .../>` (shorthand tag เก่า) ใช้อยู่ใน **ทั้ง 3 โมดูลรายงาน** — `odoo/tools/convert.py` ของ 19.0 ไม่มี handler สำหรับ tag `report` เลย dispatcher (`_tag_root`) ทำ `if f is None: continue` คือเพิกเฉยเงียบ ๆ ไม่ error | `x_account_withholding_tax_document/reports/x_withholding_tax_document_report.xml:20-27`, `telco_expense_qweb/report/telco_expense_qweb_by_date_report.xml:16-25`, `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report.xml:16-24` | **ร้ายแรง**: ir.actions.report จะไม่ถูกสร้างเลยหลัง `-i` แต่ AC-4 (`--stop-after-init --log-level=error`) จะผ่านเพราะไม่มี error — AC-4 จับบั๊กนี้ไม่ได้ ต้องแปลงเป็น `<record id="..." model="ir.actions.report">` ก่อน ไม่มีอยู่ใน G-1..G-13 เลยสักข้อ |
| 2 | AC-3 (_description) | AC-3 มองข้าม 2 จุดที่ต้องแก้จริง: `x_report_timesheet_perdiem/report/x_report_timesheet_perdiem_report_util.py:11` และ `telco_expense_qweb/report/telco_expense_qweb_by_date_report_util.py:15` — ทั้งคู่ `_name = 'report.<module>.<template>'` (โมเดลใหม่จริง) แต่ไม่มี `_description` เลย = ตรงเงื่อนไข warning จริง (ต่างจาก A-7 ที่เป็น false positive) | บรรทัดที่อ้าง | plan-scope line 74 พูดถูกที่ "AC-3 ยังเป็นเป้าหมาย" แต่ชี้ผิดไฟล์ — คนที่แก้ตามแผนจะพลาด 2 ไฟล์ที่ต้องแก้จริง |
| 3 | G-11 ไม่ครบ | `telco_expense/models/telco_expense.py:15-16,22-24` มี Python field-kwarg `states={...}` (คนละกลไกกับ view attribute `states=`) บนฟิลด์ `accounting_date`/`payment_mode` — ไม่ถูกระบุที่ไหนใน G-11 เลย | `telco_expense/models/telco_expense.py:12-25` | ต้องแปลง field-kwarg `states=` แยกจาก XML `attrs=` fix — ทำตาม G-11 ตรง ๆ จะพลาดจุดนี้ |
| 4 | R-1 ประเมินความเสี่ยงต่ำไป | `x_report_timesheet_perdiem/__manifest__.py:10`: `'depends': ['x_hr_timesheet_sheet', 'report']` — เป็น hard manifest dependency ไม่ใช่แค่ "อ้าง field custom" ตามที่ R-1 บอก | manifest บรรทัดที่อ้าง | ถ้า `x_hr_timesheet_sheet` ยังพอร์ตไม่เสร็จ AC-4 จะ fail ตั้งแต่ dependency resolution (Odoo ปฏิเสธติดตั้งทั้ง batch) ไม่ใช่แค่ "รายงานเป็นค่าว่าง" ตามที่ R-1 อธิบาย — รุนแรงกว่าที่เขียนไว้ |
| 5 | Step 0 baseline | "สิ่งที่ต้องขอจากเจ้าของ" ระบุแค่ "Odoo 19 instance" — ไม่ระบุว่าต้องมี Odoo 10 instance/ข้อมูลจริงเพื่อเก็บ characterization baseline (Step 0) ก่อนแตะโค้ดตาม §5.1 | `odoo19_agent_prompt.md:37-42`, เทียบ Step 0 บรรทัด 46-50 | ถ้าไม่มี Odoo 10 รันอยู่ agent จะเก็บ baseline ไม่ได้ตั้งแต่ Step 0 แต่ไม่มีใครถูกขอให้เตรียมสิ่งนี้ล่วงหน้า |
| 6 | telco_expense.py dead code | `telco_expense/models/telco_expense.py:40-68` มี `@api.multi def submit_expenses(...)` ทั้งฟังก์ชันอยู่ในบล็อก docstring `"""..."""` (โค้ดตาย ไม่รัน) — grep ของ AC-2 จะเจอ `@api.multi` ตรงนี้ตลอดไปแม้ลบ deprecated API จริงหมดแล้ว | `telco_expense/models/telco_expense.py:42` | G-1 ไม่ได้ระบุ telco_expense เป็น location ของ `@api.multi` เลย — agent อาจงงว่าทำไม AC-2 ไม่ผ่าน |

---

## C. CONFLICT / JUDGEMENT (ส่งต่อเจ้าของ)

| # | ประเด็น | มุมมองผู้รีวิว | ทางเลือก + trade-off |
|---|---|---|---|
| 1 | `mode: REFACTOR` ใน plan-scope block (`odoo19_plan.md:32`) vs prose ของแผนเอง (`odoo19_plan.md:5-6`) ที่ยอมรับว่าเข้าเงื่อนไข "CROSS-MODULE/CROSS-CUTTING" และ "CONTRACT-TOUCHING" ตามตาราง §2 ของ BASE_PLAYBOOK | template ระบุชัดว่าบล็อก plan-scope คือแหล่งความจริงเดียว prose ไม่มีผลบังคับ — ถ้า mode ที่แท้จริงควรเป็น CROSS-MODULE/CONTRACT-TOUCHING แต่ YAML ยัง REFACTOR = tooling อัตโนมัติจะไม่ trigger §4 Forward-only mode หรือ "หยุดเสนอ amendment" | (ก) แก้ `mode:` ให้ตรง prose แล้วรับภาระ §4 เพิ่ม (ข) คงไว้ REFACTOR แล้วอธิบายเหตุผล 1 บรรทัดตามกฎ §5 ข้อ 2 — ไม่ใช่เรื่องที่ผู้รีวิวตัดสินแทนได้ |
| 2 | citation "เข้าเกณฑ์ independent review... ข้อ 1–3" อ้างอิง `README.md` หัวข้อ "ปล่อยเวอร์ชันใหม่" ซึ่งเขียนขึ้นเพื่อการปล่อยเวอร์ชันของ BASE_PLAYBOOK.md เอง ไม่ใช่ของโปรเจกต์ลูก — ข้อ 2/3 ไม่มีความหมาย map ตรงกับงาน port addon เลย | แต่ `PLAN.template.md:18-19` เองก็สั่งให้ใช้ citation รูปแบบนี้ — เป็นความไม่ชัดเจนของ template เอง ไม่ใช่ความผิดของผู้เขียนแผน | ต้องให้เจ้าของ/ผู้ดูแล template ตัดสิน: ยอมรับว่า "ข้อ 1" พอสำหรับ trigger หรือปรับ citation ให้แม่นยำขึ้น |
| 3 | Adopt OCA `l10n-thailand` ตอนนี้ไหม — ยืนยันแล้วว่า branch 19.0 มี 4 module merge จริง (คืบหน้ากว่าที่แผนประเมิน) | D-1 ปิดไปแล้วว่า "ไม่ใช่รอบนี้" แต่ข้อมูลใหม่อาจเปลี่ยนสมการต้นทุน/ผลประโยชน์ | เป็น business call ของเจ้าของ — แค่ flag ว่าข้อมูลที่ D-1 ใช้ตัดสินใจอาจ outdated |
| 4 | E-1 อาศัยสมมติฐาน "v16+" ที่ผิด — merge จริงเพิ่งเกิดใน v19 เอง พร้อม OCA กำลังเพิ่ม `hr_expense_sheet` แยกกลับมาสำหรับ 19.0 เพราะ core ตัด | ควรยกระดับความเข้มงวดของ Step 2 (owner decision gate) เพิ่มไหม เพราะพื้นที่นี้ของ Odoo core ไม่นิ่งในเวอร์ชันเป้าหมายเอง | ตัดสินใจ scope/rigor เพิ่มเติมเป็นของเจ้าของ |

---

## D. PLAYBOOK_GAP

| # | ข้อกำหนด base (§..) | แผน/prompt ทำอะไร | ควรแก้เป็น |
|---|---|---|---|
| 1 | Adoption (§9) | **repo `x_odoo_10_addons` ไม่ได้ adopt dev-playbook เลย** — ไม่มี `docs/playbook/`, ไม่มี `.claude/` ทั้งไดเรกทอรี, ไม่มี CLAUDE.md/AGENTS.md อ้างอิง, ไม่มี symlink/copy ของ dev-playbook ใน repo นี้เลย (`dev-playbook/` ตัวจริงอยู่ที่ path พี่น้อง `/home/kitcharoenp/respo/dev-playbook/` คนละ repo) — path สัมพัทธ์ `dev-playbook/BASE_PLAYBOOK.md` ที่แผน/prompt สั่งอ่านจาก cwd ที่ระบุ **ไม่มีอยู่จริง** ที่ path นั้น | ต้อง adopt จริงหรืออย่างน้อยระบุ absolute path ที่ถูกต้องแทนการอ้างแบบ relative ที่ผิด |
| 2 | §5 Applicability / plan-scope grammar (`allow_bash`) | รันจริงด้วย `plan_scope.sh`: **AC-2 ถูก deny** (grep entry ผิดไวยากรณ์ `*` อยู่กลางสตริง ไม่ใช่ตัวสุดท้ายตามกฎ `PLAN.template.md:45-46` เอง + cmd จริงมี `! grep -rnE` ไม่ตรง prefix อยู่ดี) · **AC-4 ถูก deny** (cmd ยังเป็น placeholder ดิบ `<db19>` ชน guard's redirection-block ก่อนถึง allow_bash เลย และไม่มี entry สำหรับ `odoo`) · Step 1's verify command (`python3 -c "import xml.etree..."`) ก็ไม่มี entry รองรับ | แก้ allow_bash entries ให้ตรงไวยากรณ์ + เติม `odoo -d * -i * --stop-after-init *` + เติมค่า `<db19>` จริงก่อนใช้ |
| 3 | §5 กฎข้อ 2 | สอดคล้องกับ C-1 — ถ้า mode ควรเป็น CROSS-MODULE/CONTRACT-TOUCHING แต่ plan-scope ยัง REFACTOR โดยไม่มีบรรทัดอธิบายเหตุผล = ผิดกฎข้อนี้ | เพิ่ม 1 บรรทัดอธิบาย หรือแก้ `mode:` |
| 4 | (เพื่อความสมดุล — ไม่ใช่ gap) | บล็อก plan-scope syntactically ถูกต้องครบตามกฎ 7 ข้อของ template (`--lint` ผ่าน จริง) | ไม่ต้องแก้ — ปัญหาใน D-2 เป็นระดับ semantic ไม่ใช่ syntax |

**หลักฐานรันจริง (reproducible):**
```
$ sh /home/kitcharoenp/respo/dev-playbook/scripts/plan_scope.sh --run-acs docs/migration/odoo19_plan.md
AC-1   | exit | 0 | exit 0 | ok
AC-2   | exit | 0 | exit 1 | FAIL   (คาดว่า fail อยู่แล้วก่อน migrate — ใช้ตรวจ mechanics เท่านั้น)

$ sh .../plan_scope.sh --check-cmd docs/migration/odoo19_plan.md "! grep -rnE '...' x_report_timesheet_perdiem ..."
deny  segment "! grep -rnE '@api\.(multi" ไม่อยู่ใน allow_bash

$ sh .../plan_scope.sh --check-cmd docs/migration/odoo19_plan.md "odoo -d <db19> -i x_account_withholding_tax_document,... --stop-after-init --log-level=error"
deny  พบ redirection (> หรือ >>) ที่ไม่ใช่ fd-dup N>&M

$ sh .../plan_scope.sh --check-cmd docs/migration/odoo19_plan.md "git status --porcelain"
allow git status --porcelain   ← control: guard ทำงานถูกต้อง ไม่ใช่ artifact การทดสอบ
```

---

## E. คำถามที่ต้องส่งต่อให้เจ้าของ

1. ทราบหรือไม่ว่า repo นี้ไม่เคย adopt dev-playbook จริง (ไม่มี `.claude/settings.json`/`docs/playbook/PLAYBOOK.md`) — ต้องการ set up ให้ guard บังคับจริง หรือใช้ dev-playbook เป็นแค่แนวทางอ้างอิงโดยไม่มี technical enforcement?
2. Mode ควรเป็น REFACTOR ตามที่ `plan-scope.mode` ประกาศ หรือควรยกเป็น CROSS-MODULE/CONTRACT-TOUCHING ตามที่ prose ของแผนเองยอมรับเงื่อนไข?
3. ต้องแก้ `allow_bash` (grep entry ผิดไวยากรณ์, ไม่มี `odoo` entry) และเติมค่า `<db19>` จริงใน AC-4 ก่อนให้ agent เริ่มงานไหม?
4. ทราบหรือยังว่า `hr.expense.sheet` เพิ่งถูก merge เข้า `hr.expense` ใน v19 เอง (ไม่ใช่ v16 ตามที่ E-1 อ้าง) และ state selection มี 7 ค่าไม่ใช่ 5 — ต้องการ re-scope Step 2 (owner decision gate) ใหม่ไหม?
5. มี Odoo 10 instance จริงสำหรับเก็บ characterization baseline (Step 0) หรือไม่ — ควรเพิ่มเข้าตาราง "สิ่งที่ต้องขอจากเจ้าของ"?
6. ต้องการให้แก้ `<report id=.../>` เป็น `<record model="ir.actions.report">` เป็นงานเพิ่มใน Step 1/3/4 ไหม — เป็นบั๊กที่ AC-4 จับไม่ได้เอง

---

## F. สรุป verdict

- **สถานะรวม: ต้องแก้ก่อนใช้** — โครงสร้างเอกสารตาม template ถูกต้อง (`--lint` ผ่าน), ตาราง G/E ส่วนใหญ่ตรงกับ Odoo 19 จริง (G-1, G-2, G-3, G-5, G-6, G-7, G-12, G-13, E-2, E-4 verify แล้วถูกต้อง) แต่มีข้อผิดพลาดเชิงข้อเท็จจริงที่กระทบ AC โดยตรง (โดยเฉพาะ E-1 เรื่อง hr.expense.sheet merge เวอร์ชัน) และช่องโหว่ที่ AC ปัจจุบันตรวจจับไม่ได้ (`<report>` tag, AC-2/AC-4 รันไม่ผ่าน guard ของแผนเอง) — ไม่ถึงขั้นต้องร่างใหม่ทั้งหมด

- **ความเสี่ยงที่ยังเหลือหลังอ่านจบ:**
  1. AC-2/AC-4 ตามที่เขียนไว้รันไม่ผ่าน guard ของ dev-playbook เอง (ยืนยันด้วยการรันจริง) — agent ที่ทำตามกฎเคร่งครัดจะติด PLAN AMENDMENT ตั้งแต่ Step 1
  2. `<report>` XML tag ถูก Odoo 19 เพิกเฉยเงียบ ๆ (ไม่ error) — report ไม่ถูกสร้างเลย แต่ AC-4 จะผ่าน
  3. `x_report_timesheet_perdiem` hard-depends บน `x_hr_timesheet_sheet` (นอกขอบเขต, ยัง Odoo 10) — AC-4 มีโอกาส fail ตั้งแต่ dependency resolution รุนแรงกว่าที่ R-1 อธิบาย
  4. E-1 อ้างเวอร์ชันผิดสำหรับจุดเสี่ยงที่สุดของงานทั้งหมด (hr.expense state mapping) — เพิ่งเปลี่ยนใน v19 เอง ไม่ใช่ของเก่าที่นิ่งแล้ว
  5. dev-playbook ไม่ได้ adopt จริงใน repo นี้ — governance ทั้งหมดที่แผน/prompt อ้างอิงเป็น advisory text ไม่มี technical backstop

- **สิ่งที่ไม่สามารถยืนยันได้จากเครื่องนี้:**
  1. AC-4/AC-5 ทั้งหมด — ไม่มี Odoo 19 instance ในเครื่องนี้
  2. ผลกระทบจริง 100% ของ `<report>` tag ที่ถูก drop — ยืนยันจาก source ของ `convert.py` เท่านั้น ไม่ได้รัน `-i` จริง
  3. OCA l10n-thailand/hr-expense "พร้อมใช้งานจริงแค่ไหน" ต้องอ่าน PR ที่ยัง open ทีละใบ — ข้อมูลเป็น snapshot ณ วันที่ตรวจ (2026-09-22) เท่านั้น
