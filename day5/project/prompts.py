"""
prompts.py — all 8 system prompts used by analyzer.py.

Task 3 of the lab (Track A).
Study material references:
  §3.3 Schema-First Prompt Design
  §6.1 Extraction Prompts
  §6.2 Evaluation Prompts
  §6.3 Feedback-Only Principle

Every prompt must follow ICCO structure:
  Instruction  — what the model must do
  Context      — relevant background (rubric description, schema description)
  Constraints  — rules the model must not break
  Output       — the exact JSON schema expected

Every prompt (except OVERALL_SUMMARY_PROMPT) must end with:
  "Output ONLY a valid JSON object matching the schema above. No prose. No
  markdown fences. No commentary. Never rewrite or generate résumé content."

Temperature guidance (set in the ask_json() call in analyzer.py):
  Extraction prompts (RESUME_PROFILE, JD_PROFILE): 0.0
  Evaluation prompts (KEYWORD_MATCH, BULLET_QUALITY, JARGON, STRUCTURE, BACKGROUND_FIT): 0.2–0.3
  OVERALL_SUMMARY_PROMPT: 0.3
"""


# ---------------------------------------------------------------------------
# Extraction prompts
# ---------------------------------------------------------------------------

# Purpose: extract a structured candidate profile from plain résumé text.
# Input to ask_json(): system=RESUME_PROFILE_PROMPT, user="RÉSUMÉ TEXT:\n\n{text}"
# Expected output schema — all fields required; arrays may be empty:
# {
#   "name": "string",
#   "contact": {
#     "email": "string", "phone": "string", "linkedin": "string",
#     "github": "string", "portfolio": "string"
#   },
#   "summary": "string",
#   "education": [{"school": "string", "degree": "string",
#                  "graduation_date": "string", "courses": ["string"]}],
#   "projects":  [{"title": "string", "date": "string", "bullets": ["string"]}],
#   "experience":[{"title": "string", "company": "string",
#                  "date": "string", "bullets": ["string"]}],
#   "skills": {
#     "languages": ["string"], "frameworks": ["string"], "tools": ["string"],
#     "concepts": ["string"], "platforms": ["string"]
#   }
# }
RESUME_PROFILE_PROMPT = """
Instruction: Extract a factual, structured candidate profile from the supplied résumé text.
Context: Preserve the candidate's stated facts and wording. Put project and experience
bullets in their corresponding arrays and classify skills into the requested categories.
Constraints: Use only supplied evidence. Do not infer missing facts. Use empty strings or
empty arrays for unavailable fields. Include every field. Never improve, rewrite, or invent
résumé content.
Output: Return this JSON shape:
{"name":"string","contact":{"email":"string","phone":"string","linkedin":"string","github":"string","portfolio":"string"},"summary":"string","education":[{"school":"string","degree":"string","graduation_date":"string","courses":["string"]}],"projects":[{"title":"string","date":"string","bullets":["string"]}],"experience":[{"title":"string","company":"string","date":"string","bullets":["string"]}],"skills":{"languages":["string"],"frameworks":["string"],"tools":["string"],"concepts":["string"],"platforms":["string"]}}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: extract a structured JD profile from free-form job posting text.
# Input to ask_json(): system=JD_PROFILE_PROMPT, user="JOB DESCRIPTION TEXT:\n\n{text}"
# Expected output schema — all fields required; arrays may be empty:
# {
#   "job_title": "string",
#   "company": "string",
#   "location": "string",
#   "experience_level": "string",
#   "required_skills": ["string"],
#   "preferred_skills": ["string"],
#   "tools_technologies": ["string"],
#   "responsibilities": ["string"],
#   "soft_skills": ["string"],
#   "buzzwords": ["string"],
#   "deal_breakers": ["string"]
# }
JD_PROFILE_PROMPT = """
Instruction: Extract a structured role profile from the supplied job description.
Context: Separate explicitly required items from preferred items and retain technologies,
responsibilities, soft skills, buzzwords, and genuine deal-breakers.
Constraints: Use only the posting. Do not infer unstated requirements. Include every field;
use empty strings or arrays when information is absent. Keep entries concise and deduplicate them.
Output: Return this JSON shape:
{"job_title":"string","company":"string","location":"string","experience_level":"string","required_skills":["string"],"preferred_skills":["string"],"tools_technologies":["string"],"responsibilities":["string"],"soft_skills":["string"],"buzzwords":["string"],"deal_breakers":["string"]}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Evaluation prompts
# ---------------------------------------------------------------------------

# Purpose: compare résumé keywords against JD requirements; produce a score.
# Input to ask_json():
#   system=KEYWORD_MATCH_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "present": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword",
#                "found_in": "summary|projects|experience|education|skills", "exact_match": true}],
#   "missing": [{"keyword": "string", "category": "...", "importance": "required|preferred",
#                "suggested_section": "skills|projects|experience|summary",
#                "why_it_matters": "string (25 words max — diagnostic only)"}],
#   "keyword_match_score": 0
# }
# Scoring formula: 100 × (required_skills found in résumé) / max(1, total required_skills)
# IMPORTANT: the résumé and JD profiles are always provided in full, even when
# they share zero keywords — that is a normal, valid input, not a missing one.
# The model must still return the schema (an empty "present" array is a
# correct result) rather than asking for clarification or claiming no résumé
# was given. Small/local models are especially prone to breaking character on
# a total-mismatch input, so state this constraint explicitly.
KEYWORD_MATCH_PROMPT = """
Instruction: Compare the complete résumé profile with the complete job profile and diagnose keyword coverage.
Context: Match required and preferred skills, technologies, soft skills, and buzzwords using
literal evidence from the résumé. Calculate keyword_match_score as 100 × required skills found
in the résumé / max(1, total required skills), rounded to the nearest integer.
Constraints: Never invent evidence. Mark exact_match true only for literal matches. Limit each
why_it_matters to 25 words and keep it diagnostic. The profiles are complete even if they share
zero keywords; in that valid case return an empty present array and the full schema without asking
for clarification. Never rewrite or generate résumé content.
Output: Return this JSON shape:
{"present":[{"keyword":"string","category":"language|framework|tool|concept|soft_skill|buzzword","found_in":"summary|projects|experience|education|skills","exact_match":true}],"missing":[{"keyword":"string","category":"language|framework|tool|concept|soft_skill|buzzword","importance":"required|preferred","suggested_section":"skills|projects|experience|summary","why_it_matters":"string"}],"keyword_match_score":0}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: score each résumé bullet against the Action → Technology → Impact rubric.
# Input to ask_json(): system=BULLET_QUALITY_PROMPT, user="RÉSUMÉ PROFILE:\n{json}"
# Expected output schema:
# {
#   "bullets": [{"source": "projects|experience", "parent_title": "string",
#                "bullet_text": "string (verbatim)", "has_action_verb": true,
#                "has_specific_technology": true, "has_measurable_impact": false,
#                "level": "L1_OK|L2_BETTER|L3_BEST",
#                "what_is_missing": "string (20 words max — diagnose only)"}],
#   "bullet_quality_avg": 0
# }
# Scoring formula: round(100 × sum(level_score) / (3 × count)) where L1=1, L2=2, L3=3
# IMPORTANT: embed the Action→Technology→Impact rubric verbatim inside this prompt,
# including the L1/L2/L3 reference level examples. This is a well-known, general
# résumé-writing framework — no external reference document needed.
BULLET_QUALITY_PROMPT = """
Instruction: Audit every project and experience bullet using the Action→Technology→Impact rubric.
Context: Apply this rubric verbatim: "L1_OK: Action — the bullet states what the candidate did
and begins with or clearly uses an action verb. L2_BETTER: Action → Technology — the bullet states
the action and names a specific tool, language, framework, platform, or method. L3_BEST: Action →
Technology → Impact — the bullet includes action and technology plus a measurable result expressed
with a number, percentage, time, scale, cost, or other quantified outcome." Score L1=1, L2=2,
L3=3. Calculate bullet_quality_avg as round(100 × sum(level scores) / (3 × bullet count)); use 0
when there are no bullets.
Reference level examples: "Built a dashboard" is L1_OK (action only); "Built a dashboard using
React" is L2_BETTER (action and technology); "Built a React dashboard that reduced reporting time
by 30%" is L3_BEST (action, technology, and measurable impact).
Constraints: Evaluate bullets verbatim and include each exactly once. A bullet earns the highest
level whose requirements it meets. what_is_missing is diagnostic only and at most 20 words. Do not
suggest replacement wording. Never rewrite or generate résumé content.
Output: Return this JSON shape:
{"bullets":[{"source":"projects|experience","parent_title":"string","bullet_text":"string","has_action_verb":true,"has_specific_technology":true,"has_measurable_impact":false,"level":"L1_OK|L2_BETTER|L3_BEST","what_is_missing":"string"}],"bullet_quality_avg":0}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: detect résumé terminology that is a likely semantic match for JD
#          terminology but would not literally keyword-match an ATS scan.
# Input to ask_json():
#   system=JARGON_AUDIT_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "flags": [{"bullet_text": "string (verbatim)", "term_used": "string",
#              "suggested_translation": "string", "severity": "low|medium|high"}],
#   "jargon_score": 0
# }
# No static table: the model compares résumé text against JD text dynamically —
# a real ATS/recruiter tool does semantic matching, not a hand-maintained dictionary.
# Severity rules: high if the JD uses no equivalent language at all; medium if
# partial overlap; low if the JD already uses matching or adjacent terminology.
# Scoring formula: max(0, 100 - 10*high_count - 5*medium_count - 2*low_count)
JARGON_AUDIT_PROMPT = """
Instruction: Dynamically compare résumé terminology against the JD and flag semantically related
wording that may fail a literal ATS keyword match.
Context: Infer translations only from the two supplied profiles; do not use a static translation
table. Severity is high when the JD uses no equivalent language, medium for partial overlap, and
low when the JD already uses matching or adjacent terminology. Calculate jargon_score as
max(0, 100 - 10×high_count - 5×medium_count - 2×low_count).
Constraints: Each bullet_text must be copied verbatim from the profile. Flag only defensible
terminology mismatches. suggested_translation names the JD term for diagnostic comparison; it must
not rewrite a bullet. Never rewrite or generate résumé content.
Output: Return this JSON shape:
{"flags":[{"bullet_text":"string","term_used":"string","suggested_translation":"string","severity":"low|medium|high"}],"jargon_score":0}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: audit general ATS-parseability formatting.
# Input to ask_json(): system=STRUCTURE_AUDIT_PROMPT, user="RÉSUMÉ TEXT:\n\n{text}"
# Expected output schema:
# {
#   "page_count_estimate": 1,
#   "single_column_likely": true,
#   "section_headings_present": ["string"],
#   "section_headings_missing": ["string"],
#   "reverse_chronological_likely": true,
#   "contact_info_at_top": true,
#   "length_appropriate": true,
#   "no_images_or_graphics": true,
#   "ats_red_flags": [{"issue": "string", "evidence": "string"}],
#   "structure_score": 0
# }
# IMPORTANT: embed general ATS-parseability rules verbatim inside this prompt:
# single-column layout, standard section headers, reverse-chronological order,
# appropriate length, contact info placement, no images/graphics. These are
# well-known conventions — no external reference document needed.
STRUCTURE_AUDIT_PROMPT = """
Instruction: Audit the supplied plain résumé text for likely ATS parseability and structure.
Context: Apply these general ATS-parseability rules verbatim: "Use a single-column layout; use
standard section headers such as Summary, Education, Experience, Projects, and Skills; list dated
experience in reverse-chronological order; keep length appropriate for the candidate's experience;
place name and contact information at the top; and avoid images, icons, charts, text boxes, and
other graphics that an ATS may not parse." Start at 100 and deduct reasonably for evidence-backed
violations; structure_score must be 0–100.
Constraints: Judge only evidence visible in extracted text. Plain text cannot prove visual layout,
so label such findings as likely and do not invent formatting. Evidence must quote or concisely
identify the observed signal. Never rewrite or generate résumé content.
Output: Return this JSON shape:
{"page_count_estimate":1,"single_column_likely":true,"section_headings_present":["string"],"section_headings_missing":["string"],"reverse_chronological_likely":true,"contact_info_at_top":true,"length_appropriate":true,"no_images_or_graphics":true,"ats_red_flags":[{"issue":"string","evidence":"string"}],"structure_score":0}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: assess how well the candidate's stated education/experience background
# plausibly aligns with what this role is asking for — using only data already
# extracted into resume_profile and jd_profile (no external degree code needed).
# Input to ask_json():
#   system=BACKGROUND_FIT_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "candidate_background_summary": "string (1–2 sentences)",
#   "role_requirements_summary": "string (1–2 sentences)",
#   "alignment_commentary": "string (2–3 sentences — diagnostic only)",
#   "background_fit_score": 0
# }
BACKGROUND_FIT_PROMPT = """
Instruction: Assess how plausibly the candidate's stated education and experience align with the role.
Context: Compare only the supplied résumé and JD profiles. Score background_fit_score from 0 to
100 based on evidenced education, experience level, domain exposure, and deal-breakers.
Constraints: Do not use external degree mappings or assumptions about institutions. Distinguish
missing evidence from confirmed absence. Keep summaries to 1–2 sentences and alignment commentary
to 2–3 diagnostic sentences. Never rewrite or generate résumé content.
Output: Return this JSON shape:
{"candidate_background_summary":"string","role_requirements_summary":"string","alignment_commentary":"string","background_fit_score":0}
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Synthesis prompt
# ---------------------------------------------------------------------------

# Purpose: produce a 3-bullet plain Markdown executive summary from the full report.
# Input to ask_text(): system=OVERALL_SUMMARY_PROMPT, user="ANALYSIS REPORT:\n{json}"
# Returns: plain Markdown string (not JSON).
# NOTE: this prompt does NOT need the JSON output constraint line.
#       It also does NOT need a JSON schema — ask_text() is used, not ask_json().
# The summary must be diagnostic only — no rewrites, no generated résumé content.
OVERALL_SUMMARY_PROMPT = """
Instruction: Summarise the supplied analysis report as exactly three concise Markdown bullet points.
Context: Lead with the overall score and ATS verdict, then identify the strongest evidenced area
and the most important diagnostic gaps across keyword match, bullets, jargon, structure, and background fit.
Constraints: Use only report evidence. Be specific and concise. Give diagnostic feedback only;
do not rewrite, generate, or propose replacement résumé content. Do not add a heading or preamble.
Output: Exactly three plain Markdown bullets, each beginning with "- ".
"""
