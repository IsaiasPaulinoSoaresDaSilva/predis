import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StaffGauge from '../StaffGauge.vue'

describe('StaffGauge.vue', () => {
  it('exposes the current reading in an accessible label', () => {
    const wrapper = mount(StaffGauge, { props: { probability: 0.83, level: 2 } })
    expect(wrapper.attributes('aria-label')).toContain('83%')
    expect(wrapper.attributes('aria-label')).toContain('alto')
  })

  it('applies the size modifier class', () => {
    const wrapper = mount(StaffGauge, { props: { probability: 0.1, level: 0, size: 'sm' } })
    expect(wrapper.classes()).toContain('staff-gauge--sm')
  })
})
