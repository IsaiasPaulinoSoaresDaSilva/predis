import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import App from '../../App.vue'
import Sidebar from '../Sidebar.vue'
import Dashboard from '../Dashboard.vue'

describe('App.vue', () => {
  it('starts with "Centro" as the default selected region', () => {
    const wrapper = shallowMount(App)
    const dashboard = wrapper.findComponent(Dashboard)
    expect(dashboard.props('selectedRegion')).toBe('centro')
    expect(dashboard.props('selectedRegionName')).toBe('Centro')
  })

  it('updates the selected region when Sidebar emits region-selected', async () => {
    const wrapper = shallowMount(App)
    const sidebar = wrapper.findComponent(Sidebar)
    await sidebar.vm.$emit('region-selected', 'leste')

    const dashboard = wrapper.findComponent(Dashboard)
    expect(dashboard.props('selectedRegion')).toBe('leste')
    expect(dashboard.props('selectedRegionName')).toBe('Leste')
  })
})
