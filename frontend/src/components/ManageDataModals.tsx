import React, { useState, useEffect } from "react";
import {
  X,
  Plus,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Play,
  ShieldCheck,
} from "lucide-react";
import {
  createHeritageSite,
  getImportBatches,
  getStateTracker,
  runBaselineIngestion,
  type HeritageSiteCreateInput,
  type ImportBatch,
  type StateTrackerResponse,
} from "../api";

/* =========================================================
   ADD NEW SITE MODAL
========================================================= */

interface AddSiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddSiteModal: React.FC<AddSiteModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<HeritageSiteCreateInput>({
    external_id: `BHARAT-SITE-${Date.now().toString().slice(-6)}`,
    name: "",
    state: "Uttar Pradesh",
    district: "",
    city: "",
    category: "temple",
    period: "Medieval",
    latitude: 27.1751,
    longitude: 78.0421,
    description: "",
    significance: "",
    architecture: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.state.trim()) {
      setStatusMsg({ type: "error", text: "Name and State are required fields." });
      return;
    }

    if (
      typeof formData.latitude !== "number" ||
      typeof formData.longitude !== "number" ||
      isNaN(formData.latitude) ||
      isNaN(formData.longitude)
    ) {
      setStatusMsg({ type: "error", text: "Valid coordinates (latitude and longitude) are required." });
      return;
    }

    setSubmitting(true);
    setStatusMsg(null);

    try {
      await createHeritageSite(formData);
      setStatusMsg({ type: "success", text: "Heritage monument registered in national database!" });
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1200);
    } catch (err: any) {
      const msg = err.message || "";
      if (msg.includes("401") || msg.includes("503") || msg.includes("Unauthorized")) {
        setStatusMsg({
          type: "error",
          text: "Write Access Restricted: Registration requires authorized administrator permissions under the preservation security policy.",
        });
      } else {
        setStatusMsg({
          type: "error",
          text: msg || "Failed to register site. Verify inputs and database status.",
        });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="manage-modal-window" onClick={(e) => e.stopPropagation()}>
        <div className="dossier-header">
          <div className="dossier-header-title-box">
            <div className="tile-icon-circle green">
              <Plus className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="modal-title">Register New Heritage Site</h3>
              <p className="modal-subtitle">Direct intake into the verified national inventory</p>
            </div>
          </div>
          <button className="dossier-close-btn" onClick={onClose} aria-label="Close modal">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {statusMsg && (
            <div className={`status-banner ${statusMsg.type}`}>
              {statusMsg.type === "success" ? (
                <CheckCircle className="w-4 h-4 inline mr-2 text-emerald-400" />
              ) : (
                <AlertCircle className="w-4 h-4 inline mr-2 text-red-400" />
              )}
              <span>{statusMsg.text}</span>
            </div>
          )}

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Monument Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Meenakshi Amman Temple"
              />
            </div>
            <div className="form-group flex-1">
              <label>State / UT *</label>
              <input
                type="text"
                required
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="e.g. Tamil Nadu"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Category</label>
              <select
                value={formData.category || "temple"}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                <option value="temple">Temple & Shrine</option>
                <option value="monument">Monument / Mausoleum</option>
                <option value="fort">Fort & Citadel</option>
                <option value="stupa">Stupa Complex</option>
                <option value="cave">Rock-cut Cave</option>
                <option value="stepwell">Stepwell</option>
                <option value="archaeological">Archaeological Site</option>
              </select>
            </div>
            <div className="form-group flex-1">
              <label>Period / Dynasty</label>
              <input
                type="text"
                value={formData.period || ""}
                onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                placeholder="e.g. 7th Century CE / Pandya Dynasty"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Latitude (Decimal Degrees) *</label>
              <input
                type="number"
                step="0.0001"
                required
                value={formData.latitude ?? ""}
                onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group flex-1">
              <label>Longitude (Decimal Degrees) *</label>
              <input
                type="number"
                step="0.0001"
                required
                value={formData.longitude ?? ""}
                onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Historical Description & Provenance</label>
            <textarea
              rows={3}
              value={formData.description || ""}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Significance, architectural craftsmanship, and archival citations..."
            />
          </div>

          <div className="modal-actions-bar">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                  Saving...
                </>
              ) : (
                "Save Monument"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

/* =========================================================
   REPORTS & INGESTION BATCHES MODAL
========================================================= */

interface ReportsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ReportsModal: React.FC<ReportsModalProps> = ({ isOpen, onClose }) => {
  const [batches, setBatches] = useState<ImportBatch[]>([]);
  const [tracker, setTracker] = useState<StateTrackerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [runningBaseline, setRunningBaseline] = useState(false);
  const [baselineMsg, setBaselineMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    Promise.all([getImportBatches(), getStateTracker()])
      .then(([b, t]) => {
        setBatches(b);
        setTracker(t);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const handleRunBaselineDryRun = async (source: "unesco" | "asi") => {
    setRunningBaseline(true);
    setBaselineMsg(null);
    try {
      const res: any = await runBaselineIngestion(source, true);
      setBaselineMsg({
        type: "success",
        text: `Pipeline Verification Passed (${source.toUpperCase()}): ${res.total_records} records parsed with 0 database mutations (dry-run).`,
      });
    } catch (err: any) {
      const msg = err.message || "";
      if (msg.includes("401") || msg.includes("503")) {
        setBaselineMsg({
          type: "error",
          text: "Privileged Execution Policy: Pipeline execution requires backend server authorization key.",
        });
      } else {
        setBaselineMsg({
          type: "error",
          text: `Pipeline check error: ${msg}`,
        });
      }
    } finally {
      setRunningBaseline(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="manage-modal-window large" onClick={(e) => e.stopPropagation()}>
        <div className="dossier-header">
          <div className="dossier-header-title-box">
            <div className="tile-icon-circle purple">
              <FileText className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="modal-title">National Ingestion & Scalability Reports</h3>
              <p className="modal-subtitle">ASI Centrally Protected & UNESCO World Heritage Import Audit</p>
            </div>
          </div>
          <button className="dossier-close-btn" onClick={onClose} aria-label="Close modal">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div className="reports-modal-body">
          {baselineMsg && (
            <div className={`status-banner ${baselineMsg.type} mb-4`}>
              {baselineMsg.type === "success" ? (
                <CheckCircle className="w-4 h-4 inline mr-2 text-emerald-400" />
              ) : (
                <AlertCircle className="w-4 h-4 inline mr-2 text-red-400" />
              )}
              <span>{baselineMsg.text}</span>
            </div>
          )}

          {/* National Coverage Summary */}
          {tracker && (
            <div className="coverage-summary-bar">
              <div className="cov-stat">
                <span className="cov-label">Total States & UTs</span>
                <span className="cov-val">{tracker.summary.total_states_and_uts}</span>
              </div>
              <div className="cov-stat">
                <span className="cov-label">Ingestion Regions Tracked</span>
                <span className="cov-val text-amber-400">
                  {tracker.summary.states_with_baseline_or_completed} / 36
                </span>
              </div>
              <div className="cov-stat">
                <span className="cov-label">Estimated National Baseline</span>
                <span className="cov-val">{tracker.summary.total_estimated_national_monuments}</span>
              </div>
              <div className="cov-stat">
                <span className="cov-label">State Coverage Rate</span>
                <span className="cov-val text-emerald-400">
                  {tracker.summary.national_state_coverage_pct}%
                </span>
              </div>
            </div>
          )}

          {/* Pipeline Dry-Run Verification */}
          <div className="dry-run-actions-bar">
            <span className="font-semibold text-xs text-amber-300">
              <ShieldCheck className="w-3.5 h-3.5 inline mr-1" />
              Pipeline Safety Drill:
            </span>
            <button
              className="btn-dry-run"
              onClick={() => handleRunBaselineDryRun("unesco")}
              disabled={runningBaseline}
            >
              <Play className="w-3.5 h-3.5 inline mr-1" />
              Test UNESCO Adapter (Dry-Run)
            </button>
            <button
              className="btn-dry-run"
              onClick={() => handleRunBaselineDryRun("asi")}
              disabled={runningBaseline}
            >
              <Play className="w-3.5 h-3.5 inline mr-1" />
              Test ASI Adapter (Dry-Run)
            </button>
          </div>

          {/* Batches Table */}
          <h4 className="section-heading mt-4 mb-2">Ingestion Batch Execution History ({batches.length} Batches)</h4>
          {loading ? (
            <div className="loading-state">
              <Loader2 className="w-6 h-6 text-amber-400 animate-spin" />
            </div>
          ) : (
            <div className="table-responsive">
              <table className="reports-table">
                <thead>
                  <tr>
                    <th>Batch ID</th>
                    <th>Source Org</th>
                    <th>Dataset</th>
                    <th>Status</th>
                    <th>Total</th>
                    <th>Inserted</th>
                    <th>Duplicates</th>
                  </tr>
                </thead>
                <tbody>
                  {batches.map((b) => (
                    <tr key={b.id}>
                      <td className="font-mono text-xs text-amber-300">{b.batch_id}</td>
                      <td>{b.source_organization}</td>
                      <td>{b.source_dataset}</td>
                      <td>
                        <span className={`status-badge ${b.status.toLowerCase()}`}>
                          {b.status}
                        </span>
                      </td>
                      <td>{b.total_records}</td>
                      <td className="text-emerald-400 font-semibold">{b.inserted_records}</td>
                      <td className="text-gray-400">{b.duplicate_records}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default ReportsModal;
