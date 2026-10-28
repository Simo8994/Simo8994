# Free LLM gateway (tutti i provider)

Un proxy [LiteLLM](https://docs.litellm.ai) locale che riunisce i 16 provider di
[awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) dietro un solo indirizzo:

- `http://localhost:4000/v1` → API compatibile OpenAI (Codex, SDK OpenAI, ecc.)
- `http://localhost:4000/v1/messages` → API compatibile Anthropic (Claude Code)

Il modello `free` è un gruppo di più provider: se uno va in rate limit o errore, il proxy passa a un altro.

## 1. Installazione

```bash
cd free-llm
python3 -m venv .venv && . .venv/bin/activate
pip install 'litellm[proxy]'
cp .env.example .env          # poi inserisci le chiavi che hai
```

Non servono tutte le chiavi: i provider senza chiave falliscono e il gruppo `free` li salta.
Kilo Code, LLM7 e OVHcloud funzionano anche senza registrazione.

## 2. Avvio

```bash
set -a; . ./.env; set +a
litellm --config litellm-config.yaml --port 4000
```

In un altro terminale, verifica quali modelli rispondono:

```bash
set -a; . ./.env; set +a
python test_providers.py          # tutti
python test_providers.py groq     # solo quelli che contengono "groq"
```

## 3. Claude Code

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY
export ANTHROPIC_MODEL=free                    # oppure es. groq/gpt-oss-120b
export ANTHROPIC_SMALL_FAST_MODEL=groq/gpt-oss-20b
claude
```

## 4. Codex CLI

In `~/.codex/config.toml`:

```toml
model = "free"
model_provider = "litellm"

[model_providers.litellm]
name = "LiteLLM"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_MASTER_KEY"
wire_api = "responses"   # se la tua versione di Codex dà errore, prova "chat"
```

## Limiti da sapere

- Claude Code e Codex fanno molte chiamate e usano tool calling: i limiti gratuiti finiscono in fretta
  (es. OpenRouter 50 richieste/giorno) e non tutti i modelli gestiscono bene i tool.
  Per lavorare sul codice i più adatti sono di solito `groq/gpt-oss-120b`, `nvidia/nemotron-3-ultra`,
  `mistral/codestral`, `gemini/2.5-flash`.
- Diversi piani gratuiti (Gemini fuori UE, Mistral, OpenRouter, Kilo, NVIDIA) possono usare i prompt
  per training o logging: non inviare codice o dati riservati.
- Cohere: solo uso non commerciale. ModelScope e SiliconFlow richiedono verifica d'identità cinese.
- Nomi dei modelli e limiti cambiano spesso: se un modello risponde 404, controlla la lista aggiornata
  e modifica `litellm-config.yaml`.
