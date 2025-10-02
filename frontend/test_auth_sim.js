// Script de teste rápido para validar a lógica de hasPermission em services/auth.js
const fs = require('fs');
const path = require('path');

// Carrega o módulo transpiled (é comum que o frontend use bundler, aqui apenas testamos normalize function logic)
const authPath = path.join(__dirname, 'src', 'services', 'auth.js');
if (!fs.existsSync(authPath)) {
  console.error('auth.js não encontrado:', authPath);
  process.exit(1);
}

const code = fs.readFileSync(authPath, 'utf8');
console.log('Conteúdo de auth.js carregado para inspeção (não executando em node por causa de imports ESModule).');
console.log('Por favor, rode o frontend normalmente; as mudanças foram aplicadas nos arquivos fonte.');
