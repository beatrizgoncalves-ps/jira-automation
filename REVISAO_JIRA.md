# REVISÃO DE BACKLOG - 1 ITENS IDENTIFICADOS

## ITEM 1: Cálculo de Distância Percorrida por Intervalo de Macro no Relatório de Produtividade vFleets (User Story)
**ÉPICO:** LAPDT-938

### 1. Persona e Valor de Negócio
**Como** Gestor de Frota / Analista de Operações,
**Quero** visualizar a distância exata percorrida por um veículo durante o período em que uma macro específica esteve ativa,
**Para que** eu possa auditar a produtividade das viagens, entender o deslocamento real em atividades operacionais (ex: trânsito, coleta, entrega) e identificar desperdícios de combustível ou desvios de rota.

---

### 2. Critérios de Aceite
1. **Detecção de Ciclo de Macro**: O sistema deve identificar o par de eventos: ativação (início) e desativação/troca (fim) de uma macro de telemetria para um determinado veículo.
2. **Cálculo de Distância**: 
   - A distância deve ser calculada utilizando a diferença do odômetro (preferencialmente via CAN-bus) ou, na ausência deste, a soma da distância geodésica (Haversine) das coordenadas de GPS coletadas estritamente entre o timestamp de ativação e o de desativação da macro.
3. **Tratamento de Deslocamento Zero**: Se a macro for ativada e desativada sem que o veículo se desloque fisicamente (mesma coordenada/sem alteração de odômetro), o valor registrado deve ser obrigatoriamente `0 km`.
4. **Apresentação no Relatório de Produtividade**: No relatório do vFleets, deve ser disponibilizada a tabela/campos com:
   - Identificador/Nome da Macro.
   - Placa/Prefixo do Veículo.
   - Data/Hora de Início.
   - Data/Hora de Fim.
   - Distância Percorrida (em quilômetros, com precisão de duas casas decimais, ex: `12.45 km`).
5. **Filtro de Relatório**: Permitir filtrar o relatório de produtividade por período, veículo e tipo de macro.

---

### 3. POV Técnico Crítico (Análise de Arquitetura e Engenharia)
- **Gargalo de Performance e Escalabilidade**: O cálculo em tempo de execução (on-the-fly) de distâncias geodésicas baseadas em pontos de GPS de alta frequência para múltiplos veículos travará o relatório de produtividade (timeout de requisição). 
  - *Solução proposta*: Abordagem orientada a eventos. O cálculo da distância da macro deve ser assíncrono. Um consumer (ex: Kafka/RabbitMQ) deve escutar os eventos de macro, acumular os pontos de telemetria daquele intervalo, calcular o delta e salvar o resultado consolidado em uma tabela otimizada para leitura (Read Model - CQRS) no banco de dados.
- **Dependências Técnicas e Riscos de Integração**: Dependência crítica da confiabilidade do firmware do rastreador em enviar os eventos de macro na ordem correta. Se o evento de "desativação" chegar antes da "ativação" devido a problemas de rede celular, o sistema precisa tratar mensagens fora de ordem (out-of-order events) reordenando-as por timestamp de geração no dispositivo, e não de recepção no servidor.
- **Segurança e Conformidade (LGPD)**: Os dados de localização (GPS) atrelados ao motorista que acionou a macro são considerados dados pessoais sob a LGPD. O relatório deve garantir mascaramento de dados ou controle de acesso baseado em roles (RBAC), limitando quem pode ver o histórico detalhado de trajetos.
- **Perguntas Incômodas / Casos de Borda Extremos**:
  1. *E se a macro for ativada e o veículo entrar em uma zona de sombra de sinal de celular (túnel/interior do país), desativando a macro horas depois sem sinal?* O sistema deve ser capaz de processar retroativamente os dados assim que o rastreador descarregar o buffer de memória (ignoring ingestion-time delay).
  2. *Como mitigar o "GPS Drift" (ruído de GPS)?* Se o veículo estiver estacionado com a macro ligada, o GPS pode oscilar lateralmente, gerando uma falsa distância acumulada de alguns metros. Devemos implementar um threshold mínimo de velocidade (ex: > 3 km/h) ou utilizar estritamente o odômetro do veículo para validar se houve movimento real.
---

