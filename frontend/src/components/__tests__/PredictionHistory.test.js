import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import axios from 'axios'
import PredictionHistory from '../PredictionHistory.vue'

vi.mock('axios')

describe('PredictionHistory.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders one row per persisted prediction', async () => {
    axios.get.mockResolvedValue({
      data: [
        { id: 2, created_at: '2026-08-18T12:00:00', risk_level: 1, risk_probability: 0.42 },
        { id: 1, created_at: '2026-08-17T09:00:00', risk_level: 0, risk_probability: 0.05 },
      ],
    })
    const wrapper = mount(PredictionHistory, { props: { region: 'centro' } })
    await flushPromises()

    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/predictions'), expect.objectContaining({
      params: { region: 'centro', limit: 8 },
    }))
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
    expect(wrapper.text()).toContain('42.0%')
  })

  it('shows an empty-state message when there is no history yet', async () => {
    axios.get.mockResolvedValue({ data: [] })
    const wrapper = mount(PredictionHistory, { props: { region: 'centro' } })
    await flushPromises()

    expect(wrapper.find('.prediction-history__empty').exists()).toBe(true)
    expect(wrapper.find('table').exists()).toBe(false)
  })

  it('refetches when the region prop changes', async () => {
    axios.get.mockResolvedValue({ data: [] })
    const wrapper = mount(PredictionHistory, { props: { region: 'centro' } })
    await flushPromises()
    expect(axios.get).toHaveBeenCalledTimes(1)

    await wrapper.setProps({ region: 'leste' })
    await flushPromises()
    expect(axios.get).toHaveBeenCalledTimes(2)
    expect(axios.get).toHaveBeenLastCalledWith(expect.stringContaining('/predictions'), expect.objectContaining({
      params: { region: 'leste', limit: 8 },
    }))
  })
})
