export const mockData = {
    users: {
        admin: { 
            id: 1, 
            name: "Admin User", 
            role: "admin", 
            email: "admin@college.edu", 
            avatar: "https://ui-avatars.com/api/?name=Admin+User&background=ef4444&color=fff" 
        },
        faculty: { 
            id: 2, 
            name: "Sarah Smith", 
            role: "faculty", 
            email: "sarah@college.edu", 
            dept: "Computer Science", 
            avatar: "https://ui-avatars.com/api/?name=Sarah+Smith&background=ef4444&color=fff" 
        },
        student: { 
            id: 3, 
            name: "John Doe", 
            role: "student", 
            email: "john@college.edu", 
            batch: "CSE-2026", 
            avatar: "https://ui-avatars.com/api/?name=John+Doe&background=ef4444&color=fff" 
        }
    },
    courses: [
        { id: "CS101", name: "Intro to CS", credits: 4 },
        { id: "CS102", name: "Data Structures", credits: 4 },
        { id: "MA101", name: "Calculus I", credits: 3 },
        { id: "PH101", name: "Physics", credits: 3 },
    ],
    rooms: [
        { id: "LH-101", capacity: 60, type: "Lecture Hall" },
        { id: "LH-102", capacity: 60, type: "Lecture Hall" },
        { id: "LAB-1", capacity: 30, type: "Lab" },
    ],
    timetable: {
        "Monday": [
            { id: 1, time: "09:00 - 10:00", course: "CS101", room: "LH-101", faculty: "Dr. Sarah Smith", batch: "CSE-A" },
            { id: 2, time: "10:00 - 11:00", course: "MA101", room: "LH-102", faculty: "Prof. Math", batch: "CSE-A" },
            { id: 3, time: "14:00 - 16:00", course: "CS102 Lab", room: "LAB-1", faculty: "Dr. Sarah Smith", batch: "CSE-B" },
        ],
        "Tuesday": [
            { id: 4, time: "09:00 - 10:00", course: "PH101", room: "LH-101", faculty: "Dr. Physics", batch: "CSE-A" },
            { id: 5, time: "11:00 - 13:00", course: "CS102", room: "LH-102", faculty: "Dr. Sarah Smith", batch: "CSE-A" },
        ],
        "Wednesday": [
            { id: 6, time: "10:00 - 11:00", course: "CS101", room: "LH-101", faculty: "Dr. Sarah Smith", batch: "CSE-B" },
        ],
        "Thursday": [],
        "Friday": [
            { id: 7, time: "09:00 - 11:00", course: "Project", room: "LAB-1", faculty: "All", batch: "CSE-A" },
        ]
    },
    notifications: [
        { id: 1, title: "Timetable Updated", message: "The schedule for CS101 has changed.", time: "2h ago" },
        { id: 2, title: "Preference Deadline", message: "Submit preferences by Friday.", time: "1d ago" },
    ],
    recentChanges: [
        { id: 1, course: "CS101", faculty: "Dr. Smith", time: "Mon, 10:00 AM", status: "Approved" },
        { id: 2, course: "MA101", faculty: "Prof. Math", time: "Tue, 11:00 AM", status: "Pending" },
        { id: 3, course: "PH101", faculty: "Dr. Physics", time: "Wed, 09:00 AM", status: "Approved" },
    ],
    stats: {
        totalCourses: "124",
        activeFaculty: "48",
        weeklyHours: "1,240",
        conflicts: "0"
    },
    days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    times: ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"],
    ingestionTypes: [
        { type: "Courses", description: "Required fields: ID, Name, Credits" },
        { type: "Faculty", description: "Required fields: ID, Name, Dept, Email" },
        { type: "Rooms", description: "Required fields: ID, Capacity, Type" },
    ],
    constraintOptions: {
        maxConsecutiveHours: [
            { label: "2 Hours", value: "2" },
            { label: "3 Hours", value: "3" },
            { label: "4 Hours", value: "4" }
        ],
        preferredRoomTypes: [
            { label: "Lecture Hall", value: "lecture" },
            { label: "Smart Lab", value: "lab" }
        ]
    }
};
