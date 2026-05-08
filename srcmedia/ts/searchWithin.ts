import { Application } from '@hotwired/stimulus'
import SearchWithinController from './controllers/search_within_controller'

// Bootstrap Stimulus for the search-within bundle
const application = Application.start()
application.register('search-within', SearchWithinController)

