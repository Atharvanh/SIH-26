import React, { useState, useEffect } from 'react';
import { getAcceptedOffers } from '../api/client';
import { Package, Truck, PackageCheck, AlertCircle, CheckCircle2 } from 'lucide-react';
import './BuyerDashboard.css';

export default function BuyerDashboard() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOffers = async () => {
      try {
        const data = await getAcceptedOffers();
        setOffers(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load accepted offers.");
      } finally {
        setLoading(false);
      }
    };
    fetchOffers();
  }, []);

  const renderLogisticsBadge = (status) => {
    switch (status) {
      case "REQUESTED": return <span className="log-badge requested"><Package size={14} /> Requested</span>;
      case "SCHEDULED": return <span className="log-badge scheduled"><CheckCircle2 size={14} /> Scheduled</span>;
      case "IN_TRANSIT": return <span className="log-badge in-transit"><Truck size={14} /> In Transit</span>;
      case "DELIVERED": return <span className="log-badge delivered"><PackageCheck size={14} /> Delivered</span>;
      default: return null;
    }
  };

  return (
    <div className="page buyer-dashboard-page">
      <h1 className="page-title">Active Orders</h1>
      <p className="page-subtitle">Track your purchases from farmers</p>

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your orders...</p>
        </div>
      )}

      {error && (
        <div className="error-state card">
          <AlertCircle color="var(--color-danger)" size={24} />
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && offers.length === 0 && (
        <div className="card empty-state">
          <p>No active orders yet. Orders will appear here once a farmer accepts your offer.</p>
        </div>
      )}

      {!loading && !error && offers.length > 0 && (
        <div className="offers-list">
          {offers.map(offer => (
            <div key={offer.id} className="card offer-card">
              <div className="offer-header">
                <h3>{offer.buyer_name}</h3>
                {offer.logistics && renderLogisticsBadge(offer.logistics.status)}
              </div>
              
              <div className="offer-details">
                <div className="detail-col">
                  <span className="label">Commodity</span>
                  <span className="val">{offer.lot.commodity} (Grade {offer.lot.quality_grade})</span>
                </div>
                <div className="detail-col">
                  <span className="label">Quantity</span>
                  <span className="val">{offer.lot.quantity_quintals} qtl</span>
                </div>
              </div>

              <div className="offer-finances">
                <div className="finance-row">
                  <span className="label">Price Agreed</span>
                  <span className="val">₹{offer.offered_price_per_quintal}/qtl</span>
                </div>
                <div className="finance-row total">
                  <span className="label">Total Amount</span>
                  <span className="val">₹{(offer.offered_price_per_quintal * offer.lot.quantity_quintals).toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
