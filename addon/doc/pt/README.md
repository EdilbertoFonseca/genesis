# Gênesis - Gerador de Projetos de Complementos para o NVDA

- **Autor:** Edilberto Fonseca <edilberto.fonseca@outlook.com>
- **Licença:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)
- **Versão:** 2025.1.0

## Descrição

O Gênesis é um complemento para o NVDA projetado para simplificar a criação de projetos de complementos.
Ele oferece uma interface totalmente acessível para definir os metadados iniciais e gerar automaticamente a estrutura do projeto.

Opcionalmente, o Gênesis pode criar o repositório remoto no GitHub, utilizando o template oficial.

A estrutura gerada é baseada no template oficial da comunidade NVDA:
[https://github.com/nvaccess/addonTemplate](https://github.com/nvaccess/addonTemplate)

## Principais recursos

- Interface gráfica intuitiva e acessível
- Geração automática da estrutura inicial do complemento
- Preenchimento dos metadados essenciais
- Opção para incluir pastas de documentação e localização
- Opção para clonar o repositório oficial do NVDA
- Integração opcional com o GitHub
- Painel próprio de configurações no NVDA

## Público-alvo

O complemento é indicado para:

- Iniciantes que desejam criar seu primeiro complemento
- Desenvolvedores experientes que desejam agilizar o início de novos projetos

## Requisitos

### Para usar o Gênesis

Nenhum requisito externo. O complemento funciona diretamente no NVDA.

### Para desenvolver o complemento gerado

Instalar:

- Python 3.13 (64 bits recomendado)
  [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- Git
  [https://git-scm.com/](https://git-scm.com/)
- Scons 4.5.2 ou superior
  `pip install scons`
- GNU Gettext
  Necessário para compilar arquivos de tradução
  [https://gnuwin32.sourceforge.net/downlinks/gettext.php](https://gnuwin32.sourceforge.net/downlinks/gettext.php)
- Markdown 3.3.0+ (opcional)
  `pip install markdown`

### Para publicar no GitHub (opcional)

- Conta no GitHub
- Token de acesso (PAT) com permissão `repo`

A publicação remota só ocorre quando ativada em:
NVDA > Preferências > Configurações > Gênesis

## Autenticação no GitHub

Se a opção “Permitir publicar repositório no GitHub” estiver ativada, o Gênesis solicitará seu token de acesso.

Quando desativada:

- Nenhuma autenticação será pedida
- Nada será enviado ao GitHub
- O projeto será criado somente localmente

### Como gerar um token no GitHub

1. Acesse [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Vá em "Tokens (classic)" → "Generate new token (classic)"
3. Defina um nome
4. Escolha a validade
5. Marque a permissão `repo`
6. Gere o token e armazene-o com segurança

### Observações

- O token não é salvo pelo complemento
- É validado diretamente pela API do GitHub
- Pode ser revogado a qualquer momento

## Instalação

### Via Loja de Complementos

1. NVDA > Ferramentas > Loja de Complementos
2. Aba “Disponíveis”
3. Pesquise por “Gênesis”
4. Clique em “Instalar”
5. Reinicie o NVDA

### Instalação manual

1. Baixe o arquivo [`genesis.nvda-addon`](https://github.com/EdilbertoFonseca/genesis/)
2. Precione enter no arquivo baixado
3. Siga as instruções para a instalação do add-on
4. Reinicie o NVDA

## Características técnicas

- Usa o template oficial do NVDA como base
- Compatível com o sistema oficial de build
- Publicação remota é opcional
- Metadados aplicados automaticamente ao arquivo `buildVars.py`

## Atalhos de teclado

| Atalho     | Ação                                |
| ---------- | ----------------------------------- |
| NVDA+Alt+G | Abre o Gênesis                      |
| Alt+G      | Gera um novo projeto                |
| Alt+L      | Limpa todos os campos               |
| Alt+T      | Clona o repositório oficial do NVDA |
| Alt+S      | Fecha o Gênesis                     |

## Tradutores

- Português (Brasil), pt_BR - Edilberto Fonseca
