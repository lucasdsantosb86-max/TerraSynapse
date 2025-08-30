# Integração ClimaTempo (API Advisor)

1) Cadastre-se e obtenha seu **token** no Advisor ClimaTempo.
2) Descubra o **localeId** da sua cidade e **registre** esse ID no token.
3) Preencha o token e localeId na página Streamlit **“Clima – Provedor”** e clique em **Registrar**.
4) Teste o endpoint **GET /weather/current**.

Endpoints principais:

- **Atual**: `GET http://apiadvisor.climatempo.com.br/api/v1/weather/locale/{id}/current?token={token}`
- **Registro de cidade no token**: `PUT http://apiadvisor.climatempo.com.br/api-manager/user-token/locale/register?token={token}`
  Body JSON: `{{ "localeId": [ ID_DA_CIDADE ] }}`

> Observação: alguns ambientes exigem codificar nomes de cidades ao buscar IDs e usar `localeId` antes das consultas.