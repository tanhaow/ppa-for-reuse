import { Application } from '@hotwired/stimulus'
import HomeController from './controllers/home_controller'

// Bootstrap Stimulus for the home page bundle
const application = Application.start()
application.register('home', HomeController)
