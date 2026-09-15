import { Route, Routes } from 'react-router-dom'
import PublicLayout from './Layout'
import About from './pages/About'
import Academics from './pages/Academics'
import Admissions from './pages/Admissions'
import AdmissionsApply from './pages/AdmissionsApply'
import AdmissionsStatus from './pages/AdmissionsStatus'
import Careers from './pages/Careers'
import Contact from './pages/Contact'
import EventDetail from './pages/EventDetail'
import Events from './pages/Events'
import FAQ from './pages/FAQ'
import Home from './pages/Home'
import News from './pages/News'
import NewsDetail from './pages/NewsDetail'
import NotFound from './pages/NotFound'
import ParentRegister from './pages/ParentRegister'
import Privacy from './pages/Privacy'
import Programs from './pages/Programs'
import Terms from './pages/Terms'

export default function PublicApp() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="academics" element={<Academics />} />
        <Route path="programs" element={<Programs />} />
        <Route path="admissions" element={<Admissions />} />
        <Route path="admissions/apply" element={<AdmissionsApply />} />
        <Route path="admissions/status" element={<AdmissionsStatus />} />
        <Route path="register/parent" element={<ParentRegister />} />
        <Route path="careers" element={<Careers />} />
        <Route path="news" element={<News />} />
        <Route path="news/:slug" element={<NewsDetail />} />
        <Route path="events" element={<Events />} />
        <Route path="events/:slug" element={<EventDetail />} />
        <Route path="contact" element={<Contact />} />
        <Route path="faq" element={<FAQ />} />
        <Route path="privacy" element={<Privacy />} />
        <Route path="terms" element={<Terms />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
