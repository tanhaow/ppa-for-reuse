import { Controller } from '@hotwired/stimulus'
import Parallax from 'parallax-js'

/**
 * Stimulus controller for the homepage parallax effect.
 *
 * Replaces home.js.
 *
 * Usage:
 *   <div id="scene" data-controller="home">...</div>
 */
export default class HomeController extends Controller {
    connect() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
        if (!prefersReducedMotion) {
            this._parallax = new Parallax(this.element)
        }
    }

    disconnect() {
        this._parallax?.destroy()
    }
}
