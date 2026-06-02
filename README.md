# LIVEKIT AGENT EXAMPLE

Ejemplo agente livekit console mode (console | dev) con tools.

## Stack

- Python 3.10+
- LiveKit Agents SDK
- Gemini Realtime (`gemini-2.5-flash-native-audio-latest`)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env or cp .env.example .env.local (Server livekit local)
# Edita .env or .env.local con tus credenciales

python agent_live_basic.py console (dev -> mode server)
python agent_live_tools.py console (dev -> mode server)

```

## LiveKit: Cloud + Self-hosted

### Cloud (recomendado)

1. Crea cuenta en LiveKit Cloud: `https://livekit.com/`
2. Crea un proyecto en el portal.
3. Copia `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`.
4. Pega esas variables en `.env`.
5. Indica/adapta el prompt del agente segun necesidades de comportamiento.
6. Arranca el agente basico o con tools con `python agent_live_tools.py console`.

Referencias oficiales LiveKit:

- `https://livekit.com/`
- `https://docs.livekit.io/intro/overview/`
- `https://docs.livekit.io/agents/start/voice-ai/`
- `https://docs.livekit.io/agents/playground/` (Playground para probar el agente)

### Self-hosted (alternativa)

1. Despliega un servidor LiveKit propio.
2. Arranca el servidor LiveKit local siguiendo la guia oficial.
3. Usa la URL y credenciales de ese servidor en `.env.local`.
4. Arranca el agente basico o con tools con `python agent_live_tools.py console`.

Referencias:

- `https://github.com/livekit`
- `https://docs.livekit.io/transport/self-hosting/local/`

Nota: el código del agente no cambia entre Cloud y self-hosted; cambia la infraestructura (operación, TLS, red y mantenimiento).

## Tools disponibles

- `get_time`, `get_weather`, `search_web`, `send_email`


