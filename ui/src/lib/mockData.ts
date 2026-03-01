
export const mockData = {
    users: {
        admin: { id: 1, name: "Admin User", role: "admin", email: "admin@college.edu", avatar: "https://ui-avatars.com/api/?name=Admin+User&background=ef4444&color=fff" },
        faculty: { id: 2, name: "Dr. Sarah Smith", role: "faculty", email: "sarah@college.edu", dept: "Computer Science", avatar: "https://ui-avatars.com/api/?name=Sarah+Smith&background=ef4444&color=fff" },
        student: { id: 3, name: "John Doe", role: "student", email: "john@college.edu", batch: "CSE-2026", avatar: "https://ui-avatars.com/api/?name=John+Doe&background=ef4444&color=fff" }
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
    ]
};
