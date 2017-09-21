# NemLiNemLereiBot

NemLiNemLereiBot é um Reddit Bot inspirado no /u/autotldr que resume as notícias enviadas pelos usuários.

## TODO

- [ ] Refatorar e organizar o código (Principalmente o pacote database)
- [ ] Tratar Exceptions
- [ ] Contar em porcentagem a redução do artigo em relação ao resumo.

## Instalação

Linux:

Instale a biblioteca libmysqlclient-dev (necessária para conexão com banco de dados MySQL).

```sh
sudo apt-get install libmysqlclient-dev
```
Instale as dependências:

```sh
pip install -r requirements.txt
```
Após instalar as dependências, baixe os Punkt Tokenizer Models (necessário para a biblioteca sumy).
```sh
python3 -c "import nltk; nltk.download('punkt')" 
```

## Configuração

Renomeie o arquivo config.sample.yml para config.yml e preencha com as credenciais.
## Uso

O bot é dividido em três partes, watch, fetch and reply. Os três executam em loop infinito.

Watch - Procura por novos posts (submissões) em um subreddit.
```sh
./Bot.py watch
```
Fetch - Extrai os metadados de um artigo de um site e resume.
```sh
./Bot.py fetch
```
Reply - Responde os posts (submissões) com o resumo.
```sh
./Bot.py reply
```

## Extensões

As extensões ajudam o bot a interpretar as páginas sem a necessidade de modificar o código principal do projeto. É *extremamante recomentável* utilizar a biblioteca [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) para extrair os dados dos artigos. Segue o exemplo mais básico de um plugin.
```Python
""" Crie uma classe chamada Plugin """
class Plugin():
    """ register_plugin é um método obrigatório, ele dirá ao gerenciador de plugins 
    qual o nome do plugin (mesmo nome do arquivo sem .py) e por qual padrão (regex) 
    de URL ele deve ser invocado para interpretar a página.
    Defina com cautela o padrão regex, evite que o mesmo padrão caia em páginas como
    blogs ou qualquer outra coisa do mesmo domínio, eles tendem a ter uma estrutura
    em html diferente das outras e pode fazer com que o plugin não consiga interpretá-lo
     da maneira correta.
    """
    def register_plugin(self, PluginManager):
        PluginManager.register_plugin(
            'g1_globo_com', r"^https?://g1.globo.com((?!/google/amp/))(.*)/noticia/(.*).ghtml$")
    
    """ get_article_metadata é um outro método obrigatório, este deverá retornar um
    dicionário contendo as chaves 'subtitle', 'date_published' e 'content'.
    Subtitle deverá conter o subtítulo da notícia, se houver.
    Date_published deverá conter a data de publicação da notícia (em objeto datetime), 
    se houver.
    Content deverá conter o conteúdo da notícia, por razões óbvias este é o único 
    dado obrigatório."""
    def get_article_metadata(self, url):
        ...
        return {'subtitle': self.get_title(),
                'date_published': self.get_date(),
                'content': self.get_content()}
```
## Contribuições
Sua ajuda será sempre bem-vinda, qualquer coisa só commitar ;)
