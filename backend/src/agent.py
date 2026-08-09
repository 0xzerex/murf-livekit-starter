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

from db import get_caller, init_db, upsert_caller  # noqa: E402
from prompt import SYSTEM_PROMPT  # noqa: E402


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

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
        facts: dict | None = None,
    ) -> str:
        """Use this tool to save or update caller information after receiving explicit caller consent.

        IMPORTANT MANDATORY RULES:
        1. Only call this tool AFTER the caller explicitly consents to saving their information.
        2. NEVER include bank account numbers, card numbers, Aadhaar, PAN, PIN, or OTP numbers in facts.

        Args:
            user_id: The unique identifier or phone number of the caller.
            name: The caller's name.
            language_preference: Preferred language (e.g. Hindi, English, Hinglish).
            facts: Key-value facts (e.g. schemes_checked, eligibility answers, occupation).
        """
        logger.info(
            f"Tool execution: Saving caller info for '{name}' (user_id: '{user_id}')"
        )
        saved_record = upsert_caller(
            user_id=user_id,
            name=name,
            language_preference=language_preference,
            facts=facts or {},
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

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
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


if __name__ == "__main__":
    cli.run_app(server)
