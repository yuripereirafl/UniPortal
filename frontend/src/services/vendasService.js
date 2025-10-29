/**
 * Serviço para gerenciar chamadas à API de Vendas
 * Integra com a tabela basecampanhas para dados de vendas reais
 */
import axios from 'axios'

const vendasService = {
  /**
   * Busca as vendas de um colaborador específico
   * @param {string} codUsuario - Código do usuário (ID Eyal)
   * @param {string|null} mesRef - Mês de referência no formato YYYY-MM (opcional)
   * @returns {Promise<Object>} Dados de vendas do colaborador
   */
  async getVendasColaborador(codUsuario, mesRef = null) {
    try {
      console.log(`[vendasService] Buscando vendas para colaborador: ${codUsuario}, mês: ${mesRef || 'atual'}`)

      const params = {}
      if (mesRef) {
        params.mes_ref = mesRef
      }

      const response = await axios.get(`/vendas/colaborador/${codUsuario}`, { params })

      if (!response.data) {
        console.warn('[vendasService] Resposta vazia da API')
        return {
          success: false,
          resumo: null,
          detalhes: [],
          message: 'Dados não disponíveis'
        }
      }

      console.log(`[vendasService] Vendas carregadas:`, {
        success: response.data.success,
        totalVendas: response.data.resumo?.total_vendas || 0,
        valorTotal: response.data.resumo?.valor_total || 0,
        detalhesCount: response.data.detalhes?.length || 0
      })

      return response.data

    } catch (error) {
      console.error('[vendasService] Erro ao buscar vendas do colaborador:', {
        codUsuario,
        mesRef,
        error: error.message,
        response: error.response?.data
      })

      // Retorna estrutura vazia em caso de erro
      return {
        success: false,
        resumo: null,
        detalhes: [],
        message: error.response?.data?.detail || error.message || 'Erro ao carregar vendas'
      }
    }
  },

  /**
   * Busca vendas por grupo de exames
   * @param {string} grupo - Nome do grupo (ODONTO, CHECK UP, BabyClick, DR CENTRAL, ORÇAMENTOS)
   * @param {string|null} mesRef - Mês de referência no formato YYYY-MM (opcional)
   * @returns {Promise<Object>} Dados de vendas do grupo
   */
  async getVendasPorGrupo(grupo, mesRef = null) {
    try {
      console.log(`[vendasService] Buscando vendas do grupo: ${grupo}, mês: ${mesRef || 'atual'}`)

      const params = {}
      if (mesRef) {
        params.mes_ref = mesRef
      }

      const response = await axios.get(`/vendas/grupo/${encodeURIComponent(grupo)}`, { params })

      if (!response.data) {
        console.warn('[vendasService] Resposta vazia da API')
        return {
          success: false,
          resumo: null,
          detalhes: [],
          message: 'Dados não disponíveis'
        }
      }

      console.log(`[vendasService] Vendas do grupo carregadas:`, {
        grupo,
        success: response.data.success,
        totalVendas: response.data.resumo?.total_vendas || 0,
        valorTotal: response.data.resumo?.valor_total || 0
      })

      return response.data

    } catch (error) {
      console.error('[vendasService] Erro ao buscar vendas do grupo:', {
        grupo,
        mesRef,
        error: error.message,
        response: error.response?.data
      })

      return {
        success: false,
        resumo: null,
        detalhes: [],
        message: error.response?.data?.detail || error.message || 'Erro ao carregar vendas do grupo'
      }
    }
  },

  /**
   * Busca vendas do mês atual
   * @param {string} codUsuario - Código do colaborador
   * @returns {Promise} Dados de vendas do mês atual
   */
  async getVendasMesAtual(codUsuario) {
    const hoje = new Date()
    const mesRef = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`
    return this.getVendasColaborador(codUsuario, mesRef)
  },

  /**
   * Formata os dados de vendas para exibição no componente
   * @param {Object} dadosAPI - Dados retornados pela API
   * @returns {Object} Dados formatados para o componente
   */
  formatarDadosVendas(dadosAPI) {
    if (!dadosAPI || !dadosAPI.success || !dadosAPI.resumo) {
      return {
        odonto: 0,
        check_up: 0,
        baby_click: 0,
        dr_central: 0,
        orcamentos: 0,
        total: 0,
        valorTotal: 0,
        detalhes: []
      }
    }

    const resumo = dadosAPI.resumo

    return {
      // Contadores individuais
      odonto: resumo.odonto || 0,
      check_up: resumo.check_up || 0,
      baby_click: resumo.baby_click || 0,
      dr_central: resumo.dr_central || 0,
      orcamentos: resumo.orcamentos || 0,

      // Totais
      total: resumo.total_vendas || 0,
      valorTotal: resumo.valor_total || 0,

      // Vendas por grupo (para gráficos)
      vendasPorGrupo: resumo.vendas_por_grupo || [],

      // Detalhes completos (para tabelas)
      detalhes: dadosAPI.detalhes || []
    }
  },

  /**
   * Formata valor monetário para exibição
   * @param {number} valor - Valor a ser formatado
   * @returns {string} Valor formatado (ex: "R$ 1.234,56")
   */
  formatarValor(valor) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor || 0)
  },

  /**
   * Formata data para exibição
   * @param {string|Date} data - Data a ser formatada
   * @returns {string} Data formatada (ex: "25/03/2024")
   */
  formatarData(data) {
    if (!data) return ''
    const d = new Date(data)
    return d.toLocaleDateString('pt-BR')
  }
}

export default vendasService
