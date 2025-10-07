/**
 * Serviço para consumir a API de Painel de Resultados
 * Usa a tabela painelresultadosdiarios com dados pré-calculados
 */

import { API_BASE_URL } from '@/api.js';

/**
 * Busca dados de realizado do colaborador usando a nova tabela otimizada
 * @param {string|number} identificador - ID Eyal ou CPF do colaborador
 * @param {string} mesRef - Mês de referência (opcional, formato YYYY-MM-DD)
 * @returns {Promise<Object>} Dados do colaborador com realizado calculado
 */
export async function getRealizadoPainel(identificador, mesRef = null) {
    try {
        let url = `${API_BASE_URL}/realizado/painel/${identificador}`;

        if (mesRef) {
            url += `?mes_ref=${mesRef}`;
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };

    } catch (error) {
        console.error('Erro ao buscar dados do painel:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Busca histórico de realizado do colaborador
 * @param {string|number} identificador - ID Eyal ou CPF
 * @param {number} limite - Quantidade de meses (padrão: 12)
 * @returns {Promise<Object>} Histórico de realizado
 */
export async function getHistoricoRealizado(identificador, limite = 12) {
    try {
        const url = `${API_BASE_URL}/realizado/painel/historico/${identificador}?limite=${limite}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };

    } catch (error) {
        console.error('Erro ao buscar histórico:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Formata os dados do painel para exibição no componente
 * @param {Object} dadosPainel - Dados retornados pela API
 * @returns {Object} Dados formatados para o componente
 */
export function formatarDadosPainel(dadosPainel) {
    if (!dadosPainel || !dadosPainel.colaborador) {
        return null;
    }

    const { colaborador, realizado, metadata } = dadosPainel;

    return {
        // Dados do colaborador
        id: colaborador.id_eyal,
        nome: colaborador.nome,
        cpf: colaborador.cpf,
        cargo: colaborador.cargo,
        nivel: colaborador.nivel || 'N/A',
        unidade: colaborador.unidade,
        liderDireto: colaborador.lider_direto || 'Sem líder',

        // Dados de meta e realizado
        metaFinal: colaborador.meta_final || 0,
        realizadoIndividual: realizado.realizado_individual || 0,
        realizadoFinal: realizado.realizado_final || 0,
        percentualAtingido: realizado.percentual_atingido || 0,

        // Metadata
        mesReferencia: realizado.mes_referencia,
        dataCarga: realizado.data_carga,
        fonte: metadata.fonte,
        tipoCalculo: metadata.tipo_calculo,

        // Campos calculados
        faltaParaMeta: Math.max(0, (colaborador.meta_final || 0) - (realizado.realizado_final || 0)),
        statusMeta: realizado.percentual_atingido >= 100 ? 'atingida' :
            realizado.percentual_atingido >= 80 ? 'proxima' : 'distante'
    };
}

export default {
    getRealizadoPainel,
    getHistoricoRealizado,
    formatarDadosPainel
};
