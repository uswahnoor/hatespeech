const API_BASE = "http://localhost:8000/api";

// API client with error handling
export const api = {
  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    // Build headers step by step to avoid merging issues
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    
    // Add auth headers
    const token = localStorage.getItem("token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    // Add any additional headers from options
    if (options.headers) {
      Object.assign(headers, options.headers);
    }
    
    const config: RequestInit = {
      ...options,
      headers,
    };

    console.log('API Request:', { url, headers, body: options.body });

    try {
      const response = await fetch(url, config);
      const contentType = response.headers.get("content-type") || "";

      // Handle empty responses (like 204 No Content)
      let body;
      if (response.status === 204 || response.headers.get("content-length") === "0") {
        body = null;
      } else if (contentType.includes("application/json")) {
        body = await response.json();
      } else {
        body = await response.text();
      }

      if (!response.ok) {
        // Simplify validation errors
        if (response.status === 400 && typeof body === 'object' && body !== null) {
          const values = Object.values(body as Record<string, unknown>);
          const first = Array.isArray(values[0]) ? (values[0] as unknown[])[0] : values[0];
          const message = typeof first === 'string' ? first : 'Please check your input and try again.';
          throw new Error(message);
        }
        
        // Don't auto-logout on 401 - let the user handle authentication errors
        // if (response.status === 401) {
        //   const errorMessage = typeof body === "string" ? body : body?.error || body?.message || '';
        //   
        //   // Only logout for JWT token issues, not API key issues
        //   if (!errorMessage.toLowerCase().includes('api key')) {
        //     localStorage.removeItem("token");
        //     window.location.href = "/auth/login";
        //     return;
        //   }
        // }
        
        const message = typeof body === "string"
          ? body.slice(0, 300)
          : body?.error || body?.message || `HTTP ${response.status}`;
        throw new Error(message);
      }

      return body;
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  // Auth endpoints
  auth: {
    signup: (userData: { name: string; email: string; password: string; confirm_password: string }) =>
      api.request("/auth/signup", { method: "POST", body: JSON.stringify(userData) }),
    
    login: (credentials: { email: string; password: string }) =>
      api.request("/auth/login", { method: "POST", body: JSON.stringify(credentials) }),
    
    verifyEmail: (token: string) =>
      api.request(`/auth/verify-email/${token}`),

    resendVerification: (email: string) =>
      api.request('/auth/resend-verification', { method: 'POST', body: JSON.stringify({ email }) }),
  },

  // User endpoints
  user: {
    getProfile: () => api.request("/user/profile"),
    updateProfile: (userData: { name: string; email: string; password?: string }) =>
      api.request("/user/profile", { method: "PUT", body: JSON.stringify(userData) }),
    
    // API Key management
    getApiKeys: () => api.request("/auth/api-keys/"),
    createApiKey: () => api.request("/auth/api-keys/create/", { method: "POST" }),
    deleteApiKey: (keyId: number) => api.request(`/auth/api-keys/delete/${keyId}/`, { method: "DELETE" }),
  },

  // Detection endpoints
  detect: {
    analyzeText: (text: string, apiKey?: string) => {
      const requestOptions: RequestInit = { 
        method: "POST", 
        body: JSON.stringify({ text }),
        headers: {}
      };
      
      if (apiKey) {
        requestOptions.headers = { 'X-API-KEY': apiKey };
        console.log('Adding API key to headers:', apiKey);
      } else {
        console.log('No API key provided');
      }
      
      return api.request("/detect/", requestOptions);
    },
    
    getHistory: () => api.request("/detect/history/"),
  },
};

// Auth utilities
export const auth = {
  isAuthenticated: () => !!localStorage.getItem("token"),
  
  login: (token: string) => {
    localStorage.setItem("token", token);
  },
  
  logout: () => {
    localStorage.removeItem("token");
    window.location.href = "/auth/login";
  },
  
  getToken: () => localStorage.getItem("token"),
};