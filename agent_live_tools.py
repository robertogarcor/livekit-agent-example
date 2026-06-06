"""
Agent-Live - Agente LiveKit con herramientas (audio unicamente).

Variante con tools (get_weather, search_web, send_email, get_time) y video,
pero SIN soporte de texto por DataChannel.
Es la version 'heredada' anterior a agent_live_tools_multimodal.

Punto de entrada: python agent_live_tools.py dev|console
"""

import logging
import os

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation
from livekit.plugins import google

from prompts import AGENT_PROMPT_AGENTIC_TI_1, AGENT_PROMPT_AGENTIC_TI_2
from tools import get_weather, search_web, send_email, get_time

# Carga las variables de entorno desde el archivo .env del directorio.
load_dotenv(".env")

# Logger especifico de este modulo.
logger = logging.getLogger("Agent_Live.agent_live_tools")

class Assistant(Agent):
    """Definicion del agente: prompt del sistema + herramientas disponibles."""
    
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
    """
    Punto de entrada del worker de LiveKit.

    Por cada trabajo se crea una nueva sesion con el modelo de Gemini
    en tiempo real, se inicia el agente y se lanza un saludo en espanol.
    """
    
    logger.info(f"Job recibido en room: {ctx.room.name}")
    
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL_LIVE"),
	        voice=os.getenv("VOICE"),
            temperature=os.getenv("TEMPERATURE"),
            instructions="",
        ),
    )
    
    # Arranca la sesion conectandola al room con opciones de audio y video.
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # Aplica BVC para participantes SIP y BVC estandar para el resto.
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
	    ),
	    video_input=True,
        ),
    )
    
    # Saludo inicial para que el asistente se presente en espanol.
    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in Spanish."
    )


if __name__ == "__main__":
     # Configuracion basica del logging para que se vean los INFO del agente.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Lanza el worker de LiveKit en modo CLI (dev o console).
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
