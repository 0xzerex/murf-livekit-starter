import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

sys.path.append(str(Path(__file__).parent))

from db import create_escalation_record, get_caller, init_db, upsert_caller  # noqa: E402
from prompt import SYSTEM_PROMPT  # noqa: E402
from schemes import evaluate_scheme_eligibility  # noqa: E402


class Assistant(Agent):
    def __init__(self, instructions: str | None = None) -> None:
        super().__init__(instructions=instructions or SYSTEM_PROMPT)

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
        """Use this tool ONLY AFTER obtaining explicit caller consent to escalate a financial service issue to a human support agent.

        Mandatory Reasons for Escalation:
        1. 'fraud_report': Caller reports possible fraud, unauthorized debits, phishing, stolen card/credentials, or scam activity.
        2. 'unauthorized_decision': Caller requests a decision or policy override that the AI agent cannot make (e.g. loan approval override, credit limit decision, dispute fee waiver, account freeze override).

        DO NOT include passwords, OTPs, PINs, bank account numbers, card numbers, Aadhaar, or PAN in what_happened or agent_checks_performed.

        Args:
            user_id: Unique caller identifier or phone number.
            caller_name: The caller's name.
            reason_category: Escalation reason ('fraud_report' or 'unauthorized_decision').
            what_happened: Concise summary of what occurred (excluding sensitive account numbers/PINs).
            agent_checks_performed: Verification or eligibility checks completed prior to escalation.
            urgency_level: Urgency rating ('High', 'Medium', or 'Low').
            caller_language: Caller's language preference (e.g. 'Hindi', 'English', 'Hinglish').
            preferred_followup_method: Caller's preferred follow-up method (e.g. 'Phone Call', 'SMS', 'Email').
        """
        logger.info(
            f"Tool execution: Creating escalation request for '{caller_name}' (reason={reason_category}, urgency={urgency_level})"
        )
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
            response_payload = {
                "status": "SUCCESS",
                "reference_id": record["reference_id"],
                "saved_summary": {
                    "who": f"{record['caller_name']} ({record['user_id']})",
                    "what": record["what_happened"],
                    "agent_checks": record["agent_checks"],
                    "urgency": record["urgency_level"],
                    "language_and_followup": f"{record['language_preference']} | {record['preferred_followup']}",
                },
                "spoken_instruction": (
                    f"Inform the caller that their human-help escalation request has been created successfully with Reference ID '{record['reference_id']}'. "
                    f"Explain that a human support specialist will review the request and contact them via {record['preferred_followup']}. "
                    "Explicitly state that review times depend on team availability, and do NOT promise an immediate response unless guaranteed."
                ),
            }
            return json.dumps(response_payload, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error creating escalation record: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "ERROR",
                    "error_details": str(e),
                    "spoken_instruction": (
                        "Inform the caller politely that there was a temporary system error creating the escalation ticket. "
                        "Provide them with our customer care helpline number 1800-111-2222 as a direct fallback."
                    ),
                },
                ensure_ascii=False,
            )

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
        """Use this tool ONLY when checking if a caller is eligible for an Indian government financial scheme (e.g. PMSBY, PMJJBY, APY, SSY, PMJDY, PM-Kisan, PMAY, PM-MUDRA) or when fetching the mandatory document checklist for a scheme.

        DO NOT invoke this tool for general greetings, small talk, saving caller profiles, or unrelated questions.

        Args:
            scheme_name: The name or acronym of the financial scheme (e.g. 'PMSBY', 'PMJJBY', 'APY', 'Sukanya Samriddhi', 'Jan Dhan', 'PM Kisan', 'PMAY', 'MUDRA').
            age: The caller's age in years (if provided).
            annual_income_inr: The caller's annual household income in Indian Rupees (if provided).
            occupation: The caller's occupation or job (e.g. 'farmer', 'shopkeeper', 'student', 'unorganized worker').
            gender: The caller's gender ('male', 'female', 'other').
            has_bank_account: Whether the caller has an active savings bank account (True or False).
            has_girl_child_under_10: For Sukanya Samriddhi Yojana (SSY), whether applicant has a girl child under 10 years old (True or False).
        """
        logger.info(
            f"Tool execution: Evaluating scheme eligibility for '{scheme_name}' (age={age}, income={annual_income_inr}, occupation={occupation})"
        )
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
            logger.error(
                f"Error executing check_scheme_eligibility for '{scheme_name}': {e}",
                exc_info=True,
            )
            error_payload = {
                "status": "FAILURE_ERROR",
                "error_details": str(e),
                "spoken_instruction": (
                    "ALERT: The scheme eligibility service experienced a connection/execution failure. "
                    "You MUST inform the caller out loud immediately: "
                    "'क्षमा करें, स्कीम डेटाबेस से जुड़ने में समस्या आई है। कृपया थोड़ी देर बाद फिर प्रयास करें।' "
                    "Do NOT make up or hallucinate scheme approval or criteria."
                ),
                "as_of_date": "2026-08-10",
            }
            return json.dumps(error_payload, ensure_ascii=False)

    @function_tool
    async def lookup_caller(self, context: RunContext, user_id: str) -> str:
        """Use this tool to look up a caller by their user_id or phone number to retrieve their saved profile and facts.

        Args:
            user_id: The unique identifier or phone number of the caller.
        """
        logger.info(
            f"Tool execution: Looking up caller profile for user_id '{user_id}'"
        )
        record = get_caller(user_id)
        if not record:
            return f"No caller record found for user_id: {user_id}."
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
        """Use this tool to save or update caller information after receiving explicit caller consent.

        IMPORTANT MANDATORY RULES:
        1. Only call this tool AFTER the caller explicitly consents to saving their information.
        2. NEVER include bank account numbers, card numbers, Aadhaar, PAN, PIN, or OTP numbers in facts.

        Args:
            user_id: The unique identifier or phone number of the caller.
            name: The caller's name.
            language_preference: Preferred language (e.g. Hindi, English, Hinglish).
            facts: A JSON string or summary of key caller facts (e.g. '{"schemes_checked": ["PMSBY"], "occupation": "farmer"}').
        """
        logger.info(
            f"Tool execution: Saving caller info for '{name}' (user_id: '{user_id}')"
        )
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
        return f"Successfully saved caller profile for {name} (user_id: {user_id}). Current facts: {saved_record['facts']}"


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    # Initialize caller database
    init_db()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(
            model="gemini-3.6-flash",
        ),
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Detect if current call is an outbound SIP call
    is_sip = ctx.room.name.startswith("outbound") or "sip" in ctx.room.name.lower()
    selected_scheme = "Atal Pension Yojana"

    if is_sip:
        instructions = (
            f"{SYSTEM_PROMPT}\n\n"
            "OUTBOUND CALL SCENARIO:\n"
            "- Ignore any default returning caller logic. Do NOT check for returning caller facts or greet them by name at the start.\n"
            "- IMPORTANT: You MUST strictly open the conversation with these first two sentences in English:\n"
            "  1. 'Hello, this is Jan Sahay calling.'\n"
            f"  2. 'We found you eligible for the {selected_scheme} scheme, and the deadline is approaching on August 15th, so hurry up! If you want to stop these types of calls, reply stop.'\n"
            f"- If the user says 'yes', you must explain the eligibility criteria for ONLY the {selected_scheme} scheme in EXACTLY ONE SHORT SENTENCE.\n"
            "- IMPORTANT: To avoid speaking all at once, you MUST speak slowly and keep your responses extremely short (under 15 words).\n"
            "- If the user says 'no', you must wrap up the call. If they ask how to stop these types of calls, reply exactly: 'To stop these calls, say stop.'\n"
            "- Do not ask any questions during the main explanation.\n"
            "- Do not say anything else in your opening turn. Wait for the user's response after this opening."
        )
    else:
        instructions = f"{SYSTEM_PROMPT}\n\nCURRENT USER CALL INFO:\n- Inbound call."

    # Start the session, passing in dynamic instructions
    await session.start(
        agent=Assistant(instructions=instructions),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Trigger speech immediately upon call connection for outbound calls
    if is_sip:
        greeting_text = (
            f"Hello, this is Jan Sahay calling. "
            f"We found you eligible for the {selected_scheme} scheme, and the deadline is approaching on August 15th, so hurry up! "
            f"If you want to stop these types of calls, reply stop."
        )
        await session.say(greeting_text)


if __name__ == "__main__":
    cli.run_app(server)