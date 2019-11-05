# Configuração (em ambiente linux)
## Configuração do ambiente onde vai ser executada a aplicação
 - É necessário possuir instalado o *pipenv* no computador
 - Num terminal aberto no diretório do projeto, correr:
 ```bash
 $ pipenv shell
 $ pipenv install djangorestframework==2.2.5 ; pipenv install django-rest-swagger ; pipenv install requests ; pipenv install django ; pipenv install mysqlclient ; pipenv install python3-docutils
 ```

## Configuração da base de dados
- É necessário possuir o *SGBD MySql* instalado no computador.
- Num terminal, correr:
```bash
$ sudo mysql -h localhost
```
- No ambiente que é aberto, executar:
```sql
mysql> CREATE DATABASE fool;
mysql> CREATE USER 'django'@'localhost' IDENTIFIED BY 'django';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'django'@'localhost';
```

# Executar a aplicação
 - Num terminal aberto no diretório do projeto, correr:
 ```bash
 $ pipenv shell
 $ python manage.py makemigrations page
 $ python manage.py migrate
 $ python manage.py createsuperuser         # usado para criar um super utilizador (importante, para aceder ás páginas do web site que requerem sessão de administrador)
 $ python manage.py runserver
 ```
 - Num browser, aceder à [página](localhost:8000) 


# Features do web site
 - No menu do *site*:
   - **`Equipas`**: Apresenta todas as equipas
     - **`Página da equipa`**: Após se carregar em `VER MAIS` numa das equipas da página anterior, é carregada a página da equipa escolhida, onde é possivel ver as infos desta, o seu logo e os seus jogadores ordenados de acordo com a posição em que jogam. Nesta página, é possivel carregar no **`estádio da equipa`** para aceder ás infos deste e é também possivel clicar no **`botão + em cada jogador`**, para aceder à página com as informações deste
   - **`Jogos`**: Apresentam-se listados os jogos temporalmente (primeiro os mais recentes). Ao se carregar no botão **MAIS INFO**, é aberto um *container* com todas as informações do jogo. Neste *container*, ao fundo, ao se clicar no botão **EVENTOS**, é aberto um *dropdown* com um *timeline* dos eventos que decorreram nesse jogo, ordenados temporalmente. Na página dos jogos é também possivel aceder à página de cada equipa que jogou, carregando no nome desta e aceder à página de cada jogador que participou num determinado evento, carregando-se no nome deste.
   - **`Iniciar sessão`**: Abre a página para inicio de sessão, onde é possivel fazer *login* como administrador do site. Após este procedimento, ao invés de aparecer **`Iniciar sessão`** no menu, aparece **`Conta`**, que é um dropdown com algumas das tarefas que o administrador pode realizar.
   - **`Conta`**
     - **`Adicionar estádio`**: Abre uma página onde é possivel adicionar um estádio
     - **`Adicionar equipa`** : Abre uma página onde é possivel adicionar uma nova equipa
     - **`Adicionar jogador`**: Abre uma página, onde é possivel adicionar um novo jogador (a uma equipa)
     - **`Adicionar jogo`**: Abre uma página onde é possivel adicionar um novo jogo entre duas equipas já existentes, desde que ambas possuam pelo menos 14 jogadores registados.
 - É também possivel editar todos os dados (quando logado como admin), acedendo a todas as páginas descritas nos pontos **`Equipas`** e **`Jogos`**, bastando encontrar na página um botão alaranjado com o texto **EDITAR**. É também possivel adicionar novos eventos e jogadores a um jogo na página dos jogos, nos dois botões verdes que existem em cada um dos jogos (obviamente, também só são mostrados quando o administrador tem sessão iniciada). Para editar os jogadores que jogam num jogo, basta carregar no botão **MAIS INFO** dum dos jogos da página **`Jogos`**, dirigir-se ao final do *container* que é aberto e carregar no botão **EVENTOS**, sendo que do lado direito do *dropdown* que se abre, aparece um botão laranja com o texto **EDITAR JOGADORES DO JOGO**. Para editar um evento, basta nesse *dropdown* dirigir-se a um evento e carregar no botão **EDITAR** a laranja. 
 - É também possivel efetuar operações de remoção em cada uma das páginas de edição (quando se encontra iniciada uma sessão de administrador).

# Web page onde se encontra uma demo do site
https://escaleira.pythonanywhere.com/
