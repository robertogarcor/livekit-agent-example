# LIVEKIT AGENT EXAMPLE

Ejemplo agente livekit console mode (console | dev) con tools, video, audio y texto.
Incluye agente con injección/conocimiento de skills para el agente.

## Stack

- Python 3.10+
- LiveKit Agents SDK
- Gemini Realtime (`gemini-2.5-flash-native-audio-latest` or `gemini-3.1-flash-live-preview`)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env or cp .env.example .env.local (Server livekit local)
# Edita .env or .env.local con tus credenciales

python agent_live_basic.py console (dev -> mode server)
python agent_live_tools.py console (dev -> mode server)
python agent_live_multimodal.py console (dev -> mode server)
python agent_live_multimodal_skills.py console (dev -> mode server)

```

## Gemini: API KEY and model Gemini Live

1. Crea cuenta en Google AI Studio: `https://aistudio.google.com/`
2. Crea un proyecto en el portal.
3. Crea una API KEY para el proyecto.
4. Pega la api key y el model live en `.env`.


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
3. Usa la URL y credenciales de ese servidor en `.env or .env.local`.
4. Arranca el agente basico, tools o multimodal|skills con: 
- `python agent_live_basic|tools|multimodal|skills.py console`.

Referencias:

- `https://github.com/livekit`
- `https://docs.livekit.io/transport/self-hosting/local/`

Nota: el código del agente no cambia entre Cloud y self-hosted; cambia la infraestructura (operación, TLS, red y mantenimiento).

## Skills del agente

Las skills son documentos Markdown en `.agents/.skills/<name>/SKILL.md`
que el agente carga bajo demanda con `get_skill(name)`.

### Convencion

Cada `SKILL.md` empieza con front matter YAML (sin comillas, sin comas):

```yaml
---
name: <debe coincidir con el nombre del directorio>
description: <obligatorio, texto corto que ve el LLM en su prompt>
---
```

El `name` del front matter debe coincidir con el nombre del directorio para mantener coherencia e integridad. El sistema usa el directorio como identificador; el `name` del YAML es una declaracion que deberia reflejarlo.

El cuerpo del Markdown (despues del `---`) es el contenido completo que
recibe el agente al cargar la skill. Puede incluir ROLE, instrucciones,
tablas, ejemplos, etc.

### Carga bajo demanda

El prompt del agente incluye un bloque `## SKILLS DISPONIBLES` generado
automaticamente que lista `name: description` de todas las skills en disco.
Cuando la consulta del usuario encaja con una skill, el LLM usa la tool
`get_skill(name)` para cargar el manual y responder basandose en el.

### Skills actuales

| Skill | Descripcion |
|---|---|
| test-skill | Skill de prueba. |
| manual-markdown | Referencia rapida de sintaxis Markdown. |

### Anadir una skill

1. Crear `.agents/.skills/<nombre>/SKILL.md`
2. Escribir front matter (`description` obligatorio) + contenido
3. Sin tocar codigo -- el discovery es automatico

## Tools

- `get_time`, `get_weather`, `search_web`, `send_email`, `get_skill`, `list_skills`


