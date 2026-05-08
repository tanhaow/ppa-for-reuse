import { Controller } from '@hotwired/stimulus'

/**
 * Stimulus controller for lazy-loading images.
 *
 * Replaces LazyLoad.js / ImageLazyLoader.
 *
 * Usage: add data-controller="lazy-load" to any container that holds
 * <img data-src="..."> elements. The controller will observe each image
 * and swap in the real src/srcset when it scrolls into view.
 *
 * Can also be placed directly on an <img> element.
 */
export default class LazyLoadController extends Controller {
    connect() {
        const images = this.element.tagName === 'IMG'
            ? [this.element]
            : Array.from(this.element.querySelectorAll('img[data-src]'))

        if ('IntersectionObserver' in window) {
            this._observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this._loadImage(entry.target)
                        observer.unobserve(entry.target)
                    }
                })
            })
            images.forEach(img => this._observer.observe(img))
        } else {
            images.forEach(img => this._loadImage(img))
        }
    }

    disconnect() {
        this._observer?.disconnect()
    }

    _loadImage(img) {
        // srcset must be set first — Safari otherwise loads both src and srcset
        if (img.hasAttribute('data-srcset')) {
            img.setAttribute('srcset', img.getAttribute('data-srcset'))
        }
        if (img.hasAttribute('data-src')) {
            img.setAttribute('src', img.getAttribute('data-src'))
        }
        img.onload = () => {
            img.removeAttribute('data-src')
            img.removeAttribute('data-srcset')
            // HathiTrust Image API throttling returns a 468px-wide placeholder image
            if (img.naturalWidth === 468) {
                img.removeAttribute('srcset')
            }
        }
    }
}
