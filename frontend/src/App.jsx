import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import FarmerDashboard from './pages/FarmerDashboard'
import PriceIntel from './pages/PriceIntel'
import CreateLot from './pages/CreateLot'
import BuyerDashboard from './pages/BuyerDashboard'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing — no shared layout (full-screen) */}
        <Route path="/" element={<Landing />} />

        {/* Farmer routes — shared layout with tab bar */}
        <Route element={<Layout />}>
          <Route path="/farmer/dashboard" element={<FarmerDashboard />} />
          <Route path="/farmer/price-intel" element={<PriceIntel />} />
          <Route path="/farmer/create-lot" element={<CreateLot />} />
        </Route>

        {/* Buyer routes — shared layout, no tab bar (handled in Layout) */}
        <Route element={<Layout />}>
          <Route path="/buyer/dashboard" element={<BuyerDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
