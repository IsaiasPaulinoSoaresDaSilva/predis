import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Sidebar from '../Sidebar.vue'

describe('Sidebar.vue', () => {
  it('renders the 6 São José dos Campos regions', () => {
    const wrapper = mount(Sidebar, { props: { selectedRegion: 'centro' } })
    const items = wrapper.findAll('.region-item')
    expect(items).toHaveLength(6)
    expect(items.map(i => i.text())).toEqual([
      'Centro', 'Norte', 'Sul', 'Leste', 'Oeste', 'Sudeste',
    ])
  })

  it('marks the selected region as active', () => {
    const wrapper = mount(Sidebar, { props: { selectedRegion: 'leste' } })
    const active = wrapper.find('.region-item.active')
    expect(active.text()).toBe('Leste')
  })

  it('emits region-selected with the region id when a region is clicked', async () => {
    const wrapper = mount(Sidebar, { props: { selectedRegion: 'centro' } })
    const items = wrapper.findAll('.region-item')
    await items[2].trigger('click') // 'Sul'
    expect(wrapper.emitted('region-selected')).toBeTruthy()
    expect(wrapper.emitted('region-selected')[0]).toEqual(['sul'])
  })
})
