#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

TOTAL_SCORE=0
TOTAL_ITEMS=0

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

has_file() {
  [[ -f "$1" ]]
}

has_dir() {
  [[ -d "$1" ]]
}

contains() {
  local pattern="$1"
  shift

  if [[ "$#" -eq 0 ]]; then
    return 1
  fi

  if command -v rg >/dev/null 2>&1; then
    rg -q -- "$pattern" "$@"
    return
  fi

  grep -R -E -q -- "$pattern" "$@" 2>/dev/null
}

count_matches() {
  local pattern="$1"
  shift

  if [[ "$#" -eq 0 ]]; then
    echo 0
    return
  fi

  if command -v rg >/dev/null 2>&1; then
    rg -- "$pattern" "$@" | wc -l | tr -d ' '
    return
  fi

  grep -R -E -h -- "$pattern" "$@" 2>/dev/null | wc -l | tr -d ' '
}

status_line() {
  local status="$1"
  local message="$2"

  case "$status" in
    pass)
      PASS_COUNT=$((PASS_COUNT + 1))
      printf "  [ok] %s\n" "$message"
      ;;
    warn)
      WARN_COUNT=$((WARN_COUNT + 1))
      printf "  [warn] %s\n" "$message"
      ;;
    fail)
      FAIL_COUNT=$((FAIL_COUNT + 1))
      printf "  [fail] %s\n" "$message"
      ;;
  esac
}

principle() {
  local name="$1"
  local _base_score="$2"
  local reason="$3"

  TOTAL_ITEMS=$((TOTAL_ITEMS + 1))

  printf "\n## %s\n" "$name"
  printf "%s\n" "$reason"
}

print_header() {
  printf "# Architecture Evaluation\n"
  printf "\nProject: transcrito-app\n"
  printf "Root: %s\n" "$ROOT_DIR"
  printf "Date: %s\n" "$(date '+%Y-%m-%d %H:%M:%S')"
  printf "\nGuideline sources:\n"
  printf "%s\n" "- docs/ARCHITECTURE_GUIDELINES.MD"
  printf "%s\n" "- docs/PROJECT_GUIDELINES.MD"
  printf "%s\n" "- docs/EVOLUTION_RULES.MD"
  printf "%s\n" "- docs/rules/*.rules.md"
}

score_dependency_direction() {
  local score=10

  principle "Direcao das Dependencias" "$score" "Verifica se camadas internas nao importam camadas externas."

  if contains "src\\.(application|infrastructure|interfaces)" "src/domain"; then
    status_line fail "domain importa camada externa."
    score=$((score - 4))
  else
    status_line pass "domain nao importa application, infrastructure ou interfaces."
  fi

  if contains "import whisper|from whisper|import torch|from torch|import argparse" "src/application"; then
    status_line fail "application contem dependencia externa/CLI proibida."
    score=$((score - 3))
  else
    status_line pass "application nao importa Whisper, Torch ou argparse."
  fi

  if contains "src\\.infrastructure" "src/domain" "src/application"; then
    status_line fail "domain/application dependem de infrastructure."
    score=$((score - 3))
  else
    status_line pass "domain/application nao dependem de infrastructure."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[0]=$score
}

score_layer_separation() {
  local score=8

  principle "Separacao de Camadas" "$score" "Verifica se cada camada possui responsabilidade clara."

  for path in src/domain src/application src/infrastructure src/interfaces/cli; do
    if has_dir "$path"; then
      status_line pass "Diretorio encontrado: $path."
    else
      status_line fail "Diretorio ausente: $path."
      score=$((score - 2))
    fi
  done

  if contains "print\\(" "src/application"; then
    status_line fail "application contem prints."
    score=$((score - 2))
  else
    status_line pass "application nao contem prints."
  fi

  if contains "argparse" "src/domain" "src/application"; then
    status_line fail "argparse vazou para domain/application."
    score=$((score - 2))
  else
    status_line pass "argparse esta restrito a camada de interface."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[1]=$score
}

score_domain_independence() {
  local score=10

  principle "Dominio Independente" "$score" "Verifica se dominio e pequeno, tipado e sem dependencias externas."

  if has_file "src/domain/transcription.py" && has_file "src/domain/transcription_service.py"; then
    status_line pass "Entidade e contrato de transcricao existem."
  else
    status_line fail "Arquivos centrais do dominio estao ausentes."
    score=$((score - 4))
  fi

  if contains "@dataclass" "src/domain/transcription.py"; then
    status_line pass "Entidades usam dataclass."
  else
    status_line warn "Entidades nao usam dataclass."
    score=$((score - 1))
  fi

  if contains "ABC|abstractmethod" "src/domain/transcription_service.py"; then
    status_line pass "Contrato usa ABC/abstractmethod."
  else
    status_line warn "Contrato nao usa ABC/abstractmethod."
    score=$((score - 1))
  fi

  if contains "whisper|torch|argparse|Path|open\\(" "src/domain"; then
    status_line fail "Dominio contem detalhe externo ou IO."
    score=$((score - 4))
  else
    status_line pass "Dominio nao contem Whisper, Torch, argparse ou IO concreto."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[2]=$score
}

score_use_cases() {
  local score=8

  principle "Casos de Uso" "$score" "Verifica se application orquestra contratos e evita detalhes externos."

  if has_file "src/application/transcribe_video.py"; then
    status_line pass "Caso de uso TranscribeVideo existe."
  else
    status_line fail "Caso de uso principal ausente."
    score=$((score - 4))
  fi

  if contains "TranscriptionService" "src/application/transcribe_video.py"; then
    status_line pass "Caso de uso depende do contrato de transcricao."
  else
    status_line warn "Caso de uso nao referencia TranscriptionService."
    score=$((score - 1))
  fi

  if contains "FileWriter" "src/application/transcribe_video.py"; then
    status_line warn "Caso de uso depende de FileWriter concreto."
    score=$((score - 1))
  else
    status_line pass "Caso de uso nao depende de writer concreto."
  fi

  if contains "whisper|argparse|print\\(" "src/application/transcribe_video.py"; then
    status_line fail "Caso de uso contem detalhe de infraestrutura/interface."
    score=$((score - 3))
  else
    status_line pass "Caso de uso sem Whisper, argparse ou prints."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[3]=$score
}

score_infrastructure_isolation() {
  local score=8

  principle "Infraestrutura Isolada" "$score" "Verifica adapter Whisper e conversao para entidades de dominio."

  if has_file "src/infrastructure/whisper_transcription_service.py"; then
    status_line pass "Adapter Whisper existe."
  else
    status_line fail "Adapter Whisper ausente."
    score=$((score - 4))
  fi

  if contains "TranscriptionService" "src/infrastructure/whisper_transcription_service.py"; then
    status_line pass "Adapter implementa contrato do dominio."
  else
    status_line fail "Adapter nao referencia TranscriptionService."
    score=$((score - 2))
  fi

  if contains "TranscriptionSegment|Transcription\\(" "src/infrastructure/whisper_transcription_service.py"; then
    status_line pass "Adapter converte retorno externo para entidades do dominio."
  else
    status_line fail "Adapter pode estar vazando retorno externo."
    score=$((score - 3))
  fi

  if contains "warnings\\.filterwarnings\\(\"ignore\"\\)" "src/infrastructure/whisper_transcription_service.py"; then
    status_line warn "Warnings sao suprimidos globalmente."
    score=$((score - 1))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[4]=$score
}

score_cli_thinness() {
  local score=8

  principle "CLI Fina" "$score" "Verifica se CLI adapta entrada e delega para casos de uso."

  if contains "argparse" "src/interfaces/cli/commands.py"; then
    status_line pass "argparse esta na camada CLI."
  else
    status_line warn "CLI nao usa argparse ou arquivo mudou."
    score=$((score - 1))
  fi

  if contains "TranscribeVideo" "src/interfaces/cli/commands.py"; then
    status_line pass "CLI delega para caso de uso."
  else
    status_line fail "CLI nao delega para TranscribeVideo."
    score=$((score - 3))
  fi

  if contains "Whisper \\(base \\| CPU\\)" "src/interfaces/cli/commands.py"; then
    status_line warn "CLI contem texto fixo de engine/modelo/device."
    score=$((score - 1))
  fi

  if contains "writer\\.write|model\\.transcribe|whisper" "src/interfaces/cli/commands.py"; then
    status_line fail "CLI contem escrita direta ou detalhe de engine."
    score=$((score - 3))
  else
    status_line pass "CLI nao chama Whisper nem writer diretamente."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[5]=$score
}

score_formatters_writers() {
  local score=8

  principle "Formatadores e Writers" "$score" "Verifica separacao entre formatar e persistir."

  if has_file "src/application/formatters/base_formatter.py" && has_file "src/application/formatters/timestamp_formatter.py"; then
    status_line pass "Contrato e formatter atual existem."
  else
    status_line fail "Contrato ou formatter atual ausente."
    score=$((score - 3))
  fi

  if contains "open\\(|write\\(" "src/application/formatters"; then
    status_line fail "Formatter contem IO/escrita."
    score=$((score - 3))
  else
    status_line pass "Formatters nao escrevem arquivos."
  fi

  if contains "open\\(.+encoding=\"utf-8\"" "src/application/writers/file_writer.py"; then
    status_line pass "FileWriter escreve texto com UTF-8."
  else
    status_line warn "FileWriter nao declara UTF-8 ou arquivo mudou."
    score=$((score - 1))
  fi

  if has_file "src/application/writers/base_writer.py"; then
    status_line pass "Existe contrato abstrato de writer."
  else
    status_line warn "Nao ha contrato abstrato de writer."
    score=$((score - 1))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[6]=$score
}

score_configuration() {
  local score=7

  principle "Configuracao Pela Borda" "$score" "Verifica se modelo, device, idioma e formato sao configuraveis."

  if contains "WhisperTranscriptionService\\(\"base\"\\)" "src/main.py"; then
    status_line warn "Modelo base esta fixo no composition root."
    score=$((score - 1))
  else
    status_line pass "Modelo nao parece fixo em main.py."
  fi

  if contains "device=\"cpu\"" "src/infrastructure"; then
    status_line warn "Device CPU esta fixo na infraestrutura."
    score=$((score - 1))
  else
    status_line pass "Device parece configuravel."
  fi

  if contains "language=\"pt\"" "src/infrastructure"; then
    status_line warn "Idioma pt esta fixo na infraestrutura."
    score=$((score - 1))
  else
    status_line pass "Idioma parece configuravel."
  fi

  if contains "--format|--model|--language|--device" "src/interfaces/cli/commands.py"; then
    status_line pass "CLI expoe parametros configuraveis."
  else
    status_line warn "CLI ainda nao expoe model/language/device/format."
    score=$((score - 1))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[7]=$score
}

score_error_handling() {
  local score=6

  principle "Tratamento de Erros" "$score" "Verifica validacoes e tratamento de falhas esperadas."

  if contains "exists\\(\\)" "src/interfaces/cli/commands.py"; then
    status_line pass "CLI valida existencia do video."
  else
    status_line fail "CLI nao valida existencia do video."
    score=$((score - 2))
  fi

  if contains "try:|except " "src"; then
    status_line pass "Existe tratamento com try/except."
  else
    status_line warn "Nao ha try/except para falhas de Whisper, ffmpeg ou escrita."
    score=$((score - 2))
  fi

  if contains "ffmpeg" "src"; then
    status_line pass "Codigo menciona/verifica ffmpeg."
  else
    status_line warn "Codigo nao verifica ffmpeg."
    score=$((score - 1))
  fi

  if contains "mkdir\\(exist_ok=True\\)" "src/interfaces/cli/commands.py"; then
    status_line warn "mkdir nao usa parents=True para paths aninhados."
    score=$((score - 1))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[8]=$score
}

score_extensibility() {
  local score=8

  principle "Extensibilidade" "$score" "Verifica pontos de extensao para engines, formatos e CLI."

  if has_file "src/domain/transcription_service.py"; then
    status_line pass "Contrato permite novos engines."
  else
    status_line fail "Contrato de engine ausente."
    score=$((score - 3))
  fi

  if has_file "src/application/formatters/base_formatter.py"; then
    status_line pass "Contrato permite novos formatadores."
  else
    status_line fail "Contrato de formatter ausente."
    score=$((score - 3))
  fi

  if has_file "src/application/writers/base_writer.py"; then
    status_line pass "Contrato permite novos writers."
  else
    status_line warn "Extensao de writers ainda depende de concreto."
    score=$((score - 1))
  fi

  if contains "subparsers|add_subparsers" "src/interfaces/cli/commands.py"; then
    status_line pass "CLI ja suporta subcomandos."
  else
    status_line warn "CLI ainda nao tem subcomandos, ok para fase atual."
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[9]=$score
}

score_testability() {
  local score=6

  principle "Testabilidade" "$score" "Verifica existencia de testes e facilidade de isolar dependencias."

  if has_dir "tests"; then
    status_line pass "Diretorio tests existe."
  else
    status_line warn "Nao existe diretorio tests."
    score=$((score - 2))
  fi

  if contains "TranscriptionService" "src/application/transcribe_video.py"; then
    status_line pass "Caso de uso pode receber fake de TranscriptionService."
  else
    status_line warn "Caso de uso nao usa contrato claro para fake de service."
    score=$((score - 1))
  fi

  if contains "FileWriter" "src/application/transcribe_video.py"; then
    status_line warn "Writer concreto reduz isolamento em teste."
    score=$((score - 1))
  fi

  if python3 -m compileall -q src; then
    status_line pass "src compila com python3 -m compileall -q src."
  else
    status_line fail "src nao compila."
    score=$((score - 4))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[10]=$score
}

score_documentation() {
  local score=10

  principle "Documentacao Arquitetural" "$score" "Verifica guidelines, rules, agents e mapa estrutural."

  for path in \
    README.md \
    docs/ARCHITECTURE_GUIDELINES.MD \
    docs/PROJECT_GUIDELINES.MD \
    docs/EVOLUTION_RULES.MD \
    docs/rules/README.md \
    docs/agents/README.md \
    projectStructure.json
  do
    if has_file "$path"; then
      status_line pass "Documento encontrado: $path."
    else
      status_line fail "Documento ausente: $path."
      score=$((score - 1))
    fi
  done

  if python3 -m json.tool projectStructure.json >/dev/null; then
    status_line pass "projectStructure.json e JSON valido."
  else
    status_line fail "projectStructure.json invalido."
    score=$((score - 3))
  fi

  [[ "$score" -lt 1 ]] && score=1
  SCORES[11]=$score
}

print_summary() {
  local sum=0

  for score in "${SCORES[@]}"; do
    sum=$((sum + score))
  done

  local count="${#SCORES[@]}"
  local average
  average="$(awk "BEGIN { printf \"%.1f\", $sum / $count }")"

  printf "\n# Summary\n"
  printf "\nOverall architecture score: %s/10\n" "$average"
  printf "Checks: %s ok, %s warnings, %s failures\n" "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"

  printf "\nScores:\n"
  printf "%s\n" "- Direcao das Dependencias: ${SCORES[0]}/10"
  printf "%s\n" "- Separacao de Camadas: ${SCORES[1]}/10"
  printf "%s\n" "- Dominio Independente: ${SCORES[2]}/10"
  printf "%s\n" "- Casos de Uso: ${SCORES[3]}/10"
  printf "%s\n" "- Infraestrutura Isolada: ${SCORES[4]}/10"
  printf "%s\n" "- CLI Fina: ${SCORES[5]}/10"
  printf "%s\n" "- Formatadores e Writers: ${SCORES[6]}/10"
  printf "%s\n" "- Configuracao Pela Borda: ${SCORES[7]}/10"
  printf "%s\n" "- Tratamento de Erros: ${SCORES[8]}/10"
  printf "%s\n" "- Extensibilidade: ${SCORES[9]}/10"
  printf "%s\n" "- Testabilidade: ${SCORES[10]}/10"
  printf "%s\n" "- Documentacao Arquitetural: ${SCORES[11]}/10"

  printf "\nRecommended next steps:\n"
  printf "1. Implementar SRT como proxima fatia vertical pequena.\n"
  printf "2. Adicionar selecao real de formatter quando --format ganhar novos formatos.\n"
  printf "3. Avaliar subcomandos CLI quando houver batch, srt ou outros fluxos.\n"
  printf "4. Refinar tratamento de erros com excecoes especificas de infraestrutura/escrita.\n"
  printf "5. Atualizar projectStructure.json quando a estrutura estabilizar.\n"
}

SCORES=(0 0 0 0 0 0 0 0 0 0 0 0)

print_header
score_dependency_direction
score_layer_separation
score_domain_independence
score_use_cases
score_infrastructure_isolation
score_cli_thinness
score_formatters_writers
score_configuration
score_error_handling
score_extensibility
score_testability
score_documentation
print_summary
