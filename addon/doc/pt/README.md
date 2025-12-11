# Gênesis - Gerador de Projetos de Complementos para o NVDA

* **Autor:** Edilberto Fonseca <edilberto.fonseca@outlook.com>  
* **Licença:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)  
* **Versão:** 2025.1.0  

## Descrição

O Gênesis é um complemento para o NVDA que simplifica a criação de novos projetos de complementos.  
Ele oferece uma interface acessível para definir os metadados iniciais e gerar automaticamente toda a estrutura do projeto. Quando ativado, também pode criar o repositório do projeto na sua conta do GitHub.

A estrutura é baseada no **template oficial da comunidade NVDA**:  
<https://github.com/nvaccess/addonTemplate>

## Principais recursos

* Interface gráfica intuitiva e acessível  
* Geração automática da estrutura do projeto usando o template oficial  
* Preenchimento automático de informações como nome, descrição, autor e versão  
* Opção para incluir pastas de documentação e localização  
* Opção para clonar o repositório oficial do NVDA  
* **Integração opcional com o GitHub** para criar o repositório remoto  
* Configurações próprias no painel de configurações do NVDA  

## Público-alvo

Ideal para:

* **Iniciantes** que desejam criar seu primeiro complemento  
* **Desenvolvedores experientes** que querem agilizar o início de novos projetos  

## Requisitos

### Para usar o Gênesis

Nenhum requisito externo - funciona diretamente no NVDA.

### Para desenvolver o complemento gerado

Instale:

* **Python 3.11 (32 bits recomendado)** - <https://www.python.org/downloads/windows/>  
* **Git** - <https://git-scm.com/>  
* **Scons 4.5.2 ou superior** - via `pip install scons`  
* **GNU Gettext** - necessário para a compilação de traduções  
  * Windows: <https://gnuwin32.sourceforge.net/downlinks/gettext.php>  
* **Markdown 3.3.0+** - opcional, para documentação (`pip install markdown`)  

### Para publicar no GitHub (opcional)

* Conta no GitHub  
* Token de acesso (PAT) com permissão `repo`  

A publicação só ocorre quando ativada em:  
**NVDA > Preferências > Configurações > Gênesis**

## Autenticação no GitHub

Se a opção **“Permitir publicar repositório no GitHub”** estiver ativada, o Gênesis solicitará seu token.

Se estiver desativada:

✔ Nenhuma autenticação é pedida  
✔ Nada é enviado ao GitHub  
✔ O projeto é criado somente localmente  

### Como criar um token no GitHub

1. Acesse: <https://github.com/settings/tokens>  
2. Vá em **“Tokens (classic)” → “Generate new token (classic)”**  
3. Nomeie o token (ex.: *Genesis NVDA*)  
4. Defina a validade  
5. Marque a permissão necessária:  
   * `repo`  
6. Gere o token e guarde-o com segurança  

### Observações

* O token **nunca** é salvo  
* É validado diretamente pelo GitHub  
* Pode ser revogado a qualquer momento  

## Instalação

### Via Loja de Complementos

1. No NVDA → **Ferramentas** → **Loja de Complementos**  
2. Aba **Disponíveis**  
3. Pesquise por **Gênesis**  
4. Clique em **Instalar**  
5. Reinicie o NVDA  

### Instalação manual

1. Baixe `genesis.nvda-addon`  
2. NVDA → Ferramentas → **Gerenciar Complementos**  
3. Clique em **Instalar** e selecione o arquivo  
4. Reinicie o NVDA  

## Características

* Usa o **template oficial do NVDA** como base  
* Compatível com todo o sistema de build oficial  
* Publicação remota é **opcional**  
* Metadados são aplicados automaticamente aos arquivos do projeto  

## Atalhos de Teclado

| Atalho             | Ação                                         |
|--------------------|----------------------------------------------|
| `NVDA+Shift+G`     | Abre o Gênesis                               |
| `Alt+G`            | Gera um novo projeto                         |
| `Alt+L`            | Limpa todos os campos                         |
| `Alt+T`            | Clona o repositório oficial do NVDA          |
| `Alt+S`            | Fecha o Gênesis                              |

## Tradutores

* **Português (Brasil), pt_BR:** Edilberto Fonseca
