 — Sistema de PDV e Controle de Estoque (Python) —



Um sistema desktop de PDV (Ponto de Venda) e controle de estoque, desenvolvido em Python com foco em usabilidade, manutenibilidade e integração com banco de dados relacional. Projeto prático criado para demonstrar habilidades em desenvolvimento de software, construção de interfaces gráficas e organização de sistemas do mundo real.

Badges:  
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

Visão geral
----------
- Interface gráfica desenvolvida com Tkinter, pensada para fluxos rápidos de venda.
- Cadastro e busca de produtos via código de barras.
- Controle de quantidade por item, cálculo automático de subtotal e total da venda.
- Tabela de itens da venda com opções para remover itens, limpar e finalizar a venda.
- Persistência de dados em PostgreSQL (falta).
- Arquitetura para facilitar manutenção e evolução.

Principais funcionalidades

- Registro e consulta de produtos por código de barras.
- Adição de itens à venda com quantidade variável.
- Cálculo automático de subtotal por item e total da venda.
- Remoção de item selecionado / limpeza do carrinho.
- Finalização de venda (registro no banco de dados).
- Interface responsiva e organizada para operação em balcão.

Screenshots
-----------
![Tela Principal](https://github.com/user-attachments/assets/a1208e3b-9996-4d15-9672-20d68b014715)
![Atualização da Interface](https://github.com/user-attachments/assets/85eea441-86c6-47db-a530-46546b37acd3)
![Screenshot_2](https://github.com/user-attachments/assets/df7ebc4f-3ee1-4548-a09e-ceeac31f7b79)


Tecnologias
-----------
- Python 3
- Tkinter (GUI)
- PostgreSQL (persistência)
- Git / GitHub (controle de versão)
- Ferramentas de apoio: scripts de migração, ambiente virtual IDEs.

Melhorias planejadas (Roadmap)
------------------------------
- Testes automatizados (unitários e de integração);
- Melhorias de UI/UX com organização de telas e validações;
- Exportação/backup dos dados;
- Integração com leitor físico de código de barras;
- Agente de IA para análises preditivas e insights de vendas (prova de conceito).

