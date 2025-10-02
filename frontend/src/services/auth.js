import axios from 'axios';

const USER_KEY = 'current_user';

export async function loadCurrentUser() {
  try {
    const res = await axios.get('/me');
    const user = res.data;
    // normalizar códigos de permissão e salvar em campo auxiliar
      if (user && Array.isArray(user.permissoes)) {
        // Normaliza tanto o código quanto a descrição (caso o backend tenha descrições legadas)
        const perms = new Set();
        user.permissoes.forEach(p => {
          if (p && p.codigo) perms.add(normalizeCode(p.codigo));
          if (p && p.descricao) perms.add(normalizeCode(p.descricao));
          // backend may provide codigo_normalized already
          if (p && p.codigo_normalized) perms.add(normalizeCode(p.codigo_normalized));
        });
        user._perms_normalized = Array.from(perms);
      } else {
        user._perms_normalized = [];
      }
      // debug: mostrar permissões carregadas e normalizadas
      try { console.debug('[auth] current_user loaded:', { raw: res.data, normalized: user._perms_normalized }); } catch(e){}
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    // emitir evento global para avisar que o usuário foi carregado/atualizado
    try {
      window.dispatchEvent(new CustomEvent('auth:updated', { detail: { user } }));
    } catch (e) {
      // fallback para navegadores antigos
      window.dispatchEvent(new Event('auth:updated'));
    }
    return user;
  } catch (err) {
    console.warn('Não foi possível carregar usuário atual:', err && err.response ? err.response.data : err.message);
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setCurrentUser(user) {
  if (user) {
    // garantir campo normalizado
    if (user && Array.isArray(user.permissoes)) {
      const perms = new Set();
      user.permissoes.forEach(p => {
        if (p && p.codigo) perms.add(normalizeCode(p.codigo));
        if (p && p.descricao) perms.add(normalizeCode(p.descricao));
        if (p && p.codigo_normalized) perms.add(normalizeCode(p.codigo_normalized));
      });
      user._perms_normalized = Array.from(perms);
    } else {
      user._perms_normalized = [];
    }
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
  else localStorage.removeItem(USER_KEY);
}

export function clearCurrentUser() {
  localStorage.removeItem(USER_KEY);
}

export function hasPermission(codigo) {
  const user = getCurrentUser();
  if (!user) return false;
  // support passing array (any must match)
  const wanted = Array.isArray(codigo) ? codigo.map(normalizeCode) : [normalizeCode(codigo)];
  // prefer the precomputed normalized list
  const have = Array.isArray(user._perms_normalized) ? user._perms_normalized : [];
  if (have.length > 0) {
    return wanted.some(w => have.includes(w));
  }
  // fallback: compare normalizing each stored codigo/descricao
  if (!user.permissoes || !Array.isArray(user.permissoes)) return false;
  const store = user.permissoes.map(p => normalizeCode(p.codigo)).concat(user.permissoes.map(p => normalizeCode(p.descricao)));
  return wanted.some(w => store.includes(w));
}

function normalizeCode(s) {
  if (!s && s !== 0) return '';
  try {
    return String(s).trim().toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  } catch (e) {
    return String(s);
  }
}

export default {
  loadCurrentUser,
  getCurrentUser,
  setCurrentUser,
  clearCurrentUser,
  hasPermission
};
