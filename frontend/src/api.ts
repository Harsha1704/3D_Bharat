const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

/* =========================================================
   TYPES
========================================================= */

export interface HeritageSite {
  id: number;
  external_id?: string | null;
  name: string;
  alternative_names?: string[] | null;
  state?: string | null;
  district?: string | null;
  city?: string | null;
  category?: string | null;
  period?: string | null;
  description?: string | null;
  significance?: string | null;
  architecture?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  tags?: string[];
  historical_events?: string[];
  associated_people?: string[];
  traditions?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface HeritageSiteCreateInput {
  external_id: string;
  name: string;
  alternative_names?: string[];
  state: string;
  district?: string;
  city?: string;
  category?: string;
  period?: string;
  description?: string;
  significance?: string;
  architecture?: string;
  latitude?: number;
  longitude?: number;
  tags?: string[];
  historical_events?: string[];
  associated_people?: string[];
  traditions?: string[];
}

export interface HeritageSiteSearchResponse {
  items: HeritageSite[];
  total: number;
  skip: number;
  limit: number;
  has_next: boolean;
}

export interface HeritageSiteRecommendation {
  id: number;
  external_id?: string | null;
  name: string;
  state?: string | null;
  district?: string | null;
  city?: string | null;
  category?: string | null;
  period?: string | null;
  description?: string | null;
  significance?: string | null;
  architecture?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  tags?: string[];
  historical_events?: string[];
  associated_people?: string[];
  traditions?: string[];
  structured_score?: number;
  semantic_score?: number;
  recommendation_score: number;
  recommendation_reasons: string[];
}

export interface HeritageConnection {
  id: number;
  source_site_id: number;
  target_site_id: number;
  relationship_type: string;
  description?: string | null;
  confidence_score: number;
  created_at?: string;
  updated_at?: string;
}

export interface HeritageSource {
  id: number;
  heritage_site_id: number;
  source_type: string;
  title: string;
  author_or_institution?: string | null;
  publication_year?: number | null;
  url_or_identifier?: string | null;
  citation?: string | null;
  license?: string | null;
  reliability_score?: number | null;
  created_at?: string;
}

export interface HeritageMedia {
  id: number;
  heritage_site_id: number;
  title: string;
  description?: string | null;
  media_type: string;
  attribution?: string | null;
  license?: string | null;
  capture_date?: string | null;
  verification_status: string;
  file_size_bytes: number;
  checksum_sha256: string;
  storage_key: string;
  original_filename: string;
  mime_type: string;
  file_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Heritage3DAsset {
  id: number;
  heritage_site_id: number;
  title: string;
  description?: string | null;
  asset_type: string;
  file_format: string;
  vertex_count?: number | null;
  polygon_count?: number | null;
  texture_resolution?: string | null;
  has_companion_files?: boolean;
  companion_files_count?: number;
  verification_status: string;
  file_size_bytes: number;
  checksum_sha256: string;
  storage_key: string;
  original_filename: string;
  mime_type: string;
  file_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface HeritageConnectionDetailItem {
  connection_id: number;
  connected_site_id: number;
  connected_site_name: string;
  relationship_type: string;
  confidence_score?: number | null;
}

export interface HeritageSiteDetailResponse extends HeritageSite {
  sources: HeritageSource[];
  media: HeritageMedia[];
  assets_3d: Heritage3DAsset[];
  connections: HeritageConnectionDetailItem[];
  stats: {
    sources_count: number;
    media_count: number;
    assets_3d_count: number;
    connections_count: number;
  };
}

export interface DocumentedConnectionItem {
  connection_id: number;
  connected_site_id: number;
  connected_site_name: string;
  relationship_type: string;
  confidence_score?: number | null;
}

export interface StructuredRelationItem {
  site_id: number;
  name: string;
  category: string;
  state: string;
  period?: string | null;
}

export interface SemanticSuggestionItem {
  site_id: number;
  name: string;
  state: string;
  category: string;
  recommendation_score: number;
}

export interface HeritageRelatedSitesResponse {
  site_id: number;
  site_name: string;
  documented_connections: DocumentedConnectionItem[];
  structured_relations: StructuredRelationItem[];
  semantic_suggestions: SemanticSuggestionItem[];
  total_documented: number;
  total_structured: number;
  total_semantic: number;
}

export interface StateCoverageEntry {
  state_name: string;
  region: string;
  asi_circles: string[];
  estimated_monuments: number;
  status: string;
  records_ingested: number;
  records_with_coordinates: number;
  quality_notes?: string | null;
}

export interface StateTrackerSummary {
  total_states_and_uts: number;
  states_with_baseline_or_completed: number;
  total_estimated_national_monuments: number;
  total_records_ingested: number;
  total_records_with_coordinates: number;
  national_state_coverage_pct: number;
}

export interface StateTrackerResponse {
  summary: StateTrackerSummary;
  states: StateCoverageEntry[];
}

export interface ImportBatch {
  id: number;
  batch_id: string;
  source_organization: string;
  source_dataset: string;
  source_url?: string | null;
  license?: string | null;
  status: string;
  total_records: number;
  accepted_records: number;
  rejected_records: number;
  duplicate_records: number;
  updated_records: number;
  inserted_records: number;
  error_log?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface GraphNode {
  id: number;
  name: string;
  state?: string | null;
  district?: string | null;
  city?: string | null;
  category?: string | null;
  period?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface GraphEdge {
  id: number;
  source: number;
  target: number;
  relationship_type: string;
  description?: string | null;
  confidence_score?: number | null;
}

export interface HeritageGraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/* =========================================================
   API REQUEST HELPER
========================================================= */

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `API Error: ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData?.detail) {
        message =
          typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
      }
    } catch {
      // Ignore JSON parsing error
    }

    throw new Error(message);
  }

  return response.json();
}

/* =========================================================
   ROOT / HEALTH
========================================================= */

export async function getApiInfo(signal?: AbortSignal) {
  const response = await fetch("http://127.0.0.1:8000/", { signal });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(signal?: AbortSignal) {
  const response = await fetch("http://127.0.0.1:8000/health", { signal });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}

/* =========================================================
   HERITAGE SITES
========================================================= */

/**
 * Get all heritage sites
 */
export async function getHeritageSites(
  skip = 0,
  limit = 100,
  signal?: AbortSignal
): Promise<HeritageSite[]> {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  return apiRequest<HeritageSite[]>(`/heritage-sites?${params.toString()}`, {
    signal,
  });
}

/**
 * Get one heritage site
 */
export async function getHeritageSite(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageSite> {
  return apiRequest<HeritageSite>(`/heritage-sites/${siteId}`, { signal });
}

/**
 * Get full heritage site details with eager loaded sources, media, 3D assets, and connections
 */
export async function getHeritageSiteDetails(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageSiteDetailResponse> {
  return apiRequest<HeritageSiteDetailResponse>(
    `/heritage-sites/${siteId}/details`,
    { signal }
  );
}

/**
 * Get related sites (categorized into documented, structured, and semantic)
 */
export async function getRelatedHeritageSites(
  siteId: number,
  limit = 10,
  signal?: AbortSignal
): Promise<HeritageRelatedSitesResponse> {
  const params = new URLSearchParams({ limit: limit.toString() });
  return apiRequest<HeritageRelatedSitesResponse>(
    `/heritage-sites/${siteId}/related?${params.toString()}`,
    { signal }
  );
}

/**
 * Search heritage sites with multi-field matching
 */
export async function searchHeritageSites(
  query: string,
  category?: string,
  state?: string,
  skip = 0,
  limit = 100,
  signal?: AbortSignal
): Promise<{ items: HeritageSite[]; total: number }> {
  const params = new URLSearchParams();

  if (query.trim()) {
    params.set("query", query.trim());
  }
  if (category && category.trim()) {
    params.set("category", category.trim());
  }
  if (state && state.trim()) {
    params.set("state", state.trim());
  }
  params.set("skip", skip.toString());
  params.set("limit", limit.toString());

  const result = await apiRequest<HeritageSiteSearchResponse | HeritageSite[]>(
    `/heritage-sites/search?${params.toString()}`,
    { signal }
  );

  if (Array.isArray(result)) {
    return { items: result, total: result.length };
  }
  return { items: result?.items || [], total: result?.total || 0 };
}

/**
 * Bounding box discovery query for map viewports
 */
export async function getBboxHeritageSites(
  min_lat: number,
  min_lon: number,
  max_lat: number,
  max_lon: number,
  category?: string,
  state?: string,
  limit = 100,
  signal?: AbortSignal
): Promise<HeritageSite[]> {
  const params = new URLSearchParams({
    min_lat: min_lat.toString(),
    min_lon: min_lon.toString(),
    max_lat: max_lat.toString(),
    max_lon: max_lon.toString(),
    limit: limit.toString(),
  });

  if (category && category.trim()) {
    params.set("category", category.trim());
  }
  if (state && state.trim()) {
    params.set("state", state.trim());
  }

  return apiRequest<HeritageSite[]>(
    `/heritage-sites/bbox?${params.toString()}`,
    { signal }
  );
}

/**
 * Nearby sites by geographic radius
 */
export async function getNearbySites(
  latitude: number,
  longitude: number,
  radius?: number,
  signal?: AbortSignal
) {
  const params = new URLSearchParams({
    latitude: latitude.toString(),
    longitude: longitude.toString(),
  });

  if (radius !== undefined) {
    params.set("radius", radius.toString());
  }

  return apiRequest(`/heritage-sites/nearby?${params.toString()}`, {
    signal,
  });
}

/**
 * Recommendations
 */
export async function getHeritageRecommendations(
  siteId: number,
  limit = 5,
  signal?: AbortSignal
): Promise<HeritageSiteRecommendation[]> {
  const params = new URLSearchParams({ limit: limit.toString() });
  return apiRequest<HeritageSiteRecommendation[]>(
    `/heritage-sites/${siteId}/recommendations?${params.toString()}`,
    { signal }
  );
}

/**
 * Create a new heritage site
 */
export async function createHeritageSite(
  siteData: HeritageSiteCreateInput,
  signal?: AbortSignal
): Promise<HeritageSite> {
  return apiRequest<HeritageSite>("/heritage-sites", {
    method: "POST",
    body: JSON.stringify(siteData),
    signal,
  });
}

/* =========================================================
   HERITAGE CONNECTIONS
========================================================= */

export async function getSiteConnections(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}`,
    { signal }
  );
}

export async function getOutgoingConnections(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}/outgoing`,
    { signal }
  );
}

export async function getIncomingConnections(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}/incoming`,
    { signal }
  );
}

export async function getHeritageConnection(
  connectionId: number,
  signal?: AbortSignal
): Promise<HeritageConnection> {
  return apiRequest<HeritageConnection>(
    `/heritage-connections/${connectionId}`,
    { signal }
  );
}

/* =========================================================
   HERITAGE GRAPH
========================================================= */

export async function getCompleteGraph(
  signal?: AbortSignal
): Promise<HeritageGraphResponse> {
  return apiRequest<HeritageGraphResponse>("/heritage-graph", { signal });
}

export async function getSiteGraph(
  siteId: number,
  signal?: AbortSignal
): Promise<HeritageGraphResponse> {
  return apiRequest<HeritageGraphResponse>(`/heritage-graph/site/${siteId}`, {
    signal,
  });
}

export async function generateSiteGraph(
  siteId: number,
  signal?: AbortSignal
) {
  return apiRequest(`/heritage-graph/generate/${siteId}`, {
    method: "POST",
    signal,
  });
}

export async function generateCompleteGraph(signal?: AbortSignal) {
  return apiRequest("/heritage-graph/generate", {
    method: "POST",
    signal,
  });
}

/* =========================================================
   HERITAGE SOURCES, MEDIA & 3D ASSETS
========================================================= */

export async function getHeritageSources(
  siteId?: number,
  signal?: AbortSignal
): Promise<HeritageSource[]> {
  if (siteId) {
    return apiRequest<HeritageSource[]>(`/heritage-sources/site/${siteId}`, {
      signal,
    });
  }
  return apiRequest<HeritageSource[]>("/heritage-sources", { signal });
}

export async function getHeritageMedia(
  siteId?: number,
  signal?: AbortSignal
): Promise<HeritageMedia[]> {
  if (siteId) {
    return apiRequest<HeritageMedia[]>(`/heritage-media/site/${siteId}`, {
      signal,
    });
  }
  const result = await apiRequest<{ items: HeritageMedia[] } | HeritageMedia[]>(
    "/heritage-media",
    { signal }
  );
  return Array.isArray(result) ? result : result?.items || [];
}

export async function getHeritage3DAssets(
  siteId?: number,
  signal?: AbortSignal
): Promise<Heritage3DAsset[]> {
  if (siteId) {
    return apiRequest<Heritage3DAsset[]>(`/heritage-3d-assets/site/${siteId}`, {
      signal,
    });
  }
  const result = await apiRequest<
    { items: Heritage3DAsset[] } | Heritage3DAsset[]
  >("/heritage-3d-assets", { signal });
  return Array.isArray(result) ? result : result?.items || [];
}

/* =========================================================
   NATIONAL INGESTION & STATE TRACKER
========================================================= */

export async function getStateTracker(
  signal?: AbortSignal
): Promise<StateTrackerResponse> {
  return apiRequest<StateTrackerResponse>("/heritage-ingestion/state-tracker", {
    signal,
  });
}

export async function getImportBatches(
  skip = 0,
  limit = 50,
  signal?: AbortSignal
): Promise<ImportBatch[]> {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  return apiRequest<ImportBatch[]>(
    `/heritage-ingestion/batches?${params.toString()}`,
    { signal }
  );
}

export async function runBaselineIngestion(
  sourceType: "unesco" | "asi",
  dryRun = false,
  signal?: AbortSignal
) {
  return apiRequest(
    `/heritage-ingestion/run-baseline/${sourceType}?dry_run=${dryRun}`,
    {
      method: "POST",
      signal,
    }
  );
}

/* =========================================================
   DEFAULT API OBJECT
========================================================= */

const api = {
  getApiInfo,
  checkHealth,
  getHeritageSites,
  getHeritageSite,
  getHeritageSiteDetails,
  getRelatedHeritageSites,
  searchHeritageSites,
  getBboxHeritageSites,
  getNearbySites,
  getHeritageRecommendations,
  createHeritageSite,
  getSiteConnections,
  getOutgoingConnections,
  getIncomingConnections,
  getHeritageConnection,
  getCompleteGraph,
  getSiteGraph,
  generateSiteGraph,
  generateCompleteGraph,
  getHeritageSources,
  getHeritageMedia,
  getHeritage3DAssets,
  getStateTracker,
  getImportBatches,
  runBaselineIngestion,
};

export default api;
