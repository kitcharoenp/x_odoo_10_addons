#!/bin/sh
# audit_playbook.sh — ตรวจ compliance ของระบบ playbook (BASE_PLAYBOOK.md §9.8)
#
# รวมคำสั่งตรวจที่กระจายอยู่ในเอกสารมาไว้ที่เดียว เพื่อให้ผล reproduce ได้และเลิกนับด้วยมือ
#   --upstream    รันใน repo แม่แบบ    : portability · แม่แบบครบชุด · R-ID ครบใน template · manifest
#   --downstream  รันในโปรเจกต์ที่ adopt : Adoption Status · base integrity · งบบรรทัด Layer 1 · marker
#
# POSIX sh โดยเจตนา (base §0 กฎ portability ข้อ 3 — ห้ามพึ่งเครื่องมือที่ไม่มีทุกเครื่อง)
#
# ข้อจำกัดที่ยอมรับไว้อย่างรู้ตัว (ห้ามเคลมว่า POSIX ล้วน):
#   - `grep -R` และ `grep --exclude-dir` ไม่ใช่ POSIX แต่มีใน GNU/BSD grep ทุกตัวที่ใช้งานจริง
#   - `sort -t. -k1,1n` ใช้เทียบ SemVer ซึ่งพอสำหรับเลขที่ไม่มี pre-release suffix เท่านั้น
#   - ตรวจ JSON ต้องมี python3 · ถ้าไม่มีจะรายงานเป็น note ไม่ใช่ผ่าน
#
# exit 0 = ผ่านทุกข้อ · exit 1 = มีข้อที่ไม่ผ่าน · exit 2 = เรียกใช้ผิด/หาไฟล์ไม่เจอ

set -u

FAIL=0
WARN=0
R_EXPECTED=14

pass() { printf '  ok    %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAIL=$((FAIL + 1)); }
note() { printf '  note  %s\n' "$1"; WARN=$((WARN + 1)); }
head_() { printf '\n== %s\n' "$1"; }

usage() {
	cat >&2 <<'USAGE'
usage: audit_playbook.sh --upstream | --downstream [--dir <path>] [--layer1 <path>]

  --upstream        รันใน repo แม่แบบ
  --downstream      รันในโปรเจกต์ที่ adopt
  --normative       รายงานคำบังคับ (ควร/ต้อง) ในหมวด §5/§7 — report-only ไม่มีผลต่อ exit code
  --plan <file>     ตรวจไวยากรณ์บล็อก plan-scope ของไฟล์แผน (เรียก scripts/plan_scope.sh --lint)
  --dir <path>      ไดเรกทอรีเป้าหมาย (default: cwd)
  --layer1 <path>   ระบุไฟล์ Layer 1 เองเมื่อ canonical ใช้ชื่อที่ค้นอัตโนมัติไม่พบ (base §9.1)
USAGE
	exit 2
}

# ---------- ตัวช่วย ----------

# นับบรรทัดที่ไม่ว่าง
nonblank() { grep -c '[^[:space:]]' "$1" 2>/dev/null || echo 0; }

# อ่านค่า frontmatter: $1 = key, $2 = ไฟล์
#
# RM-12: ถ้าบรรทัดแรกของไฟล์เป็น `---` ให้อ่านถึง `---` ที่ปิด (เพดาน 200 บรรทัด
# นับจากหลัง fence เปิด เพื่อกันไฟล์ที่ไม่ปิด fence) — เดิมอ่านแค่ 20 บรรทัดแรก
# ทำให้ key ที่อยู่ลึกกว่านั้นกลายเป็นค่าว่างโดยไม่มีเสียงเตือน
# ถ้าบรรทัดแรกไม่ใช่ `---` ให้ใช้หน้าต่าง 20 บรรทัดแรกแบบเดิมทุกตัวอักษร —
# จำเป็นกับไฟล์ที่ไม่มี frontmatter จริง (`---` ในเนื้อความคือ horizontal rule)
#
# ต้องตรงกับสำเนาใน scripts/doc_state.sh (มี assertion กัน drift ใน
# tests/doc_state_test.sh — เทียบเฉพาะ body ของฟังก์ชัน ไม่เทียบ comment)
fm() {
	if [ "$(sed -n '1p' "$2" 2>/dev/null | sed 's/[[:space:]]*$//')" = "---" ]; then
		fm_region=$(sed -n '2,201p' "$2" 2>/dev/null | sed '/^---[[:space:]]*$/,$d')
	else
		fm_region=$(sed -n '1,20p' "$2" 2>/dev/null)
	fi
	printf '%s\n' "$fm_region" |
		sed -n "s/^$1:[[:space:]]*\"\{0,1\}\([^\"]*\)\"\{0,1\}[[:space:]]*\$/\1/p" |
		sed -n 1p
}

sha_of() {
	if command -v sha256sum >/dev/null 2>&1; then
		sha256sum "$1" | cut -d' ' -f1
	elif command -v shasum >/dev/null 2>&1; then
		shasum -a 256 "$1" | cut -d' ' -f1
	else
		echo "NO_SHA_TOOL"
	fi
}

# เทียบเวอร์ชันแบบ SemVer: คืน 0 ถ้า $1 < $2 (V-02)
ver_lt() {
	[ "$1" = "$2" ] && return 1
	lo=$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | sed -n 1p)
	[ "$lo" = "$1" ]
}

# เวอร์ชันเก่าสุดที่มีใน manifest (V-02)
manifest_oldest() {
	grep -E '^[0-9]+\.[0-9]+\.[0-9]+[[:space:]]' "$1" 2>/dev/null |
		awk '{print $1}' | sort -t. -k1,1n -k2,2n -k3,3n | sed -n 1p
}

# ---------- ตรวจร่วม 2 โหมด ----------

# นับไฟล์ที่มี pattern (fixed-string) โดยจำกัดขอบเขตให้เหลือเฉพาะ "โค้ดของโปรเจกต์"
#
# W3-01: เดิมใช้ `grep -R … .` ซึ่งไล่ทุกไฟล์บนดิสก์ · วัดกับ downstream จริงได้
# 60,061 ไฟล์ / 4GB ทั้งที่ git track แค่ 344 ไฟล์ → 13 วินาทีต่อ pattern (4 pattern = ~53 วิ)
# ทำให้การรัน audit ซ้ำในคำสั่งเดียวชนกับ timeout · และมันผิดความหมายด้วย เพราะ data/
# กับ artifact ที่ไม่ได้ track ไม่ใช่ "โค้ดของโปรเจกต์" ที่ §6 พูดถึง
_count_marker_files() {
	pat="$1"
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		git ls-files -z 2>/dev/null |
			xargs -0 -r grep -lF -- "$pat" 2>/dev/null |
			grep -vE '^(docs|scripts|tests)/' | wc -l
	else
		grep -RlF --exclude-dir=.git --exclude-dir=docs \
			--exclude-dir=scripts --exclude-dir=tests -- "$pat" . 2>/dev/null | wc -l
	fi
}

check_marker_collision() {
	head_ "Marker collision (base §6) — ต้องไม่ปนชุด [DN-]/[DEC-] กับ [DECISION-]/[RATIONALE-]"
	# -F เพราะ [ เปิด bracket expression ของ regex · ตัด docs/scripts/tests เพราะเอกสารและ
	# ตัวตรวจมี marker ตัวอย่างอยู่ ถ้าไม่ตัดจะ false positive ตั้งแต่วันแรก
	gen=0
	uni=0
	for pat in '[DN-' '[DEC-'; do
		gen=$((gen + $(_count_marker_files "$pat")))
	done
	for pat in '[DECISION-' '[RATIONALE-'; do
		uni=$((uni + $(_count_marker_files "$pat")))
	done
	if [ "$gen" -gt 0 ] && [ "$uni" -gt 0 ]; then
		fail "พบทั้ง 2 ชุด marker ในโค้ด (generic=$gen ไฟล์, universal=$uni ไฟล์) — base §6 บังคับให้เลือกชุดเดียว"
	else
		pass "ไม่ปนชุด marker (generic=$gen ไฟล์, universal=$uni ไฟล์)"
	fi
	git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
		note "ไม่ใช่ git repo — marker check ไล่ทุกไฟล์บนดิสก์ อาจช้าถ้าโปรเจกต์มี data/artifact เยอะ"
}

check_layer1_budget() {
	f="$1"
	head_ "งบบรรทัด Layer 1 (base §1) — core <=30 · ช่องกับดัก <=6 (นับบรรทัดไม่ว่าง)"
	[ -f "$f" ] || {
		fail "ไม่พบไฟล์ Layer 1 ที่ $f — R1 เป็นระดับ 'ต้องมี' (base §9.0)"
		return
	}

	# V-05: detection ใช้ token ที่ไม่ผูกภาษา — ช่องกับดักคั่นด้วย
	#   <!-- trap-slot -->  ... <!-- /trap-slot -->
	# และคำกำกับเหตุผลอยู่ในบรรทัดที่มี <!-- trap-caption --> ซึ่ง **ไม่นับ** เข้างบ
	# (เดิม detect ด้วยคำไทย "กับดัก"/"ปกติ Layer 1" → Layer 1 ภาษาอื่นถูกนับเข้า core แล้ว false-fail
	#  และ caption ที่ base §1 บังคับให้มี ถูกนับเข้างบ ≤6 เอง ทำให้เหลือ bullet จริงได้แค่ 5)
	total=$(nonblank "$f")
	trap_n=$(awk '
		/<!-- *trap-slot *-->/ {f=1; next}
		/<!-- *\/trap-slot *-->/ {f=0; next}
		f && /<!-- *trap-caption *-->/ {next}
		f && NF {c++}
		END {print c+0}' "$f")
	# บรรทัดกำกับขอบเขต/caption ไม่นับเข้า total ด้วย เพื่อให้ core สะท้อนเนื้อจริง
	meta_n=$(grep -cE '<!-- */?trap-(slot|caption) *-->' "$f")
	core=$((total - trap_n - meta_n))

	[ "$core" -le 30 ] && pass "core = $core (<=30)" || fail "core = $core เกิน 30 — ย้ายเนื้อหาไป PLAYBOOK.md ไม่ใช่ขยายงบ"
	[ "$trap_n" -le 6 ] && pass "ช่องกับดัก = $trap_n (<=6, ไม่นับบรรทัด caption)" || fail "ช่องกับดัก = $trap_n เกิน 6"

	if [ "$trap_n" -gt 0 ]; then
		if grep -q '<!-- *trap-caption *-->' "$f"; then
			pass "ช่องกับดักมีคำกำกับเหตุผล (base §1 บังคับ)"
		else
			fail "ช่องกับดักมีเนื้อหาแต่ไม่มีบรรทัด <!-- trap-caption --> กำกับว่าทำไมจึงคุ้มที่จะกิน Layer 1 (base §1 บังคับ)"
		fi
	elif grep -q '<!-- *trap-slot *-->' "$f"; then
		note "มี trap-slot แต่ว่างเปล่า — ถ้าโปรเจกต์ไม่มีกับดัก ให้ลบทั้งช่องออก (base §1)"
	fi

	grep -q 'PLAYBOOK.md' "$f" && pass "มี pointer ไป PLAYBOOK.md" ||
		fail "ไม่มี pointer ไป PLAYBOOK.md (base §1 ข้อ 3)"
	grep -qiE 'commit|push|deploy|no-external-action' "$f" && pass "มีข้อห้าม commit/push/deploy" ||
		fail "ไม่มีข้อห้าม commit/push/deploy (base §1 ข้อ 4 / §5.11) — ถ้า Layer 1 เขียนภาษาอื่นและไม่ใช้คำอังกฤษเลย ให้กำกับบรรทัดนั้นด้วย <!-- no-external-action -->"
}

# ---------- โหมด normative (report-only — ไม่ fail ไม่ว่าผลเป็นอย่างไร) ----------
#
# ตอบ V-07: ให้มีตัวรายงานคำบังคับที่ reproduce ได้ แทนการรัน awk ด้วยมือทุกรอบ review
# **นี่คือรายงาน ไม่ใช่คำตัดสิน** — การจัดประเภทใช้ heuristic ที่ประกาศไว้ด้านล่าง
# ตัวสคริปต์ตัดสินความหมายของภาษาไม่ได้ (base §9.8 ตาราง "สิ่งที่สคริปต์ยังไม่ครอบ")

normative_report() {
	f="$1"
	printf '=== normative report (report-only · ไม่มีผลต่อ exit code) ===\n'
	printf 'ไฟล์: %s\n\n' "$f"

	cat <<'RULES'
heuristic ที่ใช้จัดประเภท (ประกาศไว้เพื่อให้เถียงได้ ไม่ใช่เพื่อให้เชื่อ):
  descriptive   = "ที่ควร…"            → เป็นคุณศัพท์ขยายนาม ไม่ได้สั่งผู้อ่าน
  descriptive   = อยู่ในประโยคเงื่อนไข "ถ้า…"  → บรรยายสภาพสมมติ
  advisory      = "ไม่ควร…"            → ข้อห้ามระดับแนะนำ (ยังเป็น normative)
  needs-review  = ที่เหลือทั้งหมด        → ต้องให้คนตัดสินว่าเจตนาเป็นบังคับหรือแนะนำ
RULES
	printf '\n'

	# นับ 2 หน่วยเสมอ เพราะการเทียบข้ามหน่วยเคยทำให้สรุปผิดมาแล้ว
	lines=$(grep -c 'ควร' "$f" 2>/dev/null || echo 0)
	occs=$(grep -o 'ควร' "$f" 2>/dev/null | wc -l | tr -d ' ')
	printf 'จำนวนรวมทั้งไฟล์: %s บรรทัดที่มีคำนี้ · %s ครั้งที่ปรากฏ (สองหน่วยนี้ไม่เท่ากันเป็นเรื่องปกติ)\n\n' \
		"$lines" "$occs"

	printf 'รายการในหมวดที่ระดับความบังคับสำคัญที่สุด (§5 gates และ §7 DoD):\n\n'
	printf '  %-6s %-7s %-4s %s\n' "section" "line" "occ" "การจัดประเภทตาม heuristic"
	awk '
		/^# [0-9]/ { sec = $0; sub(/^# /, "", sec); sub(/\..*/, "", sec) }
		/ควร/ {
			if (sec != "5" && sec != "7") next
			# เงื่อนไขต้องขึ้นต้นบรรทัด/รายการ เท่านั้น — ถ้าจับ "ถ้า" ที่ไหนก็ได้ในบรรทัดยาว
			# จะไปกลบ occurrence ที่เป็นคำแนะนำจริงในบรรทัดเดียวกัน (เจอที่ §5.11)
			cond = ($0 ~ /^-?[[:space:]]*ถ้า/)
			k = 0
			rest = $0
			while (match(rest, /ควร/)) {
				pre = substr(rest, 1, RSTART - 1)
				k++
				kind = "needs-review  (ต้องให้คนตัดสิน)"
				if (pre ~ /ที่$/)      kind = "descriptive   (คุณศัพท์ขยายนาม)"
				else if (pre ~ /ไม่$/) kind = "advisory      (ข้อห้ามระดับแนะนำ)"
				else if (cond)         kind = "descriptive   (ในประโยคเงื่อนไข)"
				printf "  §%-5s L%-6s #%-3s %s\n", sec, FNR, k, kind
				rest = substr(rest, RSTART + RLENGTH)
			}
		}
	' "$f"
	printf '\n(ไม่พิมพ์ข้อความรอบ ๆ คำ เพราะการตัดสตริงกลางตัวอักษรหลายไบต์ทำให้ตัวอักษรเพี้ยน\n'
	printf ' ให้เปิดเลขบรรทัดที่รายงานไว้แทน — occ = ตัวที่เท่าไรในบรรทัดนั้น)\n'

	printf '\nนอกหมวด §5/§7 ไม่ถูกลิสต์รายบรรทัดโดยเจตนา — เพื่อลด noise ตามที่รอบ review ร้องขอ\n'
	printf 'ถ้าต้องการทั้งไฟล์: grep -n "ควร" %s\n' "$f"
	note "normative report เป็น report-only — ข้อที่ยัง needs-review ต้องปิดในรอบ review ไม่ใช่ด้วยสคริปต์"
}

run_normative() {
	f=""
	for c in "$DIR/BASE_PLAYBOOK.md" "$DIR/docs/playbook/BASE_PLAYBOOK.md" \
		"$DIR/docs/playbook/PLAYBOOK.md" "$DIR/PLAYBOOK.md"; do
		[ -f "$c" ] && f="$c" && break
	done
	if [ -z "$f" ]; then
		printf 'ไม่พบ BASE_PLAYBOOK.md หรือ PLAYBOOK.md ใน %s\n' "$DIR" >&2
		exit 2
	fi
	normative_report "$f"
}

# ---------- โหมด upstream ----------

run_upstream() {
	printf '=== audit_playbook.sh --upstream (%s) ===\n' "$DIR"

	head_ "แม่แบบครบชุด (derive จาก git — ห้ามกลับไป list literal, W8 root cause)"
	# derive: git ls-files ใน upstream repo · fallback glob เมื่อไม่ใช่ git repo
	# (degrade เดียวกับ marker check L101–108) — ครอบคลุม template ทุกตัวที่ track
	# ไม่ใช่แค่ 8 ตัวเดิมที่คนต้องตาม maintain ด้วยมือ
	if git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		template_files=$(git -C "$DIR" ls-files -- '*.template.md' '*.template.json' \
			BASE_PLAYBOOK.md CHANGELOG.md MANIFEST.sha256)
	else
		# degrade: glob — ครอบคลุมทั้ง 8 ตัวเดิม + PLAN/PROMPT/RESPONSE template
		template_files=$( (cd "$DIR" && ls BASE_PLAYBOOK.md CHANGELOG.md MANIFEST.sha256 \
			*.template.md *.template.json 2>/dev/null) )
	fi
	for f in $template_files; do
		[ -f "$DIR/$f" ] && pass "$f" || fail "ขาด $f"
	done

	head_ "Portability (base §0 กฎ portability ข้อ 1) — base ต้องไม่รู้จักโปรเจกต์ใด"
	if [ -f "$DIR/.audit-portability-denylist" ]; then
		pat=$(tr '\n' '|' <"$DIR/.audit-portability-denylist" | sed 's/|$//')
		pf_hit=0
		for pf in "$DIR/BASE_PLAYBOOK.md" "$DIR/CHANGELOG.md"; do
			[ -f "$pf" ] || continue
			if [ -n "$pat" ] && grep -inE "$pat" "$pf" >/dev/null 2>&1; then
				fail "พบชื่อโปรเจกต์/โมดูลใน $(basename "$pf"):"
				grep -inE "$pat" "$pf" | sed 's/^/        /'
				pf_hit=1
			fi
		done
		[ "$pf_hit" -eq 0 ] && pass "ไม่พบชื่อโปรเจกต์/โมดูลใน BASE_PLAYBOOK.md/CHANGELOG.md (deny-list $(nonblank "$DIR/.audit-portability-denylist") รายการ)"
	else
		fail "ไม่มี .audit-portability-denylist ใน upstream — ไฟล์นี้ tracked ตั้งแต่ 2.15.1 (ตรวจซ้ำ: git log -- .audit-portability-denylist); subclass ยังข้ามได้เพราะบล็อกนี้อยู่ใน run_upstream() เท่านั้น (base §0)"
	fi

	head_ "CI suite coverage (W8) — suite ที่ commit ไว้ต้องถูกรันจริง ไม่ใช่ถูกลืม"
	# root cause เดียวกับที่ก่อ findings ทั้งรอบ: list สองฉบับที่คนดูแลด้วยมือ
	# (job ใน .gitlab-ci.yml หนึ่งฉบับ · ไฟล์ใน tests/ อีกฉบับ) — ห้ามกลับไป
	# enumerate ชื่อ suite ใน CI อีก ตัวตรวจนี้ derive จาก git ไม่ใช่ความจำ
	if ! git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		: # ไม่ใช่ git repo — ไม่รู้จะนับ suite ยังไง ข้ามเงียบ (degrade เดียวกับ marker check)
	elif [ ! -f "$DIR/.gitlab-ci.yml" ]; then
		note "ไม่มี .gitlab-ci.yml — ข้ามการตรวจว่า suite ถูกรันอัตโนมัติ"
	else
		# เทียบ "glob ที่ job test:suites ใช้ไล่ suite" (เขียนไว้ใน .gitlab-ci.yml) กับ glob ที่
		# ตัวตรวจนี้ตกลงไว้ — ถ้า CI กลับไป enumerate รายชื่อ suite ด้วยมือ หรือเปลี่ยน glob
		# โดยไม่อัปเดตตัวตรวจนี้ จะจับได้ที่นี่ ทุก branch reachable — ไม่นับสอง ways ซ้ำแล้วเทียบกันเอง
		if ! grep -qF 'for t in tests/*_test.sh tests/smoke_*.sh' "$DIR/.gitlab-ci.yml"; then
			fail ".gitlab-ci.yml ไม่มี discovery loop 'for t in tests/*_test.sh tests/smoke_*.sh' ของ job test:suites — กลับไป enumerate suite ด้วยมือ หรือเปลี่ยน glob โดยไม่อัปเดตตัวตรวจนี้"
		else
			suite_tracked=$(git -C "$DIR" ls-files 'tests/*_test.sh' 'tests/smoke_*.sh' | grep -c .)
			pass "CI discovery glob ครอบคลุม suite ที่ track อยู่ $suite_tracked ตัว"
			# suite บนดิสก์ที่ยังไม่ commit — loop ของ CI ไล่จากดิสก์จะรันมัน แต่จะไม่ถูกนับ
			# ใน expected ของ job ที่เทียบจำนวน; รายงานให้รู้ก่อน (ไม่ใช่ suite จริงก็ ignore note ได้)
			if [ -d "$DIR/tests" ]; then
				for t in "$DIR"/tests/*_test.sh "$DIR"/tests/smoke_*.sh; do
					[ -f "$t" ] || continue
					rel=${t#"$DIR/"}
					git -C "$DIR" ls-files --error-unmatch "$rel" >/dev/null 2>&1 ||
						note "$rel ยังไม่ถูก git track — ถ้าเป็น suite ให้ commit ก่อนอ้างอิง coverage"
				done
			fi
		fi
	fi

	head_ "R-ID ครบใน PLAYBOOK.template.md (base §9.0 — ต้องได้ $R_EXPECTED)"
	n1=$(grep -cE '^\| ?`?R[0-9]+' "$DIR/PLAYBOOK.template.md" 2>/dev/null || echo 0)
	n2=$(grep -cE '^\| ?`?R[0-9]+.*(present|missing)' "$DIR/PLAYBOOK.template.md" 2>/dev/null || echo 0)
	[ "$n1" -eq "$R_EXPECTED" ] && pass "R-ID rows = $n1" || fail "R-ID rows = $n1 (ต้อง $R_EXPECTED)"
	[ "$n2" -eq "$R_EXPECTED" ] && pass "rows ที่มีสถานะ = $n2" || fail "rows ที่มีสถานะ = $n2 (ต้อง $R_EXPECTED)"

	head_ "Layer 1 template — งบบรรทัดต้องผ่านหลังถอดกล่องแนะนำ/คอมเมนต์ออก"
	tmp=$(mktemp) || {
		fail "mktemp ไม่สำเร็จ"
		return
	}
	# ถอดกล่องแนะนำ (blockquote) และคอมเมนต์แนะนำออก แต่ **ต้องคง token trap-* ไว้**
	# ไม่งั้น range ของ sed จะกินเลยไปลบหัวข้ออื่นด้วย (เจอจริงตอนแก้ V-05)
	# W2-01: ต้องใช้ /^>/ ไม่ใช่ /^> / เพราะบรรทัดคั่นในกล่องเป็น ">" เปล่าไม่มีเว้นวรรคตาม
	#        ถ้าใช้ /^> / บรรทัดพวกนั้นจะถูกนับเป็น core ทำให้ตัวเลขที่รายงานสูงกว่าความจริง
	awk '
		/^>/ {next}
		/trap-slot|trap-caption/ {print; next}
		/^<!--/ {inc=1}
		inc { if (/-->/) inc=0; next }
		{print}' "$DIR/AGENTS.template.md" >"$tmp"
	check_layer1_budget "$tmp"
	rm -f "$tmp"

	head_ "settings.template.json — ต้องเป็น JSON ที่ valid และแยก ask ออกจาก deny (base §5.11)"
	if command -v python3 >/dev/null 2>&1; then
		if python3 -m json.tool "$DIR/settings.template.json" >/dev/null 2>&1; then
			pass "JSON valid"
		else
			fail "JSON ไม่ valid"
		fi
	else
		note "ไม่มี python3 — ข้ามการตรวจ JSON syntax"
	fi
	grep -q '"ask"' "$DIR/settings.template.json" && pass "มีหมวด ask (ของที่ทำได้เมื่อถูกสั่ง)" ||
		fail "ไม่มีหมวด ask — base §5.11 ห้ามบล็อกถาวรของที่ทำได้เมื่อถูกสั่ง"
	grep -q 'Read(' "$DIR/settings.template.json" && pass "มี deny rule สำหรับอ่านไฟล์ secret (base §5.12)" ||
		fail "ไม่มี deny rule ของ Read() — deny-list §5.12 จะเป็นเพียงการประกาศ"

	head_ "MANIFEST — ต้องมี checksum ของทุกเวอร์ชันที่ปล่อยแล้ว (base §9.8)"
	mf="$DIR/MANIFEST.sha256"
	vers=$(grep -cE '^[0-9]+\.[0-9]+\.[0-9]+[[:space:]]' "$mf" 2>/dev/null || echo 0)
	[ "$vers" -ge 1 ] && pass "manifest มี $vers เวอร์ชัน" || fail "manifest ไม่มี entry ที่อ่านได้"
	cur=$(fm version "$DIR/BASE_PLAYBOOK.md")
	if [ -n "$cur" ]; then
		want=$(grep -E "^$(echo "$cur" | sed 's/\./\\./g')[[:space:]]" "$mf" 2>/dev/null | awk '{print $2}' | sed -n 1p)
		got=$(sha_of "$DIR/BASE_PLAYBOOK.md")
		if [ -z "$want" ]; then
			fail "manifest ไม่มี entry ของเวอร์ชันปัจจุบัน ($cur) — ต้องเพิ่มก่อนปล่อย"
		elif [ "$want" = "$got" ]; then
			pass "checksum ของ $cur ตรงกับ manifest"
		else
			fail "checksum ของ $cur ไม่ตรง manifest (manifest=$want file=$got)"
		fi
	else
		fail "อ่าน version จาก frontmatter ของ BASE_PLAYBOOK.md ไม่ได้"
	fi

	check_deny_symmetry
	check_skills_layer
}

# ---------- parity invariant (W10c · Phase 3 v2.19.0 · upgrade จาก smoke-only เป็น --upstream fail) ----------
# ทุก path ใน deny array ต้องมีทั้ง Write() และ Edit() ครบคู่ — Phase 2 lesson (smoke L405):
# grep/sed/awk parse JSON แบบ multiline ไม่รอด → false positive · ใช้ python3.json.match กับ
# pattern `^(Write|Edit)\((.+)\)$` เหมือน smoke parity_check · ตรวจเฉพาะ settings.template.json
# (shape ของ upstream template) — subclass config ไม่ถูกบังคับ cross-check เพราะ subclass
# อาจวาง template ที่ path อื่น
#
# TODO(plan §2 bug): code draft ในแผนใช้ `settings.template.json` แบบ relative → CWD ≠ $DIR
# ตอน invoke ด้วย --dir จาก tests/ → silent return 0 ทุกครั้ง · แก้ที่ source ให้ใช้ $DIR/...
# ตามแบบ run_upstream L337-350 (consistent path model)
check_deny_symmetry() {
	TPL="$DIR/settings.template.json"
	[ -f "$TPL" ] || return 0
	_out=$(python3 - "$TPL" <<'PY'
import json, re, sys
paths = {}
try:
    cfg = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
for rule in (cfg.get("permissions") or {}).get("deny") or []:
    m = re.match(r'^(Write|Edit)\((.+)\)$', rule)
    if not m: continue
    paths.setdefault(m.group(2), set()).add(m.group(1))
for path, tools in sorted(paths.items()):
    if tools != {"Write", "Edit"}:
        missing = "Write" if "Write" not in tools else "Edit"
        print(f"{path} (ขาด {missing}())")
PY
)
	if [ -n "$_out" ]; then
		fail "deny symmetry broken (v2.19.0 gate) — paths lacking Write↔Edit pair in settings.template.json: $(printf '%s' "$_out" | tr '\n' ';')"
	else
		pass "deny symmetry check (settings.template.json) — ทุก path ครบคู่ Write↔Edit"
	fi
}

# ---------- ชั้น Agent Skills (2.15.0) ----------

# SKILL.md เป็นเนื้อหาที่ถูกใช้เป็นคำสั่งโดยเจตนา ⇒ ต้องไม่กลายเป็นที่เก็บเกณฑ์ gate ชุดที่สอง
# ที่ drift จาก PLAYBOOK.md เมื่อ base bump (§5.10 single-source)
#
# ข้อจำกัดของ heuristic (ประกาศตรง ๆ ตาม §9.8 ห้ามเคลมเกินที่ตรวจได้):
#   จับได้เฉพาะ "ตัวเลข + หน่วย" และ "ตัวเปรียบเทียบ + ตัวเลข" ในไฟล์ SKILL.md
#   จับไม่ได้ถ้าเขียนเกณฑ์เป็นตัวหนังสือ · ไม่ fail กับการ *อ้างอิง* เลข gate ซึ่งเป็นสิ่งที่ต้องการ
#   ขอบเขตคือ SKILL.md เท่านั้น — สคริปต์ใน skills/ เป็นโค้ด เงื่อนไขอย่าง c>=2 ไม่ใช่ threshold ของ gate
check_skills_layer() {
	[ -d "$DIR/skills/shared" ] || return 0

	head_ "Agent Skills — เนื้อหา skill ต้องไม่คัดลอกเกณฑ์ gate (§5.10) และ registry ต้องตรงกับของจริง"

	sk_unit='[0-9]+[[:space:]]*(วัน|ชั่วโมง|นาที|รอบ|บรรทัด|ครั้ง|ไฟล์|จุด)'
	sk_cmp='(<=|>=|≤|≥)[[:space:]]*[0-9]+'
	sk_hits=$(find "$DIR/skills" -name 'SKILL.md' -type f -exec grep -nE "$sk_unit|$sk_cmp" {} + 2>/dev/null)
	if [ -z "$sk_hits" ]; then
		pass "ไม่พบเกณฑ์/threshold ที่ถูกคัดลอกมาไว้ใน SKILL.md"
	else
		fail "พบ threshold ใน SKILL.md — ต้องอ้าง gate ID แล้วชี้ไป PLAYBOOK.md แทน:"
		printf '%s\n' "$sk_hits" | sed 's/^/        /'
	fi

	reg="$DIR/skills/registry.yaml"
	if [ -f "$reg" ]; then
		n_dir=$(find "$DIR/skills/shared" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
		n_reg=$(sed -n 's/^[[:space:]]*-[[:space:]]*id:[[:space:]]*//p' "$reg" | grep -c '[^[:space:]]')
		if [ "$n_dir" -eq "$n_reg" ]; then
			pass "จำนวน skill ตรงกับ registry (ไดเรกทอรี $n_dir · entry $n_reg)"
		else
			fail "จำนวน skill ไม่ตรงกับ registry (ไดเรกทอรี $n_dir · entry $n_reg) — skill ที่ไม่มี entry จะถูกลืมเวลาติดตั้ง"
		fi
	else
		note "ไม่มี skills/registry.yaml — ข้ามการนับ skill"
	fi
}

# ---------- โหมด plan (2.15.0) ----------

# ตรวจไวยากรณ์บล็อก plan-scope ของแผน — เป็น wrapper บาง ๆ ของ plan_scope.sh --lint
# เพื่อให้ทุกการตรวจของระบบเรียกผ่านคำสั่งเดียวกันได้ ไม่ใช่จำสองคำสั่ง
run_plan() {
	printf '=== audit_playbook.sh --plan %s ===\n' "$PLAN_FILE"
	head_ "บล็อก plan-scope (PLAN.template.md)"

	ps="$DIR/scripts/plan_scope.sh"
	[ -f "$ps" ] || ps="$(dirname "$0")/plan_scope.sh"
	if [ ! -f "$ps" ]; then
		fail "ไม่พบ scripts/plan_scope.sh — ตรวจแผนไม่ได้ (ไม่ใช่ว่าแผนถูกต้อง)"
		return
	fi
	if [ ! -f "$PLAN_FILE" ]; then
		fail "ไม่พบไฟล์แผน: $PLAN_FILE"
		return
	fi
	if sh "$ps" --lint "$PLAN_FILE"; then
		pass "แผนผ่าน --lint"
	else
		fail "แผนไม่ผ่าน --lint (ดูรายละเอียดข้างบน)"
	fi
}

# ---------- โหมด downstream ----------

run_downstream() {
	printf '=== audit_playbook.sh --downstream (%s) ===\n' "$DIR"

	PB=""
	for c in "$DIR/docs/playbook/PLAYBOOK.md" "$DIR/PLAYBOOK.md"; do
		[ -f "$c" ] && PB="$c" && break
	done
	BASE=""
	for c in "$DIR/docs/playbook/BASE_PLAYBOOK.md" "$DIR/BASE_PLAYBOOK.md"; do
		[ -f "$c" ] && BASE="$c" && break
	done

	head_ "ไฟล์ที่จำเป็น"
	if [ -n "$PB" ]; then pass "PLAYBOOK.md ที่ $PB"; else
		fail "ไม่พบ PLAYBOOK.md — โปรเจกต์นี้ยังไม่ adopt (base §9)"
		printf '\nสรุป: FAIL=%s WARN=%s\n' "$((FAIL))" "$WARN"
		exit 1
	fi
	[ -n "$BASE" ] && pass "BASE_PLAYBOOK.md ที่ $BASE" || fail "ไม่พบ BASE_PLAYBOOK.md"

	head_ "Adoption Status (base §9 เกณฑ์ข้อ 2 — ต้องได้ $R_EXPECTED ทั้งสองค่า)"
	n1=$(grep -cE '^\| ?`?R[0-9]+' "$PB" 2>/dev/null || echo 0)
	n2=$(grep -cE '^\| ?`?R[0-9]+.*(present|missing)' "$PB" 2>/dev/null || echo 0)
	[ "$n1" -eq "$R_EXPECTED" ] && pass "R-ID rows = $n1" || fail "R-ID rows = $n1 (ต้อง $R_EXPECTED — มีแถวหาย)"
	[ "$n2" -eq "$R_EXPECTED" ] && pass "rows ที่มีสถานะ = $n2" || fail "rows ที่มีสถานะ = $n2 (ต้อง $R_EXPECTED — มีแถวไม่ได้กรอกสถานะ)"

	head_ "Frontmatter (R2) + invariant ของ §10"
	pv=$(fm base_version "$PB")
	lr=$(fm last_reviewed_base_version "$PB")
	st=$(fm playbook_status "$PB")
	[ -n "$pv" ] && pass "base_version = $pv" || fail "ไม่มี base_version ใน frontmatter (R2)"
	[ -n "$lr" ] && pass "last_reviewed_base_version = $lr" || fail "ไม่มี last_reviewed_base_version (R2)"
	[ -n "$st" ] && pass "playbook_status = $st" || fail "ไม่มี playbook_status"
	if [ -n "$pv" ] && [ -n "$lr" ]; then
		lo=$(printf '%s\n%s\n' "$pv" "$lr" | sort -t. -k1,1n -k2,2n -k3,3n | sed -n 1p)
		[ "$lo" = "$pv" ] && pass "invariant last_reviewed_base_version >= base_version" ||
			fail "invariant ผิด: last_reviewed_base_version ($lr) < base_version ($pv) — base §10"
	fi

	head_ "next_review (base §10 — เฟส note-only)"
	nr=$(fm next_review "$PB")
	if [ -z "$nr" ]; then
		note "ไม่มี next_review ใน frontmatter — ยังไม่ตรวจว่าเลยกำหนดหรือไม่"
	else
		today=$(date +%Y-%m-%d)
		lo=$(printf '%s\n%s\n' "$nr" "$today" | sort | sed -n 1p)
		if [ "$lo" = "$nr" ] && [ "$nr" != "$today" ]; then
			note "next_review ($nr) เลยวันนี้ ($today) แล้ว — ยังเป็น note ในเฟสนี้ (base §10) เวอร์ชันถัดไปอาจยกเป็น fail พร้อม compliance deadline"
		else
			pass "next_review ($nr) ยังไม่ถึงกำหนด"
		fi
	fi

	head_ "Base integrity (base §9.8) — สำเนา base ต้องตรงกับเวอร์ชันที่ pin ไว้"
	mf=""
	for c in "$DIR/docs/playbook/MANIFEST.sha256" "$DIR/MANIFEST.sha256" \
		"$(dirname "$0")/../MANIFEST.sha256"; do
		[ -f "$c" ] && mf="$c" && break
	done
	if [ -z "$mf" ]; then
		note "ไม่พบ MANIFEST.sha256 — ข้ามการตรวจ integrity (ก๊อปมาจากต้นทางพร้อม base)"
	elif [ -z "$BASE" ] || [ -z "$pv" ]; then
		fail "ตรวจ integrity ไม่ได้เพราะขาด BASE_PLAYBOOK.md หรือ base_version"
	else
		want=$(grep -E "^$(echo "$pv" | sed 's/\./\\./g')[[:space:]]" "$mf" | awk '{print $2}' | sed -n 1p)
		got=$(sha_of "$BASE")
		fmv=$(fm version "$BASE")
		oldest=$(manifest_oldest "$mf")
		if [ "$got" = "NO_SHA_TOOL" ]; then
			# V-12: ไม่มีเครื่องมือ hash = ตรวจไม่ได้ ไม่ใช่ "checksum ไม่ตรง"
			note "ไม่มี sha256sum/shasum บนเครื่องนี้ — ข้ามการตรวจ integrity (ไม่ใช่การผ่าน)"
		elif [ -z "$want" ] && [ -n "$oldest" ] && ver_lt "$pv" "$oldest"; then
			# V-02: pinned เก่ากว่าเวอร์ชันเก่าสุดใน manifest = pre-manifest era ไม่ใช่ความผิดของโปรเจกต์
			note "เวอร์ชันที่ pin ($pv) เก่ากว่าเวอร์ชันเก่าสุดใน manifest ($oldest) — pre-manifest era ตรวจ integrity ด้วย checksum ไม่ได้ · ยัง compliant ตาม base §10 ข้อ 3 · ตรวจด้วยมือ/grep แทน แล้วอัป pin ภายใน deadline"
		elif [ -z "$want" ]; then
			fail "manifest ไม่มี entry ของเวอร์ชันที่ pin ไว้ ($pv) ทั้งที่ไม่เก่ากว่าเวอร์ชันเก่าสุดใน manifest ($oldest) — manifest ไม่ครบ"
		elif [ "$want" = "$got" ]; then
			pass "BASE_PLAYBOOK.md ตรงกับ $pv ที่ pin ไว้ (ไม่ถูกแก้)"
		else
			fail "BASE_PLAYBOOK.md ไม่ตรงกับ $pv ที่ pin ไว้ — pin เลขผิด (ยังไม่อัป pin หลัง review) หรือ base ถูกแก้ในโปรเจกต์ (ขัด base §0)"
			printf '        manifest(%s) = %s\n        ไฟล์จริง      = %s\n' "$pv" "$want" "$got"
		fi
		if [ -n "$fmv" ] && [ "$fmv" != "$pv" ]; then
			fail "เลขใน BASE_PLAYBOOK.md ($fmv) ไม่ตรงกับ base_version ที่ pin ($pv) — ก๊อป base ใหม่มาแต่ยังไม่ review/อัป pin (base §10, R13)"
		fi
	fi

	# V-04: เพิ่ม synonym ของกลไกบังคับที่ base §9.1 อนุญาต (ไม่ใช่แค่ permission ของเครื่องมือเดียว)
	# และบอกใน fail message ว่ารับ keyword อะไร เพราะการตรวจนี้เป็น guardrail ด้วย "คำ" ไม่ใช่ proof ของการติดตั้ง
	R10_KW='กลไกบังคับ|permission|settings\.json|hook|pre-push|pre-commit|CI|protected branch|branch protection|ruleset|required check'
	head_ "R10 — ต้องประกาศกลไกบังคับและข้อจำกัด (base §9.1)"
	if grep -qiE "$R10_KW" "$PB"; then
		pass "มีการประกาศกลไกบังคับ"
	else
		fail "ไม่พบการประกาศกลไกบังคับใน PLAYBOOK.md (base §9.1 บังคับ) — keyword ที่รับ: $R10_KW"
		note "ถ้าติดตั้งจริงด้วยกลไกที่คำไม่ตรงรายการข้างบน ให้เขียนคำใดคำหนึ่งกำกับไว้ แล้วถือผลข้อนี้เป็น note ไม่ใช่ fail (การตรวจด้วยคำเป็น guardrail ไม่ใช่ proof ของการติดตั้ง — base §9.8)"
	fi
	grep -qiE 'ข้อจำกัด|limitation|caveat' "$PB" &&
		pass "มีการประกาศข้อจำกัดของกลไก" || fail "ไม่พบการประกาศข้อจำกัดของกลไก (base §9.1 ห้ามเคลมว่ากันได้ 100%)"

	# ยกระดับจาก keyword matching: การเขียนคำว่า "hook" ผ่านได้โดยไม่ต้องมี hook จริง
	# ⇒ ถ้าโปรเจกต์ประกาศว่ารัน agent แบบ unattended ให้ **ยืนยันว่ามีไฟล์ hook อยู่จริง**
	# การตรวจนี้จุดชนวนเฉพาะเมื่อประกาศ unattended — โปรเจกต์ที่ไม่ประกาศไม่ได้รับผล
	if grep -qiE 'unattended|ไม่มีคนคุม|scope guard|plan scope guard' "$PB"; then
		head_ "Unattended mode — ประกาศแล้วต้องมีไฟล์ hook จริง (ยกระดับจากการตรวจด้วยคำ)"
		uh=""
		for h in hooks/claude-code hooks .claude/hooks .git/hooks/pre-commit .pre-commit-config.yaml; do
			[ -e "$DIR/$h" ] && uh="$uh $h"
		done
		if [ -n "$uh" ]; then
			pass "พบไฟล์/ไดเรกทอรี hook จริง:$uh"
		else
			fail "PLAYBOOK.md ประกาศว่ารันแบบ unattended แต่ไม่พบไฟล์ hook จริง — คำประกาศกับของจริงไม่ตรงกัน (นี่คือช่องที่การตรวจด้วย keyword เดิมปล่อยผ่าน)"
		fi
		if grep -qiE 'ACTIVE_PLAN|แผนที่บังคับอยู่' "$PB"; then
			pass "ประกาศที่เก็บแผนที่บังคับอยู่"
		else
			note "ไม่พบการประกาศที่เก็บแผนที่บังคับอยู่ — ถ้าใช้ scope guard ควรระบุ path ไว้ในแถวของ R10 พร้อมว่าใครมีหน้าที่ลบเมื่องานจบ"
		fi
	fi

	head_ "Hook registration integrity (C1) — settings.json ลงทะเบียนไว้ ไฟล์ต้องมีจริง"
	# จุดชนวน: "มี hook registration จริงใน .claude/settings.json" ไม่ใช่ keyword ใน PLAYBOOK.md
	# ⇒ subclass ที่ไม่ลง hook ไว้ไม่ได้รับผล · พบว่า ADOPTING §1 ไม่เคยสั่งก๊อปชั้น
	# enforcement (scripts/plan_scope.sh + hooks/claude-code/*.sh) ขณะที่ settings.template.json
	# ลงทะเบียน path ที่ downstream ไม่มีจริง = class ที่ 3 ของ silent-off (gate fail-closed
	# เงียบ ๆ ไม่มี error) — Phase 1 (v2.18.0) ประกาศ note ล่วงหน้า · Phase 3 (v2.19.0) =
	# fail จริง (base §10 — ยกระดับหลังเตือนแล้ว)
	if [ -f "$DIR/.claude/settings.json" ] && command -v python3 >/dev/null 2>&1; then
		registered=$(python3 - "$DIR" <<'PY'
import json, os, re, sys
d = sys.argv[1] if len(sys.argv) > 1 else "."
try:
    cfg = json.load(open(os.path.join(d, ".claude/settings.json")))
except Exception:
    sys.exit(0)
seen = set()
for ev, lst in (cfg.get("hooks") or {}).items():
    for m in lst or []:
        for h in (m or {}).get("hooks") or []:
            cmd = (h or {}).get("command") or ""
            # จับ ${CLAUDE_PROJECT_DIR}/<path>.sh และ ${QODER_PROJECT_DIR}/<path>.sh
            for mm in re.finditer(r'\$\{(?:CLAUDE|QODER)_PROJECT_DIR\}/([^"\s]+\.sh)', cmd):
                p = mm.group(1)
                if p not in seen:
                    seen.add(p); print(p)
PY
)
		if [ -n "$registered" ]; then
			miss=""
			for r in $registered; do
				[ -e "$DIR/$r" ] || miss="$miss $r"
			done
			if [ -n "$miss" ]; then
				fail "hook-registration missing (v2.19.0 gate) — settings.json registers hook that doesn't exist:$miss · ก๊อปตาม ADOPTING.md §1 enforcement tier หรือลบ hook ออกจาก settings.json · deadline: 2026-12-05"
			else
				pass "settings.json hook registrations ตรงกับไฟล์จริง ($(printf '%s\n' $registered | grep -c .) รายการ)"
			fi
		fi
	fi

	# ยกระดับจาก "มีคำในเอกสาร" เป็น "ประกาศแล้ว และมีไฟล์ config อยู่จริง"
	# ยังไม่ใช่ proof ว่ากฎในไฟล์นั้นถูกต้อง — แต่แยก "เขียนไว้เฉย ๆ" ออกจาก "ติดตั้งแล้ว" ได้
	found=""
	for c in .claude/settings.json .claude/settings.local.json .qwen/settings.json \
		.gitlab-ci.yml .github/workflows .pre-commit-config.yaml \
		.git/hooks/pre-push .git/hooks/pre-commit .cursor/rules; do
		[ -e "$DIR/$c" ] && found="$found $c"
	done
	if [ -n "$found" ]; then
		pass "พบไฟล์กลไกบังคับจริงในโปรเจกต์:$found"
	else
		note "ไม่พบไฟล์ config ของกลไกบังคับใด ๆ ในโปรเจกต์ — ถ้ากลไกที่ประกาศไว้อยู่ฝั่ง server (protected branch, required check, ruleset) เป็นเรื่องปกติที่ตรวจจากในเครื่องไม่ได้ · แต่ถ้าประกาศว่าติดตั้ง permission/hook ไว้ในเครื่อง แสดงว่าคำประกาศกับของจริงไม่ตรงกัน"
	fi

	# V-03: อ่านชื่อไฟล์ canonical จากแถว R1 ของ PLAYBOOK.md ก่อน แล้วจึง fallback
	#       เพราะ base §9.1 อนุญาตชื่ออื่น (QWEN.md, .ai-guidelines.md, ฯลฯ) — เดิม hardcode
	#       AGENTS.md/CLAUDE.md จึง false-fail กับ subclass ที่ compliant แต่ใช้ชื่ออื่น
	head_ "ค้นหาไฟล์ Layer 1 (base §9.1 — canonical ชื่ออะไรก็ได้ ประกาศไว้ที่ R1)"
	if [ -n "$L1_OPT" ]; then
		L1="$DIR/$L1_OPT"
		[ -f "$L1_OPT" ] && L1="$L1_OPT"
		pass "ใช้ path จาก --layer1: $L1"
	else
		L1=""
		# ดึงชื่อไฟล์ .md ที่อ้างในแถว R1 (รับทั้งใน backtick และลิงก์ markdown)
		for cand in $(grep -E '^\| ?`?R1`? ?\|' "$PB" |
			grep -oE '[A-Za-z0-9_.@/-]+\.md' | sed 's#^\./##' | sort -u); do
			if [ -f "$DIR/$cand" ]; then
				L1="$DIR/$cand"
				pass "canonical จากแถว R1: $cand"
				break
			fi
		done
		if [ -z "$L1" ]; then
			for c in AGENTS.md CLAUDE.md QWEN.md GEMINI.md .ai-guidelines.md; do
				if [ -f "$DIR/$c" ]; then
					L1="$DIR/$c"
					note "แถว R1 ไม่ได้ชี้ไฟล์ที่หาได้ — ใช้ fallback ตามชื่อที่พบ: $c (ควรระบุชื่อ canonical ในแถว R1 ให้ชัด)"
					break
				fi
			done
		fi
		[ -n "$L1" ] || fail "หาไฟล์ Layer 1 ไม่พบทั้งจากแถว R1 และจาก fallback — ระบุด้วย --layer1 <path> ถ้าใช้ชื่ออื่น (base §9.1 อนุญาตชื่ออื่นได้)"
	fi
	[ -n "$L1" ] && check_layer1_budget "$L1"

	OLD=$PWD
	cd "$DIR" 2>/dev/null && check_marker_collision
	cd "$OLD" || true
}

# ---------- main ----------

MODE=""
DIR="$PWD"
L1_OPT=""
PLAN_FILE=""
while [ $# -gt 0 ]; do
	case "$1" in
	--upstream) MODE=upstream ;;
	--downstream) MODE=downstream ;;
	--normative) MODE=normative ;;
	--plan)
		shift
		[ $# -gt 0 ] || usage
		MODE=plan
		PLAN_FILE="$1"
		;;
	--dir)
		shift
		[ $# -gt 0 ] || usage
		DIR="$1"
		;;
	--layer1)
		shift
		[ $# -gt 0 ] || usage
		L1_OPT="$1"
		;;
	-h | --help) usage ;;
	*)
		printf 'unknown arg: %s\n' "$1" >&2
		usage
		;;
	esac
	shift
done
[ -n "$MODE" ] || usage
[ -d "$DIR" ] || {
	printf 'not a directory: %s\n' "$DIR" >&2
	exit 2
}

case "$MODE" in
upstream) run_upstream ;;
downstream) run_downstream ;;
normative) run_normative ;;
plan) run_plan ;;
esac

printf '\n---\nสรุป: %s ข้อไม่ผ่าน · %s note\n' "$FAIL" "$WARN"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
