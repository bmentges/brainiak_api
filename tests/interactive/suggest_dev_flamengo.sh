curl -X POST http://brainiak.semantica.dev.globoi.com/_suggest -d '{
                "search": {
                    "pattern": "flamengo",
                    "target": "esportes:tem_como_conteudo",
                    "fields": ["base:dados_buscaveis"],
                    "graphs": ["http://semantica.globo.com/esportes/"]
                },
                "response": {
                    "meta_fields": ["base:detalhe_da_cortina"],
                    "class_fields": ["base:thumbnail"]
                }
            }'

