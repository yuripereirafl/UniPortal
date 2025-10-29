# Deploy na VM (192.168.1.37)

Este arquivo descreve como usar o `deploy.sh` incluído para atualizar/clonar a branch `Portal_atual` e subir o stack via `docker compose`.

Pré-requisitos na VM:
- Git instalado
- Docker instalado e configurado
- Usuário com permissão para executar `docker compose` (ou uso de sudo)

Uso rápido:

1. Copie o repositório para a VM (ou use git clone manualmente)

2. Execute o script (na pasta do usuário, por exemplo):

```bash
cd ~
bash System_ti-main/deploy.sh Portal_atual true
```

Parâmetros opcionales do `deploy.sh`:
- `branch` — branch do Git a clonar/atualizar (padrão: Portal_atual)
- `use_compose` — `true` ou `false`. Quando `true` o script ajusta `.env` para `DB_HOST=db` (padrão: true).

Notas:
- O script faz backup da pasta `System_ti-main` existente movendo-a para `System_ti-main.bak.<timestamp>`.
- O script também cria backup do `.env` existente como `.env.bak.<timestamp>`.
- Se preferir atualizar um repositório já existente em vez de clonar limpo, não use este script; em vez disso execute `git fetch && git reset --hard origin/Portal_atual` dentro da pasta.

Depois do deploy, verifique os logs com:

```bash
cd ~/System_ti-main
sudo docker compose logs -f backend
```

Se houver problemas no startup do backend (ex.: dependências Python), entre no container backend para debugging:

```bash
sudo docker compose exec backend /bin/sh
# dentro do container, você pode checar arquivos, instalar dependências, rodar uvicorn manualmente etc.
```
