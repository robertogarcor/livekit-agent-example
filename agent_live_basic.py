"""
Agent-Live - Agente LiveKit basico (solo audio).

Variante minima del agente: un saludo inicial y un prompt generico.
Sirve como ejemplo/plantilla sin herramientas ni soporte de texto.

Punto de entrada: python agent_live_basic.py dev|console
"""

import logging
import os

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation
from livekit.plugins import google

# Carga las variables de entorno desde el archivo .env del directorio.
load_dotenv(".env")

# Logger especifico de este modulo.
logger = logging.getLogger("Agent_Live.agent_live_basic")

class Assistant(Agent):
    """Definicion del agente: solo prompt del sistema, sin tools."""
    
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

# Servidor del agente (variante con AgentServer en vez de WorkerOptions).
server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):
    """
    Punto de entrada del worker de LiveKit.

    Por cada trabajo se crea una nueva sesion con el modelo de Gemini
    en tiempo real, se inicia el agente y se lanza un saludo en espanol.
    """
    
    logger.info(f"Job recibido en room: {ctx.room.name}")
    
    # Crea la sesion del agente con el modelo de Gemini Realtime.
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL_LIVE"),
            voice=os.getenv("VOICE"),
            temperature=os.getenv("TEMPERATURE"),
            instructions="You are a helpful assistant.",
        ),
    )
    
    # Arranca la sesion conectandola al room (solo audio, sin video en este ejemplo).
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # Aplica BVC para participantes SIP y BVC estandar para el resto.
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )
    
    # Saludo inicial para que el asistente se presente en espanol.
    await session.generate_reply(
        instructions="Your name is Zoe and Greet the user and offer your assistance. You should start by speaking in Spanish."
    )


if __name__ == "__main__":
    # Configuracion basica del logging para que se vean los INFO del agente.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Lanza el worker de LiveKit usando AgentServer.
    agents.cli.run_app(server)
