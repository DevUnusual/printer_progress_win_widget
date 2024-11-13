# Widget de Monitoramento de Progresso de Impressão 3D

Este é um widget de bandeja do sistema, desenvolvido em Python, que monitora o progresso de impressão de uma impressora 3D conectada a uma API. Ele exibe a porcentagem de conclusão da impressão em tempo real, centralizada em um fundo branco.

## Funcionalidades

- **Exibição de Progresso**: Exibe a porcentagem de conclusão no ícone de bandeja do sistema.
- **Execução Contínua**: Pode ser configurado para iniciar automaticamente junto com o sistema operacional.

## Pré-requisitos

- **Python 3**: Certifique-se de que o Python 3 está instalado no sistema.
- **Bibliotecas Python Necessárias**:
  - `pystray`: Para manipular o ícone na bandeja do sistema.
  - `Pillow`: Para criar e modificar a imagem do ícone.
  - `requests`: Para fazer requisições HTTP para a API da impressora 3D.

### Instalação das Dependências

Execute o seguinte comando para instalar todas as bibliotecas necessárias:
```bash
pip install pystray pillow requests
```

## Como Usar
Executar o script:
### Windows
```bash
python monitor.py
```
### Linux
```bash
python3 monitor.py
```

## Inicializar junto ao sistema (buildando um executavel - windows verificado):
### Windows
-- Instalar o pyinstaller:
"--onefile" para gerar um único arquivo executável.
"--noconsole" para não abrir um console ao executar o arquivo.
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole monitor.py
```
feito isso vai ser gerado um executável na pasta "dist" com o nome "monitor.exe"
abrir o task scheduler e criar uma nova tarefa com o trigger "at startup" e na aba "actions" adicionar o caminho do executável gerado.

## Inicializar junto ao sistema (Só com script [não consegui]):
### Windows:
Abra o Agendador de Tarefas | Task schedule:
- No menu Iniciar, procure por "Agendador de Tarefas" e abra-o.
Crie uma Nova Tarefa | Create a New Task:
- Clique em Ação | Action > Criar Tarefa | Task... e dê um nome, como “Iniciar Widget de Impressão 3D”.
Configurar o Gatilho | Configure the Trigger:
- Vá para a aba Gatilhos | Trigger e clique em Novo....
- Escolha Ao iniciar para que a tarefa seja executada toda vez que o sistema iniciar | At a startup.
Configurar a Ação | Configure the Action:
- Na aba Ações, clique em Novo....
- Em Programa/script, insira o caminho completo para o executável Python, por exemplo:
```
- C:\Caminho\Para\Python\python.exe
```
- Em Adicionar argumentos, insira o caminho completo do script, por exemplo:
```
"C:\Caminho\Para\SeuScript\widget_impressao.py"
```	
Clique em OK para salvar a tarefa.
