import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Landmark } from "lucide-react";

export const NotFoundView: React.FC = () => {
  return (
    <div className="not-found-container">
      <div className="not-found-card">
        <div className="not-found-icon-wrapper">
          <Landmark className="w-12 h-12 text-amber-400" />
        </div>
        <h2 className="not-found-code">404</h2>
        <h3 className="not-found-title">Heritage Record Not Found</h3>
        <p className="not-found-desc">
          The requested cultural archive route or monument record does not exist in the national registry.
        </p>
        <Link to="/" className="not-found-btn">
          <ArrowLeft className="w-4 h-4 mr-2 inline" />
          <span>Return to Command Centre</span>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundView;
