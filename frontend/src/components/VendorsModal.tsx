import React from 'react';
import './VendorsModal.css';

interface VendorsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const VendorsModal: React.FC<VendorsModalProps> = ({ isOpen, onClose }) => {
  const vendors = [
    {
      id: 1,
      name: 'BioTech Solutions',
      datasets: 12,
      status: 'Active',
      lastSync: '1 hour ago'
    },
    {
      id: 2,
      name: 'Genomics Corp',
      datasets: 8,
      status: 'Active',
      lastSync: '3 hours ago'
    },
    {
      id: 3,
      name: 'Protein Labs Inc',
      datasets: 5,
      status: 'Inactive',
      lastSync: '2 days ago'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="vendors-modal-overlay" onClick={onClose}>
      <div className="vendors-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🏢 Vendors</h2>
          <div className="simulation-badge" title="This data is simulated for demonstration purposes. Real vendor management needs to be implemented for production use.">🧪 Simulation Data</div>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-content">
          <div className="vendors-list">
            {vendors.map(vendor => (
              <div key={vendor.id} className="vendor-item" title={`${vendor.name} - ${vendor.datasets} datasets available. Status: ${vendor.status}. Last sync: ${vendor.lastSync}`}>
                <div className="vendor-info">
                  <h3 className="vendor-name">{vendor.name}</h3>
                  <p className="vendor-details">{vendor.datasets} datasets • Last sync: {vendor.lastSync}</p>
                </div>
                                            <span className={`status-badge ${vendor.status.toLowerCase()}`} title={`Vendor status: ${vendor.status} - ${vendor.status === 'Active' ? 'Vendor is active and providing data' : 'Vendor is inactive or suspended'}`}>
                              {vendor.status}
                            </span>
              </div>
            ))}
          </div>
          <div className="integration-note" title="Click to learn more about implementing real vendor management">
            <p>💡 <strong>Production Integration Required:</strong> This demo shows simulated data. For production use, implement custom integrations with your actual vendor management systems and APIs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorsModal;
