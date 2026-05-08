import { Application } from '@hotwired/stimulus'
import NavController from './controllers/nav_controller'
import ClearableController from './controllers/clearable_controller'
import LazyLoadController from './controllers/lazy_load_controller'
import 'fomantic-ui-less/semantic.less'

document.firstElementChild.classList.remove('no-js') // remove the no-js class

// Bootstrap Stimulus application
const application = Application.start()
application.register('nav', NavController)
application.register('clearable', ClearableController)
application.register('lazy-load', LazyLoadController)

