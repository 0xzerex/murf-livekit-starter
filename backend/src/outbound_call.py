import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit import api

# Load environment variables from .env.local
load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outbound-caller")


def sanitize_sip_target(target: str) -> str:
    """Strips 'sip:' prefix and domain suffix to pass a clean username or phone number to LiveKit."""
    cleaned = target.strip()
    if cleaned.lower().startswith("sip:"):
        cleaned = cleaned[4:]
    if "@" in cleaned:
        cleaned = cleaned.split("@")[0]
    return cleaned


async def make_outbound_call(destination_sip_uri: str, room_name: str = "outbound-room"):
    """
    Creates an explicit agent dispatch and dials out to the target SIP user using Linphone/LiveKit.
    """
    lkapi = api.LiveKitAPI()

    agent_name = os.getenv("AGENT_NAME", "my-agent")
    sip_trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID")
    raw_uri = os.getenv("LINPHONE_SIP_URI", destination_sip_uri)
    
    # Sanitize the target string so LiveKit receives only the username/number
    clean_target = sanitize_sip_target(raw_uri)

    logger.info(f"Dispatching agent '{agent_name}' into room '{room_name}'...")

    # 1. Start/Dispatch your AI agent into the designated room
    try:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room_name,
                metadata="Day 6 Outbound Call for Jan Sahay"
            )
        )
        logger.info(f"Agent dispatch created: {dispatch.id}")
    except Exception as e:
        logger.error(f"Failed to create agent dispatch: {e}")

    # 2. Dial out via SIP to Linphone / phone target
    logger.info(f"Initiating outbound SIP call to '{clean_target}'...")
    try:
        if sip_trunk_id:
            request = api.CreateSIPParticipantRequest(
                sip_trunk_id=sip_trunk_id,
                sip_call_to=clean_target,
                room_name=room_name,
                participant_identity="linphone-user",
                participant_name="Jan Sahay Callee"
            )
        else:
            sip_host = os.getenv("SIP_OUTBOUND_HOST", "sip.linphone.org")
            trunk_config = api.SIPOutboundConfig(
                hostname=sip_host,
                address=sip_host
            )
            request = api.CreateSIPParticipantRequest(
                trunk=trunk_config,
                sip_call_to=clean_target,
                room_name=room_name,
                participant_identity="linphone-user",
                participant_name="Jan Sahay Callee"
            )

        participant = await lkapi.sip.create_sip_participant(request)
        logger.info(f"Outbound call initiated! SIP Participant ID: {participant.participant_id}")
    except Exception as e:
        logger.error(f"Error dialing SIP participant: {e}")
    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    target_uri = os.getenv("LINPHONE_SIP_URI", "sohel786")
    asyncio.run(make_outbound_call(target_uri))