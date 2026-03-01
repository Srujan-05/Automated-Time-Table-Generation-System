import type React from "react";

export type IconComponent = React.ComponentType<any>;

export interface User {
    id: number;
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

export interface TimetableEntry {
    id: number;
    time: string; // e.g. "09:00 - 10:00"
    course: string;
    room: string;
    faculty: string;
    batch?: string;
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

