-- =====================================================
-- PPG HUB - SISTEMA MULTI-PROGRAMA - SQL MVP
-- Agora (MVP): core, oauth, academic.
-- Banco escalável para gestão de múltiplos programas de pós-graduação
-- Integração completa com OpenAlex + Sistema de usuários robusto
-- =====================================================


-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_crypto";

-- =====================================================
-- SCHEMA: CORE (Estrutura base multi-tenant)
-- =====================================================
CREATE SCHEMA core;

-- Tabela de Instituições (nível mais alto da hierarquia)
CREATE TABLE core.instituicoes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- UEPB, UFCG, etc.
    nome_completo VARCHAR(500) NOT NULL,
    nome_abreviado VARCHAR(50) NOT NULL,
    sigla VARCHAR(10) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    tipo VARCHAR(50) NOT NULL, -- Federal, Estadual, Municipal, Privada
    natureza_juridica VARCHAR(100),
    endereco JSONB,
    contatos JSONB,
    redes_sociais JSONB,
    logo_url TEXT,
    website TEXT,
    fundacao DATE,
    -- Integração OpenAlex
    openalex_institution_id TEXT,
    ror_id TEXT,
    -- Metadados
    ativo BOOLEAN DEFAULT TRUE,
    configuracoes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Programas (multi-programa por instituição)
CREATE TABLE core.programas (
    id SERIAL PRIMARY KEY,
    instituicao_id INTEGER NOT NULL REFERENCES core.instituicoes(id),
    codigo_capes VARCHAR(20) UNIQUE, -- Código oficial CAPES
    nome VARCHAR(255) NOT NULL,
    sigla VARCHAR(20) NOT NULL,
    area_concentracao VARCHAR(255),
    nivel VARCHAR(50) NOT NULL, -- Mestrado, Doutorado, Mestrado/Doutorado
    modalidade VARCHAR(50) DEFAULT 'Presencial', -- Presencial, EAD, Semipresencial
    inicio_funcionamento DATE,
    -- Avaliação CAPES
    conceito_capes INTEGER CHECK (conceito_capes >= 1 AND conceito_capes <= 7),
    data_ultima_avaliacao DATE,
    triênio_avaliacao VARCHAR(20), -- 2019-2021, 2022-2024
    -- Coordenação
    coordenador_id INTEGER, -- FK para usuarios (será criada depois)
    coordenador_adjunto_id INTEGER,
    mandato_inicio DATE,
    mandato_fim DATE,
    -- Configurações específicas do programa
    creditos_minimos_mestrado INTEGER DEFAULT 24,
    creditos_minimos_doutorado INTEGER DEFAULT 48,
    prazo_maximo_mestrado INTEGER DEFAULT 24, -- meses
    prazo_maximo_doutorado INTEGER DEFAULT 48, -- meses
    -- Integração OpenAlex
    openalex_institution_id TEXT,
    -- Status e metadados
    status VARCHAR(50) DEFAULT 'Ativo', -- Ativo, Suspenso, Descredenciado
    configuracoes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(instituicao_id, sigla)
);

-- Tabela de Linhas de Pesquisa
CREATE TABLE core.linhas_pesquisa (
    id SERIAL PRIMARY KEY,
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    palavras_chave TEXT,
    coordenador_id INTEGER, -- FK para usuarios
    ativa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(programa_id, nome)
);

-- =====================================================
-- SCHEMA: AUTH (Sistema de autenticação e autorização)
-- =====================================================
CREATE SCHEMA auth;

-- Tabela de Roles (papéis no sistema)
CREATE TABLE auth.roles (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    nivel_acesso INTEGER NOT NULL, -- 1=baixo, 5=admin total
    permissoes JSONB DEFAULT '{}',
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inserindo roles padrão
INSERT INTO auth.roles (nome, descricao, nivel_acesso, permissoes) VALUES
('superadmin', 'Administrador de sistema', 5, '{"all": true}'),
('admin_institucional', 'Administrador da instituição', 4, '{"manage_institution": true, "manage_programs": true}'),
('coordenador', 'Coordenador de programa', 3, '{"manage_program": true, "view_analytics": true}'),
('secretaria', 'Secretaria acadêmica', 2, '{"manage_students": true, "manage_documents": true}'),
('docente', 'Professor do programa', 2, '{"view_students": true, "manage_advisees": true}'),
('discente', 'Estudante do programa', 1, '{"view_profile": true, "submit_documents": true}'),
('tecnico', 'Técnico administrativo', 2, '{"manage_data": true, "view_reports": true}'),
('visitante', 'Acesso de consulta', 1, '{"view_public": true}');

-- Tabela principal de usuários
CREATE TABLE auth.usuarios (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    -- Dados básicos
    nome_completo VARCHAR(255) NOT NULL,
    nome_preferido VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_alternativo VARCHAR(255),
    telefone VARCHAR(20),
    cpf VARCHAR(14) UNIQUE,
    rg VARCHAR(20),
    passaporte VARCHAR(50),
    -- Autenticação
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    email_verificado BOOLEAN DEFAULT FALSE,
    email_verificado_em TIMESTAMP,
    -- Dados pessoais
    data_nascimento DATE,
    genero VARCHAR(20),
    nacionalidade VARCHAR(50) DEFAULT 'Brasileira',
    naturalidade VARCHAR(100),
    endereco JSONB,
    -- Dados acadêmicos/profissionais
    orcid VARCHAR(100) UNIQUE,
    lattes_id VARCHAR(100),
    google_scholar_id VARCHAR(100),
    researchgate_id VARCHAR(100),
    linkedin VARCHAR(100),
    -- Integração OpenAlex
    openalex_author_id TEXT,
    ultimo_sync_openalex TIMESTAMP,
    -- Configurações de conta
    configuracoes JSONB DEFAULT '{}',
    preferencias JSONB DEFAULT '{}',
    avatar_url TEXT,
    biografia TEXT,
    -- Segurança
    ultimo_login TIMESTAMP,
    tentativas_login INTEGER DEFAULT 0,
    conta_bloqueada BOOLEAN DEFAULT FALSE,
    bloqueada_ate TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expira TIMESTAMP,
    -- Auditoria
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES auth.usuarios(id),
    updated_by INTEGER REFERENCES auth.usuarios(id)
);

-- Tabela de vinculações usuário-programa-role
CREATE TABLE auth.usuario_programa_roles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES auth.usuarios(id),
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    role_id INTEGER NOT NULL REFERENCES auth.roles(id),
    -- Dados específicos da vinculação
    data_vinculacao DATE DEFAULT CURRENT_DATE,
    data_desvinculacao DATE,
    status VARCHAR(50) DEFAULT 'Ativo', -- Ativo, Suspenso, Desligado
    observacoes TEXT,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES auth.usuarios(id),
    -- Constraints
    UNIQUE(usuario_id, programa_id, role_id),
    CHECK (data_desvinculacao IS NULL OR data_desvinculacao >= data_vinculacao)
);

-- Tabela de sessões
CREATE TABLE auth.sessoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES auth.usuarios(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de logs de auditoria
CREATE TABLE auth.audit_logs (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES auth.usuarios(id),
    acao VARCHAR(100) NOT NULL,
    entidade VARCHAR(100),
    entidade_id INTEGER,
    dados_anteriores JSONB,
    dados_novos JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- SCHEMA: ACADEMIC (Dados acadêmicos)
-- =====================================================
CREATE SCHEMA academic;

-- Tabela de Docentes (herda dados de auth.usuarios)
CREATE TABLE academic.docentes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES auth.usuarios(id),
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    linha_pesquisa_id INTEGER REFERENCES core.linhas_pesquisa(id),
    -- Dados específicos de docente
    matricula VARCHAR(50),
    categoria VARCHAR(50), -- Professor Titular, Associado, Adjunto, Assistente
    regime_trabalho VARCHAR(50), -- DE, 40h, 20h
    titulacao_maxima VARCHAR(100),
    instituicao_titulacao VARCHAR(255),
    ano_titulacao INTEGER,
    pais_titulacao VARCHAR(50),
    -- Vinculação ao programa
    tipo_vinculo VARCHAR(50) NOT NULL, -- Permanente, Colaborador, Visitante, Voluntário
    data_vinculacao DATE NOT NULL,
    data_desvinculacao DATE,
    -- Métricas acadêmicas (cache do OpenAlex)
    h_index INTEGER DEFAULT 0,
    total_publicacoes INTEGER DEFAULT 0,
    total_citacoes INTEGER DEFAULT 0,
    publicacoes_ultimos_5_anos INTEGER DEFAULT 0,
    -- Orientações
    orientacoes_mestrado_andamento INTEGER DEFAULT 0,
    orientacoes_doutorado_andamento INTEGER DEFAULT 0,
    orientacoes_mestrado_concluidas INTEGER DEFAULT 0,
    orientacoes_doutorado_concluidas INTEGER DEFAULT 0,
    coorientacoes INTEGER DEFAULT 0,
    -- Bolsas e financiamentos
    bolsista_produtividade BOOLEAN DEFAULT FALSE,
    nivel_bolsa_produtividade VARCHAR(20),
    vigencia_bolsa_inicio DATE,
    vigencia_bolsa_fim DATE,
    -- Dados complementares
    areas_interesse TEXT,
    projetos_atuais TEXT,
    curriculo_resumo TEXT,
    -- Status
    status VARCHAR(50) DEFAULT 'Ativo', -- Ativo, Afastado, Aposentado, Desligado
    motivo_desligamento TEXT,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(usuario_id, programa_id),
    CHECK (data_desvinculacao IS NULL OR data_desvinculacao >= data_vinculacao)
);

-- Tabela de Discentes
CREATE TABLE academic.discentes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES auth.usuarios(id),
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    linha_pesquisa_id INTEGER REFERENCES core.linhas_pesquisa(id),
    orientador_id INTEGER REFERENCES academic.docentes(id),
    coorientador_interno_id INTEGER REFERENCES academic.docentes(id),
    -- Dados de matrícula
    numero_matricula VARCHAR(50) NOT NULL,
    tipo_curso VARCHAR(20) NOT NULL, -- Mestrado, Doutorado
    turma INTEGER NOT NULL, -- Ano de ingresso
    semestre_ingresso VARCHAR(10) NOT NULL, -- 2024.1, 2024.2
    data_ingresso DATE NOT NULL,
    data_primeira_matricula DATE,
    -- Dados do projeto
    titulo_projeto TEXT,
    resumo_projeto TEXT,
    palavras_chave_projeto TEXT,
    area_cnpq VARCHAR(255),
    -- Processo seletivo
    tipo_ingresso VARCHAR(50), -- Ampla concorrência, Cota racial, etc.
    nota_processo_seletivo DECIMAL(5,2),
    classificacao_processo INTEGER,
    -- Coorientador externo
    coorientador_externo_nome VARCHAR(255),
    coorientador_externo_instituicao VARCHAR(255),
    coorientador_externo_email VARCHAR(255),
    coorientador_externo_titulacao VARCHAR(100),
    -- Proficiência em idiomas
    proficiencia_idioma VARCHAR(50),
    proficiencia_status VARCHAR(50), -- Aprovado, Pendente, Dispensado
    data_proficiencia DATE,
    arquivo_proficiencia TEXT,
    -- Financiamento
    bolsista BOOLEAN DEFAULT FALSE,
    tipo_bolsa VARCHAR(100), -- CAPES, CNPq, FAPESQ, UEPB, etc.
    modalidade_bolsa VARCHAR(50), -- Demanda Social, Taxa, PROAP
    valor_bolsa DECIMAL(10,2),
    data_inicio_bolsa DATE,
    data_fim_bolsa DATE,
    numero_processo_bolsa VARCHAR(100),
    agencia_fomento VARCHAR(100),
    -- Histórico acadêmico
    creditos_obrigatorios INTEGER DEFAULT 0,
    creditos_eletivos INTEGER DEFAULT 0,
    creditos_cursados INTEGER DEFAULT 0,
    creditos_aprovados INTEGER DEFAULT 0,
    creditos_necessarios INTEGER,
    coeficiente_rendimento DECIMAL(4,2),
    -- Qualificação
    qualificacao_realizada BOOLEAN DEFAULT FALSE,
    data_qualificacao DATE,
    resultado_qualificacao VARCHAR(50), -- Aprovado, Reprovado, Aprovado com Restrições
    -- Prazos
    prazo_original DATE,
    prorrogacoes JSONB DEFAULT '[]', -- Array de prorrogações
    data_limite_atual DATE,
    -- Defesa
    data_defesa DATE,
    resultado_defesa VARCHAR(50), -- Aprovado, Reprovado, Aprovado com Correções
    nota_defesa DECIMAL(4,2),
    titulo_final TEXT,
    -- Documentos
    documentos JSONB DEFAULT '{}',
    -- Status
    status VARCHAR(50) DEFAULT 'Matriculado', -- Matriculado, Cursando, Qualificado, Defendendo, Titulado, Desligado
    motivo_desligamento TEXT,
    data_desligamento DATE,
    -- Egresso
    destino_egresso TEXT,
    atuacao_pos_formatura TEXT,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(programa_id, numero_matricula),
    CHECK (data_defesa IS NULL OR data_defesa >= data_ingresso)
);

-- Tabela de Disciplinas
CREATE TABLE academic.disciplinas (
    id SERIAL PRIMARY KEY,
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    codigo VARCHAR(50) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    nome_ingles VARCHAR(255),
    ementa TEXT,
    ementa_ingles TEXT,
    objetivos TEXT,
    conteudo_programatico TEXT,
    metodologia_ensino TEXT,
    criterios_avaliacao TEXT,
    bibliografia_basica TEXT,
    bibliografia_complementar TEXT,
    -- Carga horária
    carga_horaria_total INTEGER NOT NULL,
    carga_horaria_teorica INTEGER DEFAULT 0,
    carga_horaria_pratica INTEGER DEFAULT 0,
    creditos INTEGER NOT NULL,
    -- Classificação
    tipo VARCHAR(50) NOT NULL, -- Obrigatória, Eletiva, Tópicos Especiais
    nivel VARCHAR(50) NOT NULL, -- Mestrado, Doutorado, Ambos
    linha_pesquisa_id INTEGER REFERENCES core.linhas_pesquisa(id),
    -- Requisitos
    pre_requisitos JSONB DEFAULT '[]',
    co_requisitos JSONB DEFAULT '[]',
    -- Configurações
    modalidade VARCHAR(50) DEFAULT 'Presencial', -- Presencial, EAD, Híbrida
    periodicidade VARCHAR(50), -- Anual, Semestral, Eventual
    maximo_alunos INTEGER,
    minimo_alunos INTEGER DEFAULT 1,
    -- Status
    status VARCHAR(50) DEFAULT 'Ativa', -- Ativa, Inativa, Suspensa
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(programa_id, codigo)
);

-- Tabela de Ofertas de Disciplinas
CREATE TABLE academic.ofertas_disciplinas (
    id SERIAL PRIMARY KEY,
    disciplina_id INTEGER NOT NULL REFERENCES academic.disciplinas(id),
    docente_responsavel_id INTEGER NOT NULL REFERENCES academic.docentes(id),
    docente_colaborador_id INTEGER REFERENCES academic.docentes(id),
    -- Período
    ano INTEGER NOT NULL,
    semestre INTEGER NOT NULL CHECK (semestre IN (1, 2)),
    periodo VARCHAR(10) NOT NULL, -- 2024.1, 2024.2
    -- Horários
    horarios JSONB NOT NULL, -- [{"dia": "segunda", "inicio": "14:00", "fim": "17:00"}]
    sala VARCHAR(50),
    modalidade VARCHAR(50) DEFAULT 'Presencial',
    link_virtual TEXT,
    -- Datas
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    -- Vagas
    vagas_oferecidas INTEGER NOT NULL,
    vagas_ocupadas INTEGER DEFAULT 0,
    lista_espera INTEGER DEFAULT 0,
    -- Status
    status VARCHAR(50) DEFAULT 'Planejada', -- Planejada, Aberta, Em_Curso, Concluída, Cancelada
    observacoes TEXT,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(disciplina_id, ano, semestre),
    CHECK (data_fim > data_inicio),
    CHECK (vagas_ocupadas <= vagas_oferecidas)
);

-- Tabela de Matrículas em Disciplinas
CREATE TABLE academic.matriculas_disciplinas (
    id SERIAL PRIMARY KEY,
    discente_id INTEGER NOT NULL REFERENCES academic.discentes(id),
    oferta_disciplina_id INTEGER NOT NULL REFERENCES academic.ofertas_disciplinas(id),
    -- Matrícula
    data_matricula TIMESTAMP DEFAULT NOW(),
    situacao VARCHAR(50) DEFAULT 'Matriculado', -- Matriculado, Trancado, Cancelado
    -- Avaliações
    avaliacoes JSONB DEFAULT '{}', -- Notas de provas, trabalhos, etc.
    frequencia_percentual DECIMAL(5,2),
    nota_final DECIMAL(4,2),
    conceito VARCHAR(10), -- A, B, C, D, E ou aprovado/reprovado
    -- Resultado
    status_final VARCHAR(50), -- Aprovado, Reprovado, Trancado, Cancelado
    data_resultado DATE,
    observacoes TEXT,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    UNIQUE(discente_id, oferta_disciplina_id)
);

-- Tabela de Trabalhos de Conclusão (Dissertações/Teses)
CREATE TABLE academic.trabalhos_conclusao (
    id SERIAL PRIMARY KEY,
    discente_id INTEGER NOT NULL REFERENCES academic.discentes(id),
    programa_id INTEGER NOT NULL REFERENCES core.programas(id),
    orientador_id INTEGER NOT NULL REFERENCES academic.docentes(id),
    coorientador_id INTEGER REFERENCES academic.docentes(id),
    -- Dados básicos
    tipo VARCHAR(20) NOT NULL, -- Dissertação, Tese
    titulo TEXT NOT NULL,
    titulo_ingles TEXT,
    subtitulo TEXT,
    -- Resumos
    resumo_portugues TEXT,
    resumo_ingles TEXT,
    abstract TEXT,
    -- Palavras-chave
    palavras_chave_portugues TEXT,
    palavras_chave_ingles TEXT,
    keywords TEXT,
    -- Classificação
    area_cnpq TEXT,
    area_concentracao TEXT,
    linha_pesquisa TEXT,
    -- Dados de publicação
    data_defesa DATE,
    ano_defesa INTEGER,
    semestre_defesa INTEGER,
    local_defesa TEXT,
    -- Características físicas
    numero_paginas INTEGER,
    idioma VARCHAR(10) DEFAULT 'pt',
    -- Arquivos
    arquivo_pdf TEXT,
    arquivo_ata_defesa TEXT,
    tamanho_arquivo_bytes BIGINT,
    -- Repositório
    handle_uri TEXT,
    uri_repositorio TEXT,
    url_download TEXT,
    tipo_acesso VARCHAR(50) DEFAULT 'Acesso Aberto', -- Acesso Aberto, Restrito, Embargado
    -- Integração OpenAlex
    openalex_work_id TEXT,
    doi TEXT,
    isbn TEXT,
    -- Métricas
    downloads_count INTEGER DEFAULT 0,
    visualizacoes_count INTEGER DEFAULT 0,
    citacoes_count INTEGER DEFAULT 0,
    -- Qualidade
    nota_avaliacao DECIMAL(4,2),
    premios_reconhecimentos TEXT,
    -- Status
    status VARCHAR(50) DEFAULT 'Em_Preparacao', -- Em_Preparacao, Qualificado, Defendido, Aprovado, Publicado
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Bancas
CREATE TABLE academic.bancas (
    id SERIAL PRIMARY KEY,
    trabalho_conclusao_id INTEGER REFERENCES academic.trabalhos_conclusao(id),
    discente_id INTEGER NOT NULL REFERENCES academic.discentes(id),
    tipo VARCHAR(50) NOT NULL, -- Qualificação, Defesa_Dissertacao, Defesa_Tese
    -- Agendamento
    data_agendada DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME,
    local_realizacao TEXT,
    modalidade VARCHAR(50) DEFAULT 'Presencial', -- Presencial, Virtual, Híbrida
    link_virtual TEXT,
    -- Presidente e secretário
    presidente_id INTEGER NOT NULL REFERENCES academic.docentes(id),
    secretario_id INTEGER REFERENCES academic.docentes(id),
    -- Documentação
    ata_numero VARCHAR(50),
    ata_arquivo TEXT,
    -- Resultado
    resultado VARCHAR(50), -- Aprovado, Reprovado, Aprovado_com_Correcoes, Aprovado_com_Restricoes
    nota_final DECIMAL(4,2),
    prazo_correcoes_dias INTEGER,
    correcoes_exigidas TEXT,
    observacoes_banca TEXT,
    recomendacoes TEXT,
    sugestao_publicacao BOOLEAN DEFAULT FALSE,
    -- Status
    status VARCHAR(50) DEFAULT 'Agendada', -- Agendada, Realizada, Cancelada, Adiada
    data_realizacao DATE,
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Membros de Banca
CREATE TABLE academic.membros_banca (
    id SERIAL PRIMARY KEY,
    banca_id INTEGER NOT NULL REFERENCES academic.bancas(id),
    -- Membro interno
    docente_id INTEGER REFERENCES academic.docentes(id),
    -- Membro externo
    nome_completo VARCHAR(255),
    instituicao VARCHAR(255),
    titulacao VARCHAR(100),
    email VARCHAR(255),
    curriculo_resumo TEXT,
    -- Função na banca
    funcao VARCHAR(50) NOT NULL, -- Presidente, Examinador_Interno, Examinador_Externo, Suplente
    tipo VARCHAR(50) NOT NULL, -- Interno, Externo
    ordem_apresentacao INTEGER,
    -- Participação
    confirmado BOOLEAN DEFAULT FALSE,
    presente BOOLEAN,
    justificativa_ausencia TEXT,
    -- Avaliação
    parecer_individual TEXT,
    nota_individual DECIMAL(4,2),
    -- Auditoria
    created_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    CHECK ((docente_id IS NOT NULL AND tipo = 'Interno') OR
           (docente_id IS NULL AND tipo = 'Externo' AND nome_completo IS NOT NULL))
);