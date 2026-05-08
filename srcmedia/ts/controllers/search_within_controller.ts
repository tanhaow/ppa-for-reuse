import { Controller } from '@hotwired/stimulus'
import { fromEvent } from 'rxjs'
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators'
import { ImageLazyLoader } from '../../js/modules/LazyLoad'
import clearable from '../../js/clearable'
import { ajax } from '../../js/modules/Utilities'

/**
 * Stimulus controller for the "search within a work" page.
 *
 * Replaces searchWithin.ts (PageSearchForm + RxTextInput + RxOutput).
 *
 * Expected HTML:
 *   <div data-controller="search-within">
 *     <form id="search-within" data-search-within-target="form" ...>
 *       <input name="query" data-search-within-target="queryInput"
 *              data-action="input->search-within#onQueryInput">
 *     </form>
 *     <output form="search-within" data-search-within-target="output"></output>
 *   </div>
 */
export default class SearchWithinController extends Controller {
    static targets = ['form', 'queryInput', 'output']

    // Stimulus-generated target properties (declared for TypeScript)
    declare readonly hasFormTarget: boolean
    declare readonly formTarget: HTMLFormElement
    declare readonly hasQueryInputTarget: boolean
    declare readonly queryInputTarget: HTMLInputElement
    declare readonly hasOutputTarget: boolean
    declare readonly outputTarget: HTMLElement

    private _subscription?: { unsubscribe(): void }

    connect() {
        this._initClearable()
        this._initPopups()
        this._initLazyLoad()
        this._initDebounce()
    }

    disconnect() {
        this._subscription?.unsubscribe()
    }

    // queryInputTarget may be the <input> itself or a wrapper <div>
    private get _queryInput(): HTMLInputElement | null {
        if (!this.hasQueryInputTarget) return null
        const el = this.queryInputTarget as HTMLElement
        return el.tagName === 'INPUT'
            ? el as HTMLInputElement
            : el.querySelector('input') as HTMLInputElement | null
    }

    _initDebounce() {
        const input = this._queryInput
        if (!input) return
        this._subscription = fromEvent(input, 'input').pipe(
            map(() => input.value),
            debounceTime(750),
            distinctUntilChanged(),
        ).subscribe(() => this._submit())
    }

    onQueryInput() {
        // handled by RxJS debounce in _initDebounce
    }

    async _submit() {
        if (!this.hasFormTarget) return
        const form = this.formTarget
        const target = form.getAttribute('target') || window.location.pathname
        const params = new URLSearchParams(Array.from(new FormData(form) as Iterable<[string, string]>))
        const url = `${target}?${params.toString()}`

        const res = await fetch(url, ajax)
        const html = await res.text()

        if (this.hasOutputTarget) {
            this.outputTarget.innerHTML = html
            const images = Array.from(this.outputTarget.querySelectorAll('img[data-src]')) as Element[]
            new ImageLazyLoader(images)
        }
        window.history.pushState(null, document.title, `?${params.toString()}`)
    }

    _initClearable() {
        const input = this._queryInput
        if (input) clearable(input)
    }

    _initPopups() {
        // Popups are handled via native title attributes; no jQuery needed
    }

    _initLazyLoad() {
        new ImageLazyLoader(Array.from(this.element.querySelectorAll('img[data-src]')))
    }
}
