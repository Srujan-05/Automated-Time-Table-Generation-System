import type React from "react";

export type IconComponent = React.ComponentType<React.SVGProps<SVGSVGElement>>;

export interface RecentChange {
    id: number;
    course: string;
    faculty: string;
    time: string;
    status: string;
}

export interface User {
    name: string;
    role: string;
    email: string;
    avatar?: string;
    dept?: string;
    batch?: string;
}

export interface Course {
    id: string;
    name: string;
    credits: number;
}

export interface Room {
    id: string;
    capacity: number;
    type: string;
}

export interface AuthResponse {
    access_token: string;
    role: string;
}

export interface IngestionSeedResponse {
    professors_added: number;
    rooms_added: number;
    instances_created: number;
    groups_found: number;
}

export interface BackendActivity {
    id: number;
    category: 'NOTIFICATION' | 'CHANGE';
    title: string;
    message: string;
    time: string;
}

export interface DashboardStats {
    active_schedule: boolean;
    requirements: number;
    professors: number;
    rooms?: number;
    activities?: BackendActivity[];
    upcoming?: TimetableEntry[];
    // Dynamic Role-based stats
    primary?: { label: string, value: string | number };
    secondary?: { label: string, value: string | number };
    tertiary?: { label: string, value: string | number };
    quaternary?: { label: string, value: string | number };
}

export interface TimetableEntry {
    id: number;
    course: string;
    room: string;
    professor: string;
    type: string;
    group: string;
    day?: string;
    slot?: number;
    time?: string;
}

export interface NotificationItem {
    id: number;
    title: string;
    message: string;
    time: string;
}

export type SidebarItemProps = {
    icon: IconComponent;
    label: string;
    path: string;
    active: boolean;
    collapsed: boolean;
};

export type RoleCardProps = {
    icon: IconComponent;
    label: string;
    selected: boolean;
    onClick: () => void;
};

export type StatCardProps = {
    title: string;
    value: string;
    icon: IconComponent;
    trend?: string;
};

export type TimeSlotProps = {
    time: string;
    selected: boolean | undefined;
    unavailable?: boolean;
    onClick: () => void;
};

export type FileUpload = { name: string; status: "uploading" | "completed" };

export type TimetableMap = Record<string, TimetableEntry[]>;
export type TimetableCellProps = { entry?: TimetableEntry };

