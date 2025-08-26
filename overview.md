# 📘 PPG Analytics Hub – Visão Geral do Projeto

## 🎯 Propósito
O **PPG Analytics Hub** é uma plataforma integrada de **gestão e analytics** para Programas de Pós-Graduação (PPGs).  
O sistema busca resolver:
- Fragmentação de dados em planilhas e sistemas isolados.  
- Dificuldade em mapear a produção científica (CAPES/Sucupira).  
- Processos administrativos ineficientes.  
- Baixa visibilidade de impacto científico e colaborações.  

---

## 🛠 Stack Tecnológica

### Backend
- **Linguagem**: Python 3.11+  
- **Framework**: FastAPI (API-first, async, OpenAPI automático)  
- **ORM**: SQLAlchemy 2.x (`metadata.create_all()` para criação inicial)  
- **Validação**: Pydantic v2  
- **Autenticação**: JWT RS256 + RBAC (roles multi-nível)  

> 🔮 **Futuro:** integração com **Alembic** para migrações versionadas.  

### Banco de Dados
- **Supabase (PostgreSQL 15+)**  
  - Schemas:  
    - `core` → instituições, programas, linhas de pesquisa  
    - `auth` → usuários, papéis, sessões, logs  
    - `academic` → docentes, discentes, disciplinas, bancas, trabalhos  
  - Extensões: `uuid-ossp`, `pg_trgm`, `unaccent`, `pg_stat_statements`  

### Orquestração / ETL
- **n8n** (cron jobs, ingestão OpenAlex, processamento CSV/XLS, integração com Gemini).  

### IA / Analytics
- **Google Gemini API** para análise de resumos, tendências e insights.  
- **Redis** para cache de métricas e queries frequentes.  

### Frontend
- **React/Next.js + Tailwind CSS + TypeScript**  
- Dashboard responsivo com KPIs e relatórios.  

### Observabilidade
- Logs estruturados (JSON) com `request_id`.  
- Métricas via Prometheus + Grafana.  
- Health/Ready endpoints (`/healthz`, `/readyz`).  

---

## 🏗 Arquitetura do Sistema

```plaintext
(OpenAlex API / CSV / ORCID / Gemini)
         │
         ▼
 ┌─────────────────┐
 │   n8n Workflows │───▶ Supabase (Postgres)
 └─────────────────┘
         │
         ▼
 ┌─────────────────┐
 │   FastAPI APIs  │───▶ Dashboards / Relatórios
 └─────────────────┘
         │
         ▼
  (Coordenação / Docentes / Secretaria)

# Fluxos principais

ETL (n8n): coleta OpenAlex, planilhas internas, valida e insere no Supabase.

API Layer (FastAPI): expõe endpoints RESTful com autenticação e RBAC.

Analytics (Gemini + Views SQL): gera insights e relatórios CAPES.

Dashboards (Frontend): exibe KPIs e métricas em tempo real

O ChatGPT disse:

Boa, Thiago 👍 — então vamos simplificar o documento: vamos manter SQLAlchemy 2.x como ORM, mas sem Alembic agora. A modelagem inicial será criada via scripts manuais (SQL) ou metadata.create_all(). No futuro, quando o schema estabilizar, você entra com Alembic para migrações versionadas.

Aqui está a versão reestruturada do documento em Markdown:

# 📘 PPG Analytics Hub – Visão Geral do Projeto

## 🎯 Propósito
O **PPG Analytics Hub** é uma plataforma integrada de **gestão e analytics** para Programas de Pós-Graduação (PPGs).  
O sistema busca resolver:
- Fragmentação de dados em planilhas e sistemas isolados.  
- Dificuldade em mapear a produção científica (CAPES/Sucupira).  
- Processos administrativos ineficientes.  
- Baixa visibilidade de impacto científico e colaborações.  

---

## 🛠 Stack Tecnológica

### Backend
- **Linguagem**: Python 3.11+  
- **Framework**: FastAPI (API-first, async, OpenAPI automático)  
- **ORM**: SQLAlchemy 2.x (`metadata.create_all()` para criação inicial)  
- **Validação**: Pydantic v2  
- **Autenticação**: JWT RS256 + RBAC (roles multi-nível)  

> 🔮 **Futuro:** integração com **Alembic** para migrações versionadas.  

### Banco de Dados
- **Supabase (PostgreSQL 15+)**  
  - Schemas:  
    - `core` → instituições, programas, linhas de pesquisa  
    - `auth` → usuários, papéis, sessões, logs  
    - `academic` → docentes, discentes, disciplinas, bancas, trabalhos  
  - Extensões: `uuid-ossp`, `pg_trgm`, `unaccent`, `pg_stat_statements`  

### Orquestração / ETL
- **n8n** (cron jobs, ingestão OpenAlex, processamento CSV/XLS, integração com Gemini).  

### IA / Analytics
- **Google Gemini API** para análise de resumos, tendências e insights.  
- **Redis** para cache de métricas e queries frequentes.  

### Frontend
- **React/Next.js + Tailwind CSS + TypeScript**  
- Dashboard responsivo com KPIs e relatórios.  

### Observabilidade
- Logs estruturados (JSON) com `request_id`.  
- Métricas via Prometheus + Grafana.  
- Health/Ready endpoints (`/healthz`, `/readyz`).  

---

## 🏗 Arquitetura do Sistema

```plaintext
(OpenAlex API / CSV / ORCID / Gemini)
         │
         ▼
 ┌─────────────────┐
 │   n8n Workflows │───▶ Supabase (Postgres)
 └─────────────────┘
         │
         ▼
 ┌─────────────────┐
 │   FastAPI APIs  │───▶ Dashboards / Relatórios
 └─────────────────┘
         │
         ▼
  (Coordenação / Docentes / Secretaria)

Fluxos principais

ETL (n8n): coleta OpenAlex, planilhas internas, valida e insere no Supabase.

API Layer (FastAPI): expõe endpoints RESTful com autenticação e RBAC.

Analytics (Gemini + Views SQL): gera insights e relatórios CAPES.

Dashboards (Frontend): exibe KPIs e métricas em tempo real.

🗄 Estrutura do Banco de Dados (MVP)
Schema core

instituicoes → dados institucionais (CNPJ, ROR, OpenAlex ID).

programas → cada programa de pós-graduação (multi-tenant).

linhas_pesquisa → agrupamento temático.

Schema auth

roles → perfis (superadmin, coordenador, docente, discente, etc.).

usuarios → dados pessoais, acadêmicos e integrações (ORCID, Lattes).

usuario_programa_roles → vínculo usuário-programa com role.

sessoes → tokens ativos (JWT/refresh).

audit_logs → trilha de auditoria.

Schema academic

docentes → cache de métricas OpenAlex (h-index, publicações, citações).

discentes → matrícula, bolsa, prazo, defesa, egresso.

disciplinas / ofertas_disciplinas / matriculas_disciplinas → estrutura curricular.

trabalhos_conclusao → dissertações/teses com metadados e repositório.

bancas / membros_banca → composição de bancas de qualificação e defesa.

📋 Requisitos Funcionais (MVP)

 Autenticação com JWT + RBAC.

 CRUD de docentes e discentes.

 Sincronização OpenAlex diária via n8n.

 Dashboard inicial com KPIs CAPES.

 Gestão de defesas (trabalhos, bancas, atas).

🚀 Roadmap do MVP (90 dias)

Semana 1-2: Fundação

Setup Supabase + FastAPI

Criação inicial de tabelas via metadata.create_all()

Configuração n8n (primeiro workflow)

Semana 3-4: Core Development

Autenticação + RBAC

CRUD Docentes/Discentes

Endpoint /sync/openalex

Semana 5-6: Analytics Básico

Views analíticas (produtividade, evolução temporal)

Relatório automatizado CAPES

Semana 7-8: Refinamento

Dashboard Next.js

Observabilidade (logs, métricas)

Deploy produção

✅ Critérios de Aceite do MVP

Funcionalidade: 100% dos core features ativos.

Performance: API < 2s / Dashboard < 3s.

Confiabilidade: sincronização OpenAlex diária com 99% sucesso.

Segurança: RBAC aplicado em todas as rotas críticas.

Usabilidade: relatórios gerados em < 10min pela coordenação.
