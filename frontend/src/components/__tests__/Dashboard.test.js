import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import axios from 'axios'
import Dashboard from '../Dashboard.vue'

// Chart.js precisa de um <canvas> com contexto 2D real, que o happy-dom não
// fornece — mockado para um no-op, já que o gráfico em si não é o alvo
// destes testes (a lógica de risco/estados é).
vi.mock('chart.js/auto', () => ({
  default: class FakeChart {
    destroy() {}
  },
}))

vi.mock('axios')

const HISTORICAL_RESPONSE = [
  { data: '2024-01-01', precipitacao_mm: 5, nivel_rio_m: 2.1 },
  { data: '2024-01-02', precipitacao_mm: 8, nivel_rio_m: 2.2 },
]

function mountDashboard(props = {}) {
  return mount(Dashboard, {
    props: { selectedRegion: 'centro', selectedRegionName: 'Centro', ...props },
    global: { stubs: { Map: true } },
  })
}

describe('Dashboard.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    axios.get.mockResolvedValue({ data: HISTORICAL_RESPONSE })
  })

  it('shows the risk probability returned by the API', async () => {
    axios.post.mockResolvedValue({
      data: { risk_level: 2, risk_probability: 0.83, feature_importance: { subida_rio_14d: 0.4 }, message: null },
    })
    const wrapper = mountDashboard()
    await flushPromises()

    expect(wrapper.find('.risk-level-text').text()).toBe('83%')
  })

  it('shows a loading indicator while the prediction request is pending, then hides it', async () => {
    let resolvePost
    axios.post.mockReturnValue(new Promise(resolve => { resolvePost = resolve }))

    const wrapper = mountDashboard()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.loading-message').exists()).toBe(true)

    resolvePost({ data: { risk_level: 0, risk_probability: 0, feature_importance: {}, message: null } })
    await flushPromises()
    expect(wrapper.find('.loading-message').exists()).toBe(false)
  })

  it('shows a distinct connection-error message when the API call fails', async () => {
    axios.post.mockRejectedValue(new Error('network down'))
    const wrapper = mountDashboard()
    await flushPromises()

    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.warning-message').exists()).toBe(false)
  })

  it('shows a backend-provided warning (not styled as a connection error) separately', async () => {
    axios.post.mockResolvedValue({
      data: { risk_level: 0, risk_probability: 0, feature_importance: {}, message: 'Dados insuficientes para a região.' },
    })
    const wrapper = mountDashboard()
    await flushPromises()

    expect(wrapper.find('.warning-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').exists()).toBe(false)
  })

  it('renders the most important features first, filtering out negligible ones', async () => {
    axios.post.mockResolvedValue({
      data: {
        risk_level: 1,
        risk_probability: 0.4,
        feature_importance: {
          subida_rio_14d: 0.38,
          precipitacao_acumulada_3d: 0.27,
          previsao_chuva_d3: 0.001, // desprezível, deve ser filtrada
        },
        message: null,
      },
    })
    const wrapper = mountDashboard()
    await flushPromises()

    const features = wrapper.findAll('.feature-importance .feature span:first-child').map(f => f.text())
    expect(features[0]).toContain('Subida do rio')
    expect(features).not.toContain('Previsão de chuva (d+3)')
  })
})
