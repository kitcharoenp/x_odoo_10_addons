#!/bin/sh
# plan_scope.sh — บังคับ scope ของแผนที่อนุมัติแล้ว (PLAN.template.md บล็อก `plan-scope`)
#
# แผนที่เป็น prose บังคับไม่ได้ · สคริปต์นี้อ่านบล็อก ```yaml plan-scope ในไฟล์แผน
# แล้วตอบคำถามเดียวกันซ้ำ ๆ ให้เครื่องมือ (hook) และคนใช้:
#   --lint <plan>                 ไวยากรณ์ถูกไหม · กฎบังคับครบไหม
#   --check-path <plan> <path>    เขียนไฟล์นี้ได้ไหม
#   --check-cmd  <plan> <cmd>     รันคำสั่งนี้ได้ไหม
#   --go-ahead   <plan>           แผนนี้ได้รับ go-ahead จริงหรือยัง
#   --verify-diff <plan> [range]  สิ่งที่ทำไปแล้ว อยู่ในแผนครบไหม (รวมไฟล์ untracked)
#   --run-acs    <plan>           รัน acceptance_criteria ทุกข้อแล้วสรุปเป็นตาราง
#
# POSIX sh โดยเจตนา (base §0 กฎ portability ข้อ 3 — ห้ามพึ่ง yq/jq ที่ไม่มีทุกเครื่อง)
#
# ข้อจำกัดที่ยอมรับไว้อย่างรู้ตัว (ห้ามเคลมว่าปิดครบ):
#   - เป็น guardrail ไม่ใช่ security boundary — คนที่ตั้งใจเลี่ยงย่อมเลี่ยงได้
#   - `--check-cmd` เทียบ prefix ของ command string: เลี่ยงได้ด้วย wrapper script หรือเปลี่ยน cwd
#     ครอบแล้ว: redirection (> >> tee dd) · chaining (&& || ; | ` $( )
#     ยังไม่ครอบ: sed -i · python3 -c ที่เปิดไฟล์เขียน · editor ใน terminal · script ที่เขียนแล้วเรียก
#   - glob รองรับแค่ 2 รูป: `<dir>/**` (ครอบทุกชั้นใต้ dir) และ `*` ที่ **ไม่ข้าม** `/`
#   - ค่าที่มี `#` อยู่ข้างในและไม่ได้ใส่ quote จะถูกตัดเป็น comment
#   - escape ของ YAML รองรับ `\\` → `\` และ `\"` → `"` เท่านั้น (ใช้ตอนแยกค่าทุก field ใน
#     acceptance_criteria) · escape อื่น (เช่น \n \t) ไม่ unescape — เก็บ backslash+ตัวอักษรไว้ตามที่เขียน
#   - path ที่มี newline ในชื่อไม่รองรับ (`--verify-diff`)
#   - `--run-acs` **รันคำสั่งจากไฟล์แผน** ⇒ ไฟล์แผนต้องถูก review อย่างโค้ด ไม่ใช่อย่างเอกสาร
#
# exit 0 = ผ่าน/allow · exit 1 = ไม่ผ่าน/deny · exit 2 = เรียกใช้ผิด/หาไฟล์ไม่เจอ

# -f (noglob) จำเป็น ไม่ใช่ความสะอาด: entry ในแผนเป็น glob เช่น `skills/*.sh`
# ถ้าเปิด pathname expansion ไว้ `for pat in $(list_of ...)` จะขยาย pattern เป็น
# "ชื่อไฟล์ที่มีอยู่จริงบนดิสก์ตอนนั้น" ก่อนเทียบ ⇒ deny_write หลุดเป็น fail-open
set -uf

# 3 path ที่ deny_write ต้องครอบเสมอเมื่อ require_go_ahead: true
# (ทั้งสามคือช่องที่ agent จะแก้กฎของตัวเองกลางเซสชัน)
REQUIRED_DENY='docs/playbook/ACTIVE_PLAN .claude/settings.json .claude/skills/**'

KNOWN_KEYS='plan_id tier mode blast_radius allow_write deny_write allow_bash
acceptance_criteria require_go_ahead go_ahead evidence_path'

REQUIRED_KEYS='plan_id tier mode allow_write deny_write require_go_ahead go_ahead evidence_path'

usage() {
	cat >&2 <<'USAGE'
usage: plan_scope.sh <subcommand> <plan> [args]

  --lint        <plan>              ตรวจไวยากรณ์ + กฎบังคับของบล็อก plan-scope
  --check-path  <plan> <path>       0 = เขียนได้ · 1 = ถูกห้าม
  --check-cmd   <plan> <command>    0 = รันได้ · 1 = ถูกห้าม
  --go-ahead    <plan>              0 = อนุมัติแล้ว · 1 = ยังเป็น placeholder
  --verify-diff <plan> [range]      0 = ทุกไฟล์ที่เปลี่ยนอยู่ในแผน (default range: HEAD)
  --run-acs     <plan>              รัน acceptance_criteria ทุกข้อ

exit 0 = ผ่าน/allow · 1 = ไม่ผ่าน/deny · 2 = เรียกใช้ผิด
USAGE
	exit 2
}

# ---------- parser ----------

# พิมพ์เนื้อในบล็อก ```yaml plan-scope (บล็อกแรกเท่านั้น)
block() {
	awk '
		/^```yaml[ \t]+plan-scope[ \t]*$/ { inb=1; next }
		inb && /^```/ { exit }
		inb { print }
	' "$1" 2>/dev/null
}

# รายการใต้ key แบบ list (`  - item`) — ตัด comment ท้ายบรรทัด, ถอด quote
list_of() {
	block "$1" | awk -v k="$2" '
		$0 ~ "^" k ":[ \t]*$" { inl = 1; next }
		/^[^ \t#]/ { inl = 0 }
		inl {
			line = $0
			sub(/^[ \t]+/, "", line)
			if (line ~ /^#/) next
			if (line !~ /^- /) next
			sub(/^- /, "", line)
			if (line ~ /^"/) { sub(/^"/, "", line); sub(/".*$/, "", line) }
			else { sub(/[ \t]+#.*$/, "", line); sub(/[ \t]+$/, "", line) }
			if (line != "") print line
		}
	'
}

# ค่าของ key แบบ scalar (`key: value`) — ระดับบนสุดเท่านั้น
scalar_of() {
	block "$1" | awk -v k="$2" '
		$0 ~ "^" k ":" {
			v = $0
			sub("^" k ":[ \t]*", "", v)
			if (v ~ /^"/) { sub(/^"/, "", v); sub(/".*$/, "", v) }
			else { sub(/[ \t]+#.*$/, "", v); sub(/[ \t]+$/, "", v) }
			print v
			exit
		}
	'
}

# มีบล็อกจริงไหม (fail closed: ไม่มี = deny ทุกอย่าง)
has_block() {
	[ -f "$1" ] || return 1
	[ -n "$(block "$1")" ]
}

# คืน 1 ถ้าพบ key ที่ไม่รู้จัก (fail closed ตามกฎข้อ 4) · พิมพ์ชื่อ key ที่ผิด
bad_keys() {
	block "$1" | awk -v known="$KNOWN_KEYS" '
		BEGIN { n = split(known, a, /[ \t\n]+/); for (i = 1; i <= n; i++) if (a[i] != "") ok[a[i]] = 1 }
		/^[ \t]/ { next }
		/^[ \t]*#/ { next }
		/^[A-Za-z_][A-Za-z0-9_]*:/ {
			k = $0; sub(/:.*$/, "", k)
			if (!(k in ok)) print k
		}
	'
}

# ---------- glob ----------

slashes() { printf '%s' "$1" | tr -cd '/' | wc -c | tr -d ' '; }

# path_match <pattern> <path> — 0 ถ้าตรง
# รองรับ 2 รูปเท่านั้น (ประกาศไว้ที่หัวไฟล์):
#   "<dir>/**" = ทุกชั้นใต้ dir · "*" = ไม่ข้าม `/` (บังคับด้วยการเทียบจำนวน `/`)
path_match() {
	pm_pat="$1"
	pm_p="$2"
	case "$pm_pat" in
	*/'**')
		pm_pref=${pm_pat%/'**'}
		[ "$pm_p" = "$pm_pref" ] && return 0
		case "$pm_p" in "$pm_pref"/*) return 0 ;; esac
		return 1
		;;
	*'*'*)
		# shellcheck disable=SC2254 # ตั้งใจให้ $pm_pat ทำงานเป็น glob
		case "$pm_p" in
		$pm_pat)
			[ "$(slashes "$pm_p")" -eq "$(slashes "$pm_pat")" ] && return 0
			;;
		esac
		return 1
		;;
	*)
		[ "$pm_p" = "$pm_pat" ] && return 0
		case "$pm_p" in "$pm_pat"/*) return 0 ;; esac
		return 1
		;;
	esac
}

# match_list <plan> <key> <path> — 0 ถ้า path ตรงกับ entry ใดใน list
match_list() {
	ml_hit=1
	for ml_pat in $(list_of "$1" "$2"); do
		if path_match "$ml_pat" "$3"; then
			ml_hit=0
			MATCHED_PATTERN="$ml_pat"
			break
		fi
	done
	return $ml_hit
}

# ---------- normalize path (PB-02) ----------
#
# รับได้ทั้ง absolute และ relative — **ยืนยันจากเอกสารทางการไม่ได้** ว่า tool_input.file_path
# เป็น absolute เสมอ จึงต้องถูกทั้งสองทาง ไม่ใช่พึ่งข้ออ้างนั้น
norm_path() {
	np_p="$1"
	case "$np_p" in
	'~') np_p="$HOME" ;;
	'~'/*) np_p="$HOME/${np_p#'~'/}" ;;
	esac
	np_p=$(printf '%s' "$np_p" | tr '\\' '/' | sed 's://*:/:g; s:/\./:/:g')
	while :; do
		case "$np_p" in
		./*) np_p=${np_p#./} ;;
		*) break ;;
		esac
	done
	np_cwd=${PLAN_SCOPE_CWD:-$(pwd)}
	np_cwd=$(printf '%s' "$np_cwd" | sed 's:/*$::')
	case "$np_p" in
	"$np_cwd") np_p="." ;;
	"$np_cwd"/*) np_p=${np_p#"$np_cwd"/} ;;
	esac
	printf '%s' "$np_p"
}

# ---------- subcommand: --lint ----------

cmd_lint() {
	lint_fail=0
	if ! has_block "$1"; then
		printf 'FAIL  ไม่พบบล็อก ```yaml plan-scope ใน %s — fail closed: ถือว่า deny ทุกอย่าง\n' "$1"
		return 1
	fi

	bk=$(bad_keys "$1")
	if [ -n "$bk" ]; then
		printf 'FAIL  พบ key ที่ไม่รู้จัก (fail closed — กฎข้อ 4): %s\n' "$(printf '%s' "$bk" | tr '\n' ' ')"
		lint_fail=1
	fi

	for k in $REQUIRED_KEYS; do
		if ! block "$1" | grep -q "^$k:"; then
			printf 'FAIL  ขาด key ที่บังคับ: %s\n' "$k"
			lint_fail=1
		fi
	done

	tier=$(scalar_of "$1" tier)
	case "$tier" in
	0 | 1 | 2 | 3 | 4) : ;;
	*)
		printf 'FAIL  tier ต้องเป็น 0–4 (ได้: %s)\n' "$tier"
		lint_fail=1
		;;
	esac

	rga=$(scalar_of "$1" require_go_ahead)
	case "$rga" in
	true | false) : ;;
	*)
		printf 'FAIL  require_go_ahead ต้องเป็น true หรือ false (ได้: %s)\n' "$rga"
		lint_fail=1
		;;
	esac

	# กฎข้อ 7 — ตัวตรวจของคำว่า "อยู่ใน deny_write เสมอ"
	if [ "$rga" = "true" ]; then
		for need in $REQUIRED_DENY; do
			found=1
			for pat in $(list_of "$1" deny_write); do
				[ "$pat" = "$need" ] && found=0 && break
			done
			if [ $found -ne 0 ]; then
				printf 'FAIL  require_go_ahead: true แต่ deny_write ไม่ครอบ %s (กฎข้อ 7)\n' "$need"
				lint_fail=1
			fi
		done
	fi

	# กฎข้อ 6 — note ไม่ fail (เป็น "ควร" ไม่ใช่ "ห้าม")
	# ข้อจำกัด: จับได้แค่ path ที่สะกดตรงกัน จับไม่ได้ถ้าแผนบรรยายเป็นคำ
	blk_start=$(grep -n '^```yaml[ \t]*plan-scope' "$1" | head -1 | cut -d: -f1)
	if [ -n "${blk_start:-}" ]; then
		blk_len=$(block "$1" | wc -l | tr -d ' ')
		blk_end=$((blk_start + blk_len + 1))
		for pat in $(list_of "$1" allow_write; list_of "$1" deny_write); do
			lit=${pat%/'**'}
			lit=${lit%'*'}
			case "$lit" in '' | '.' | './') continue ;; esac
			hits=$(grep -n -F -- "$lit" "$1" 2>/dev/null |
				awk -F: -v s="$blk_start" -v e="$blk_end" '$1 < s || $1 > e' | wc -l | tr -d ' ')
			if [ "${hits:-0}" -gt 0 ]; then
				printf 'note  path "%s" ปรากฏนอกบล็อก plan-scope %s จุด — ควรอ้างบล็อกแทนการเขียนซ้ำ (กฎข้อ 6)\n' "$lit" "$hits"
			fi
		done
	fi

	[ $lint_fail -eq 0 ] && printf 'ok    บล็อก plan-scope ของ %s ผ่านทุกกฎ\n' "$1"
	return $lint_fail
}

# ---------- subcommand: --check-path ----------

cmd_check_path() {
	if ! has_block "$1"; then
		printf 'deny  ไม่พบบล็อก plan-scope ใน %s — fail closed\n' "$1"
		return 1
	fi
	if [ -n "$(bad_keys "$1")" ]; then
		printf 'deny  บล็อก plan-scope มี key ที่ไม่รู้จัก — fail closed (กฎข้อ 4)\n'
		return 1
	fi

	p=$(norm_path "$2")
	case "$p" in
	/*)
		printf 'deny  %s อยู่นอก repo (normalize แล้วยังเป็น absolute)\n' "$p"
		return 1
		;;
	esac

	MATCHED_PATTERN=''
	if match_list "$1" deny_write "$p"; then
		printf 'deny  %s ตรงกับ deny_write: %s\n' "$p" "$MATCHED_PATTERN"
		return 1
	fi
	if match_list "$1" allow_write "$p"; then
		printf 'allow %s (allow_write: %s)\n' "$p" "$MATCHED_PATTERN"
		return 0
	fi
	printf 'deny  %s ไม่อยู่ใน allow_write — กล่องปิด: สิ่งที่ไม่อนุญาตคือสิ่งที่ห้าม (กฎข้อ 3)\n' "$p"
	return 1
}

# ---------- subcommand: --check-cmd ----------

# แยก command เป็น segment ที่ตัวคั่น && || ; | ` $( )
seg_split() {
	printf '%s' "$1" | awk '{
		gsub(/&&/, "\n"); gsub(/\|\|/, "\n"); gsub(/;/, "\n")
		gsub(/\|/, "\n"); gsub(/`/, "\n"); gsub(/\$\(/, "\n"); gsub(/\)/, "\n")
		print
	}'
}

trim() { printf '%s' "$1" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'; }

# ---------- P3: mask ค่าของ -m/-F/--message/--file ก่อนตรวจ metacharacter ----------
#
# ปัญหาเดิม (ROADMAP.md P3): เช็ค `*'>'*` และ seg_split() สแกน/ตัดทั้งคำสั่งดิบโดยไม่สนใจ
# เครื่องหมายคำพูด ⇒ `git commit -m` ที่มี `>` (blockquote ในข้อความไทย) วงเล็บ trailer
# `Co-Authored-By: … <email>` หรือ heredoc (`git commit -m "$(cat <<'EOF' ... EOF)"` —
# รูปแบบที่ Claude Code ใช้เป็นมาตรฐาน) ถูกบล็อกทุกกรณี แม้ `git commit *` อยู่ใน allow_bash แล้ว
#
# ทางแก้ที่เลือก (ตัวเลือก (ก) ใน ROADMAP — "ยกเว้นการตรวจ metacharacter ในอาร์กิวเมนต์ที่
# ตามหลัง -m/-F") **ไม่ใช่การผ่อนตัวตรวจทั้งชุด** ตามที่ ROADMAP เตือนไว้ห้าม: มาสก์เฉพาะ span
# ที่พิสูจน์ได้ด้วยกฎ POSIX ล้วนว่าเป็น quoted value จริงของ 4 flag นี้เท่านั้น — ถ้าพิสูจน์ไม่ได้
# (unterminated / ไม่ตรงรูป / มี expansion) **ไม่มาสก์อะไรเลย** ปล่อยให้ตัวตรวจเดิม (บล็อกกว้าง)
# ทำงานเหมือนเดิม ⇒ ทิศทางความผิดพลาดมีทางเดียวคือ over-block ไม่ใช่ under-block
#
# 3 รูปที่รองรับ (นอกนี้ = ไม่มาสก์):
#   1. `-m '...'`   — single-quote: ปิดที่ `'` ตัวแรกเสมอ (POSIX ไม่มี escape ในนี้ ไม่กำกวม)
#   2. `-m "..."`   — double-quote ที่ **ไม่มี `$(` และไม่มี backtick** อยู่ข้างใน
#   3. `-m "$(cat <<'DELIM'` … บรรทัด `DELIM` … `)"` — heredoc ที่ delimiter ถูก single-quote
#
# 6 กติกาที่ทำให้ทิศทางความผิดพลาดเป็น over-block จริง — ทุกข้อคือช่อง fail-open ที่ **พิสูจน์แล้ว
# ว่าเปิดจริง** ในฉบับร่างแรกของ P3 (ห้ามลดข้อใดข้อหนึ่งโดยไม่มี test ใหม่มายืนยัน):
#   1. ห้ามตั้งชื่อตัวแปร awk ว่า `close` — เป็นชื่อ built-in function ⇒ mawk/busybox awk
#      syntax error **ทั้งโปรแกรม** ⇒ ฟังก์ชันนี้พิมพ์ค่าว่าง ⇒ `c_scan` ว่าง ⇒ ลูป validate
#      ไม่มี segment ให้ตรวจเลย ⇒ **allow ทุกคำสั่งรวม `rm -rf /`** · ร่างแรกเป็นจริงข้อนี้บน
#      Ubuntu (awk = mawk) แต่ผ่านบนเครื่องที่ awk = gawk ⇒ ต้องรัน test บนอย่างน้อย 2 awk
#   2. ห้าม `tr '\n' ' '` — newline เป็นตัวคั่นคำสั่งของ shell และ seg_split() แยก segment
#      ตามบรรทัด · ร่างแรกยุบ newline ทำให้ `git status<newline>rm -rf /` เหลือ segment เดียว
#      ที่ขึ้นต้นด้วย `git status ` ⇒ allow · ที่นี่จึงต่อทุกบรรทัดเป็น buffer เดียวใน END
#      โดย **คง newline ไว้ทุกตัว** แล้วมาสก์เฉพาะข้างใน span (newline ที่หายไปอยู่ใน quote เท่านั้น)
#   3. `"..."` ที่มี `$(` หรือ backtick = ไม่มาสก์ — double-quote ยัง expand จริง · ร่างแรกมาสก์
#      `git commit -m "$(curl … | sh)"` เป็น MSGVALUE ⇒ allow ทั้งที่คำสั่งนั้นรันจริง
#   4. เดินสแกนซ้าย→ขวาแบบรู้สถานะ quote (lexer ย่อ) — มาสก์ได้เฉพาะเมื่ออยู่ **นอก** quote
#      ร่างแรกเช็คแค่ "ตัวหน้าเป็น space" ⇒ `grep 'a -m "b' > FILE 'c "d'` เริ่มมาสก์จาก `"`
#      ที่อยู่ใน single-quote แล้วกลืน `> FILE` หายไปด้วย ⇒ allow ทั้งที่ redirection จริง
#   5. quote ที่ไม่ปิด = parse ไม่ได้ ⇒ คืนสตริงเดิมทั้งก้อน ไม่มาสก์อะไรเลย
#   6. span ที่มาสก์ต้องจบเป็น "คำ" (ตัวถัดไปเป็น whitespace หรือจบสตริง) — กันกรณีที่ปลาย
#      quote ที่หาได้ไปโผล่กลางคำอื่น
#
# heredoc (รูปที่ 3) ปลอดภัยเพราะ 3 เงื่อนไขพร้อมกัน — ห้ามลดข้อใดข้อหนึ่ง:
#   ก. delimiter ต้องถูก single-quote (`<<'DELIM'`) ⇒ shell จริงไม่ expand `$`/backtick ใน body
#      เลย · `<<DELIM`/`<<"DELIM"` ยัง expand ได้ ⇒ ไม่รองรับ ปล่อยให้ deny ต่อไป
#   ข. หลัง `<<'DELIM'` ต้องขึ้นบรรทัดใหม่ทันที และบรรทัดปิดต้องเป็น `DELIM` ล้วน (`<<-` อนุญาต
#      tab นำหน้า) — ตามกฎ heredoc จริง ไม่ใช่ "เจอคำนี้ที่ไหนก็ได้"
#   ค. หลังบรรทัดปิด ข้ามได้แต่ whitespace แล้วต้องเจอ `)"` ทันที — ถ้ามีอย่างอื่นคั่น (เช่นคำสั่ง
#      ที่แฝงมา) ให้ถือว่า parse ไม่ได้ ห้ามไปหา `)"` ที่ลึกกว่านั้น เพราะจะกลืนคำสั่งนั้นเป็น "ข้อมูล"
#
# ยังไม่ครอบ (over-block โดยเจตนา — เพิ่มได้ต่อเมื่อมี test คู่มาด้วย): `-am "…"` และ short flag
# แบบรวมตัวอื่น · `--message=…` · `-m"…"` (ไม่มี space) · ค่าที่ไม่ได้ใส่ quote · quoted string
# ของ flag อื่นทั้งหมด (คำสั่งอื่นยังถูกสแกนแบบเดิมทุกตัวอักษร)
mask_msg_args() {
	printf '%s' "$1" | awk '
		# ปิด single-quote: POSIX ไม่มี escape ข้างใน ⇒ ปิดที่ตัวแรกที่เจอเสมอ
		function q_single(s, p,   n, j) {
			n = length(s)
			for (j = p + 1; j <= n; j++) if (substr(s, j, 1) == "\047") return j
			return -1
		}
		# ปิด double-quote: `\` ทำให้ตัวถัดไปไม่นับ (ครอบ \" และ \\ ตามกฎ POSIX)
		function q_double(s, p,   n, j, cj) {
			n = length(s); j = p + 1
			while (j <= n) {
				cj = substr(s, j, 1)
				if (cj == "\\" && j < n) { j += 2; continue }
				if (cj == "\"") return j
				j++
			}
			return -1
		}
		# หาบรรทัดปิด heredoc แล้วบังคับว่าถัดไปต้องเป็น `)"` — คืน index ของ `"` ตัวปิด
		function hd_close(s, from, delim, dash,   n, pos, e, line, k) {
			n = length(s); pos = from
			while (pos <= n) {
				e = index(substr(s, pos), "\n")
				if (e == 0) return -1
				line = substr(s, pos, e - 1)
				if (dash) sub(/^\t+/, "", line)
				if (line == delim) {
					k = pos + e
					while (k <= n && substr(s, k, 1) ~ /[ \t\n]/) k++
					if (substr(s, k, 2) == ")\"") return k + 1
					return -1
				}
				pos = pos + e
			}
			return -1
		}
		# คืน index ของ quote ตัวปิดของ "ค่าของ flag" ที่ p (หรือ -1 ถ้าพิสูจน์ไม่ได้)
		function msg_close(s, p,   rest, rl, delim, dash, span, j) {
			if (substr(s, p, 1) == "\047") return q_single(s, p)
			rest = substr(s, p + 1)
			if (match(rest, /^\$\(cat[ \t]+<<-?\047[A-Za-z_][A-Za-z0-9_]*\047[ \t]*\n/)) {
				rl = RLENGTH
				delim = substr(rest, 1, rl)
				dash = (delim ~ /^\$\(cat[ \t]+<<-/) ? 1 : 0
				sub(/^\$\(cat[ \t]+<<-?\047/, "", delim)
				sub(/\047[ \t]*\n$/, "", delim)
				return hd_close(s, p + rl + 1, delim, dash)
			}
			j = q_double(s, p)
			if (j < 0) return -1
			span = substr(s, p, j - p + 1)
			if (span ~ /\$\(/ || index(span, "`") > 0) return -1
			return j
		}
		{ buf = (NR == 1) ? $0 : buf "\n" $0 }
		END {
			s = buf; n = length(s); out = ""; i = 1
			while (i <= n) {
				c = substr(s, i, 1)
				# `\` นอก quote = escape ตัวถัดไป — copy ทั้งคู่ กันเข้าใจผิดว่า \" เปิด quote
				if (c == "\\" && i < n) { out = out substr(s, i, 2); i += 2; continue }
				if (c == "\047" || c == "\"") {
					j = (c == "\047") ? q_single(s, i) : q_double(s, i)
					if (j < 0) { print s; exit }        # กติกา 5: ปิดไม่ครบ ⇒ ไม่มาสก์อะไรเลย
					out = out substr(s, i, j - i + 1)   # quote ที่ไม่ใช่ค่าของ 4 flag: copy ดิบ
					i = j + 1
					continue
				}
				# c == "-" ก่อน: กัน substr()+match() ต่อ 1 ตัวอักษรของคำสั่งยาว ๆ (O(n²))
				if (c == "-" && (i == 1 || substr(s, i - 1, 1) ~ /[ \t\n]/) &&
				    match(substr(s, i), /^(-m|-F|--message|--file)[ \t]+/)) {
					fl = RLENGTH                        # ต้องเก็บก่อน match() ครั้งถัดไปทับ
					vpos = i + fl
					vc = substr(s, vpos, 1)
					if (vc == "\047" || vc == "\"") {
						cpos = msg_close(s, vpos)
						nc = (cpos > 0 && cpos < n) ? substr(s, cpos + 1, 1) : ""
						if (cpos > 0 && (cpos == n || nc ~ /[ \t\n]/)) {
							out = out substr(s, i, fl) "MSGVALUE"
							i = cpos + 1
							continue
						}
					}
				}
				out = out c; i++
			}
			print out
		}
	'
}

cmd_check_cmd() {
	if ! has_block "$1"; then
		printf 'deny  ไม่พบบล็อก plan-scope ใน %s — fail closed\n' "$1"
		return 1
	fi
	c="$2"
	# c_scan = c หลัง mask ค่า -m/-F/--message/--file (ดูหมายเหตุยาวที่ mask_msg_args)
	# ใช้ c_scan สำหรับ "ตรวจโครงสร้าง" เท่านั้น (redirection/segment/allow_bash) —
	# $c ตัวจริง (ไม่ถูกแก้) ยังเป็นค่าที่ถูก log/return กลับไป
	c_scan=$(mask_msg_args "$c")

	# 1. ปฏิเสธก่อนดู allow_bash — redirection เขียนไฟล์ได้โดยไม่เรียก tool Write
	#    ⇒ plan_scope_guard ไม่มีโอกาสทำงานเลย (L-1b)
	#
	#    P7: `N>&M` (dup fd เช่น `2>&1`) ไม่ได้เขียนไฟล์ ⇒ มาสก์เฉพาะ pattern นี้
	#    *ก่อนตรวจด่านนี้เท่านั้น* (ตัวแปรเฉพาะที่จาก pipe ไม่ใช่ c_scan ที่ถูกแก้)
	#    c_scan / seg_split / การตรวจ allow_bash ยังใช้ค่าเดิมทุกตัวอักษร
	#
	#    ต้องมีตัวเลขทั้งสองข้างของ `>&` ⇒ ยังบล็อก `> F`, `>> F`, `>&2` (ไม่มี N),
	#    `&> F`, `echo 2> F` และ `cmd 2>&1 > F` (ยังเหลือ `> F` ดิบ) เหมือนเดิม
	#    ทิศทางความผิดพลาดเป็น over-block เท่านั้น (กติกาเดียวกับ P3)
	case "$(printf '%s' "$c_scan" | sed 's/[0-9][0-9]*>&[0-9][0-9]*/FDDUP/g')" in
	*'>'*)
		printf 'deny  พบ redirection (> หรือ >>) ที่ไม่ใช่ fd-dup N>&M — เขียนไฟล์ได้โดยข้าม guard ของ Write/Edit (L-1b)\n'
		return 1
		;;
	esac
	if seg_split "$c_scan" | while IFS= read -r seg; do
		seg=$(trim "$seg")
		case "$seg" in
		tee | dd | 'tee '* | 'dd '*)
			printf 'deny  segment "%s" เรียก tee/dd — เขียนไฟล์ได้โดยข้าม guard ของ Write/Edit (L-1b)\n' "$seg"
			exit 1
			;;
		esac
	done; then :; else return 1; fi

	# 2–4. แยก segment แล้ว validate ทุก segment (L-1)
	seg_split "$c_scan" | while IFS= read -r seg; do
		seg=$(trim "$seg")
		[ -z "$seg" ] && continue
		hit=1
		# entry ของ allow_bash มี space ในตัว ⇒ ห่อด้วย \001 กัน word splitting
		for pat in $(list_of "$1" allow_bash | tr ' ' '\001'); do
			pat=$(printf '%s' "$pat" | tr '\001' ' ')
			case "$pat" in
			*'*')
				pref=${pat%'*'}
				case "$pref" in
				*' ') : ;;
				*)
					continue
					;; # ไวยากรณ์บังคับ "<prefix> *" — entry ที่ไม่มี space ก่อน * ใช้ไม่ได้
				esac
				case "$seg" in "$pref"*) hit=0 ;; esac
				;;
			*)
				[ "$seg" = "$pat" ] && hit=0
				;;
			esac
			[ $hit -eq 0 ] && break
		done
		if [ $hit -ne 0 ]; then
			printf 'deny  segment "%s" ไม่อยู่ใน allow_bash\n' "$seg"
			exit 1
		fi
	done || return 1

	printf 'allow %s\n' "$c"
	return 0
}

# ---------- subcommand: --go-ahead ----------

cmd_go_ahead() {
	if ! has_block "$1"; then
		printf 'deny  ไม่พบบล็อก plan-scope ใน %s — fail closed\n' "$1"
		return 1
	fi
	g=$(scalar_of "$1" go_ahead)
	g=$(trim "$g")
	case "$g" in
	'')
		printf 'deny  go_ahead ว่าง — ยังไม่ได้รับอนุมัติ\n'
		return 1
		;;
	'<'*'>')
		printf 'deny  go_ahead ยังเป็น placeholder: %s\n' "$g"
		return 1
		;;
	esac
	printf 'ok    go_ahead: %s\n' "$g"
	return 0
}

# ---------- subcommand: --verify-diff ----------

# ไฟล์ที่เปลี่ยน = tracked (git diff) + untracked (git status) — git diff มองไม่เห็น
# ไฟล์ใหม่ที่ยังไม่ git add ⇒ ถ้าไม่รวม untracked เครื่องมือจะเขียวทั้งที่ทำเกินแผน (L-3)
changed_files() {
	cf_range="$1"
	git diff --name-only -z "$cf_range" 2>/dev/null | tr '\0' '\n'
	git status --porcelain -z 2>/dev/null | tr '\0' '\n' | sed -n 's/^?? //p' | while IFS= read -r u; do
		[ -z "$u" ] && continue
		case "$u" in
		*/) find "$u" -type f 2>/dev/null ;;
		*) printf '%s\n' "$u" ;;
		esac
	done
}

cmd_verify_diff() {
	if ! has_block "$1"; then
		printf 'FAIL  ไม่พบบล็อก plan-scope ใน %s — fail closed\n' "$1"
		return 1
	fi
	vd_range=${2:-HEAD}
	vd_bad=0
	tmp=$(mktemp) || return 2
	changed_files "$vd_range" | sort -u | grep -v '^$' >"$tmp"
	while IFS= read -r f; do
		[ -z "$f" ] && continue
		if match_list "$1" deny_write "$f"; then
			printf 'FAIL  %s อยู่ใน deny_write (%s) — ทำเกินแผน\n' "$f" "$MATCHED_PATTERN"
			vd_bad=1
		elif ! match_list "$1" allow_write "$f"; then
			printf 'FAIL  %s ไม่อยู่ใน allow_write — ทำเกินแผน\n' "$f"
			vd_bad=1
		fi
	done <"$tmp"
	n=$(wc -l <"$tmp" | tr -d ' ')
	rm -f "$tmp"
	if [ $vd_bad -eq 0 ]; then
		printf 'ok    ไฟล์ที่เปลี่ยน %s รายการ อยู่ในแผนทั้งหมด (range: %s รวม untracked)\n' "$n" "$vd_range"
	fi
	return $vd_bad
}

# ---------- subcommand: --run-acs ----------

ac_records() {
	block "$1" | awk '
		/^acceptance_criteria:[ \t]*$/ { ina = 1; next }
		/^[^ \t#]/ { if (ina) { flush(); ina = 0 } }
		ina {
			line = $0
			sub(/^[ \t]+/, "", line)
			if (line ~ /^#/) next
			if (line ~ /^- id:/) { flush(); sub(/^- id:[ \t]*/, "", line); id = strip(line); next }
			if (line ~ /^cmd:/)  { sub(/^cmd:[ \t]*/, "", line);  cmd = strip(line); next }
			if (line ~ /^expect_exit:/)   { sub(/^expect_exit:[ \t]*/, "", line);   kind = "exit";   want = strip(line); next }
			if (line ~ /^expect_stdout:/) { sub(/^expect_stdout:[ \t]*/, "", line); kind = "stdout"; want = strip(line); next }
		}
		END { flush() }
		function strip(s,   i, n, c, d, out) {
			if (s ~ /^"/) {
				sub(/^"/, "", s)
				n = length(s); out = ""
				for (i = 1; i <= n; i++) {
					c = substr(s, i, 1)
					if (c == "\\" && i < n) {
						d = substr(s, i + 1, 1)
						if (d == "\"" || d == "\\") { out = out d } else { out = out c d }
						i++
						continue
					}
					if (c == "\"") break
					out = out c
				}
				return out
			}
			sub(/[ \t]+#.*$/, "", s); sub(/[ \t]+$/, "", s)
			return s
		}
		function flush() {
			if (id != "") printf "%s\t%s\t%s\t%s\n", id, kind, want, cmd
			id = ""; cmd = ""; kind = ""; want = ""
		}
	'
}

cmd_run_acs() {
	if ! has_block "$1"; then
		printf 'FAIL  ไม่พบบล็อก plan-scope ใน %s — fail closed\n' "$1"
		return 1
	fi
	recs=$(ac_records "$1")
	if [ -z "$recs" ]; then
		printf 'FAIL  ไม่มี acceptance_criteria ในแผน — AC ที่ "ตรวจด้วยตา" ไม่นับเป็น AC\n'
		return 1
	fi
	printf '%-6s | %-8s | %-14s | %-14s | %s\n' "id" "kind" "expected" "actual" "ผล"
	printf -- '-------|----------|----------------|----------------|------\n'
	acs_bad=0
	tab=$(printf '\t')
	printf '%s\n' "$recs" | while IFS="$tab" read -r id kind want c; do
		out=$(sh -c "$c" 2>/dev/null)
		code=$?
		got=$(printf '%s' "$out" | tr -d '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
		if [ "$kind" = "stdout" ]; then
			[ "$got" = "$want" ] && res="ok" || res="FAIL"
			actual="$got"
		else
			[ "$code" = "$want" ] && res="ok" || res="FAIL"
			actual="exit $code"
		fi
		printf '%-6s | %-8s | %-14s | %-14s | %s\n' "$id" "$kind" "$want" "$actual" "$res"
		if [ "$res" = "FAIL" ]; then
			printf '       cmd: %s\n' "$c"
			exit 1
		fi
		:
	done || acs_bad=1
	return $acs_bad
}

# ---------- dispatch ----------

[ $# -ge 2 ] || usage
sub="$1"
plan="$2"
[ -f "$plan" ] || {
	printf 'plan_scope.sh: ไม่พบไฟล์แผน: %s\n' "$plan" >&2
	exit 2
}

case "$sub" in
--lint) cmd_lint "$plan" ;;
--check-path)
	[ $# -eq 3 ] || usage
	cmd_check_path "$plan" "$3"
	;;
--check-cmd)
	[ $# -eq 3 ] || usage
	cmd_check_cmd "$plan" "$3"
	;;
--go-ahead) cmd_go_ahead "$plan" ;;
--verify-diff) cmd_verify_diff "$plan" "${3:-HEAD}" ;;
--run-acs) cmd_run_acs "$plan" ;;
*) usage ;;
esac
