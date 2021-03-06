# NemLiNemLereiBot

NemLiNemLereiBot é um Reddit Bot inspirado no /u/autotldr que resume as notícias enviadas pelos usuários.

## TODO

- [x] Refatorar e organizar o código (Em andamento).
- [x] Tratar Exceptions (Em andamento).
- [x] Contar em porcentagem a redução do artigo em relação ao resumo.
- [ ] Apagar automaticamente comentários com karma negativo.
- [ ] Adicionar opção "opt out' para que o usuário possa impedir o bot de comentar suas publicações.

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

O bot criará uma pasta vazia chamada 'plugins', sem os plugins ele não trabalha pois necessita saber como processar cada página, os plugins usados no bot estão disponíveis [neste repositório](https://github.com/CaioWzy/NemLiNemLereiBot-plugins)

Você pode clonar o repositório dentro da pasta plugins:
```sh
git clone https://github.com/CaioWzy/NemLiNemLereiBot-plugins.git .
```

## Plugins

Os plugins ajudam o bot a interpretar as páginas sem a necessidade de modificar o código principal do projeto. É *extremamante recomentável* utilizar a biblioteca [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) para extrair os dados dos artigos. Segue o exemplo mais básico de um plugin.
As extensões usadas no bot estão disponíveis [aqui](https://github.com/CaioWzy/NemLiNemLereiBot-plugins), fique livre para contribuir =)
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
    
    """ extract_metadata é um outro método obrigatório, este deverá retornar um
    dicionário contendo as chaves 'subtitle', 'date_published' e 'content'.
    Subtitle deverá conter o subtítulo da notícia, se houver.
    Date_published deverá conter a data de publicação da notícia (em objeto datetime), 
    se houver.
    Content deverá conter o conteúdo da notícia, por razões óbvias este é o único 
    dado obrigatório."""
    def extract_metadata(self, url):
        ...
        return {'subtitle': self._get_subtitle(),
                'date_published': self._get_published_date(),
                'content': self._get_content()}
```
## Contribuições
Sua ajuda será sempre bem-vinda, qualquer coisa só mandar um pull request ;)
