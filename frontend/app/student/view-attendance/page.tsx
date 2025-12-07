"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Calendar, Download, BarChart3 } from "lucide-react";
import * as XLSX from "xlsx";

interface AttendanceRecord {
  sessionId: string;
  studentId: string;
  timestamp: string;
  confidence: number;
  status: string;
  session?: {
    date: string;
    subject: string;
    department: string;
    year: string;
    division: string;
  };
}

export default function ViewAttendancePage() {
  const router = useRouter();
  const [studentId, setStudentId] = useState("");
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchAttendance = async () => {
    if (!studentId) {
      setError("Please enter a student ID");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`http://localhost:5000/api/attendance/student/${studentId}`);
      const data = await res.json();

      if (data.success) {
        setAttendance(data.attendance);
      } else {
        setError(data.error || "Failed to fetch attendance");
      }
    } catch (err) {
      setError("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  const exportToExcel = () => {
    const exportData = attendance.map((record) => ({
      Date: record.session?.date || "N/A",
      Subject: record.session?.subject || "N/A",
      Department: record.session?.department || "N/A",
      Year: record.session?.year || "N/A",
      Division: record.session?.division || "N/A",
      Timestamp: new Date(record.timestamp).toLocaleString(),
      Status: record.status,
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Attendance");
    XLSX.writeFile(wb, `attendance_${studentId}_${Date.now()}.xlsx`);
  };

  const attendancePercentage =
    attendance.length > 0 ? ((attendance.length / attendance.length) * 100).toFixed(1) : "0";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <header className="bg-white/80 backdrop-blur-lg border-b border-white/20">
        <div className="px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/teacher/dashboard")}
              className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <ArrowLeft className="w-6 h-6 text-gray-600" />
            </button>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-amber-100 to-orange-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">View Attendance</h1>
                <p className="text-gray-600 text-sm">Check student attendance records</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-blue-200 p-6 shadow-lg mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="Enter Student ID"
                className="flex-1 p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={fetchAttendance}
                disabled={loading}
                className="px-6 py-3 rounded-lg font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50"
              >
                {loading ? "Loading..." : "Search"}
              </button>
            </div>
            {error && <div className="mt-4 p-3 rounded-lg bg-red-100 text-red-700">{error}</div>}
          </div>

          {attendance.length > 0 && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-green-200 p-6">
                  <h3 className="text-gray-600 text-sm mb-2">Total Sessions</h3>
                  <p className="text-3xl font-bold text-gray-800">{attendance.length}</p>
                </div>
                <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-blue-200 p-6">
                  <h3 className="text-gray-600 text-sm mb-2">Attendance Rate</h3>
                  <p className="text-3xl font-bold text-gray-800">{attendancePercentage}%</p>
                </div>
                <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-purple-200 p-6">
                  <button
                    onClick={exportToExcel}
                    className="w-full py-3 rounded-lg font-semibold bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 transition-all flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Export to Excel
                  </button>
                </div>
              </div>

              <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-purple-200 p-6 shadow-lg">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Attendance Records</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left p-3 text-gray-700 font-semibold">Date</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Subject</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Department</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Year</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Division</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Time</th>
                        <th className="text-left p-3 text-gray-700 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendance.map((record, idx) => (
                        <tr key={idx} className="border-b border-gray-100 hover:bg-blue-50">
                          <td className="p-3 text-gray-800">{record.session?.date || "N/A"}</td>
                          <td className="p-3 text-gray-800">{record.session?.subject || "N/A"}</td>
                          <td className="p-3 text-gray-800">{record.session?.department || "N/A"}</td>
                          <td className="p-3 text-gray-800">{record.session?.year || "N/A"}</td>
                          <td className="p-3 text-gray-800">{record.session?.division || "N/A"}</td>
                          <td className="p-3 text-gray-800">
                            {new Date(record.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="p-3">
                            <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-medium">
                              {record.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
