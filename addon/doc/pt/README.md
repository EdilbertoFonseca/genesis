# Gênesis - Gerador de Projetos de Complementos para o NVDA

* **Autor:** Edilberto Fonseca <edilberto.fonseca@outlook.com>
* **Licença:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)
* **Versão:** 2026.1.0

## Descrição

O Gênesis é um complemento para o NVDA desenvolvido para simplificar a criação de projetos de complementos.

Ele oferece uma interface gráfica totalmente acessível, permitindo definir os metadados iniciais e gerar automaticamente a estrutura necessária para iniciar o desenvolvimento de um novo complemento.

Opcionalmente, o Gênesis pode criar um repositório remoto no GitHub utilizando o template oficial da comunidade NVDA. Quando essa opção está habilitada, o projeto também pode ser publicado automaticamente no repositório criado.

A estrutura dos projetos gerados é baseada no template oficial da comunidade NVDA:

[https://github.com/nvaccess/addonTemplate](https://github.com/nvaccess/addonTemplate)

## Principais recursos

* Interface gráfica intuitiva e acessível.
* Geração automática da estrutura inicial do complemento.
* Preenchimento dos metadados essenciais do projeto.
* Opção para incluir pastas de documentação e localização.
* Opção para clonar o repositório oficial do template de complementos do NVDA.
* Integração opcional com o GitHub para criação e publicação de repositórios.
* Painel próprio de configurações no NVDA.
* Armazenamento seguro do token de acesso ao GitHub por meio do Gerenciador de Credenciais do Windows.

## Público-alvo

O Gênesis é indicado para:

* Iniciantes que desejam criar seu primeiro complemento para o NVDA.
* Desenvolvedores experientes que desejam agilizar a configuração inicial de novos projetos.

## Requisitos

### Para usar o Gênesis

Não são necessários programas ou ferramentas externas. O complemento funciona diretamente no NVDA.

### Para desenvolver o complemento gerado

As seguintes ferramentas são recomendadas:

* **Python 3.13:** versão de 64 bits recomendada.
  [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

* **Git:** necessário para operações com repositórios.
  [https://git-scm.com/](https://git-scm.com/)

* **SCons 4.5.2 ou superior:** ferramenta utilizada no processo de compilação.

  ```bash
  pip install scons
  ```

* **GNU Gettext:** necessário para compilar os arquivos de tradução.
  [https://gnuwin32.sourceforge.net/downlinks/gettext.php](https://gnuwin32.sourceforge.net/downlinks/gettext.php)

* **Markdown 3.3.0 ou superior:** dependência opcional para recursos relacionados à documentação.

  ```bash
  pip install markdown
  ```

## Integração com o GitHub

A integração com o GitHub é opcional. Quando habilitada, o Gênesis pode:

* Criar um novo repositório remoto utilizando o template oficial do NVDA.
* Clonar o repositório criado para a pasta de destino.
* Gerar a estrutura do complemento.
* Preencher os arquivos de configuração e metadados.
* Publicar as alterações no repositório remoto.

A publicação remota depende das configurações definidas em:

**`NVDA > Preferências > Configurações > Gênesis`**

Nessa seção, é possível habilitar ou desabilitar a publicação no GitHub e configurar o proprietário do repositório, que pode ser um usuário ou uma organização.

A opção de privacidade também permite definir se o repositório será público ou privado.

Quando a publicação estiver desabilitada:

* Nenhuma autenticação será solicitada.
* Nenhum repositório será criado ou modificado no GitHub.
* O projeto será gerado somente na pasta local selecionada.

## Autenticação no GitHub

Para criar e publicar repositórios no GitHub, o Gênesis utiliza um token de acesso pessoal (*Personal Access Token — PAT*).

Quando a opção **Permitir publicar repositório no GitHub** estiver habilitada, o Gênesis verificará se existe um token armazenado no Gerenciador de Credenciais do Windows.

Se nenhum token estiver cadastrado, será exibida uma janela para informar e validar uma credencial antes de continuar a criação do projeto.

Após a validação, o token será armazenado no **Gerenciador de Credenciais do Windows**, não sendo gravado nas configurações do NVDA nem nos arquivos do projeto.

Quando já existir um token armazenado, o Gênesis o recuperará automaticamente durante o processo de criação e publicação, sem solicitar novamente a autenticação.

### Como gerar um token no GitHub

1. Acesse a página de configurações de tokens do GitHub:
   [https://github.com/settings/tokens](https://github.com/settings/tokens)

2. Escolha o tipo de token adequado:
   * **Fine-grained personal access tokens:** permite configurar permissões específicas e limitar o acesso a determinados repositórios.
   * **Tokens (classic):** utiliza um modelo de permissões mais abrangente.

3. Defina um nome para identificar o token.
4. Configure a validade desejada.
5. Conceda as permissões necessárias para criar e publicar repositórios.
6. Gere o token e copie seu conteúdo.
7. Informe o token na janela de autenticação apresentada pelo Gênesis.

**Importante:** as permissões necessárias dependem do tipo de token e das operações realizadas. O token deve permitir as operações de criação do repositório e publicação dos arquivos no GitHub.

### Segurança do token

* O token é armazenado no Gerenciador de Credenciais do Windows.
* O Gênesis não grava o token nas configurações do NVDA.
* O token não é incluído nos arquivos do projeto gerado.
* O token é recuperado pelo complemento somente quando necessário para as operações com o GitHub.
* O token pode ser revogado a qualquer momento nas configurações da conta do GitHub.

## Instalação

### Via Loja de Complementos

1. Abra o NVDA.
2. Acesse **Ferramentas > Loja de Complementos**.
3. Abra a aba **Disponíveis**.
4. Pesquise por **Gênesis**.
5. Selecione o complemento e escolha **Instalar**.
6. Reinicie o NVDA, se solicitado.

### Instalação manual

1. Acesse o repositório oficial do Gênesis:
   [https://github.com/EdilbertoFonseca/genesis](https://github.com/EdilbertoFonseca/genesis)

2. Baixe o arquivo `genesis.nvda-addon`, disponível na seção de versões (*Releases*).

3. Localize o arquivo baixado e pressione Enter para iniciar a instalação.

4. Siga as instruções apresentadas pelo NVDA.

5. Reinicie o NVDA, se necessário.

## Características técnicas

* Utiliza o template oficial de complementos do NVDA como base.
* Gera projetos compatíveis com o sistema oficial de compilação.
* Permite criar projetos localmente, sem necessidade de autenticação.
* Oferece integração opcional com o GitHub.
* Aplica automaticamente os metadados ao arquivo `buildVars.py`.
* Utiliza o Gerenciador de Credenciais do Windows para armazenar o token de acesso ao GitHub.
* Organiza a estrutura do projeto de acordo com as convenções do template oficial.

## Atalhos de teclado

| Atalho | Ação |
| --- | --- |
| NVDA+Alt+G | Abre o Gênesis. |
| Alt+G | Gera um novo projeto. |
| Alt+L | Limpa todos os campos. |
| Alt+T | Clona o repositório oficial do NVDA. |
| Alt+S | Fecha o Gênesis. |

## Tradução

As traduções deste complemento são gerenciadas por meio do [projeto de complementos do NVDA no Crowdin](https://crowdin.com/project/nvdaaddons).

Para contribuir com uma tradução:

1. Crie uma conta no Crowdin.
2. Junte-se à equipe do idioma correspondente, se necessário.
3. Traduza as strings da interface e da documentação disponíveis no projeto.

Também é possível utilizar o Poedit para trabalhar localmente com arquivos `.po` e `.xliff`.

As traduções concluídas são sincronizadas com o repositório do complemento por meio do fluxo de trabalho de localização.

Para dúvidas ou assistência, participe da [lista de discussão de traduções do NVDA](https://groups.io/g/nvda-translations).
