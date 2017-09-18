{% if article.subtitle %}
**{{ article.subtitle|trim }}**  
{% endif %}

{% if article.date_published %}
^Notícia ^publicada ^em ^{{ article.date_published.strftime('%d/%m/%Y') }}  
{% endif %}

> {{ article.summary }}

^(O site está fora do ar ou algum problema com paywall?) [^(Leia aqui.)]({{ article.archiveis_link }})

***

^[[desenvolvedor](https://#) ^| ^[código-fonte](https://#)]