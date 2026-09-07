import React, { useState } from 'react';
import { matchBuyers, createLot, createOffer, acceptOffer } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ChevronDown, ChevronUp, MapPin, Truck, Award, ShieldCheck, ShieldAlert, Shield } from 'lucide-react';
import './CreateLot.css';

const LOCATION_OPTIONS = [
  { label: "Cabbage — Aralamoodu, Kerala", commodity: "Cabbage", lat: 8.3912, lon: 77.0620, state: "Kerala", market: "Aralamoodu" },
  { label: "Wheat — Raibareilly, Uttar Pradesh", commodity: "Wheat", lat: 26.2300, lon: 81.2400, state: "Uttar Pradesh", market: "Raibareilly" },
  { label: "Brinjal — Gondal, Gujarat", commodity: "Brinjal", lat: 21.9600, lon: 70.8000, state: "Gujarat", market: "Gondal(Veg.market Gondal)" }
];

export default function CreateLot() {
  const navigate = useNavigate();
  const [selectedLocation, setSelectedLocation] = useState(LOCATION_OPTIONS[0]);
  const [quantity, setQuantity] = useState(10);
  const [qualityGrade, setQualityGrade] = useState("A");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [createdLotId, setCreatedLotId] = useState(null);
  const [expandedCards, setExpandedCards] = useState({});
  const [acceptingBuyerId, setAcceptingBuyerId] = useState(null);

  const handleMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMatchResult(null);
    setExpandedCards({});
    
    try {
      // 1. Create the Lot in the backend
      const lotData = {
        commodity: selectedLocation.commodity,
        quantity_quintals: parseFloat(quantity),
        quality_grade: qualityGrade,
        state: selectedLocation.state,
        market: selectedLocation.market,
        farmer_lat: selectedLocation.lat,
        farmer_lon: selectedLocation.lon
      };
      const lot = await createLot(lotData);
      setCreatedLotId(lot.id);

      // 2. Find Best Buyers
      const data = await matchBuyers(
        selectedLocation.commodity,
        parseFloat(quantity),
        qualityGrade,
        selectedLocation.lat,
        selectedLocation.lon
      );
      setMatchResult(data);
    } catch (err) {
      console.error("API Error:", err);
      setError("Failed to process request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (buyer) => {
    if (!createdLotId) return;
    setAcceptingBuyerId(buyer.buyer_id);
    try {
      // a) Create Offer
      const offerData = {
        buyer_id: buyer.buyer_id,
        buyer_name: buyer.name,
        offered_price_per_quintal: buyer.offered_price_per_quintal,
        net_realization_per_quintal: buyer.breakdown.net_realization_per_quintal
      };
      const offer = await createOffer(createdLotId, offerData);
      
      // b) Accept Offer
      await acceptOffer(offer.id);
      
      // c) Navigate to Order Status
      navigate(`/farmer/order/${offer.id}`);
    } catch (err) {
      console.error("Acceptance Error:", err);
      setError("Failed to accept offer. Please try again.");
      setAcceptingBuyerId(null);
    }
  };

  const toggleCard = (id) => {
    setExpandedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const renderReliability = (pct) => {
    if (pct >= 90) return <span className="rel-tag rel-good"><ShieldCheck size={14}/> {pct}% on-time</span>;
    if (pct >= 75) return <span className="rel-tag rel-ok"><Shield size={14}/> {pct}% on-time</span>;
    return <span className="rel-tag rel-bad"><ShieldAlert size={14}/> {pct}% on-time</span>;
  };

  return (
    <div className="page createlot-page">
      <h1 className="page-title">Create Lot</h1>
      <p className="page-subtitle">List your produce and find the best buyers</p>

      <form className="card form-card" onSubmit={handleMatch}>
        <div className="form-group">
          <label htmlFor="crop-loc">Crop & Location</label>
          <select 
            id="crop-loc"
            value={LOCATION_OPTIONS.indexOf(selectedLocation)}
            onChange={(e) => setSelectedLocation(LOCATION_OPTIONS[e.target.value])}
          >
            {LOCATION_OPTIONS.map((opt, idx) => (
              <option key={idx} value={idx}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="qty">Quantity (quintals)</label>
            <input 
              type="number" 
              id="qty" 
              min="1" 
              step="0.1" 
              value={quantity} 
              onChange={(e) => setQuantity(e.target.value)} 
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="grade">Quality Grade</label>
            <select 
              id="grade"
              value={qualityGrade}
              onChange={(e) => setQualityGrade(e.target.value)}
            >
              <option value="A">Grade A</option>
              <option value="B">Grade B</option>
              <option value="C">Grade C</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Processing..." : "Find Best Buyers"}
        </button>
      </form>

      {error && (
        <div className="error-state card">
          <AlertCircle color="var(--color-danger)" size={24} />
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Crunching transport and reliability costs...</p>
        </div>
      )}

      {matchResult && matchResult.matched_buyers && (
        <div className="results-section">
          {matchResult.matched_buyers.length === 0 ? (
            <div className="card no-results">
              <p>No eligible buyers found for this combination.</p>
            </div>
          ) : (
            <>
              <div className="insight-banner">
                {matchResult.naive_top_pick_would_have_earned_less_by > 0 ? (
                  <p>
                    Selling to the highest bidder would have cost you <strong className="text-accent">₹{matchResult.naive_top_pick_would_have_earned_less_by.toFixed(2)} per quintal</strong> (₹{(matchResult.naive_top_pick_would_have_earned_less_by * quantity).toFixed(2)} total on this lot) compared to our actual #1 recommendation.
                  </p>
                ) : (
                  <p>
                    The highest bidder is also your best net option this time.
                  </p>
                )}
              </div>

              <div className="buyer-list">
                {matchResult.matched_buyers.map((buyer, idx) => (
                  <div key={buyer.buyer_id} className={`card buyer-card ${idx === 0 ? 'buyer-card--top' : ''}`}>
                    
                    <div className="buyer-header">
                      <div className="buyer-rank-badge">#{buyer.net_realization_rank}</div>
                      <div className="buyer-title">
                        <h3>{buyer.name}</h3>
                        <span className="buyer-type">{buyer.buyer_type}</span>
                      </div>
                    </div>

                    <div className="buyer-metrics">
                      <div className="metric">
                        <span className="metric-label">Offered Price</span>
                        <span className="metric-val">₹{buyer.offered_price_per_quintal}/qtl</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Distance</span>
                        <span className="metric-val"><MapPin size={12}/> {buyer.distance_km} km</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Reliability</span>
                        <span className="metric-val">{renderReliability(buyer.on_time_payment_pct)}</span>
                      </div>
                    </div>

                    <div className="buyer-net">
                      <span className="net-label">Net Realization</span>
                      <span className="net-value">₹{buyer.breakdown.net_realization_per_quintal.toFixed(2)}<span className="net-unit">/qtl</span></span>
                    </div>
                    
                    {buyer.naive_price_rank !== buyer.net_realization_rank && (
                      <div className="rank-flip-tag">
                        {buyer.net_realization_rank < buyer.naive_price_rank 
                          ? `↑ moved up from #${buyer.naive_price_rank} by price`
                          : `↓ was priced #${buyer.naive_price_rank}`}
                      </div>
                    )}

                    <div className="details-toggle" onClick={() => toggleCard(buyer.buyer_id)}>
                      <span>{expandedCards[buyer.buyer_id] ? 'Hide' : 'See'} full breakdown</span>
                      {expandedCards[buyer.buyer_id] ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>

                    {expandedCards[buyer.buyer_id] && (
                      <div className="breakdown-details">
                        <div className="detail-row">
                          <span>Gross Revenue</span>
                          <span>₹{buyer.breakdown.gross_revenue.toFixed(2)}</span>
                        </div>
                        <div className="detail-row cost">
                          <span><Truck size={14}/> Transport Cost</span>
                          <span>-₹{buyer.breakdown.transport_cost.toFixed(2)}</span>
                        </div>
                        <div className="detail-row cost">
                          <span><Award size={14}/> Commission</span>
                          <span>-₹{buyer.breakdown.commission_cost.toFixed(2)}</span>
                        </div>
                        <div className="detail-row cost">
                          <span><ShieldAlert size={14}/> Reliability Adj.</span>
                          <span>-₹{buyer.breakdown.reliability_adjustment.toFixed(2)}</span>
                        </div>
                        <div className="detail-row total">
                          <span>Final Net Realization</span>
                          <span className="text-positive">₹{buyer.breakdown.net_realization.toFixed(2)}</span>
                        </div>
                      </div>
                    )}
                    
                    <button 
                      className="btn-primary accept-btn" 
                      onClick={() => handleAccept(buyer)}
                      disabled={acceptingBuyerId !== null}
                    >
                      {acceptingBuyerId === buyer.buyer_id ? "Accepting..." : "Accept This Offer"}
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
