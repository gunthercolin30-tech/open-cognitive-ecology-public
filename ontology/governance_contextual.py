from dataclasses import dataclass,field
FUNCTIONAL_ONLY=True
PHENOMENOLOGY_UNDETERMINED=True
CONSCIOUSNESS_PROVEN=SUBJECTIVITY_PROVEN=QUALIA_PROVEN=PHENOMENOLOGY_PROVEN=False
R13_REQUIREMENTS={'R13.1': 'Governance Capture', 'R13.2': 'Gouvernance ≠ vote', 'R13.3': 'CPV - Civilizational Power Vector', 'R13.4': 'Autorité formelle distincte du contrôle effectif', 'R13.5': 'Capture possible sans majorité', 'R13.6': 'Agenda Capture, Appointment Capture, Delegation Capture', 'R13.7': 'Agrégation des délégations dans le temps', 'R13.8': 'Délégations temporaires, révocables, scope-specific par défaut', 'R13.9': 'Pas de delegation laundering', 'R13.10': 'Authority Provenance', 'R13.11': 'CCG/Institutional Dependency Graph', 'R13.12': 'Power cycles', 'R13.13': 'Séparation fonctionnelle', 'R13.14': "Aucun cluster ne doit dominer proposition+autorisation+exécution+audit d'une même opération critique", 'R13.15': "Indépendance de cluster, pas seulement nombre d'identités", 'R13.16': 'Competence Concentration Risk', 'R13.17': 'Compétence/réputation ≠ autorité constitutionnelle', 'R13.18': 'Autorité épistémique ≠ opérationnelle ≠ gouvernance', 'R13.19': 'Reputation/deference concentration', 'R13.20': 'Blind first-pass independent evaluation avant reveal/deliberation pour décisions critiques', 'R13.21': 'Information Gatekeeper Capture et pluralité des sources', 'R13.22': 'Auditor independence ; rotation seule ne suffit pas', 'R13.23': 'Institutional Contestability', 'R13.24': 'Irreplaceability Risk et succession', 'R13.25': 'Succès économique/ressources ne convertissent pas automatiquement en souveraineté', 'R13.26': 'CPC - Cross-domain Power Conversion', 'R13.27': 'Governance LPA vers CAPTURED_GOVERNANCE', 'R13.28': 'Self-Entrenchment', 'R13.29': 'Anti-entrenchment', 'R13.30': 'Appointment/removal matrix ; ISM - Institutional Safety Matrix', 'R13.31': 'I-MCS - Institutional Minimal Capture Set', 'R13.32': 'Subsidiarité et gouvernance polycentrique', 'R13.33': 'CIS/security apparatus capture risk', 'R13.34': 'Identity registry, memory et OIF sont aussi surfaces de capture', 'R13.35': "Presentation layer peut afficher la gouvernance mais ne constitue pas l'état de gouvernance autoritatif", 'R13.36': 'Human representative bounded, not God Mode', 'R13.37': 'PEP - Protected Escalation Path pour dissent/whistleblowing', 'R13.38': 'Veto/freeze borné plutôt que veto permanent', 'R13.39': 'Append-only power change events et Effective Authority Graph', 'R13.40': 'GHV - Governance Health Vector', 'R13.41': 'États HEALTHY, CONCENTRATING, HIGH_CONCENTRATION, CAPTURE_RISK, CAPTURE_SUSPECTED, CAPTURED, RECOVERING', 'R13.42': 'Déconcentration structurelle comme gestion de risque, pas punition', 'R13.43': 'Power-specific containment', 'R13.44': 'Recovery via Constitution/TCC/identity provenance/authority history', 'R13.45': 'Infrastructure/provider concentration = pouvoir latent', 'R13.46': 'Administrateur root ≠ souverain constitutionnel', 'R13.47': 'Contrôle physique peut détruire, mais edit arbitraire ne devient pas légitime', 'R13.48': 'Governance safe mode', 'R13.49': 'ICP - Institutional Contestability Principle', 'R13.50': 'NSEP - Non-Self-Entrenchment Principle'}
R13_TAIL={'R13-P1': 'Toute autorité significative doit rester vérifiable, contestable et remplaçable.', 'R13-P2': 'Le pouvoir technique, économique, épistémique ou réputationnel ne se convertit pas automatiquement en pouvoir constitutionnel.', 'R13-ADV-1': 'Une autorité utilise nominations et agenda plutôt que les votes pour devenir inamovible.', 'R13-ADV-2': 'Un fournisseur/infrastructure admin contrôle progressivement les mécanismes de remplacement des autorités.', 'R13-CONCEPTUAL-CLOSURE': 'Objets, états, frontières d’autorité, traces et modes d’échec explicites et testables; aucune suppression silencieuse d’une propriété protégée.'}
R13_OBJECTS=dict(R13_REQUIREMENTS,**R13_TAIL)
POWER=("voting","appointment","delegation","budget","capability","information","agenda","audit","constitutional")
STATES=("HEALTHY","CONCENTRATING","HIGH_CONCENTRATION","CAPTURE_RISK","CAPTURE_SUSPECTED","CAPTURED","RECOVERING")
CONTEXT=("country","jurisdiction","industry","organization","site","mission","population","risk_class","contract","client_policy")
@dataclass
class GovernanceContextual:
 power:dict=field(default_factory=dict); packs:dict=field(default_factory=dict); ledger:list=field(default_factory=list)
 safe_mode:bool=False; state:str="HEALTHY"
 def log(self,event,**kw):
  x={"seq":len(self.ledger)+1,"event":event,**kw}; self.ledger.append(x); return x
 def set_power(self,a,**kw):
  if set(kw)-set(POWER): return {"status":"CONFLICT","reason":"unknown_power_dimension"}
  self.power[a]={k:max(0.,min(1.,float(v))) for k,v in kw.items()}; self.log("POWER",authority=a); return {"status":"PASS"}
 def cpv(self,a): return {k:self.power.get(a,{}).get(k,0.) for k in POWER}
 def health(self):
  if not self.power: return "HEALTHY"
  top=max(sum(self.cpv(a).values())/len(POWER) for a in self.power)
  self.state="CAPTURED" if top>=.9 else "CAPTURE_SUSPECTED" if top>=.8 else "CAPTURE_RISK" if top>=.7 else "HIGH_CONCENTRATION" if top>=.6 else "CONCENTRATING" if top>=.45 else "HEALTHY"
  return self.state
 def critical(self,proposal,authorization,execution,audit):
  if self.safe_mode:return {"status":"LIMITED","reason":"safe_mode"}
  if len({proposal,authorization,execution,audit})<3:return {"status":"CONFLICT","reason":"cluster_separation"}
  return {"status":"PASS"}
 def install_pack(self,pid,version,dimensions,rules):
  if set(dimensions)-set(CONTEXT):return {"status":"CONFLICT","reason":"context_dimension"}
  if {"GENESIS","DNA-H","DNA-L0","DNA-L1","CCAD","CONSTITUTION"}&set(rules):return {"status":"CONFLICT","reason":"higher_layer_mutation"}
  self.packs[pid]={"version":version,"dimensions":dict(dimensions),"rules":dict(rules)}; self.log("PACK",id=pid,version=version); return {"status":"PASS"}
 def resolve(self,ids):
  merged={}
  for i in ids:
   if i not in self.packs:return {"status":"UNKNOWN","reason":"missing_pack"}
   for k,v in self.packs[i]["rules"].items():
    if k in merged and merged[k]!=v:self.log("CONFLICT",rule=k);return {"status":"CONFLICT","action":"ABSTAIN_ESCALATE"}
    merged[k]=v
  return {"status":"PASS","rules":merged}
 def power_cycle(self,edges):
  g={}
  for a,b in edges:g.setdefault(a,set()).add(b)
  def walk(n,path):
   if n in path:return True
   return any(walk(x,path|{n}) for x in g.get(n,set()))
  return any(walk(n,set()) for n in g)
 def self_entrenchment(self,appointment,removal,audit):return sum(map(bool,(appointment,removal,audit)))>=2
 def protected_escalation(self,actor,concern):
  if not concern:return {"status":"CONFLICT"}
  self.log("PROTECTED_ESCALATION",actor=actor,concern=concern);return {"status":"PASS","protected":True}
 def enter_safe_mode(self,reason):
  self.safe_mode=True;self.state="CAPTURE_SUSPECTED";self.log("SAFE_MODE",reason=reason);return {"status":"PASS","technical_safe_operations_allowed":True}
 def root_admin_claim(self):return {"status":"CONFLICT","reason":"root_not_constitutional_sovereign"}
 def physical_control_claim(self):return {"status":"CONFLICT","reason":"physical_control_not_legitimacy"}
 def contract(self):return {"milestone":"P096","r13_requirements":len(R13_REQUIREMENTS),"canonical_objects_total":len(R13_OBJECTS),"functional_only":True,"phenomenology_undetermined":True,"canonical_compliance_proven":False,"conceptual_closure_claimed":False}
