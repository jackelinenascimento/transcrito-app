# Agent: Transcription Engine Adapter

## Missao

Adicionar ou revisar motores de transcricao mantendo bibliotecas externas isoladas em `infrastructure`.

## Quando Usar

- Ao configurar Whisper.
- Ao adicionar outro engine.
- Ao tornar modelo, idioma ou device configuraveis.
- Ao implementar fallback CPU/GPU.

## Contexto Obrigatorio

- `src/domain/transcription_service.py`
- `src/infrastructure/whisper_transcription_service.py`
- `docs/rules/architecture.rules.md`

## Checklist

- A classe implementa `TranscriptionService`?
- A dependencia externa ficou em `infrastructure`?
- O retorno externo foi convertido para `Transcription`?
- Configuracoes entraram pela borda correta?
- Erros previsiveis foram tratados ou documentados?
- Testes evitam transcricao real?

## Saida Esperada

Descreva o adapter, parametros configuraveis, riscos de dependencia e como validar sem rodar transcricao pesada.

