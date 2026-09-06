const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

/* =========================================================
   TYPES
========================================================= */

export interface HeritageSite {
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

  created_at?: string;
  updated_at?: string;
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

export async function getApiInfo() {
  const response = await fetch("http://127.0.0.1:8000/");

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch("http://127.0.0.1:8000/health");

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
export async function getHeritageSites(): Promise<HeritageSite[]> {
  return apiRequest<HeritageSite[]>("/heritage-sites");
}

/**
 * Get one heritage site
 */
export async function getHeritageSite(
  siteId: number
): Promise<HeritageSite> {
  return apiRequest<HeritageSite>(
    `/heritage-sites/${siteId}`
  );
}

/**
 * Search heritage sites
 */
export async function searchHeritageSites(
  query: string
): Promise<HeritageSite[]> {
  const params = new URLSearchParams();

  if (query.trim()) {
    params.set("query", query.trim());
  }

  return apiRequest<HeritageSite[]>(
    `/heritage-sites/search?${params.toString()}`
  );
}

/**
 * Nearby sites
 */
export async function getNearbySites(
  latitude: number,
  longitude: number,
  radius?: number
) {
  const params = new URLSearchParams({
    latitude: latitude.toString(),
    longitude: longitude.toString(),
  });

  if (radius !== undefined) {
    params.set("radius", radius.toString());
  }

  return apiRequest(
    `/heritage-sites/nearby?${params.toString()}`
  );
}

/**
 * Recommendations
 */
export async function getHeritageRecommendations(
  siteId: number
) {
  return apiRequest(
    `/heritage-sites/${siteId}/recommendations`
  );
}

/* =========================================================
   HERITAGE CONNECTIONS
========================================================= */

/**
 * Get all connections involving a site.
 */
export async function getSiteConnections(
  siteId: number
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}`
  );
}

/**
 * Get outgoing connections
 */
export async function getOutgoingConnections(
  siteId: number
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}/outgoing`
  );
}

/**
 * Get incoming connections
 */
export async function getIncomingConnections(
  siteId: number
): Promise<HeritageConnection[]> {
  return apiRequest<HeritageConnection[]>(
    `/heritage-connections/site/${siteId}/incoming`
  );
}

/**
 * Get individual connection
 */
export async function getHeritageConnection(
  connectionId: number
): Promise<HeritageConnection> {
  return apiRequest<HeritageConnection>(
    `/heritage-connections/${connectionId}`
  );
}

/* =========================================================
   HERITAGE GRAPH
========================================================= */

export async function getCompleteGraph() {
  return apiRequest(
    "/heritage-graph"
  );
}

export async function getSiteGraph(
  siteId: number
) {
  return apiRequest(
    `/heritage-graph/site/${siteId}`
  );
}

export async function generateSiteGraph(
  siteId: number
) {
  return apiRequest(
    `/heritage-graph/generate/${siteId}`,
    {
      method: "POST",
    }
  );
}

export async function generateCompleteGraph() {
  return apiRequest(
    "/heritage-graph/generate",
    {
      method: "POST",
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
  searchHeritageSites,
  getNearbySites,
  getHeritageRecommendations,

  getSiteConnections,
  getOutgoingConnections,
  getIncomingConnections,
  getHeritageConnection,

  getCompleteGraph,
  getSiteGraph,
  generateSiteGraph,
  generateCompleteGraph,
};

export default api;