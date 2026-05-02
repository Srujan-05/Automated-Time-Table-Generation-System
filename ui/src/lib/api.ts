import type { AuthResponse, IngestionSeedResponse, TimetableEntry, DashboardStats } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

// Caching Layer
const cache: Record<string, { data: any, timestamp: number }> = {};
const CACHE_TTL = 30000; // 30 seconds

const fetchWithCache = async (url: string, options: RequestInit = {}) => {
    const isGet = !options.method || options.method === 'GET';
    const cacheKey = url + (options.headers ? JSON.stringify(options.headers) : '');

    if (isGet && cache[cacheKey] && (Date.now() - cache[cacheKey].timestamp < CACHE_TTL)) {
        return cache[cacheKey].data;
    }

    const res = await fetch(url, options);
    if (!res.ok) throw new Error((await res.json()).msg || "API Error");
    
    const data = await res.json();
    if (isGet) {
        cache[cacheKey] = { data, timestamp: Date.now() };
    } else {
        Object.keys(cache).forEach(key => delete cache[key]);
    }
    return data;
};

const getHeaders = () => {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
    };
};

export const api = {
    auth: {
        register: async (data: Record<string, string>): Promise<{ msg: string; role: string }> => {
            return fetchWithCache(`${BASE_URL}/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        },
        authenticate: async (data: Record<string, string>): Promise<AuthResponse> => {
            return fetchWithCache(`${BASE_URL}/auth/signin`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        }
    },
    timetable: {
        fetchSchedule: async (params?: string): Promise<TimetableEntry[]> => {
            const url = params ? `${BASE_URL}/timetable?${params}` : `${BASE_URL}/timetable`;
            return fetchWithCache(url, { headers: getHeaders() });
        },
        fetchDashboardStats: async (): Promise<DashboardStats> => {
            return fetchWithCache(`${BASE_URL}/timetable/stats`, { headers: getHeaders() });
        },
        search: async (query: string): Promise<any[]> => {
            return fetchWithCache(`${BASE_URL}/timetable/search?q=${query}`, { headers: getHeaders() });
        },
        listRooms: async (): Promise<string[]> => {
            return fetchWithCache(`${BASE_URL}/timetable/rooms`, { headers: getHeaders() });
        },
        listCourses: async (): Promise<string[]> => {
            return fetchWithCache(`${BASE_URL}/timetable/courses`, { headers: getHeaders() });
        },
        listProfessors: async (): Promise<string[]> => {
            return fetchWithCache(`${BASE_URL}/timetable/professors`, { headers: getHeaders() });
        },
        listGroups: async (): Promise<string[]> => {
            return fetchWithCache(`${BASE_URL}/timetable/groups`, { headers: getHeaders() });
        },
        triggerGeneration: async (config: any): Promise<{ msg: string; schedule_id: number; fitness: number }> => {
            return fetchWithCache(`${BASE_URL}/timetable/generate`, {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify(config)
            });
        },
        exportCsv: async () => {
            const res = await fetch(`${BASE_URL}/timetable/export`, { headers: getHeaders() });
            if (!res.ok) throw new Error("Failed to export timetable");
            return res.blob();
        }
    },
    ingestion: {
        triggerSeed: async (): Promise<IngestionSeedResponse> => {
            return fetchWithCache(`${BASE_URL}/ingestion/seed`, {
                method: "POST",
                headers: getHeaders()
            });
        },
        uploadFile: async (type: string, file: File): Promise<{ msg: string }> => {
            const formData = new FormData();
            formData.append("file", file);
            const token = localStorage.getItem("token");
            const res = await fetch(`${BASE_URL}/ingestion/upload/${type}`, {
                method: "POST",
                headers: {
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: formData
            });
            if (!res.ok) throw new Error("Upload failed");
            Object.keys(cache).forEach(key => delete cache[key]);
            return res.json();
        }
    },
    preferences: {
        listFaculty: async () => {
            return fetchWithCache(`${BASE_URL}/preferences/professors`, { headers: getHeaders() });
        },
        fetchShift: async (professorId?: number) => {
            const url = professorId ? `${BASE_URL}/preferences/shift?professor_id=${professorId}` : `${BASE_URL}/preferences/shift`;
            return fetchWithCache(url, { headers: getHeaders() });
        },
        updateShift: async (binId: number, professorId?: number) => {
            return fetchWithCache(`${BASE_URL}/preferences/shift`, {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({ bin_id: binId, professor_id: professorId })
            });
        }
    }
};
