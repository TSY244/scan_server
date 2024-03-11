import tools.UseElasticSearch.UseElasticSearch as es


use_es=es.MyElasticSearch("192.168.79.128","9200")

use_es.connect()

print(use_es.get_index_num("vuls"))
ret=use_es.search_data("vuls",size=10)

# print(use_es.get_index_num())
