<template>
  <div class="tabela-funcionarios">
    <div class="header header-funcionarios">
      <h2>Funcionários</h2>
      <div class="busca-adicionar">
        <label style="display: flex; align-items: center; gap: 6px;">
          <input type="checkbox" v-model="somenteAtivos" />
          Mostrar apenas funcionários ativos
        </label>
        <input v-model="buscaFuncionario" placeholder="Buscar funcionário..." class="input-busca" />
        <button class="btn-relatorio" @click="abrirModalRelatorio">📊 Relatórios</button>
        <button class="btn-cadastrar" @click="showForm = !showForm">
          + Adicionar Funcionário
        </button>
      </div>
    </div>
    <!-- Modal de Relatórios -->
    <div v-if="showModalRelatorio" class="modal-overlay">
      <div class="form-modal">
        <h3>Exportar Relatório</h3>
        <p>Exporte todos os funcionários em XLSX.</p>
        <div class="modal-actions">
          <button @click="exportarFuncionariosXLSX">Exportar XLSX</button>
          <button @click="fecharModalRelatorio">Fechar</button>
        </div>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th @click="toggleOrdenacaoNome" style="cursor:pointer">
            Nome
            <span v-if="ordenacaoNome === 'asc'">▲</span>
            <span v-else>▼</span>
          </th>
          <th>Sobrenome</th>
          <th>Data de Admissão</th>
          <th>Data de Desligamento</th>
          <th>Celular</th>
          <th>E-mail</th>
          <th>Grupo E-mail</th>
          <th>Pastas</th>
          <th>Setor</th>
          <th>Cargo</th>
          <th>Sistemas</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="func in funcionariosFiltrados" :key="func.id">
          <td :class="['clicavel', celulasExpandidas.has('nome-' + func.id) ? 'expandida' : '']" @click="toggleCelula('nome-' + func.id)">
            {{ func.nome }}
          </td>
          <td :class="['clicavel', celulasExpandidas.has('sobrenome-' + func.id) ? 'expandida' : '']" @click="toggleCelula('sobrenome-' + func.id)">
            {{ func.sobrenome }}
          </td>
          <td>
            {{ func.data_admissao ? func.data_admissao.split('-').reverse().join('/') : '—' }}
          </td>
          <td>
            {{ func.data_inativado ? func.data_inativado.split('-').reverse().join('/') : '—' }}
          </td>
          <td :class="['clicavel', celulasExpandidas.has('celular-' + func.id) ? 'expandida' : '']" @click="toggleCelula('celular-' + func.id)">
            {{ func.celular }}
          </td>
          <td :class="['clicavel', celulasExpandidas.has('email-' + func.id) ? 'expandida' : '']" @click="toggleCelula('email-' + func.id)">
            {{ func.email }}
          </td>
          <td :class="['clicavel', celulasExpandidas.has('grupos-' + func.id) ? 'expandida' : '']" @click="toggleCelula('grupos-' + func.id)">
            <span v-if="func.grupos_email && func.grupos_email.length">
              {{ func.grupos_email.map(g => g.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td :class="['clicavel', celulasExpandidas.has('grupos-pasta-' + func.id) ? 'expandida' : '']" @click="toggleCelula('grupos-pasta-' + func.id)">
            <span v-if="func.grupos_pasta && func.grupos_pasta.length">
              {{ func.grupos_pasta.map(g => g.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td :class="['clicavel', celulasExpandidas.has('setores-' + func.id) ? 'expandida' : '']" @click="toggleCelula('setores-' + func.id)">
            <span v-if="func.setores && func.setores.length">
              {{ func.setores.map(s => s.nome).join(', ') }}
            </span>
            <span v-else>—</span>
          </td>
          <td :class="['clicavel', celulasExpandidas.has('cargo-' + func.id) ? 'expandida' : '']" @click="toggleCelula('cargo-' + func.id)">
            {{ func.cargo || '—' }}
          </td>
          <td :class="['clicavel', celulasExpandidas.has('sistemas-' + func.id) ? 'expandida' : '']" @click="toggleCelula('sistemas-' + func.id)">
            <span v-if="func.sistemas && func.sistemas.length">
              {{ func.sistemas.map(s => `${s.nome} (${s.status})`).join(', ') }}
            </span>
            <span v-else>Nenhum sistema vinculado</span>
          </td>
          <td>
            <button class="btn-editar" @click="abrirEditar(func)">✏️</button>
            <button class="btn-excluir" @click="excluirFuncionario(func.id)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay">
      <div class="form-modal">
        <h3>{{ editando ? 'Editar Funcionário' : 'Adicionar Funcionário' }}</h3>
        <form @submit.prevent="editando ? salvarEdicaoFuncionario() : cadastrarFuncionario()">
          <!-- Bloco principal do formulário -->
          <div class="form-grid">
            <div>
              <label>Nome</label>
              <input v-model="form.nome" placeholder="Nome" required />
            </div>
            <div>
              <label>Sobrenome</label>
              <input v-model="form.sobrenome" placeholder="Sobrenome" required />
            </div>
            <div>
              <label>Celular</label>
              <input v-model="form.celular" placeholder="Celular" />
            </div>
            <div>
              <label>CPF</label>
              <input v-model="form.cpf" placeholder="CPF" />
            </div>
            <div>
              <label>Data de Admissão</label>
              <input type="date" v-model="form.data_admissao" />
            </div>
            <div>
              <label>Tipo de Contrato</label>
              <input v-model="form.tipo_contrato" placeholder="Tipo de Contrato" />
            </div>
            <div style="grid-column: span 2;">
              <label>E-mail</label>
              <input v-model="form.email" placeholder="E-mail" required type="email" />
            </div>
            <div v-if="editando" style="grid-column: span 2;">
              <label>Data de Desligamento</label>
              <input type="date" v-model="form.data_inativado" />
              <button type="button" @click="inativarFuncionario" style="width: 220px; margin-top: 8px;">Inativar hoje</button>
            </div>
            <div v-if="editando">
              <label>Data de Afastamento</label>
              <input type="date" v-model="form.data_afastamento" />
            </div>
            <div v-if="editando">
              <label>Data de Retorno</label>
              <input type="date" v-model="form.data_retorno" />
            </div>
          </div>
          <hr class="modal-divider" />
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Grupos de E-mail:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.grupos_email_ids" :key="id" class="selected-chip" @click="removeGrupo(id)">
                      {{ getGrupoNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoGrupoId" @change="addGrupo" class="multi-select">
                    <option value="">+ Adicionar grupo...</option>
                    <option v-for="grupo in gruposEmailDisponiveis" :key="grupo.id" :value="grupo.id">
                      {{ grupo.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-col">
              <div class="select-group">
                <label>Grupos de Pastas:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.grupos_pasta_ids" :key="id" class="selected-chip" @click="removeGrupoPasta(id)">
                      {{ getGrupoPastaNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoGrupoPastaId" @change="addGrupoPasta" class="multi-select">
                    <option value="">+ Adicionar grupo de pastas...</option>
                    <option v-for="grupo in gruposPastaDisponiveis" :key="grupo.id" :value="grupo.id">
                      {{ grupo.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Setores:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.setores_ids" :key="id" class="selected-chip" @click="removeSetor(id)">
                      {{ getSetorNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoSetorId" @change="addSetor" class="multi-select">
                    <option value="">+ Adicionar setor...</option>
                    <option v-for="setor in setoresDisponiveis" :key="setor.id" :value="setor.id">
                      {{ setor.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-col">
              <div class="select-group">
                <label>Sistemas:</label>
                <div class="multi-select-container">
                  <div class="selected-items">
                    <span v-for="id in form.sistemas_ids" :key="id" class="selected-chip" @click="removeSistema(id)">
                      {{ getSistemaNome(id) }}
                    </span>
                  </div>
                  <select v-model="novoSistemaId" @change="addSistema" class="multi-select">
                    <option value="">+ Adicionar sistema...</option>
                    <option v-for="sistema in sistemasDisponiveis" :key="sistema.id" :value="sistema.id">
                      {{ sistema.nome }} ({{ sistema.status }})
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-row selects-2x2">
            <div class="modal-col">
              <div class="select-group">
                <label>Cargo:</label>
                <CargoMultiSelect
                  v-model="form.cargo_id"
                  :multiple="false"
                />
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-cadastrar">Salvar</button>
            <button type="button" @click="fecharModal">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../api';
import CargoMultiSelect from '../components/CargoMultiSelect.vue';

export default {
  components: { CargoMultiSelect },
  data() {
    return {
      funcionarios: [],
      setores: [],
      sistemas: [],
      showForm: false,
      editando: false,
      funcionarioEditId: null,
      form: {
        nome: '',
        sobrenome: '',
        celular: '',
        email: '',
        cpf: '',
        tipo_contrato: '',
        data_afastamento: '',
        data_retorno: '',
        grupo_email: '',
        setores_ids: [],
        sistemas_ids: [],
        grupos_email_ids: [],
        grupos_pasta_ids: [],
        data_admissao: '',
        data_inativado: '',
        cargo_id: null
      },
      gruposEmail: [],
      gruposPasta: [],
      buscaFuncionario: '',
      celulasExpandidas: new Set(), 
      novoGrupoId: '',
      novoSetorId: '',
      novoSistemaId: '',
      novoGrupoPastaId: '',
      ordenacaoNome: 'asc',
      showModalRelatorio: false,
      somenteAtivos: true, // filtro padrão ativado
    }
  },
  computed: {
    funcionariosFiltrados() {
      let lista = this.funcionarios;
      if (this.buscaFuncionario) {
        const busca = this.buscaFuncionario.toLowerCase();
        lista = lista.filter(f => {
          const nome = (f.nome || '').toLowerCase();
          const sobrenome = (f.sobrenome || '').toLowerCase();
          const email = (f.email || '').toLowerCase();
          const cargo = (f.cargo || '').toLowerCase();
          const celular = (f.celular || '').toLowerCase();
          // Busca por sistemas
          const sistemas = (f.sistemas && f.sistemas.length)
            ? f.sistemas.map(s => (s.nome || '').toLowerCase()).join(', ')
            : '';
          // Busca por setores
          const setores = (f.setores && f.setores.length)
            ? f.setores.map(s => (s.nome || '').toLowerCase()).join(', ')
            : '';
          // Busca por grupos de pastas
          const gruposPasta = (f.grupos_pasta && f.grupos_pasta.length)
            ? f.grupos_pasta.map(g => (g.nome || '').toLowerCase()).join(', ')
            : '';
          return (
            nome.includes(busca) ||
            sobrenome.includes(busca) ||
            email.includes(busca) ||
            cargo.includes(busca) ||
            celular.includes(busca) ||
            sistemas.includes(busca) ||
            setores.includes(busca) ||
            gruposPasta.includes(busca)
          );
        });
      }
      // Filtra apenas funcionários ativos, se selecionado
      if (this.somenteAtivos) {
        lista = lista.filter(f => !f.data_inativado);
      }
      // Ordena por nome, asc ou desc
      return lista.slice().sort((a, b) => {
        const nomeA = (a.nome || '').toLowerCase();
        const nomeB = (b.nome || '').toLowerCase();
        if (nomeA < nomeB) return this.ordenacaoNome === 'asc' ? -1 : 1;
        if (nomeA > nomeB) return this.ordenacaoNome === 'asc' ? 1 : -1;
        return 0;
      });
    },
    gruposEmailDisponiveis() {
      return this.gruposEmail
        .filter(grupo => !this.form.grupos_email_ids.includes(grupo.id))
        .slice().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    },
    gruposPastaDisponiveis() {
      const gruposPastaIds = Array.isArray(this.form.grupos_pasta_ids) ? this.form.grupos_pasta_ids : [];
      return this.gruposPasta
        .filter(grupo => !gruposPastaIds.includes(grupo.id))
        .slice().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    },
    setoresDisponiveis() {
      return this.setores.filter(setor => !this.form.setores_ids.includes(setor.id));
    },
    sistemasDisponiveis() {
      return this.sistemas
        .filter(sistema => !this.form.sistemas_ids.includes(sistema.id))
        .slice().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    }
  },
  methods: {
    abrirModalRelatorio() {
      this.showModalRelatorio = true;
    },
    fecharModalRelatorio() {
      this.showModalRelatorio = false;
    },
    async exportarFuncionariosXLSX() {
      // Chama endpoint backend para exportar XLSX
      try {
        const response = await axios({
          url: `${API_BASE_URL}/relatorios/funcionarios/xlsx`,
          method: 'GET',
          responseType: 'blob',
        });
        // Cria link para download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'funcionarios.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        this.fecharModalRelatorio();
      } catch (err) {
        alert('Erro ao exportar relatório.');
      }
    },
    async carregarGruposPasta() {
      const res = await axios.get(`${API_BASE_URL}/grupos-pasta/`);
      this.gruposPasta = res.data;
    },
    inativarFuncionario() {
      // Preenche com a data atual no formato yyyy-mm-dd
      this.form.data_inativado = new Date().toISOString().slice(0, 10);
    },
    toggleCelula(key) {
      if (this.celulasExpandidas.has(key)) {
        this.celulasExpandidas.delete(key);
      } else {
        this.celulasExpandidas.add(key);
      }
      // Forçar atualização do Vue (Set não é reativo)
      this.celulasExpandidas = new Set(this.celulasExpandidas);
    },
    // Métodos para Select Múltiplo - Grupos
    addGrupo() {
      if (this.novoGrupoId && !this.form.grupos_email_ids.includes(parseInt(this.novoGrupoId))) {
        this.form.grupos_email_ids.push(parseInt(this.novoGrupoId));
        this.novoGrupoId = '';
      }
    },
    removeGrupo(id) {
      this.form.grupos_email_ids = this.form.grupos_email_ids.filter(gId => gId !== id);
    },
    getGrupoNome(id) {
      const grupo = this.gruposEmail.find(g => g.id === id);
      return grupo ? grupo.nome : 'Grupo não encontrado';
    },
    // Métodos para Select Múltiplo - Setores
    addSetor() {
      if (this.novoSetorId && !this.form.setores_ids.includes(parseInt(this.novoSetorId))) {
        this.form.setores_ids.push(parseInt(this.novoSetorId));
        this.novoSetorId = '';
      }
    },
    removeSetor(id) {
      this.form.setores_ids = this.form.setores_ids.filter(sId => sId !== id);
    },
    getSetorNome(id) {
      const setor = this.setores.find(s => s.id === id);
      return setor ? setor.nome : 'Setor não encontrado';
    },
    // Métodos para Select Múltiplo - Sistemas
    addSistema() {
      if (this.novoSistemaId && !this.form.sistemas_ids.includes(parseInt(this.novoSistemaId))) {
        this.form.sistemas_ids.push(parseInt(this.novoSistemaId));
        this.novoSistemaId = '';
      }
    },
    removeSistema(id) {
      this.form.sistemas_ids = this.form.sistemas_ids.filter(sId => sId !== id);
    },
    getSistemaNome(id) {
      const sistema = this.sistemas.find(s => s.id === id);
      return sistema ? sistema.nome : 'Sistema não encontrado';
    },
    // Métodos para Select Múltiplo - Grupos de Pastas
    addGrupoPasta() {
      if (this.novoGrupoPastaId && !this.form.grupos_pasta_ids.includes(parseInt(this.novoGrupoPastaId))) {
        this.form.grupos_pasta_ids.push(parseInt(this.novoGrupoPastaId));
        this.novoGrupoPastaId = '';
      }
    },
    removeGrupoPasta(id) {
      this.form.grupos_pasta_ids = this.form.grupos_pasta_ids.filter(gId => gId !== id);
    },
    getGrupoPastaNome(id) {
      const grupo = this.gruposPasta.find(g => g.id === id);
      return grupo ? grupo.nome : 'Grupo não encontrado';
    },
    async cadastrarFuncionario() {
      // Garante que data_admissao seja string no formato 'YYYY-MM-DD' ou vazio
      let dataAdmissaoFormatada = '';
      if (this.form.data_admissao) {
        if (typeof this.form.data_admissao === 'string') {
          dataAdmissaoFormatada = this.form.data_admissao;
        } else if (this.form.data_admissao instanceof Date) {
          const year = this.form.data_admissao.getFullYear();
          const month = String(this.form.data_admissao.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_admissao.getDate()).padStart(2, '0');
          dataAdmissaoFormatada = `${year}-${month}-${day}`;
        }
      }
      await axios.post(`${API_BASE_URL}/funcionarios/`, {
        nome: this.form.nome,
        sobrenome: this.form.sobrenome,
        cargo_id: this.form.cargo_id,
        celular: this.form.celular,
        email: this.form.email || '',
        cpf: this.form.cpf,
        tipo_contrato: this.form.tipo_contrato,
        grupos_email_ids: [...this.form.grupos_email_ids],
        setores_ids: [...this.form.setores_ids],
        sistemas_ids: [...this.form.sistemas_ids],
        grupos_pasta_ids: [...this.form.grupos_pasta_ids],
        data_admissao: dataAdmissaoFormatada,
        data_inativado: ''
      });
      await this.carregarFuncionarios();
      this.fecharModal();
    },
    fecharModal() {
      this.showForm = false;
      this.editando = false;
      this.funcionarioEditId = null;
      this.form = {
        nome: '',
        sobrenome: '',
        cargo: '',
        celular: '',
        email: '',
        cpf: '',
        tipo_contrato: '',
        data_afastamento: '',
        data_retorno: '',
        grupo_email: '',
        setores_ids: [],
        sistemas_ids: [],
        grupos_email_ids: [],
        grupos_pasta_ids: [],
        data_admissao: '',
        data_inativado: ''
      };
      this.novoGrupoId = '';
      this.novoSetorId = '';
      this.novoSistemaId = '';
      this.novoGrupoPastaId = '';
    },
    async carregarGruposEmail() {
      const res = await axios.get(`${API_BASE_URL}/grupos-email/`);
      this.gruposEmail = res.data;
    },
    async carregarFuncionarios() {
      const res = await axios.get(`${API_BASE_URL}/funcionarios/`);
      this.funcionarios = res.data;
    },
    toggleOrdenacaoNome() {
      this.ordenacaoNome = this.ordenacaoNome === 'asc' ? 'desc' : 'asc';
    },
    async carregarSetores() {
      const res = await axios.get(`${API_BASE_URL}/setores/`);
      this.setores = res.data;
    },
    async carregarSistemas() {
      const res = await axios.get(`${API_BASE_URL}/sistemas/`);
      this.sistemas = res.data;
    },
    abrirEditar(func) {
      let dataInativado = '';
      if (func.data_inativado && func.data_inativado.length >= 10) {
        dataInativado = func.data_inativado.slice(0, 10);
      }
      this.form = {
        nome: func.nome,
        sobrenome: func.sobrenome,
        cargo_id: func.cargo_id || null,
        celular: func.celular,
        email: func.email,
        grupo_email: (func.grupo_email || ''),
        setores_ids: func.setores ? func.setores.map(s => s.id) : [],
        sistemas_ids: func.sistemas ? func.sistemas.map(s => s.id) : [],
        grupos_email_ids: func.grupos_email ? func.grupos_email.map(g => g.id) : [],
        grupos_pasta_ids: func.grupos_pasta ? func.grupos_pasta.map(g => g.id) : [],
        data_admissao: func.data_admissao || '',
        data_inativado: dataInativado || '',
        cpf: func.cpf || '',
        tipo_contrato: func.tipo_contrato || '',
        data_afastamento: func.data_afastamento || '',
        data_retorno: func.data_retorno || ''
      };
      this.funcionarioEditId = func.id;
      this.editando = true;
      this.showForm = true;
      axios.get(`${API_BASE_URL}/funcionarios/${func.id}/sistemas`).then(res => {
        this.form.sistemas_ids = res.data.map(s => s.id);
      });
    },
    async salvarEdicaoFuncionario() {
      // Garante tipos corretos antes do envio
      let dataInativadoFormatada = '';
      if (this.form.data_inativado) {
        if (typeof this.form.data_inativado === 'string') {
          dataInativadoFormatada = this.form.data_inativado;
        } else if (this.form.data_inativado instanceof Date) {
          const year = this.form.data_inativado.getFullYear();
          const month = String(this.form.data_inativado.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_inativado.getDate()).padStart(2, '0');
          dataInativadoFormatada = `${year}-${month}-${day}`;
        }
      }
      // Arrays nunca undefined ou string
      const grupos_email_ids = Array.isArray(this.form.grupos_email_ids) ? this.form.grupos_email_ids : [];
      const setores_ids = Array.isArray(this.form.setores_ids) ? this.form.setores_ids : [];
      const sistemas_ids = Array.isArray(this.form.sistemas_ids) ? this.form.sistemas_ids : [];
      const grupos_pasta_ids = Array.isArray(this.form.grupos_pasta_ids) ? this.form.grupos_pasta_ids : [];
      // cargo_id nunca string vazia
      let cargo_id = this.form.cargo_id;
      if (cargo_id === '' || cargo_id === undefined) cargo_id = null;
      // Garante formato correto para data_admissao
      let dataAdmissaoFormatada = '';
      if (this.form.data_admissao) {
        if (typeof this.form.data_admissao === 'string') {
          dataAdmissaoFormatada = this.form.data_admissao;
        } else if (this.form.data_admissao instanceof Date) {
          const year = this.form.data_admissao.getFullYear();
          const month = String(this.form.data_admissao.getMonth() + 1).padStart(2, '0');
          const day = String(this.form.data_admissao.getDate()).padStart(2, '0');
          dataAdmissaoFormatada = `${year}-${month}-${day}`;
        }
      }
      await axios.put(`${API_BASE_URL}/funcionarios/${this.funcionarioEditId}`, {
        nome: this.form.nome,
        sobrenome: this.form.sobrenome,
        cargo_id: this.form.cargo_id,
        celular: this.form.celular,
        email: this.form.email || '',
        cpf: this.form.cpf,
        tipo_contrato: this.form.tipo_contrato,
        data_afastamento: this.form.data_afastamento,
        data_retorno: this.form.data_retorno,
        grupos_email_ids,
        setores_ids,
        sistemas_ids,
        grupos_pasta_ids,
        data_admissao: dataAdmissaoFormatada,
        data_inativado: dataInativadoFormatada
      });
      await this.carregarFuncionarios();
      this.fecharModal();
    },
    async excluirFuncionario(id) {
      if (confirm('Tem certeza que deseja excluir este funcionário?')) {
        try {
          await axios.delete(`${API_BASE_URL}/funcionarios/${id}`);
          await this.carregarFuncionarios();
        } catch (error) {
          alert('Erro ao excluir funcionário. Verifique se o funcionário existe ou se há dependências.');
        }
      }
    },
  },
  mounted() {
    this.carregarFuncionarios();
    this.carregarSetores();
    this.carregarSistemas();
    this.carregarGruposEmail();
    this.carregarGruposPasta();
  }
}
</script>


<style scoped>
.btn-relatorio {
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  margin-right: 8px;
  transition: background 0.2s;
}
.btn-relatorio:hover {
  background: #1565c0;
}
.tabela-funcionarios {
  background: var(--cor-branco);
  border-radius: 12px;
  padding: 24px 20px;
  margin: 20px 0 0 0;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
  overflow-x: auto;
}

/* Dica de expansão */
.dica-expansao {
  text-align: center;
  margin-bottom: 16px;
  color: var(--cor-sec1);
  font-family: var(--font-corpo);
  opacity: 0.8;
}

/* Header melhorado */
.header-funcionarios {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  gap: 20px;
}
.busca-adicionar {
  display: flex;
  gap: 16px;
  align-items: center;
}
.input-busca {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1.5px solid var(--cor-sec2);
  min-width: 220px;
  font-size: 15px;
  font-family: var(--font-corpo);
  background: #f8fafc;
  transition: border 0.2s;
}
.input-busca:focus {
  border: 2px solid var(--cor-destaque);
  outline: none;
}
.header h2 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
}
.btn-cadastrar {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  transition: background 0.2s;
}
.btn-cadastrar:hover {
  background: var(--cor-sec3);
}
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 16px;
  background: #fff;
  box-shadow: 0 1px 6px rgba(20,65,121,0.06);
  border-radius: 10px;
  overflow: hidden;
}
thead th {
  position: sticky;
  top: 0;
  background: var(--cor-branco);
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  font-size: 15px;
  padding: 12px 8px;
  border-bottom: 2px solid var(--cor-destaque);
  z-index: 2;
}
tbody tr {
  transition: background 0.15s;
}
tbody tr:hover {
  background: #f6f8fa;
}
td {
  padding: 10px 8px;
  border-bottom: 1.5px solid #f3e6c2;
  font-family: var(--font-corpo);
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

td:nth-child(1), td:nth-child(2) { max-width: 120px; } /* Nome, Sobrenome */
td:nth-child(3) { max-width: 130px; } /* Celular */
td:nth-child(4) { max-width: 180px; } /* E-mail */
td:nth-child(5), td:nth-child(6) { max-width: 140px; } /* Grupo E-mail, Setor */
td:nth-child(7) { max-width: 120px; } /* Cargo */
td:nth-child(8) { max-width: 250px; white-space: normal; } /* Sistemas - maior espaço */
td:nth-child(9) { max-width: 100px; white-space: normal; } /* Ações */

/* Estilo especial para célula de sistemas */
.sistemas-celula {
  font-size: 13px;
  line-height: 1.3;
}

.sistemas-celula.expandida {
  font-size: 14px;
  line-height: 1.4;
  padding: 12px 8px;
}

/* Células clicáveis */
td.clicavel {
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

td.clicavel:hover {
  background-color: #e3f2fd;
}

/* Células expandidas */
td.expandida {
  white-space: normal !important;
  word-break: break-word !important;
  overflow: visible !important;
  text-overflow: clip !important;
  max-width: none !important;
  background-color: #f0f7ff;
  border: 2px solid var(--cor-destaque);
  z-index: 10;
  position: relative;
}

/* Indicador visual de que a célula é clicável */
td.clicavel::after {
  content: '👆';
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}

td.clicavel:hover::after {
  opacity: 0.6;
}
tbody tr:last-child td {
  border-bottom: none;
}
.btn-editar {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  margin-right: 4px;
  cursor: pointer;
  font-size: 14px;
}
.btn-excluir {
  background: #d32f2f;
  color: var(--cor-branco);
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 14px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(20,65,121,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.form-modal {
  margin: 0 auto; /* Centraliza horizontalmente */
  display: flex;
  flex-direction: column;
  align-items: center; /* Centraliza conteúdo verticalmente */
  background: var(--cor-branco);
  border: 1px solid var(--cor-sec1);
  border-radius: 12px;
  padding: 32px 28px;
  max-width: 600px;
  width: 96%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 24px rgba(20,65,121,0.18);
  font-family: var(--font-corpo);
}
.form-modal h3 {
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
  margin-bottom: 24px;
  text-align: center;
}
.form-modal input {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid var(--cor-sec2);
  border-radius: 4px;
  font-size: 15px;
  font-family: var(--font-corpo);
}
.form-modal input:focus {
  outline: 2px solid var(--cor-destaque);
}
.modal-actions {
  display: flex;
  justify-content: space-between;
}
.form-modal button {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  border: none;
  border-radius: 4px;
  padding: 10px 18px;
  font-size: 15px;
  font-family: var(--font-titulo);
  cursor: pointer;
  margin-right: 8px;
  transition: background 0.2s;
}
.form-modal button:last-child {
  background: var(--cor-sec1);
  color: var(--cor-branco);
  margin-right: 0;
}
.form-modal button:hover {
  background: var(--cor-sec3);
}

/* Estilos para Select Múltiplo */
.select-group {
  margin-bottom: 20px;
}

.select-group label {
  font-weight: bold;
  margin-bottom: 8px;
  display: block;
  color: var(--cor-primaria);
  font-family: var(--font-titulo);
}

.multi-select-container {
  border: 1px solid var(--cor-sec2);
  border-radius: 6px;
  padding: 8px;
  background: #f8fafc;
  min-height: 80px;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
  min-height: 32px;
  max-height: 80px;
  overflow-y: auto;
  padding-right: 8px;
}

.selected-chip {
  background: var(--cor-destaque);
  color: var(--cor-primaria);
  padding: 4px 28px 4px 8px; /* padding extra à direita para o x */
  border-radius: 16px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-corpo);
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  position: relative;
  word-break: break-all;
  cursor: pointer;
}



/* Tooltip para chips grandes */
.selected-chip:hover::after {
  content: attr(title);
  position: absolute;
  left: 0;
  top: 100%;
  background: #fffbe6;
  color: #333;
  border: 1px solid #e0c97f;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  white-space: normal;
  box-shadow: 0 2px 8px rgba(20,65,121,0.08);
  z-index: 10;
  min-width: 120px;
  max-width: 350px;
  pointer-events: none;
}
.multi-select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--cor-sec2);
  border-radius: 4px;
  background: white;
  font-family: var(--font-corpo);
  font-size: 14px;
  color: var(--cor-primaria);
}

.multi-select:focus {
  outline: 2px solid var(--cor-destaque);
}

.multi-select option {
  padding: 8px;
}

.selects-2x2 {
  display: flex;
  gap: 24px;
  margin-bottom: 0;
}
.selects-2x2 .modal-col {
  min-width: 180px;
  flex: 1 1 0;
}
@media (max-width: 768px) {
  .selects-2x2 {
    flex-direction: column;
    gap: 10px;
  }
  .selects-2x2 .modal-col {
    min-width: 100%;
  }
}
.form-modal {
  background: var(--cor-branco);
  border: 1px solid var(--cor-sec1);
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(20,65,121,0.2);
  font-family: var(--font-corpo);
}

.modal-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}
.modal-col {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.modal-divider {
  border: none;
  border-top: 1.5px solid var(--cor-sec2);
  margin: 18px 0;
}

@media (max-width: 768px) {
  .form-modal {
    max-width: 99%;
    padding: 16px;
  }
  .modal-row {
    flex-direction: column;
    gap: 10px;
  }
  .modal-col {
    min-width: 100%;
    gap: 8px;
  }
  
  .selected-items {
    background: var(--cor-destaque);
    color: var(--cor-primaria);
    padding: 4px 8px;
    border-radius: 16px;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--font-corpo);
    max-width: 220px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    position: relative;
    word-break: break-all;
    cursor: pointer;
    transition: background 0.2s;
  }
  .selected-chip:hover {
    background: #ffe082;
  }
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}
.form-grid > div {
  width: 100%;
}
@media (max-width: 700px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>

