from __future__ import annotations

import argparse
import json
import secrets
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from run_ay1_d1c_governed_human_review import (
    ROOT,
    apply as apply_workbook,
    atomic_json,
    readj,
    validate_entry,
)

HOST = "127.0.0.1"
CONFIRMATION_PHRASE = "APPLIQUER LES 12 DECISIONS"
ALLOWED_DECISIONS = ("approve", "reject", "request_revision", "abstain")
ALLOWED_ROLES = (
    "human_reviewer",
    "scientific_reviewer",
    "theory_governance_reviewer",
    "principal_investigator",
)

HTML = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AY1-D1c — Revue humaine gouvernée</title>
<style>
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#171717;background:#f4f4f4}
body{margin:0}.top{position:sticky;top:0;z-index:5;background:#111;color:#fff;padding:14px 20px;box-shadow:0 2px 10px #0004}
.top h1{font-size:19px;margin:0 0 8px}.metrics{display:flex;gap:16px;flex-wrap:wrap;font-size:14px}.wrap{max-width:1180px;margin:20px auto;padding:0 16px 60px}
.card{background:#fff;border:1px solid #ddd;border-radius:12px;margin:14px 0;padding:18px;box-shadow:0 1px 4px #0001}.card.done{border-left:6px solid #2d7}.card.invalid{border-left:6px solid #d44}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.wide{grid-column:1/-1}label{display:block;font-size:13px;font-weight:650;margin-bottom:5px}select,input,textarea{box-sizing:border-box;width:100%;border:1px solid #bbb;border-radius:7px;padding:9px;font:inherit;background:#fff}textarea{min-height:100px;resize:vertical}
.relation{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#f7f7f7;border-radius:7px;padding:9px;overflow-wrap:anywhere}.evidence{background:#fbfbfb;border-left:4px solid #bbb;padding:10px 12px;margin:8px 0}.muted{color:#666;font-size:13px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.btn{border:0;border-radius:8px;padding:10px 15px;font-weight:700;cursor:pointer}.primary{background:#1565c0;color:#fff}.danger{background:#a40000;color:#fff}.secondary{background:#ddd}.btn:disabled{opacity:.45;cursor:not-allowed}.status{padding:10px 12px;border-radius:8px;background:#eef;margin:10px 0;white-space:pre-wrap}.error{background:#fee;color:#800}.ok{background:#eafbea;color:#174f17}
.applybox{background:#fff4f4;border:1px solid #d99;border-radius:12px;padding:16px;margin-top:25px}.small{font-size:12px}.hash{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}
@media(max-width:760px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}}
</style>
</head>
<body>
<div class="top"><h1>AY1-D1c — Revue humaine gouvernée réelle</h1><div class="metrics"><span id="campaign"></span><span id="progress"></span><span id="saved"></span></div></div>
<div class="wrap">
<div id="message" class="status">Chargement…</div>
<div class="actions"><button class="btn primary" id="save">Sauvegarder toutes les décisions</button><button class="btn secondary" id="reload">Recharger depuis le disque</button></div>
<div id="cards"></div>
<div class="applybox">
<h2>Application finale au registre append-only</h2>
<p>Cette opération écrit les décisions dans le registre gouverné. Elle ne doit être exécutée qu’après revue complète des 12 candidats.</p>
<label for="confirm">Saisir exactement : <code>APPLIQUER LES 12 DECISIONS</code></label>
<input id="confirm" autocomplete="off">
<div class="actions"><button class="btn danger" id="apply" disabled>Appliquer les décisions au registre</button></div>
</div>
</div>
<script>
const TOKEN = __TOKEN__;
let workbook = null;
const decisions = ["", "approve", "reject", "request_revision", "abstain"];
const labels = {"":"— choisir —",approve:"Approuver",reject:"Rejeter",request_revision:"Demander une révision",abstain:"S’abstenir"};
function esc(v){return String(v??"").replace(/[&<>\"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function msg(t,kind=""){const e=document.getElementById("message");e.textContent=t;e.className="status "+kind;}
function count(){const filled=workbook.entries.filter(e=>e.human_decision.decision).length;document.getElementById("progress").textContent=`Décisions : ${filled}/${workbook.entries.length}`;document.getElementById("apply").disabled=filled!==workbook.entries.length||document.getElementById("confirm").value!=="APPLIQUER LES 12 DECISIONS";}
function evidenceHtml(records){return records.map(r=>`<div class="evidence"><div class="muted">${esc(r.evidence_id)} — page ${esc(r.page_number)}</div><div>${esc(r.excerpt||"")}</div></div>`).join("");}
function render(){document.getElementById("campaign").textContent=`Campagne : ${workbook.campaign_id}`;const root=document.getElementById("cards");root.innerHTML="";workbook.entries.forEach((e,i)=>{const c=e.candidate,h=e.human_decision;const card=document.createElement("section");card.className="card "+(h.decision?"done":"invalid");card.innerHTML=`<h2>${e.position}. ${esc(c.candidate_id)}</h2><div class="relation"><b>${esc(e.source_title)}</b><br>${esc(c.source)}<br><strong>— ${esc(c.relation)} →</strong><br><b>${esc(e.target_title)}</b><br>${esc(c.target)}</div><p class="muted">Confiance classificatoire non décisionnelle : ${esc(c.confidence)}</p><h3>Preuves documentaires</h3>${evidenceHtml(e.evidence_records)}<div class="grid"><div><label>Décision</label><select data-k="decision">${decisions.map(x=>`<option value="${x}" ${h.decision===x?"selected":""}>${labels[x]}</option>`).join("")}</select></div><div><label>Rôle du réviseur</label><select data-k="reviewer_role">${__ROLES__.map(x=>`<option value="${x}" ${h.reviewer_role===x?"selected":""}>${x}</option>`).join("")}</select></div><div><label>Identifiant du réviseur</label><input data-k="reviewer_id" value="${esc(h.reviewer_id)}"></div><div><label>Relation confirmée</label><input value="${esc(h.confirmed_relation)}" readonly></div><div class="wide"><label>Justification scientifique</label><textarea data-k="rationale">${esc(h.rationale)}</textarea></div><div class="wide small hash">Candidate hash: ${esc(e.candidate_payload_hash)}<br>Evidence hash: ${esc(e.evidence_payload_hash)}</div></div>`;
card.querySelectorAll("[data-k]").forEach(el=>el.addEventListener("input",()=>{h[el.dataset.k]=el.value;card.className="card "+(h.decision?"done":"invalid");count();document.getElementById("saved").textContent="Modifications non sauvegardées";}));root.appendChild(card);});count();}
async function load(){msg("Chargement…");const r=await fetch("/api/workbook",{headers:{"X-Session-Token":TOKEN}});const x=await r.json();if(!r.ok)throw new Error(x.error||"Erreur de chargement");workbook=x.workbook;render();document.getElementById("saved").textContent="État chargé depuis le disque";msg("Interface prête. Aucune décision n’est appliquée automatiquement.","ok");}
async function post(path,body){const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Session-Token":TOKEN},body:JSON.stringify(body)});const x=await r.json();if(!r.ok)throw new Error(x.error||"Erreur");return x;}
document.getElementById("save").onclick=async()=>{try{msg("Sauvegarde atomique en cours…");const x=await post("/api/save",{entries:workbook.entries.map(e=>({candidate_id:e.candidate.candidate_id,human_decision:e.human_decision}))});workbook=x.workbook;render();document.getElementById("saved").textContent=`Sauvegardé : ${x.saved_count}/${x.total_count}`;msg("Décisions sauvegardées. Aucune écriture dans le registre.","ok");}catch(e){msg(e.message,"error")}};
document.getElementById("reload").onclick=()=>load().catch(e=>msg(e.message,"error"));
document.getElementById("confirm").addEventListener("input",count);
document.getElementById("apply").onclick=async()=>{if(!confirm("Confirmer l’écriture irréversible des 12 décisions dans le registre append-only ?"))return;try{msg("Validation et application gouvernée en cours…");const x=await post("/api/apply",{confirmation:document.getElementById("confirm").value});msg(`Campagne appliquée. Décisions: ${x.result.decision_count}; approuvées: ${x.result.approved_count}; non approuvées: ${x.result.non_approved_count}.`,"ok");document.getElementById("apply").disabled=true;}catch(e){msg(e.message,"error")}};
load().catch(e=>msg(e.message,"error"));
</script>
</body></html>"""


def latest_workbook(root: Path = ROOT) -> Path:
    base = root / "theory_evolution/ay1_d1c/campaigns"
    matches = sorted(base.glob("*/human_review/governed_review_workbook.json"))
    if not matches:
        raise FileNotFoundError("No governed_review_workbook.json found; run prepare first")
    return matches[-1].resolve()


def validate_workbook_path(path: Path, root: Path = ROOT) -> Path:
    resolved = path.expanduser().resolve()
    allowed = (root / "theory_evolution/ay1_d1c/campaigns").resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise ValueError("workbook must remain under AY1-D1c campaigns") from exc
    if resolved.name != "governed_review_workbook.json" or not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    return resolved


def merge_decisions(workbook: dict[str, Any], submitted: Any) -> tuple[dict[str, Any], int]:
    if not isinstance(submitted, list):
        raise ValueError("entries must be a list")
    by_id = {str(item.get("candidate_id")): item for item in submitted if isinstance(item, dict)}
    expected = {str(entry["candidate"]["candidate_id"]) for entry in workbook["entries"]}
    if set(by_id) != expected:
        raise ValueError("submitted candidate set mismatch")
    saved = 0
    for entry in workbook["entries"]:
        cid = str(entry["candidate"]["candidate_id"])
        payload = by_id[cid].get("human_decision")
        if not isinstance(payload, dict):
            raise ValueError(f"human_decision missing for {cid}")
        current = entry["human_decision"]
        immutable = {
            "confirmed_source": current["confirmed_source"],
            "confirmed_target": current["confirmed_target"],
            "confirmed_relation": current["confirmed_relation"],
        }
        next_value = {
            "decision": str(payload.get("decision") or "").strip().lower(),
            "reviewer_id": str(payload.get("reviewer_id") or "").strip(),
            "reviewer_role": str(payload.get("reviewer_role") or "").strip(),
            "rationale": str(payload.get("rationale") or "").strip(),
            **immutable,
        }
        if next_value["decision"] and next_value["decision"] not in ALLOWED_DECISIONS:
            raise ValueError(f"unsupported decision for {cid}")
        if next_value["reviewer_role"] not in ALLOWED_ROLES:
            raise ValueError(f"unsupported reviewer role for {cid}")
        entry["human_decision"] = next_value
        if next_value["decision"]:
            saved += 1
    workbook["decision_count"] = saved
    return workbook, saved


class State:
    def __init__(self, workbook: Path, token: str):
        self.workbook = workbook
        self.token = token
        self.lock = threading.RLock()
        self.applied = False


class Handler(BaseHTTPRequestHandler):
    server_version = "OCEHumanReviewUI/1.0"

    @property
    def state(self) -> State:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[review-ui] {self.address_string()} {fmt % args}")

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        return secrets.compare_digest(self.headers.get("X-Session-Token", ""), self.state.token)

    def _body(self) -> Any:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > 2_000_000:
            raise ValueError("request body too large")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            page = HTML.replace("__TOKEN__", json.dumps(self.state.token)).replace("__ROLES__", json.dumps(ALLOWED_ROLES))
            body = page.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
            return
        if route == "/api/workbook":
            if not self._authorized():
                self._json(HTTPStatus.FORBIDDEN, {"error": "invalid session token"})
                return
            with self.state.lock:
                self._json(HTTPStatus.OK, {"workbook": readj(self.state.workbook)})
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if not self._authorized():
            self._json(HTTPStatus.FORBIDDEN, {"error": "invalid session token"})
            return
        try:
            payload = self._body()
            if route == "/api/save":
                with self.state.lock:
                    workbook = readj(self.state.workbook)
                    merged, saved = merge_decisions(workbook, payload.get("entries"))
                    atomic_json(self.state.workbook, merged)
                self._json(HTTPStatus.OK, {"saved_count": saved, "total_count": len(merged["entries"]), "workbook": merged, "registry_write_performed": False})
                return
            if route == "/api/apply":
                if payload.get("confirmation") != CONFIRMATION_PHRASE:
                    raise PermissionError("confirmation phrase mismatch")
                with self.state.lock:
                    if self.state.applied:
                        raise RuntimeError("application already performed in this UI session")
                    workbook = readj(self.state.workbook)
                    for entry in workbook["entries"]:
                        validate_entry(entry)
                    result = apply_workbook(self.state.workbook, ROOT)
                    self.state.applied = True
                self._json(HTTPStatus.OK, {"result": result})
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except (ValueError, PermissionError, FileNotFoundError, RuntimeError, KeyError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"unexpected error: {exc}"})


def main() -> int:
    parser = argparse.ArgumentParser(description="Local governed human review interface for AY1-D1c")
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not (1024 <= args.port <= 65535):
        parser.error("--port must be between 1024 and 65535")
    workbook = validate_workbook_path(args.workbook or latest_workbook())
    token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    server.state = State(workbook, token)  # type: ignore[attr-defined]
    url = f"http://{HOST}:{args.port}/"
    print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_READY")
    print(f"url={url}")
    print(f"workbook={workbook}")
    print("bind=127.0.0.1")
    print("auto_promotion_performed=false")
    print("Press Ctrl-C to stop.")
    if not args.no_browser:
        threading.Timer(0.35, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_STOPPED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
