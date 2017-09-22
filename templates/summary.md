{% if article.date_published %}
^Notícia ^publicada ^em ^20/09/2017, ^segue ^o ^melhor ^resumo ^que ^eu ^pude ^fazer:
{% else %}
^Segue ^o ^melhor ^resumo ^que ^eu ^pude ^fazer:
{% endif %}  

{% if article.subtitle %}
>**{{ article.subtitle|trim }}**  

{% endif %}
> {{ article.summary }}

{% if article.archiveis_link %}
^(O site está fora do ar ou algum problema com paywall?) [^(Leia aqui.)]({{ article.archiveis_link }})
{% endif %}

***

^[[desenvolvedor](https://www.reddit.com/u/CaioWzy) ^| ^[código-fonte](https://github.com/CaioWzy/NemLiNemLereiBot)]