#!/usr/bin/env python3
"""Step 9 — validate the Hub content (hub/journeys, hub/knowledge) and build the hand-over files.

Journeys  = procedures (Hub fields: Display name · Slug · Description · Body)
Knowledge = reference   (Hub fields: Title · Slug · ใช้เมื่อไหร่ · Content)

The two sets must stay fully separate. This script FAILS when:
  • a slug breaks the Hub's format, differs from its file name, or is duplicated
  • a description / ใช้เมื่อไหร่ line does not start with "ใช้เมื่อ"
  • a journey points to a knowledge file, journey or tool that does not exist
  • a tool of the MCP server is not covered by any journey, or a knowledge file is never opened by a journey
  • a knowledge file names a tool or contains a step-by-step procedure (procedures belong in journeys)
  • a journey states a price, threshold or policy number (facts belong in knowledge / come from tools)

Outputs: hub/hub-content.json (for bulk import), hub/INDEX.md, hub/copy-sheet.html (copy buttons per Hub field)."""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "hub"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
errors, warnings = [], []


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        errors.append(f"{path.name}: missing front matter")
        return None
    meta = {}
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["body"] = m.group(2).strip()
    meta["file"] = path.name
    return meta


journeys = [x for x in (parse(p) for p in sorted((HUB / "journeys").glob("*.md"))) if x]
knowledge = [x for x in (parse(p) for p in sorted((HUB / "knowledge").glob("*.md"))) if x]

tools_src = (ROOT / "mcp-server" / "src" / "tools.ts").read_text()
TOOLS = dict(re.findall(r'name: "([a-z_]+)", kind: "(read|write)"', tools_src))
TOOLS.pop("demo_link_persona", None)                       # hidden unless SRICHAND_DEMO_TOOLS=1
KN = {k["slug"] for k in knowledge}
JN = {j["slug"] for j in journeys}
# identifiers journeys may legitimately quote that are neither tools nor slugs (consent types, result fields, values)
ALLOWED = {"face_photo_analysis", "cross_border_processing", "skin_profile_storage", "rewards_terms", "marketing", "range_gaps"}

# ── shared field checks
for kind, items, fields in (("journey", journeys, ("display_name", "slug", "description")), ("knowledge", knowledge, ("title", "slug", "use_when"))):
    for it in items:
        for f in fields:
            if not it.get(f):
                errors.append(f"{kind} {it['file']}: missing field '{f}'")
        s = it.get("slug", "")
        if not SLUG.match(s) or len(s) > 64:
            errors.append(f"{kind} {it['file']}: slug '{s}' must be a-z, 0-9 and hyphens, at most 64 characters")
        if it["file"] != f"{s}.md":
            errors.append(f"{kind} {it['file']}: file name must equal the slug")
        when = it.get("description") or it.get("use_when") or ""
        if not when.startswith("ใช้เมื่อ"):
            errors.append(f"{kind} {s}: the selector line must start with 'ใช้เมื่อ' — the model chooses from this line, not from the name")
        if len(when) < 60:
            warnings.append(f"{kind} {s}: selector line is short; include the words customers really use")
for dup in JN & KN:
    errors.append(f"slug '{dup}' is used by both a journey and a knowledge file")

# ── journeys: references resolve, no facts
FACT = re.compile(r"฿\s?\d|\d[\d,]*\s*บาท|\d[\d,]*\s*baht|\b599\b|\b\d+\s*(?:days?|วัน)\b", re.I)
covered_tools, opened_knowledge = set(), set()
for j in journeys:
    body = j["body"]
    for sec in ("## Goal", "## Steps", "## Knowledge to open", "## Tools"):
        if sec not in body:
            errors.append(f"journey {j['slug']}: missing section '{sec}'")
    for ident in re.findall(r"`([a-z][a-z0-9_-]+)`", body):
        if ident in TOOLS:
            covered_tools.add(ident)
        elif ident in KN:
            opened_knowledge.add(ident)
        elif ident in JN:
            pass
        elif ident in ALLOWED:
            pass
        else:
            errors.append(f"journey {j['slug']}: `{ident}` is not a tool, a knowledge slug or a journey slug")
    ksec = body.split("## Knowledge to open", 1)[-1].split("## ", 1)[0]
    for ident in re.findall(r"`([a-z0-9-]+)`", ksec):
        if ident not in KN:
            errors.append(f"journey {j['slug']}: 'Knowledge to open' lists `{ident}`, which is not a knowledge file")
    for m in FACT.finditer(body):
        errors.append(f"journey {j['slug']}: states a fact ('{m.group(0)}') — prices, thresholds and time limits belong in knowledge or come from tools")

for t in sorted(set(TOOLS) - covered_tools):
    errors.append(f"tool `{t}` is not used by any journey")
for k in sorted(KN - opened_knowledge):
    errors.append(f"knowledge `{k}` is never opened by a journey")

# ── knowledge: reference only
tool_pat = re.compile(r"\b(" + "|".join(map(re.escape, TOOLS)) + r")\b")
for k in knowledge:
    for m in tool_pat.finditer(k["body"]):
        errors.append(f"knowledge {k['slug']}: names the tool '{m.group(1)}' — knowledge holds facts; tool calls belong in journeys")
    if re.search(r"^##+\s*(Steps|ขั้นตอน)\b", k["body"], re.M):
        errors.append(f"knowledge {k['slug']}: contains a 'Steps' section — procedures belong in journeys")
    for ident in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", k["body"]):
        if ident in JN:
            errors.append(f"knowledge {k['slug']}: refers to journey `{ident}` — knowledge must not depend on journeys")

print(f"journeys: {len(journeys)} · knowledge: {len(knowledge)} · tools covered: {len(covered_tools)}/{len(TOOLS)}")
for w in warnings:
    print("  warning:", w)
if errors:
    print(f"\n{len(errors)} problem(s):")
    for e in errors:
        print("  ✗", e)
    sys.exit(1)
print("  ✓ slugs valid and unique · selector lines start with ใช้เมื่อ · every reference resolves")
print("  ✓ every tool is covered by a journey · every knowledge file is opened by a journey")
print("  ✓ knowledge names no tool and holds no procedure · journeys state no prices, thresholds or time limits")

# ── per-tool Hub settings (scope path + approval rule), generated from the real tool catalogue
catalogue = json.loads(subprocess.run(["bun", "run", str(ROOT / "mcp-server" / "src" / "describe.ts")], capture_output=True, text=True, check=True).stdout)
# Suggested approval rule per WRITE tool (read tools are always "never"). Assumes "approval" = a staff member approves the call in the Hub before it runs.
APPROVAL = {
    "register_member": ("when guardian_confirmed = true", "Adult sign-ups stay instant (explicit yes collected in chat, duplicates blocked by the tool). The tool accepts a 16–19-year-old only when this flag is set, and the model cannot verify a parent — so a person does."),
    "cart_add_item": ("when quantity > 5 — add the same rule on items[].quantity", "Normal purchases stay instant. Bulk / reseller buying belongs with staff. The tool also caps one item at 10 units per cart, counting earlier lines of the same batched call, so repeated small adds cannot slip past. The batched form carries its quantities in `items[].quantity`, so the rule needs BOTH paths."),
    "cart_update_item": ("when quantity > 5", "Same as cart_add_item."),
    "clear_cart_item": ("when all = true", "Dropping the SKUs a customer asked to drop stays instant. Emptying the WHOLE basket in one call (destructiveHint) gets a human look — it is the one shape of this call the customer cannot undo by re-adding one item, and a mis-set flag would wipe a basket mid-sale. Removing named SKUs needs no approval."),
    "create_order": ("when redeem_points > 500", "Orders stay instant: the journey reads the total back and waits for a clear yes, and nothing is charged. A large points redemption gets a human look (phone numbers are unverified in the prototype). Tune the threshold."),
    "confirm_payment_mock": ("always", "DEMO ONLY stand-in for the payment gateway. The presenter approving it is the 'payment received' moment. Disable this tool in production."),
    "record_consent": ("when guardian_confirmed = true", "Adult consents stay instant. A minor's photo consent is only accepted with this flag, which the model cannot verify — so a person does. Fires for exactly those cases."),
    "set_marketing_preference": ("never", "PDPA: opting out must be as easy and as quick as opting in."),
    "withdraw_consent_and_erase": ("always", "Irreversible deletion (destructiveHint). The customer confirms in chat; staff approval guards against a misfire. PDPA allows up to 30 days, so a short wait is acceptable."),
    "save_skin_profile": ("never", "Overwrites only the customer's own profile; needs their consent, enforced by the tool."),
    "save_skin_analysis": ("never", "Needs photo + cross-border consent, enforced by the tool."),
    "save_routine": ("never", "Low risk; replaces the customer's own saved routine."),
    "log_range_gap": ("never", "Anonymous analytics; must never be blocked."),
}
for t in catalogue:
    if t["kind"] == "write" and t["name"] not in APPROVAL:
        errors.append(f"tool `{t['name']}` has no suggested approval rule in scripts/09_build_hub.py")
    if t["customer_arg"] and not t["customer_arg_required"]:
        errors.append(f"tool `{t['name']}` takes an OPTIONAL customer id — a tool must either require it (scope path) or not accept it at all (declared unbound), otherwise the model could supply someone else's id")
if errors:
    for e in errors:
        print("  ✗", e)
    sys.exit(1)

# Journey-level declared rules (the Hub enforces them at call time; the model cannot see or change them).
# tier "now"      = safe whether the Hub applies journey rules globally or only while that journey is active
# tier "if_scoped" = add ONLY after confirming that a journey's rules apply only while that journey is active
JOURNEY_RULES = [
    ("privacy-and-data-deletion", "withdraw_consent_and_erase", "ต้องให้คนอนุมัติทุกครั้ง", "now", "Irreversible deletion. PDPA allows up to 30 days, so a short wait is acceptable. Keeps the rule next to its procedure even if the organisation rule is relaxed."),
    ("cart-and-checkout", "confirm_payment_mock", "ต้องให้คนอนุมัติทุกครั้ง", "now", "Demo-only stand-in for the payment gateway; the presenter's approval is the 'payment received' moment. Disable the tool in production."),
    ("skin-reaction-or-medical-concern", "cart_add_item", "ต้องให้คนอนุมัติทุกครั้ง", "if_scoped", "Enforces 'never sell during a reaction' — the journey text alone is only advice."),
    ("skin-reaction-or-medical-concern", "create_order", "ต้องให้คนอนุมัติทุกครั้ง", "if_scoped", "Same: no order is placed while a reaction or medical concern is being discussed."),
    ("human-handover", "cart_add_item", "ต้องให้คนอนุมัติทุกครั้ง", "if_scoped", "Enforces 'stop selling' once a person is taking over."),
    ("human-handover", "create_order", "ต้องให้คนอนุมัติทุกครั้ง", "if_scoped", "Same."),
]
for jslug, tname, _, tier, _ in JOURNEY_RULES:
    if jslug not in JN:
        errors.append(f"journey rule points at unknown journey `{jslug}`")
    if tname not in TOOLS:
        errors.append(f"journey rule points at unknown tool `{tname}`")
    if tier not in ("now", "if_scoped"):
        errors.append(f"journey rule {jslug}/{tname}: unknown tier {tier}")
if errors:
    for e in errors:
        print("  ✗", e)
    sys.exit(1)

rows = []
for t in catalogue:
    bound = bool(t["customer_arg"])
    rule, why = ("never", "Read-only (readOnlyHint: true); proven by test to change nothing.") if t["kind"] == "read" else APPROVAL[t["name"]]
    rows.append(dict(tool=t["name"], kind=t["kind"], scope_path=t["customer_arg"] if bound else None,
                     scope_action=f"scope path = {t['customer_arg']}" if bound else "press “ประกาศว่า tool นี้ไม่ผูกกับลูกค้า” (not bound to a customer)",
                     unpaired="fails closed (correct: it needs the member)" if bound else "works", approval=rule, approval_reason=why,
                     hints=("destructive " if t["destructive"] else "") + ("idempotent" if t["idempotent"] else "")))
ts = ["# Hub tool settings", "", "Generated by `scripts/09_build_hub.py` from the live tool catalogue (`bun run mcp-server/src/describe.ts`). Tool names appear in the Hub with the integration prefix, e.g. `srichand-mcp__cart_add_item`.", "",
      "## What the scope path is", "",
      "The **scope path** is the input field the Hub **overwrites** with the id of the customer who is chatting — the *id หลัก* paired on the Accounts page (for this integration, the member number such as `SCR0260041`) — no matter what the model sent.",
      "- It is how customer tools know whose data to touch, and why unpaired chats *fail closed* on those tools.",
      "- It is a **security control**: these tools accept a member number, so without a scope path the model would fill the field itself and a customer could type someone else's member number to read their points or orders. With it set, that is impossible.",
      "- Every tool therefore falls into exactly one of two groups: it **requires** `line_user_id` → set the scope path to it; or it has **no** customer field → declare it not bound to a customer. No tool takes an optional customer id (the build fails if one ever does).", "",
      f"## Settings per tool ({len(rows)})", "", "| Tool | Read / write | Scope | Unpaired chat | Approval rule (suggested) | Why |", "|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: (r["scope_path"] is None, r["kind"] != "read", r["tool"])):
    ts.append(f"| `{r['tool']}` | {r['kind']}{(' · ' + r['hints'].strip()) if r['hints'].strip() else ''} | {r['scope_action']} | {r['unpaired']} | **{r['approval']}** | {r['approval_reason']} |")
ts += ["", "## Declared rules inside journeys", "",
       "Journey bodies are advice the model may ignore; declared rules are enforced by the Hub when the tool is called, and the Hub applies the strictest of the organisation rule and the journey rules. Approval means a person approves in the Hub, so every rule costs a real wait — add few.", "",
       "**First find out how journey rules are scoped.** Add a throw-away rule (`get_promotions` → approve every time) to `human-handover`, then ask the agent \"มีโปรอะไรบ้าง\" (a different journey). Approval requested → journey rules apply globally, so add only the *now* rows. No approval → rules apply only while that journey is active, so the *if scoped* rows are safe too. Delete the test rule afterwards.", "",
       "| Journey | Tool | Rule | Add | Why |", "|---|---|---|---|---|"]
ts += [f"| `{j}` | `{t}` | {r} | **{'now' if tier == 'now' else 'only if rules are journey-scoped'}** | {why} |" for j, t, r, tier, why in JOURNEY_RULES]
ts += ["", "### Conditional rules (ขออนุมัติเมื่อเข้าเงื่อนไข: Parameter · Operator · Value)", "",
       "Set these once as the organisation-level approval rule of the tool (they should hold in every journey). None of them fires in the scripted demos.", "",
       "| Tool | Parameter | Operator | Value | Why |", "|---|---|---|---|---|",
       "| `record_consent` | `guardian_confirmed` | = | `true` | The tool accepts a minor's photo consent only with this flag; the model cannot verify a parent. |",
       "| `register_member` | `guardian_confirmed` | = | `true` | Same, for sign-ups aged 16–19. |",
       "| `cart_add_item` | `quantity` | > | `5` | Bulk / reseller buying goes to staff. The tool additionally caps one item at 10 units per cart. |",
       "| `cart_add_item` | `items[].quantity` | > | `5` | The batched form (several SKUs in one call) carries its quantity per line — without this second rule a bulk buy slips through as `items`. |",
       "| `cart_update_item` | `quantity` | > | `5` | Same. |",
       "| `clear_cart_item` | `all` | = | `true` | Emptying the whole basket is the one cart action the customer cannot undo item by item. Removing named `variant_ids` stays instant. |",
       "| `create_order` | `redeem_points` | > | `500` | A large points redemption gets a human look. Tune the threshold. |", "",
       "A conditional rule tests the parameters of ONE call. Anything that must hold across calls or depends on stored data (totals, stock, ownership, age, consent, duplicates) is enforced inside the tools instead.", "",
       "Do not add rules to: `cart_add_item` / `cart_update_item` / `clear_cart_item` (removing named SKUs) / `create_order` in the normal buying journeys (the journey reads the total back and waits for a yes; approval would stall every sale) · `record_consent`, `save_skin_profile`, `save_skin_analysis`, `save_routine` (the tools already enforce consent) · `set_marketing_preference` (PDPA: opting out must be immediate) · `log_range_gap` (anonymous) · any read tool.",
       "", "## Notes", "",
       "- **Approval rules are suggestions** and assume that approval means a staff member approves the call in the Hub before it runs. The Hub applies the strictest rule among the organisation rule and any journey rule, so start permissive here and tighten per journey if needed.",
       "- The Hub does not retry write tools. `confirm_payment_mock`, `save_skin_profile`, `set_marketing_preference`, `cart_update_item` and `withdraw_consent_and_erase` are idempotent anyway; `create_order` and `register_member` are not — the journeys call them once, after an explicit yes.",
       "- `register_member` and `log_range_gap` are the two WRITE tools that are deliberately not bound to a customer: the first is for people who are not members yet, the second is anonymous by design.",
       "- After changing a tool on the server, re-run tool discovery in the Hub and re-check this table: a new tool arrives with no scope decision."]
(HUB / "TOOL-SETTINGS.md").write_text("\n".join(ts) + "\n", encoding="utf-8")
(HUB / "tool-settings.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

# ── outputs
system_prompt = (HUB / "system-prompt.md").read_text(encoding="utf-8") if (HUB / "system-prompt.md").exists() else ""
(HUB / "hub-content.json").write_text(json.dumps({
    "generated_from": "hub/journeys/*.md + hub/knowledge/*.md",
    "journeys": [dict(display_name=j["display_name"], slug=j["slug"], description=j["description"], body=j["body"]) for j in journeys],
    "knowledge": [dict(title=k["title"], slug=k["slug"], use_when=k["use_when"], content=k["body"]) for k in knowledge],
}, ensure_ascii=False, indent=1), encoding="utf-8")

uses = {k: sorted(j["slug"] for j in journeys if f"`{k}`" in j["body"]) for k in sorted(KN)}
tool_use = {t: sorted(j["slug"] for j in journeys if f"`{t}`" in j["body"]) for t in sorted(TOOLS)}
idx = ["# Hub content index", "", "Generated by `scripts/09_build_hub.py` — edit the files in `hub/journeys` and `hub/knowledge`, then re-run it.", "",
       f"## Journeys ({len(journeys)}) — procedures", "", "| Display name | Slug | Tools | Opens knowledge |", "|---|---|---|---|"]
for j in journeys:
    ts = [t for t in TOOLS if f"`{t}`" in j["body"]]
    ks = [k for k in sorted(KN) if f"`{k}`" in j["body"]]
    idx.append(f"| {j['display_name']} | `{j['slug']}` | {', '.join(ts) or '—'} | {', '.join(ks)} |")
idx += ["", f"## Knowledge ({len(knowledge)}) — reference", "", "| Title | Slug | Opened by |", "|---|---|---|"]
for k in knowledge:
    idx.append(f"| {k['title']} | `{k['slug']}` | {', '.join(uses[k['slug']])} |")
idx += ["", f"## Tool coverage ({len(TOOLS)} tools)", "", "| Tool | Kind | Journeys |", "|---|---|---|"]
for t in sorted(TOOLS):
    idx.append(f"| `{t}` | {TOOLS[t]} | {', '.join(tool_use[t])} |")
(HUB / "INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")

# copy sheet
def field(label, hint, value, big=False):
    rows = min(28, max(2, value.count("\n") + 2)) if big else 2
    return (f'<div class="f"><div class="l"><b>{html.escape(label)}</b><span>{html.escape(hint)}</span><button type="button">Copy</button></div>'
            f'<textarea readonly rows="{rows}">{html.escape(value)}</textarea></div>')


def card(kind, head, fields):
    return f'<section class="card" data-kind="{kind}"><h3>{html.escape(head)}</h3>{"".join(fields)}</section>'


settings_html = ('<section class="card" data-kind="settings"><h3>Tool settings · scope path and approval rule</h3>'
                 '<p>Scope path = the field the Hub overwrites with the paired customer\'s id. Tools that take <code>line_user_id</code> get it as scope path; the rest are declared not bound to a customer.</p>'
                 '<div style="overflow-x:auto"><table><thead><tr><th>Tool</th><th>Kind</th><th>Scope</th><th>Approval</th><th>Why</th></tr></thead><tbody>'
                 + "".join(f"<tr><td><code>{html.escape(r['tool'])}</code></td><td>{r['kind']}</td><td>{'<b>line_user_id</b>' if r['scope_path'] else 'not bound to a customer'}</td><td><b>{r['approval']}</b></td><td>{html.escape(r['approval_reason'])}</td></tr>"
                           for r in sorted(rows, key=lambda r: (r["scope_path"] is None, r["kind"] != "read", r["tool"])))
                 + "</tbody></table></div></section>")
cards = [settings_html]
if system_prompt:
    cards.append(card("prompt", "System prompt (always-on rules)", [field("Agent instructions", "paste into the agent's system prompt / persona field", system_prompt.split("---\n", 2)[-1].strip() if system_prompt.startswith("---") else system_prompt, True)]))
def rules_box(slug):
    mine = [r for r in JOURNEY_RULES if r[0] == slug]
    if not mine:
        return ""
    lis = "".join(f"<li><code>{html.escape(t)}</code> → {html.escape(rule)} <b>[{'add now' if tier == 'now' else 'add only if journey rules are scoped to the active journey'}]</b> — {html.escape(why)}</li>" for _, t, rule, tier, why in mine)
    return f'<div class="rules"><b>Declared rules for this journey</b><ul>{lis}</ul></div>'


for j in journeys:
    cards.append(card("journey", f"Journey · {j['display_name']}", [rules_box(j["slug"]),field("Display name", "ป้ายชื่อสำหรับคน", j["display_name"]), field("Slug", "a-z 0-9 และขีดกลาง", j["slug"]),
                                                                   field("Description", "โมเดลเลือก journey จากช่องนี้", j["description"]), field("Body", "Advisory", j["body"], True)]))
for k in knowledge:
    cards.append(card("knowledge", f"Knowledge · {k['title']}", [field("Title", "ชื่อเอกสารสำหรับคน", k["title"]), field("Slug", "ชื่อไฟล์ที่ agent เปิด", k["slug"]),
                                                                 field("ใช้เมื่อไหร่", "โมเดลอ่านบรรทัดนี้ก่อนตัดสินใจเปิดไฟล์", k["use_when"]), field("Content", "markdown", k["body"], True)]))
page = f"""<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Srichand Hub copy sheet</title>
<style>
:root{{--ink:#1A1A1A;--red:#FD0145;--ice:#AFF0E8;--grey:#F1F1F1;--rule:#D9D9D9}}
*{{box-sizing:border-box}} body{{margin:0;font:15px/1.5 "DM Sans","Anuphan",-apple-system,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:#fff;padding:28px clamp(16px,5vw,56px) 80px}}
h1{{font-weight:400;font-size:2rem;margin:0 0 6px}} h1 em{{font-style:normal;color:var(--red)}} p{{margin:0 0 18px;max-width:72ch}}
nav{{position:sticky;top:0;background:#fff;padding:10px 0;display:flex;gap:8px;flex-wrap:wrap;border-bottom:2px solid var(--ink);margin-bottom:22px;z-index:2}}
nav button{{font:inherit;padding:6px 12px;border:1.5px solid var(--ink);background:#fff;cursor:pointer}} nav button.on{{background:var(--ink);color:#fff}}
.card{{border-top:2px solid var(--ink);padding:14px 0 26px;max-width:1000px}} .card h3{{font-weight:400;font-size:1.25rem;margin:0 0 12px}}
.f{{margin:0 0 12px}} .l{{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}} .l span{{font-size:.8rem;color:#555;flex:1}}
.l button{{font:inherit;font-size:.82rem;padding:3px 12px;border:1.5px solid var(--red);color:var(--red);background:#fff;cursor:pointer}} .l button.done{{background:var(--red);color:#fff}}
textarea{{width:100%;font:13px/1.5 ui-monospace,Menlo,monospace;padding:10px;border:1px solid var(--rule);background:var(--grey);resize:vertical;color:var(--ink)}}
table{{border-collapse:collapse;width:100%;font-size:.86rem;min-width:760px}} th{{text-align:left;border-bottom:2px solid var(--ink);padding:6px 10px 6px 0}} td{{border-bottom:1px solid var(--rule);padding:6px 10px 6px 0;vertical-align:top}}
.rules{{border:1.5px solid var(--red);padding:10px 14px;margin:0 0 12px;font-size:.88rem}} .rules ul{{margin:6px 0 0;padding-left:18px}}
[hidden]{{display:none}}
</style>
<h1>Srichand Hub <em>copy sheet</em></h1>
<p>{len(journeys)} journeys and {len(knowledge)} knowledge files, in the Hub's own field order. Press Copy, paste into the matching Hub field. Generated by <code>scripts/09_build_hub.py</code> — edit the Markdown sources, not this page.</p>
<nav><button data-f="all" class="on">All</button><button data-f="settings">Tool settings</button><button data-f="prompt">System prompt</button><button data-f="journey">Journeys ({len(journeys)})</button><button data-f="knowledge">Knowledge ({len(knowledge)})</button></nav>
{''.join(cards)}
<script>
document.querySelectorAll('.l button').forEach(b=>b.addEventListener('click',async()=>{{
  const ta=b.closest('.f').querySelector('textarea'); let ok=false;
  try{{await navigator.clipboard.writeText(ta.value);ok=true}}catch(e){{ta.removeAttribute('readonly');ta.select();try{{ok=document.execCommand('copy')}}catch(_){{}}ta.setAttribute('readonly','')}}
  b.textContent=ok?'Copied':'Select + ⌘C';b.classList.add('done');setTimeout(()=>{{b.textContent='Copy';b.classList.remove('done')}},1400);
}}));
document.querySelectorAll('nav button').forEach(n=>n.addEventListener('click',()=>{{
  document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===n));
  document.querySelectorAll('.card').forEach(c=>c.hidden=!(n.dataset.f==='all'||c.dataset.kind===n.dataset.f));
}}));
</script></html>"""
(HUB / "copy-sheet.html").write_text(page, encoding="utf-8")
print(f"  written: hub/hub-content.json · hub/INDEX.md · hub/TOOL-SETTINGS.md · hub/tool-settings.json · hub/copy-sheet.html")
