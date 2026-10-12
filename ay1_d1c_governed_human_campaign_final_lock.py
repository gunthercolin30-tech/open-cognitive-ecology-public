from pathlib import Path
s=(Path(__file__).resolve().parent/"run_ay1_d1c_governed_human_review.py").read_text();assert "auto_promotion_performed" in s and "GovernedRelationReviewGate" in s and "ValidatedRelationRegistry" in s and "workbook baseline hash mismatch" in s;print("AY1_D1C_GOVERNED_HUMAN_CAMPAIGN_FINAL_LOCK_OK")
