import { Controller } from '@hotwired/stimulus'

/**
 * Stimulus controller that adds a clear (×) button to a text input.
 *
 * Usage:
 *   <div data-controller="clearable">
 *     <input type="text" data-clearable-target="input" data-action="input->clearable#toggle">
 *   </div>
 *
 * Or, applied directly on the input's wrapper via connect():
 *   <input type="text" data-controller="clearable">
 */
export default class ClearableController extends Controller {
    static targets = ['input']

    connect() {
        // Support both: controller on a wrapper with an input target,
        // or controller directly on the input element itself.
        this._input = this.hasInputTarget ? this.inputTarget : this.element
        this._button = this._createButton()
        this._input.insertAdjacentElement('afterend', this._button)
        this._onInput = this._toggle.bind(this)
        this._input.addEventListener('input', this._onInput)
        this._toggle()
    }

    disconnect() {
        this._input.removeEventListener('input', this._onInput)
        this._button.remove()
    }

    clear() {
        this._input.value = ''
        this._input.dispatchEvent(new Event('input', { bubbles: true }))
        this._toggle()
    }

    _toggle() {
        this._button.style.display = this._input.value === '' ? 'none' : ''
    }

    _createButton() {
        const btn = document.createElement('i')
        btn.className = 'clear times icon'
        btn.style.display = 'none'
        btn.setAttribute('role', 'button')
        btn.setAttribute('aria-label', 'Clear')
        btn.addEventListener('click', this.clear.bind(this))
        return btn
    }
}
