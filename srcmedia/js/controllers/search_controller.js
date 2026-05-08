import { Controller } from '@hotwired/stimulus'
import { fromEvent, merge } from 'rxjs'
import { map, debounceTime, distinctUntilChanged } from 'rxjs/operators'
import ImageLazyLoader from '../modules/LazyLoad'

/**
 * Stimulus controller for the archive search page.
 *
 * Replaces search.js. No jQuery or Fomantic UI JS dependencies.
 *
 * Key data-search-target attributes (see search_form.html):
 *   form, results, count, paginationTop,
 *   canvas, minDate, maxDate, minDateInput, maxDateInput,
 *   sortSelect, relevanceOption,
 *   advancedButton, workscount,
 *   collectionInput, textInput, validation,
 *   advancedSection, advancedColumn
 */
export default class SearchController extends Controller {
    static targets = [
        'form', 'results', 'count', 'paginationTop',
        'canvas', 'minDate', 'maxDate',
        'minDateInput', 'maxDateInput',
        'sortSelect', 'relevanceOption',
        'advancedButton', 'workscount',
        'collectionInput', 'textInput', 'validation',
        'advancedSection', 'advancedColumn',
    ]

    connect() {
        this._initHistogram()
        this._initReactiveForm()
        this._initCollectionInputs()
        this._initAdvancedSearch()
        this._initLazyLoad()
        this._validate()
    }

    disconnect() {
        this._subscription?.unsubscribe()
    }

    // --- Reactive form ---

    _initReactiveForm() {
        const inputs = [
            ...this.formTarget.querySelectorAll('input'),
            ...this.formTarget.querySelectorAll('select'),
        ]
        const streams = inputs.map(el => {
            const event = (el.type === 'checkbox' || el.type === 'radio') ? 'change' : 'input'
            let obs = fromEvent(el, event).pipe(map(() => null))
            if (el.type === 'text' || el.type === 'number') {
                obs = obs.pipe(debounceTime(750), distinctUntilChanged())
            }
            return obs
        })
        this._subscription = merge(...streams).subscribe(() => this._submitForm())
    }

    _submitForm() {
        if (!this._validate()) return

        const formData = new FormData(this.formTarget)
        const params = new URLSearchParams()
        for (const [key, value] of formData.entries()) {
            if (value !== '') params.append(key, value)
        }
        // signal that all collections are deselected
        if (![...params.keys()].includes('collections')) {
            params.append('collections', '')
        }

        const qs = params.toString()
        window.history.pushState(null, 'PPA Archive Search', `?${qs}`)
        this.workscountTarget.classList.add('loading')

        const searchUrl = this.formTarget.action || window.location.pathname
        fetch(`${searchUrl}?${qs}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(res => res.text())
            .then(html => {
                const doc = new DOMParser().parseFromString(html, 'text/html')
                const newPagination = doc.querySelector('.page-controls')
                if (newPagination && this.hasPaginationTopTarget) {
                    this.paginationTopTarget.innerHTML = newPagination.innerHTML
                }
                const facetsEl = doc.querySelector('script#facets')
                if (facetsEl) {
                    this._updateHistogram(JSON.parse(facetsEl.textContent))
                }
                const countEl = doc.querySelector('pre.count')
                if (countEl && this.hasCountTarget) {
                    this.countTarget.innerHTML = countEl.innerHTML
                }
                this.resultsTarget.innerHTML = html
                document.dispatchEvent(new Event('ZoteroItemUpdated', { bubbles: true, cancelable: true }))
                this.workscountTarget.classList.remove('loading')
                new ImageLazyLoader(Array.from(this.resultsTarget.querySelectorAll('img[data-src]')))
            })
        this._advancedSearchIndicator()
    }

    // --- Validation ---

    _validate() {
        const min = this.hasMinDateInputTarget ? this.minDateInputTarget : null
        const max = this.hasMaxDateInputTarget ? this.maxDateInputTarget : null
        const validationEl = this.hasValidationTarget ? this.validationTarget : null

        const ok = (!min || min.checkValidity())
            && (!max || max.checkValidity())
            && !(min?.value && max?.value && min.value > max.value)

        if (validationEl) validationEl.style.visibility = ok ? 'hidden' : 'visible'
        return ok
    }

    // --- Date range ---

    clearDates() {
        if (this.hasMinDateInputTarget) {
            this.minDateInputTarget.value = ''
            this.minDateInputTarget.dispatchEvent(new Event('input'))
        }
        if (this.hasMaxDateInputTarget) {
            this.maxDateInputTarget.value = ''
            this.maxDateInputTarget.dispatchEvent(new Event('input'))
        }
    }

    // --- Histogram ---

    _initHistogram() {
        if (!this.hasCanvasTarget) return
        const facetsEl = this.hasResultsTarget
            ? this.resultsTarget.querySelector('script#facets')
            : this.element.querySelector('script#facets')
        if (facetsEl) {
            this._updateHistogram(JSON.parse(facetsEl.textContent))
        }
    }

    _updateHistogram({ start, end, counts } = {}) {
        if (!counts || !this.hasCanvasTarget) return
        if (this.hasMinDateTarget) this.minDateTarget.textContent = start
        if (this.hasMaxDateTarget) this.maxDateTarget.textContent = end
        this._renderHistogram(counts)
    }

    _renderHistogram(counts) {
        const canvas = this.canvasTarget
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = '#efefef'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        const values = Object.values(counts)
        const yMax = Math.max(...values)
        const bins = values.length
        ctx.fillStyle = '#ccc'
        values.forEach((yVal, i) => {
            const x = Math.floor(i * (canvas.width / bins))
            const y = canvas.height - Math.floor((yVal / yMax) * canvas.height)
            const dx = Math.floor(canvas.width / bins)
            const dy = Math.floor((yVal / yMax) * canvas.height)
            ctx.fillRect(x, y, dx, dy)
        })
    }

    // --- Sort select ---

    onSortChange() {
        // the <select> change event is already wired into _initReactiveForm via merge()
        // this action handler exists for explicit data-action wiring if needed
        this._updateRelevanceSort()
    }

    _updateRelevanceSort() {
        if (!this.hasSortSelectTarget) return
        const textInputs = this.textInputTargets.flatMap(el =>
            el.tagName === 'INPUT' ? [el] : Array.from(el.querySelectorAll('input[type=text]'))
        )
        const hasText = textInputs.some(el => el.value.trim() !== '')
        if (this.hasRelevanceOptionTarget) {
            this.relevanceOptionTarget.disabled = !hasText
        }
        if (!hasText && this.sortSelectTarget.value === 'relevance') {
            this.sortSelectTarget.value = 'title_asc'
            this.sortSelectTarget.dispatchEvent(new Event('change'))
        }
    }

    // Called when a text input changes (wired via data-action in template)
    textInputChanged() {
        this._updateRelevanceSort()
    }

    // --- Collection inputs ---

    _initCollectionInputs() {
        this.collectionInputTargets.forEach(input => {
            const label = input.closest('label')
            if (!label) return
            input.addEventListener('focus', () => label.classList.add('focus'))
            input.addEventListener('blur', () => label.classList.remove('focus'))
            input.addEventListener('change', () => label.classList.toggle('active', input.checked))
            input.addEventListener('keypress', e => { if (e.key === 'Enter') input.click() })
            if (input.disabled) label.classList.add('disabled')
        })
    }

    // --- Advanced search (CSS transition-based, no jQuery) ---

    _initAdvancedSearch() {
        this.formTarget.addEventListener('keydown', e => {
            if (e.key === 'Enter') e.preventDefault()
        })
        if (sessionStorage.getItem('ppa-adv-search') === 'open') {
            this._openAdvanced(false)
        }
        this._advancedSearchIndicator()
    }

    toggleAdvancedSearch() {
        const sections = this.advancedSectionTargets
        const isHidden = sections.length === 0 || sections[0].style.display === 'none' || sections[0].style.display === ''
        isHidden ? this._openAdvanced(true) : this._closeAdvanced()
    }

    _openAdvanced(animate = true) {
        this.advancedButtonTarget?.closest('.show-advanced')?.classList.add('active')
        this.advancedSectionTargets.forEach(el => { el.style.display = 'flex' })
        this.advancedColumnTargets.forEach(el => { el.style.display = 'inline-block' })
        sessionStorage.setItem('ppa-adv-search', 'open')
    }

    _closeAdvanced() {
        this.advancedButtonTarget?.closest('.show-advanced')?.classList.remove('active')
        this.advancedSectionTargets.forEach(el => { el.style.display = 'none' })
        sessionStorage.setItem('ppa-adv-search', 'closed')
    }

    _advancedSearchIndicator() {
        const hasActive = this.advancedSectionTargets
            .flatMap(el => Array.from(el.querySelectorAll('input')))
            .some(el => el.value !== '')
        const indicator = this.element.querySelector('.show-advanced .search-active')
        if (indicator) indicator.style.display = hasActive ? '' : 'none'
    }

    // --- Lazy load ---

    _initLazyLoad() {
        new ImageLazyLoader(Array.from(this.element.querySelectorAll('img[data-src]')))
    }
}
