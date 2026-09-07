import { useNavigate } from 'react-router-dom'
import { Sprout, ShoppingCart } from 'lucide-react'
import './Landing.css'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="landing">
      <div className="landing-content">
        <div className="landing-brand">
          <span className="landing-icon">🌾</span>
          <h1 className="landing-title">AgriEdge</h1>
        </div>
        <p className="landing-tagline">
          Know when to sell, where to sell, and what you'll really earn.
        </p>

        <div className="landing-cards">
          <button
            className="role-card role-card--farmer"
            onClick={() => navigate('/farmer/dashboard')}
            id="role-farmer"
          >
            <div className="role-card-icon">
              <Sprout size={32} strokeWidth={1.8} />
            </div>
            <span className="role-card-label">I'm a Farmer</span>
            <span className="role-card-desc">
              Get price forecasts, sale-window advice, and find the best buyers
            </span>
          </button>

          <button
            className="role-card role-card--buyer"
            onClick={() => navigate('/buyer/dashboard')}
            id="role-buyer"
          >
            <div className="role-card-icon">
              <ShoppingCart size={32} strokeWidth={1.8} />
            </div>
            <span className="role-card-label">I'm a Buyer</span>
            <span className="role-card-desc">
              Browse available lots, connect with farmers, and source directly
            </span>
          </button>
        </div>
      </div>

      <p className="landing-footer">
        Built for Smart India Hackathon 2026
      </p>
    </div>
  )
}
