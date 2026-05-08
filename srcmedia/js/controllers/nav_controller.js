import { Controller } from '@hotwired/stimulus'

/**
 * Stimulus controller for the main site navigation.
 *
 * Replaces NavMenu.js (about dropdown keyboard nav) and pitbar.js (hide-on-scroll).
 *
 * Expected HTML structure (see templates/snippets/nav.html):
 *
 *   <div data-controller="nav"
 *        data-nav-scroll-container-selector-value=".pusher">
 *     <nav id="main-nav" data-nav-target="mainNav">...</nav>
 *     <nav id="mobile-nav" data-nav-target="mobileNav">
 *       <a data-action="click->nav#toggleMobile">...</a>
 *     </nav>
 *     <div class="about" data-nav-target="aboutMenu"
 *          data-action="focusin->nav#aboutFocusIn focusout->nav#aboutFocusOut keydown->nav#aboutKeydown">
 *       <div class="text" data-nav-target="aboutText" tabindex="0">About</div>
 *       ...
 *     </div>
 *   </div>
 */
export default class NavController extends Controller {
    static targets = ['mainNav', 'mobileNav', 'aboutMenu', 'aboutText']
    static values = { scrollContainerSelector: { type: String, default: '.pusher' } }

    connect() {
        this._lastScroll = 0
        this._scrollContainer = document.querySelector(this.scrollContainerSelectorValue)
        if (this._scrollContainer) {
            this._onScroll = this._checkScroll.bind(this)
            this._scrollContainer.addEventListener('scroll', this._onScroll)
        }
    }

    disconnect() {
        if (this._scrollContainer && this._onScroll) {
            this._scrollContainer.removeEventListener('scroll', this._onScroll)
        }
    }

    // --- Mobile sidebar ---

    toggleMobile() {
        const nav = this.mobileNavTarget
        const isVisible = nav.classList.contains('visible')
        if (isVisible) {
            this._hideMobile()
        } else {
            this._showMobile()
        }
    }

    _showMobile() {
        this.mobileNavTarget.classList.add('visible')
        this.element.querySelector('.close.icon')?.classList.remove('hidden')
        this.element.querySelector('.menu.icon')?.classList.add('hidden')
        this.element.querySelector('.header.brand .item')?.classList.add('hidden')
    }

    _hideMobile() {
        this.mobileNavTarget.classList.remove('visible')
        this.element.querySelector('.close.icon')?.classList.add('hidden')
        this.element.querySelector('.menu.icon')?.classList.remove('hidden')
        this.element.querySelector('.header.brand .item')?.classList.remove('hidden')
    }

    // Mobile dropdown toggle (e.g. "About" in mobile nav)
    toggleMobileDropdown(event) {
        event.currentTarget.classList.toggle('active')
    }

    // --- About dropdown keyboard navigation ---

    aboutFocusIn() {
        this.aboutMenuTarget.classList.add('hovered')
    }

    aboutFocusOut() {
        this.aboutMenuTarget.classList.remove('hovered')
    }

    aboutKeydown(event) {
        const code = event.code ?? event.key
        if (code === 'ArrowDown') {
            if (event.target.nodeName === 'A') {
                event.target.closest('.item')?.nextElementSibling?.querySelector('a')?.focus()
            } else {
                this.aboutMenuTarget.querySelector('.menu .item a')?.focus()
            }
        } else if (code === 'ArrowUp') {
            const prevLink = event.target.closest('.item')?.previousElementSibling?.querySelector('a')
            if (prevLink) {
                prevLink.focus()
            } else {
                this.aboutTextTarget.focus()
            }
        }
    }

    // --- Pit bar (hide nav on scroll down, show on scroll up) ---

    _checkScroll() {
        const scrolled = this._scrollContainer.scrollTop
        const prev = this._lastScroll
        const mobileVisible = this.hasMobileNavTarget && this.mobileNavTarget.classList.contains('visible')

        if (scrolled - prev > 25 && scrolled > prev && scrolled > 90) {
            // scrolling down fast
            if (!mobileVisible) {
                this.mainNavTarget.classList.add('hidden')
            }
        } else if (scrolled < prev && prev - scrolled > 5) {
            // scrolling up
            this.mainNavTarget.classList.remove('hidden')
        }
        this._lastScroll = scrolled
    }
}
