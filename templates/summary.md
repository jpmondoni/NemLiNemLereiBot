{% if article.percentage_decrease %}
^(Este é o melhor NL;NL que eu pude fazer, o artigo original foi reduzido em {{'%0.2f' % article.percentage_decrease|float}}%. [Eu sou um Bot] 🤖)  
{% else %}
^(Este é o melhor NL;NL que eu pude fazer: [Eu sou um Bot] 🤖)  
{% endif %}

{% if article.subtitle %}
>**{{ article.subtitle|trim }}**  

{% endif %}
> {{ article.summary }}  

{% if article.archiveis_url %}
^(O site está offline ou cai no paywall?) [^(Leia aqui.)]({{ article.archiveis_url }})  
{% endif %}

***
{% if article.date_published %}
^[colaboradores](https://github.com/CaioWzy/NemLiNemLereiBot/blob/master/AUTHORS.md) ^| ^[código-fonte](https://github.com/CaioWzy/NemLiNemLereiBot) ^| ^(notícia publicada em {{ article.date_published.strftime('%d/%m/%Y') }})  
{% else %}
^[colaboradores](https://github.com/CaioWzy/NemLiNemLereiBot/blob/master/AUTHORS.md) ^| ^[código-fonte](https://github.com/CaioWzy/NemLiNemLereiBot)  
{% endif %}
