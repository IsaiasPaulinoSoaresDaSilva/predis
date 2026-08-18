import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import axios from 'axios'
import RegionComparison from '../RegionComparison.vue'

vi.mock('axios')

const REGIONS = [
  { id: 'centro', name: 'Centro' },
  { id: 'leste', name: 'Leste' },
]

describe('RegionComparison.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches a prediction for every region on mount and renders each reading', async () => {
    axios.post.mockImplementation((_url, body) =>
      Promise.resolve({
        data: { risk_level: body.region === 'leste' ? 2 : 0, risk_probability: body.region === 'leste' ? 0.7 : 0.1 },
      })
    )
    const wrapper = mount(RegionComparison, { props: { regions: REGIONS, selectedRegion: 'centro' } })
    await flushPromises()

    expect(axios.post).toHaveBeenCalledTimes(2)
    const items = wrapper.findAll('.region-comparison__item')
    expect(items).toHaveLength(2)
    expect(items[1].text()).toContain('70%')
  })

  it('emits region-selected when a region card is clicked', async () => {
    axios.post.mockResolvedValue({ data: { risk_level: 0, risk_probability: 0 } })
    const wrapper = mount(RegionComparison, { props: { regions: REGIONS, selectedRegion: 'centro' } })
    await flushPromises()

    await wrapper.findAll('.region-comparison__item')[1].trigger('click')
    expect(wrapper.emitted('region-selected')[0]).toEqual(['leste'])
  })

  it('keeps other readings when one region request fails', async () => {
    axios.post.mockImplementation((_url, body) =>
      body.region === 'leste'
        ? Promise.reject(new Error('network down'))
        : Promise.resolve({ data: { risk_level: 0, risk_probability: 0.2 } })
    )
    const wrapper = mount(RegionComparison, { props: { regions: REGIONS, selectedRegion: 'centro' } })
    await flushPromises()

    expect(wrapper.findAll('.region-comparison__item')[0].text()).toContain('20%')
    expect(wrapper.findAll('.region-comparison__item')[1].text()).toContain('…')
  })
})
