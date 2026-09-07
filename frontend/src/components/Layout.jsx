import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, PackagePlus } from 'lucide-react'
import './Layout.css'

const farmerTabs = [
  { to: '/farmer/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/farmer/price-intel', icon: TrendingUp, label: 'Price Intel' },
  { to: '/farmer/create-lot', icon: PackagePlus, label: 'Create Lot' },
]

export default function Layout() {
  const location = useLocation()
  const isFarmerRoute = location.pathname.startsWith('/farmer')

  return (
    <div className="layout">
      <header className="layout-header">
        <NavLink to="/" className="layout-logo">
          <span className="layout-logo-icon">🌾</span>
          <span className="layout-logo-text">AgriEdge</span>
        </NavLink>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>

      {isFarmerRoute && (
        <nav className="layout-tab-bar" aria-label="Farmer navigation">
          {farmerTabs.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `tab-item ${isActive ? 'tab-item--active' : ''}`
              }
            >
              <Icon size={20} strokeWidth={2} />
              <span className="tab-label">{label}</span>
            </NavLink>
          ))}
        </nav>
      )}
    </div>
  )
}
