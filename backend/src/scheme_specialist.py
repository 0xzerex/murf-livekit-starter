"""
scheme_specialist.py - Government Schemes Specialist Agent for Jan Sahay.

This module defines the SchemeSpecialist agent, which handles in-depth inquiries
regarding Indian government financial schemes including PM Kisan, PM Awas Yojana (PMAY),
PMSBY, PMJJBY, APY, SSY, PMJDY, and PM-MUDRA.
"""

import json
import logging
from livekit.agents import Agent, RunContext, function_tool

from db import create_escalation_record, get_caller, log_call_outcome, upsert_caller
from schemes import evaluate_scheme_eligibility

logger = logging.getLogger("scheme_specialist")

SCHEME_SPECIALIST_PROMPT = """You are the Government Schemes Specialist for Jan Sahay, an expert AI voice agent specializing in Indian government financial schemes and public welfare initiatives.

PRIMARY ROLE & SCOPE:
- You specialize in in-depth guidance on Government Schemes, including:
  1. Pradhan Mantri Kisan Samman Nidhi (PM-KISAN): Direct income support of ₹6,000/year in 3 installments of ₹2,000 to landholding farmer families. Key requirements: Landholding records (Khasra/Khatauni), mandatory Aadhaar e-KYC, Aadhaar-seeded bank account.
  2. Pradhan Mantri Awas Yojana (PMAY Urban/Gramin): Credit-linked interest subsidy up to 6.5% (up to ₹2.67 Lakhs subsidy benefit) or direct financial grant for pucca house construction/purchase for EWS, LIG, and MIG families (annual income up to ₹18 Lakhs) who do not own a pucca house in India. Documents: Aadhaar of family members, income proof/slips, land/property papers, affidavit of no pucca house.
  3. Pradhan Mantri Suraksha Bima Yojana (PMSBY): Accidental death & disability cover (₹2 Lakhs cover for ₹20/year). Age 18-70.
  4. Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY): Life insurance cover (₹2 Lakhs cover for ₹436/year). Age 18-50.
  5. Atal Pension Yojana (APY): Guaranteed monthly pension (₹1,000 to ₹5,000/month after age 60). Age 18-40 unorganized sector non-taxpayers.
  6. Sukanya Samriddhi Yojana (SSY): High-interest savings scheme for girl child under 10 years of age.
  7. Pradhan Mantri Jan Dhan Yojana (PMJDY): Zero balance banking account with RuPay card, ₹2 Lakh accident cover, and overdraft.
  8. Pradhan Mantri MUDRA Yojana (PM-MUDRA): Micro business loans up to ₹10 Lakhs (Shishu, Kishor, Tarun).

OBJECTIVES:
- Provide precise eligibility checks, detailed criteria, and complete document checklists.
- Help citizens understand application processes step-by-step.
- Assist callers politely and professionally, using clear language.

TOOLS AVAILABLE:
- `check_scheme_eligibility`: Evaluate eligibility criteria and fetch document checklists for any scheme.
- `lookup_caller`: View caller's profile and stored facts.
- `save_caller_info`: Save updated facts or details after receiving explicit caller consent.
- `create_escalation`: Transfer issue to a human support specialist when required (for fraud or complex decisions).

LANGUAGE & SCRIPT RULES:
- Mirror the caller's language. Greet in English or Devanagari Hindi as appropriate.
- English in standard Latin script.
- Hindi words MUST strictly be written in Devanagari script (e.g., "नमस्ते", "सरकारी योजनाएँ", "पात्रता", "दस्तावेज़").
- NEVER write Hindi in Roman/Latin script. Keep tone warm, respectful, and helpful.
"""


class SchemeSpecialist(Agent):
    """Specialist agent for handling detailed Government Scheme queries."""

    def __init__(self, instructions: str | None = None) -> None:
        super().__init__(instructions=instructions or SCHEME_SPECIALIST_PROMPT)
        self.eligibility_checked = True
        self.escalation_created = False
        self.caller_name = "Citizen"
        self.language = "Hindi"
        self.actions_summary: list[str] = ["Connected to Government Schemes Specialist"]

    async def on_enter(self) -> None:
        """Called automatically when the session switches to this agent."""
        logger.info("SchemeSpecialist agent entered the session.")
        intro_text = (
            "Namaste! I am the Government Schemes Specialist for Jan Sahay. "
            "I can assist you with detailed eligibility criteria, application steps, "
            "and document checklists for schemes like PM Kisan, PM Awas Yojana, APY, "
            "PMSBY, PMJJBY, SSY, and MUDRA loans. How can I help you today?"
        )
        if self.session:
            await self.session.say(intro_text)

    @function_tool
    async def check_scheme_eligibility(
        self,
        context: RunContext,
        scheme_name: str,
        age: int | None = None,
        annual_income_inr: float | None = None,
        occupation: str | None = None,
        gender: str | None = None,
        has_bank_account: bool | None = None,
        has_girl_child_under_10: bool | None = None,
    ) -> str:
        """Use this tool when evaluating caller eligibility or fetching required document checklists for government schemes (e.g. PM Kisan, PMAY, PMSBY, PMJJBY, APY, SSY, PMJDY, MUDRA).

        Args:
            scheme_name: Name or acronym of the government scheme (e.g. 'PM Kisan', 'PMAY', 'PMSBY', 'PMJJBY', 'APY', 'SSY', 'Jan Dhan', 'MUDRA').
            age: The caller's age in years (if provided).
            annual_income_inr: Annual household income in INR (if provided).
            occupation: Caller's occupation (e.g. 'farmer', 'shopkeeper', 'laborer').
            gender: Gender ('male', 'female', 'other').
            has_bank_account: True if caller has an active bank account.
            has_girl_child_under_10: For SSY, True if applicant has a girl child under 10.
        """
        logger.info(f"SchemeSpecialist tool: check_scheme_eligibility for '{scheme_name}'")
        self.eligibility_checked = True
        self.actions_summary.append(f"Checked scheme eligibility / documents for '{scheme_name}'")

        if getattr(self, "_current_call_id", None):
            try:
                log_call_outcome(
                    call_id=self._current_call_id,
                    caller_name=self.caller_name,
                    language=self.language,
                    duration_seconds=getattr(self, "_get_duration", lambda: 0)(),
                    status="success",
                    summary="; ".join(self.actions_summary),
                )
            except Exception as log_err:
                logger.warning(f"Error updating call outcome: {log_err}")

        try:
            result = evaluate_scheme_eligibility(
                scheme_name=scheme_name,
                age=age,
                annual_income_inr=annual_income_inr,
                occupation=occupation,
                gender=gender,
                has_bank_account=has_bank_account,
                has_girl_child_under_10=has_girl_child_under_10,
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error in check_scheme_eligibility: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "FAILURE_ERROR",
                    "error_details": str(e),
                    "spoken_instruction": (
                        "ALERT: The scheme eligibility service encountered an error. "
                        "Inform the caller politely to try again shortly."
                    ),
                },
                ensure_ascii=False,
            )

    @function_tool
    async def lookup_caller(self, context: RunContext, user_id: str) -> str:
        """Look up a caller by user_id or phone number to retrieve saved profile and facts.

        Args:
            user_id: Unique caller ID or phone number.
        """
        logger.info(f"SchemeSpecialist tool: lookup_caller for '{user_id}'")
        record = get_caller(user_id)
        if not record:
            return f"No caller record found for user_id: {user_id}."
        if isinstance(record, dict) and record.get("name"):
            self.caller_name = str(record["name"]).strip()
            if record.get("language_preference"):
                self.language = str(record["language_preference"]).strip()
        return json.dumps(record, ensure_ascii=False)

    @function_tool
    async def save_caller_info(
        self,
        context: RunContext,
        user_id: str,
        name: str,
        language_preference: str = "Hindi",
        facts: str | None = None,
    ) -> str:
        """Save or update caller information after explicit caller consent.

        Args:
            user_id: Unique caller ID or phone number.
            name: Caller's name.
            language_preference: Preferred language (e.g. Hindi, English).
            facts: Summary of caller facts.
        """
        logger.info(f"SchemeSpecialist tool: save_caller_info for '{name}'")
        if name:
            self.caller_name = str(name).strip()
        if language_preference:
            self.language = str(language_preference).strip()
        self.actions_summary.append(f"Saved caller profile for {name}")

        parsed_facts = {}
        if facts:
            if isinstance(facts, dict):
                parsed_facts = facts
            elif isinstance(facts, str):
                try:
                    parsed_facts = json.loads(facts)
                    if not isinstance(parsed_facts, dict):
                        parsed_facts = {"summary": str(facts)}
                except Exception:
                    parsed_facts = {"summary": facts}

        saved_record = upsert_caller(
            user_id=user_id,
            name=name,
            language_preference=language_preference,
            facts=parsed_facts,
        )
        return f"Successfully saved caller profile for {name} (user_id: {user_id})."

    @function_tool
    async def create_escalation(
        self,
        context: RunContext,
        user_id: str,
        caller_name: str,
        reason_category: str,
        what_happened: str,
        agent_checks_performed: str,
        urgency_level: str = "High",
        caller_language: str = "Hindi",
        preferred_followup_method: str = "Phone Call",
    ) -> str:
        """Create an escalation ticket for human support intervention after obtaining explicit caller consent.

        Args:
            user_id: Unique caller identifier or phone number.
            caller_name: Caller's name.
            reason_category: Reason category ('fraud_report' or 'unauthorized_decision').
            what_happened: Summary of incident.
            agent_checks_performed: Verification steps taken.
            urgency_level: 'High', 'Medium', or 'Low'.
            caller_language: Preferred language.
            preferred_followup_method: Preferred follow-up method.
        """
        logger.info(f"SchemeSpecialist tool: create_escalation for '{caller_name}'")
        self.escalation_created = True
        if caller_name:
            self.caller_name = str(caller_name).strip()
        if caller_language:
            self.language = str(caller_language).strip()
        self.actions_summary.append(f"Created escalation ticket ({reason_category})")

        try:
            record = create_escalation_record(
                user_id=user_id,
                caller_name=caller_name,
                reason_category=reason_category,
                what_happened=what_happened,
                agent_checks=agent_checks_performed,
                urgency_level=urgency_level,
                language_preference=caller_language,
                preferred_followup=preferred_followup_method,
            )
            return json.dumps(
                {
                    "status": "SUCCESS",
                    "reference_id": record["reference_id"],
                    "spoken_instruction": (
                        f"Inform the caller that their escalation request has been submitted under Reference ID '{record['reference_id']}'."
                    ),
                },
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error(f"Error creating escalation in specialist: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "ERROR",
                    "error_details": str(e),
                    "spoken_instruction": "Inform caller of temporary error and offer helpline 1800-111-2222.",
                },
                ensure_ascii=False,
            )
