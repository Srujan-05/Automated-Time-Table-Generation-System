import type { AuthResponse, IngestionSeedResponse, TimetableEntry, DashboardStats } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const getHeaders = () => {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
    };
};

export const api = {
    auth: {
        signup: async (data: Record<string, string>): Promise<{ msg: string; role: string }> => {
            const res = await fetch(`${BASE_URL}/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) throw new Error((await res.json()).msg || "Signup failed");
            return res.json();
        },
        signin: async (data: Record<string, string>): Promise<AuthResponse> => {
            const res = await fetch(`${BASE_URL}/auth/signin`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) throw new Error((await res.json()).msg || "Signin failed");
            return res.json();
        }
    },
    timetable: {
        get: async (params?: string): Promise<TimetableEntry[]> => {
            const url = params ? `${BASE_URL}/timetable?${params}` : `${BASE_URL}/timetable`;
            const res = await fetch(url, { headers: getHeaders() });
            if (!res.ok) throw new Error("Failed to fetch timetable");
            return res.json();
        },
        getStats: async (): Promise<DashboardStats> => {
            const res = await fetch(`${BASE_URL}/timetable/stats`, { headers: getHeaders() });
            if (!res.ok) throw new Error("Failed to fetch stats");
            return res.json();
        },
        generate: async (): Promise<{ msg: string; schedule_id: number; fitness: number }> => {
            const res = await fetch(`${BASE_URL}/timetable/generate`, {
                method: "POST",
                headers: getHeaders()
            });
            if (!res.ok) throw new Error((await res.json()).msg || "Generation failed");
            return res.json();
        }
    },
    ingestion: {
        seed: async (): Promise<IngestionSeedResponse> => {
            const res = await fetch(`${BASE_URL}/ingestion/seed`, {
                method: "POST",
                headers: getHeaders()
            });
            if (!res.ok) throw new Error("Seeding failed");
            return res.json();
        },
        upload: async (type: string, file: File): Promise<{ msg: string }> => {
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
            return res.json();
        }
    },
    preferences: {
        listProfessors: async () => {
            const res = await fetch(`${BASE_URL}/preferences/professors`, { headers: getHeaders() });
            if (!res.ok) throw new Error("Failed to list professors");
            return res.json();
        },
        getShift: async (professorId?: number) => {
            const url = professorId ? `${BASE_URL}/preferences/shift?professor_id=${professorId}` : `${BASE_URL}/preferences/shift`;
            const res = await fetch(url, { headers: getHeaders() });
            if (!res.ok) throw new Error("Failed to get shift");
            return res.json();
        },
        updateShift: async (binId: number, professorId?: number) => {
            const res = await fetch(`${BASE_URL}/preferences/shift`, {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({ bin_id: binId, professor_id: professorId })
            });
            if (!res.ok) throw new Error("Failed to update preferences");
            return res.json();
        }
    }

};
