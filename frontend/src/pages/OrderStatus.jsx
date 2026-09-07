import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getOffer, updateLogistics, createDispute } from '../api/client';
import { ArrowLeft, CheckCircle2, Truck, Package, PackageCheck, AlertCircle } from 'lucide-react';
import './OrderStatus.css';

const STATUS_STAGES = [
  { id: "REQUESTED", label: "Requested", icon: Package },
  { id: "SCHEDULED", label: "Scheduled", icon: CheckCircle2 },
  { id: "IN_TRANSIT", label: "In Transit", icon: Truck },
  { id: "DELIVERED", label: "Delivered", icon: PackageCheck }
];

export default function OrderStatus() {
  const { offerId } = useParams();
  const navigate = useNavigate();
  
  const [offer, setOffer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [disputeReason, setDisputeReason] = useState("");
  const [showDisputeInput, setShowDisputeInput] = useState(false);
  const [submittingDispute, setSubmittingDispute] = useState(false);

  const fetchOrder = async () => {
    try {
      const data = await getOffer(offerId);
      setOffer(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load order details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrder();
  }, [offerId]);

  const handleAdvanceStage = async () => {
    if (!offer || !offer.logistics) return;
    
    const currentIdx = STATUS_STAGES.findIndex(s => s.id === offer.logistics.status);
    if (currentIdx >= 0 && currentIdx < STATUS_STAGES.length - 1) {
      const nextStatus = STATUS_STAGES[currentIdx + 1].id;
      try {
        await updateLogistics(offer.logistics.id, nextStatus);
        await fetchOrder(); // refresh
      } catch (err) {
        alert("Failed to update logistics status.");
      }
    }
  };

  const handleRaiseDispute = async () => {
    if (!disputeReason.trim()) return;
    setSubmittingDispute(true);
    try {
      await createDispute(offer.id, disputeReason);
      setDisputeReason("");
      setShowDisputeInput(false);
      await fetchOrder(); // refresh to show dispute
    } catch (err) {
      alert("Failed to raise dispute.");
    } finally {
      setSubmittingDispute(false);
    }
  };

  if (loading) {
    return (
      <div className="page order-status-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading order...</p>
        </div>
      </div>
    );
  }

  if (error || !offer) {
    return (
      <div className="page order-status-page">
        <div className="error-state card">
          <AlertCircle color="var(--color-danger)" size={24} />
          <p>{error || "Order not found."}</p>
          <button className="btn-secondary" onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  const currentStatusIdx = offer.logistics ? STATUS_STAGES.findIndex(s => s.id === offer.logistics.status) : -1;
  const hasDispute = offer.disputes && offer.disputes.length > 0;
  const activeDispute = hasDispute ? offer.disputes[0] : null;

  return (
    <div className="page order-status-page">
      <header className="page-header">
        <button className="back-btn" onClick={() => navigate('/farmer/create-lot')}>
          <ArrowLeft size={24} />
        </button>
        <h1 className="page-title">Order #{offer.id}</h1>
      </header>

      <div className="card summary-card">
        <div className="summary-header">
          <h2>{offer.buyer_name}</h2>
          <span className="status-badge status-accepted">ACCEPTED</span>
        </div>
        
        <div className="summary-grid">
          <div className="summary-item">
            <span className="label">Offered Price</span>
            <span className="value">₹{offer.offered_price_per_quintal}/qtl</span>
          </div>
          <div className="summary-item">
            <span className="label">Net Realization</span>
            <span className="value text-positive">₹{offer.net_realization_per_quintal}/qtl</span>
          </div>
        </div>
      </div>

      <div className="card logistics-card">
        <h2 className="card-title">Logistics Tracker</h2>
        
        <div className="stepper">
          {STATUS_STAGES.map((stage, idx) => {
            const isCompleted = idx <= currentStatusIdx;
            const isCurrent = idx === currentStatusIdx;
            const Icon = stage.icon;
            
            return (
              <div key={stage.id} className={`step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}>
                <div className="step-icon">
                  <Icon size={20} />
                </div>
                <div className="step-label">{stage.label}</div>
                {idx < STATUS_STAGES.length - 1 && <div className="step-line"></div>}
              </div>
            );
          })}
        </div>

        {currentStatusIdx < STATUS_STAGES.length - 1 && (
          <button className="btn-primary advance-btn" onClick={handleAdvanceStage}>
            Advance to Next Stage (Demo)
          </button>
        )}
      </div>

      <div className="card dispute-card">
        <h2 className="card-title">Support & Disputes</h2>
        
        {hasDispute ? (
          <div className="active-dispute">
            <div className="dispute-header">
              <AlertCircle size={20} className="text-danger" />
              <h3>Dispute {activeDispute.status}</h3>
            </div>
            <p className="dispute-reason">"{activeDispute.reason}"</p>
            {activeDispute.resolution_notes && (
              <div className="resolution-notes">
                <strong>Resolution:</strong> {activeDispute.resolution_notes}
              </div>
            )}
          </div>
        ) : (
          <div className="dispute-actions">
            {!showDisputeInput ? (
              <button className="btn-secondary" onClick={() => setShowDisputeInput(true)}>
                Raise a Dispute
              </button>
            ) : (
              <div className="dispute-form">
                <textarea 
                  placeholder="Describe the issue (e.g. Quality complaint, delayed pickup)..."
                  value={disputeReason}
                  onChange={(e) => setDisputeReason(e.target.value)}
                  rows={3}
                />
                <div className="dispute-form-actions">
                  <button className="btn-secondary" onClick={() => setShowDisputeInput(false)}>Cancel</button>
                  <button className="btn-danger" onClick={handleRaiseDispute} disabled={submittingDispute}>
                    {submittingDispute ? "Submitting..." : "Submit Dispute"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
