import React from "react";
import {
  ShieldCheck,
  ArrowRight,
  Plus,
  UploadCloud,
  FileText,
  DownloadCloud,
} from "lucide-react";

interface HeritageManagementProps {
  onAddNewSite: () => void;
  onUploadDataset: () => void;
  onViewReports: () => void;
  onExportData: () => void;
}

export const HeritageManagement: React.FC<HeritageManagementProps> = ({
  onAddNewSite,
  onUploadDataset,
  onViewReports,
  onExportData,
}) => {
  return (
    <div className="bottom-panel-card management-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <ShieldCheck className="panel-icon text-amber-400" />
          <h3 className="panel-title">Manage Heritage Data</h3>
        </div>
        <button className="panel-action-link" onClick={onViewReports}>
          <span>View All</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* 2x2 Action Tiles Grid */}
      <div className="management-actions-grid">
        {/* Tile 1: Add New Site */}
        <button
          className="management-tile add-site-tile"
          onClick={onAddNewSite}
          title="Register a new heritage site"
        >
          <div className="tile-icon-circle green">
            <Plus className="w-5 h-5 text-emerald-400" />
          </div>
          <span className="tile-title">Add New Site</span>
        </button>

        {/* Tile 2: Upload Dataset */}
        <button
          className="management-tile upload-tile"
          onClick={onUploadDataset}
          title="Upload or ingest baseline datasets"
        >
          <div className="tile-icon-circle blue">
            <UploadCloud className="w-5 h-5 text-sky-400" />
          </div>
          <span className="tile-title">Upload Dataset</span>
        </button>

        {/* Tile 3: View Reports */}
        <button
          className="management-tile reports-tile"
          onClick={onViewReports}
          title="View batch logs and national coverage"
        >
          <div className="tile-icon-circle purple">
            <FileText className="w-5 h-5 text-purple-400" />
          </div>
          <span className="tile-title">View Reports</span>
        </button>

        {/* Tile 4: Export Data */}
        <button
          className="management-tile export-tile"
          onClick={onExportData}
          title="Export heritage records in JSON format"
        >
          <div className="tile-icon-circle orange">
            <DownloadCloud className="w-5 h-5 text-amber-500" />
          </div>
          <span className="tile-title">Export Data</span>
        </button>
      </div>
    </div>
  );
};
export default HeritageManagement;
