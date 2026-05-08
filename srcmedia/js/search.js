import { Application } from '@hotwired/stimulus'
import SearchController from './controllers/search_controller'

// Bootstrap Stimulus for the search page bundle
const application = Application.start()
application.register('search', SearchController)

