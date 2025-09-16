FROM node:18-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["npm", "run", "serve", "--", "--port", "8080", "--host", "0.0.0.0"]
