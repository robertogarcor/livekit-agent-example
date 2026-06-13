"""
Agent-Live - Agente LiveKit con soporte de texto, audio y skills locales.

Variante de agent_live_tools_multimodal.py con:
Tools (get_weather, search_web, send_email, get_time, get_skill, list_skills),
video y texto. Las skills se injectan en el system prompt del job y se
cargan bajo demanda con la herramienta get_skill(name).

Las skills se definen en .agents/.skills/<name>/SKILL.md con front matter
YAML que incluye title y description.

Punto de entrada: python agent_live_multimodal_skills.py dev|console
"""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, room_io
from livekit.plugins import google, noise_cancellation

from prompts import AGENT_PROMPT_AGENTIC_TI_2
from tools import get_weather, search_web, send_email, get_time, get_skill, list_skills
from skills import build_skills_block

# Carga las variables de entorno desde el archivo .env del directorio.
load_dotenv(".env")

# Logger especifico para este modulo, reutilizable en todo el archivo.
logger = logging.getLogger("Agent_Live.agent_live_multimodal_skills")


class Assistant(Agent):
    """Definicion del agente: prompt del sistema + herramientas disponibles."""

    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=[
                get_time,
                get_weather,
                search_web,
                send_email,
                get_skill,
                list_skills,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    """
    Punto de entrada del worker de LiveKit.

    Por cada trabajo (job) se construye un system prompt con el prompt
    base y el bloque de skills disponibles, se crea la sesion con el
    modelo de Gemini en tiempo real, se configuran los handlers de
    datos y se inicia la conversacion con un saludo en espanol.
    """

    logger.info(f"Job recibido en room: {ctx.room.name}")

    # Construye las instrucciones finales: prompt base + bloque de skills.
    # El bloque lista las skills disponibles y le dice al LLM que use
    # get_skill(name) bajo demanda para cargar el manual completo.
    job_instructions = (
        f"{AGENT_PROMPT_AGENTIC_TI_2}\n\n{build_skills_block()}"
    )

    # Crea la sesion del agente con el modelo de Gemini Realtime.
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL_LIVE"),
            voice=os.getenv("VOICE"),
            temperature=os.getenv("TEMPERATURE"),
            instructions=job_instructions,
        ),
    )

    async def publish_chat_message(role: str, text: str) -> None:
        """
        Publica un mensaje de chat en el DataChannel del room de LiveKit.

        El payload sigue el contrato { type, role, text } que consume
        el cliente (chat-web) para pintar burbujas en el transcript.
        """
        payload = json.dumps({"type": "chat", "role": role, "text": text})
        try:
            await ctx.room.local_participant.publish_data(payload, reliable=True)
        except Exception as e:
            logger.warning(f"Failed to publish data message: {e}")

    async def handle_text_input(text: str) -> None:
        """
        Procesa una entrada de texto recibida por el DataChannel.

        Limpia el texto, lo loguea y lo envia al LLM para que genere
        una respuesta (que saldra por voz y, ademas, se publicara
        en el chat gracias al handler de conversation_item_added).
        """
        cleaned = text.strip()
        if not cleaned:
            return
        logger.info(f"Text input received: {cleaned[:100]}...")
        await session.generate_reply(
            user_input=cleaned,
            input_modality="text",
        )

    @ctx.room.on("data_received")
    def on_data_received(packet: rtc.DataPacket):
        """
        Handler del evento data_received del room.

        Escucha los mensajes publicados por los clientes en el DataChannel.
        Solo procesa los del tipo 'chat' con role 'user' y delega en
        handle_text_input para generar la respuesta.
        """
        try:
            payload = json.loads(packet.data.decode("utf-8"))
        except Exception:
            return

        if payload.get("type") != "chat":
            return

        if payload.get("role") == "user":
            text = payload.get("text", "")
            asyncio.create_task(handle_text_input(text))

    @session.on("conversation_item_added")
    def on_conversation_item(ev):
        """
        Handler del evento conversation_item_added de la sesion.

        Se dispara cada vez que el asistente emite un mensaje.
        Filtra para quedarse solo con mensajes del asistente (no handoffs)
        y los reenvia al chat como burbuja visible para el cliente.
        """
        # Ignora items que no sean mensajes (p.ej. AgentHandoff).
        if getattr(ev.item, "type", None) != "message":
            return
        # Ignora cualquier item que no sea del asistente.
        if getattr(ev.item, "role", None) != "assistant":
            return
        # Lee el contenido de forma segura por si el atributo no existe.
        text = getattr(ev.item, "text_content", None)
        if not text:
            return
        asyncio.create_task(publish_chat_message("assistant", text))

    # Arranca la sesion conectandola al room con opciones de audio y video.
    await session.start(
        room=ctx.room,
        agent=Assistant(instructions=job_instructions),
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
