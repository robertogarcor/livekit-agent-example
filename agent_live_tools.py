import os
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation
from livekit.plugins import google
from prompts import AGENT_PROMPT_AGENTIC_TI_1, AGENT_PROMPT_AGENTIC_TI_2
from tools import get_weather, search_web, send_email, get_time

load_dotenv(".env")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_PROMPT_AGENTIC_TI_2,
            tools=[
                get_time,
                get_weather,
                search_web,
                send_email,
            ],
        )
        
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL_LIVE"),
	        voice=os.getenv("VOICE"),
            temperature=os.getenv("TEMPERATURE"),
            instructions="",
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
	    ),
	    video_input=True,
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in Spanish."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
