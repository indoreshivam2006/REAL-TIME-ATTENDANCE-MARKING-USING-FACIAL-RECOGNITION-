"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  GraduationCap,
  Calendar,
  LogOut,
  Trash2,
  BarChart3,
  Shield,
  TrendingUp,
} from "lucide-react";

interface DashboardStats {
  totalTeachers: number;
  totalStudents: number;
  totalSessions: number;
  recentSessions: any[];
}

interface Teacher {
  _id: string;
  username: string;
  email: string;
  employeeId: string;
}

interface Student {
  _id: string;
  name: string;
  studentId: string;
  department: string;
  year: string;
  division: string;
}

interface Session {
  _id: string;
  sessionId: string;
  date: string;
  subject: string;
  department: string;
  year: string;
  division: string;
  totalPresent: number;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const isLoggedIn = localStorage.getItem("isLoggedIn");
      const userType = localStorage.getItem("userType");

      if (!isLoggedIn || userType !== "admin") {
        router.push("/admin/signin");
      } else {
        fetchData();
      }
    };

    checkAuth();
  }, [router]);

  const fetchData = async () => {
    try {
      const [statsRes, teachersRes, studentsRes, sessionsRes] = await Promise.all([
        fetch("http://localhost:5000/api/admin/dashboard"),
        fetch("http://localhost:5000/api/admin/teachers"),
        fetch("http://localhost:5000/api/admin/students"),
        fetch("http://localhost:5000/api/admin/sessions"),
      ]);

      const [statsData, teachersData, studentsData, sessionsData] = await Promise.all([
        statsRes.json(),
        teachersRes.json(),
        studentsRes.json(),
        sessionsRes.json(),
      ]);

      if (statsData.success) setStats(statsData.stats);
      if (teachersData.success) setTeachers(teachersData.teachers);
      if (studentsData.success) setStudents(studentsData.students);
      if (sessionsData.success) setSessions(sessionsData.sessions);
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    router.push("/");
  };

  const deleteTeacher = async (teacherId: string) => {
    if (!confirm("Are you sure you want to delete this teacher?")) return;

    try {
      const res = await fetch(`http://localhost:5000/api/admin/teachers/${teacherId}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (data.success) {
        setTeachers(teachers.filter((t) => t._id !== teacherId));
        alert("Teacher deleted successfully");
      }
    } catch (err) {
      alert("Error deleting teacher");
    }
  };

  const deleteStudent = async (studentId: string) => {
    if (!confirm("Are you sure you want to delete this student?")) return;

    try {
      const res = await fetch(`http://localhost:5000/api/admin/students/${studentId}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (data.success) {
        setStudents(students.filter((s) => s.studentId !== studentId));
        alert("Student deleted successfully");
      }
    } catch (err) {
      alert("Error deleting student");
    }
  };

  const deleteSession = async (sessionId: string) => {
    if (!confirm("Are you sure you want to delete this session?")) return;

    try {
      const res = await fetch(`http://localhost:5000/api/admin/sessions/${sessionId}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (data.success) {
        setSessions(sessions.filter((s) => s.sessionId !== sessionId));
        alert("Session deleted successfully");
      }
    } catch (err) {
      alert("Error deleting session");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mx-auto mb-4"></div>
          <p className="text-xl text-white font-medium">Loading Admin Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-lg border-b border-white/10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-gray-300 text-sm">System Management & Analytics</p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors border border-red-400/30"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="px-6">
          <div className="flex gap-4">
            {[
              { id: "overview", label: "Overview", icon: BarChart3 },
              { id: "teachers", label: "Teachers", icon: Users },
              { id: "students", label: "Students", icon: GraduationCap },
              { id: "sessions", label: "Sessions", icon: Calendar },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 font-medium transition-all border-b-2 ${
                  activeTab === tab.id
                    ? "text-purple-300 border-purple-400"
                    : "text-gray-400 border-transparent hover:text-gray-200"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Overview Tab */}
          {activeTab === "overview" && stats && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 rounded-lg">
                      <Users className="w-8 h-8 text-blue-300" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm">Total Teachers</p>
                      <p className="text-3xl font-bold text-white">{stats.totalTeachers}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-green-500/20 rounded-lg">
                      <GraduationCap className="w-8 h-8 text-green-300" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm">Total Students</p>
                      <p className="text-3xl font-bold text-white">{stats.totalStudents}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-purple-500/20 rounded-lg">
                      <Calendar className="w-8 h-8 text-purple-300" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm">Total Sessions</p>
                      <p className="text-3xl font-bold text-white">{stats.totalSessions}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Recent Sessions
                </h2>
                <div className="space-y-3">
                  {stats.recentSessions.map((session, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="text-white font-medium">{session.subject}</p>
                          <p className="text-gray-400 text-sm">
                            {session.department} - {session.year} {session.division}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-gray-400 text-sm">{session.date}</p>
                          <p className="text-green-300 text-sm">{session.totalPresent} present</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Teachers Tab */}
          {activeTab === "teachers" && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Teachers Management</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left p-3 text-gray-300 font-semibold">Username</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Email</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Employee ID</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teachers.map((teacher) => (
                      <tr key={teacher._id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="p-3 text-white">{teacher.username}</td>
                        <td className="p-3 text-gray-300">{teacher.email}</td>
                        <td className="p-3 text-gray-300">{teacher.employeeId}</td>
                        <td className="p-3">
                          <button
                            onClick={() => deleteTeacher(teacher._id)}
                            className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors flex items-center gap-2"
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Students Tab */}
          {activeTab === "students" && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Students Management</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left p-3 text-gray-300 font-semibold">Name</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Student ID</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Department</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Year</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Division</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student._id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="p-3 text-white">{student.name}</td>
                        <td className="p-3 text-gray-300">{student.studentId}</td>
                        <td className="p-3 text-gray-300">{student.department}</td>
                        <td className="p-3 text-gray-300">{student.year}</td>
                        <td className="p-3 text-gray-300">{student.division}</td>
                        <td className="p-3">
                          <button
                            onClick={() => deleteStudent(student.studentId)}
                            className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors flex items-center gap-2"
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Sessions Tab */}
          {activeTab === "sessions" && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Sessions Management</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left p-3 text-gray-300 font-semibold">Date</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Subject</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Department</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Year</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Division</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Present</th>
                      <th className="text-left p-3 text-gray-300 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map((session) => (
                      <tr key={session._id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="p-3 text-white">{session.date}</td>
                        <td className="p-3 text-gray-300">{session.subject}</td>
                        <td className="p-3 text-gray-300">{session.department}</td>
                        <td className="p-3 text-gray-300">{session.year}</td>
                        <td className="p-3 text-gray-300">{session.division}</td>
                        <td className="p-3 text-green-300">{session.totalPresent}</td>
                        <td className="p-3">
                          <button
                            onClick={() => deleteSession(session.sessionId)}
                            className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors flex items-center gap-2"
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
