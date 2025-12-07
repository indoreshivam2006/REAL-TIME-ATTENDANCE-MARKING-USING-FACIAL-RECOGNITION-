"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Search, Edit3, Trash2, Save } from "lucide-react";

interface Student {
  _id: string;
  name: string;
  studentId: string;
  department: string;
  year: string;
  division: string;
  email: string;
  phone: string;
}

export default function UpdateStudentDetailsPage() {
  const router = useRouter();
  const [searchId, setSearchId] = useState("");
  const [student, setStudent] = useState<Student | null>(null);
  const [formData, setFormData] = useState<Partial<Student>>({});
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  const departments = ["Computer Science", "IT", "Electronics", "Mechanical", "Civil"];
  const years = ["1st Year", "2nd Year", "3rd Year", "4th Year"];
  const divisions = ["A", "B", "C", "D"];

  const searchStudent = async () => {
    if (!searchId) {
      setStatus("Please enter a student ID");
      return;
    }

    setLoading(true);
    setStatus("");

    try {
      const res = await fetch(`http://localhost:5000/api/students/${searchId}`);
      const data = await res.json();

      if (data.success) {
        setStudent(data.student);
        setFormData(data.student);
        setIsEditing(false);
      } else {
        setStatus(data.error || "Student not found");
        setStudent(null);
      }
    } catch (err) {
      setStatus("Error connecting to server");
      setStudent(null);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async () => {
    if (!student) return;

    setLoading(true);
    setStatus("Updating...");

    try {
      const res = await fetch(`http://localhost:5000/api/students/${student.studentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (data.success) {
        setStatus("✅ Student updated successfully");
        setIsEditing(false);
        searchStudent(); // Refresh data
      } else {
        setStatus(`❌ ${data.error || "Update failed"}`);
      }
    } catch (err) {
      setStatus("❌ Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!student || !confirm("Are you sure you want to delete this student?")) return;

    setLoading(true);
    setStatus("Deleting...");

    try {
      const res = await fetch(`http://localhost:5000/api/students/${student.studentId}`, {
        method: "DELETE",
      });

      const data = await res.json();

      if (data.success) {
        setStatus("✅ Student deleted successfully");
        setTimeout(() => {
          router.push("/teacher/dashboard");
        }, 2000);
      } else {
        setStatus(`❌ ${data.error || "Delete failed"}`);
      }
    } catch (err) {
      setStatus("❌ Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

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
              <div className="p-2 bg-gradient-to-r from-emerald-100 to-green-100 rounded-lg">
                <Edit3 className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Update Student Details</h1>
                <p className="text-gray-600 text-sm">Search and modify student information</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-blue-200 p-6 shadow-lg mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                placeholder="Enter Student ID"
                className="flex-1 p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={searchStudent}
                disabled={loading}
                className="px-6 py-3 rounded-lg font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                <Search className="w-5 h-5" />
                {loading ? "Searching..." : "Search"}
              </button>
            </div>
          </div>

          {student && (
            <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-green-200 p-8 shadow-lg">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Student Information</h2>
                <div className="flex gap-2">
                  {!isEditing ? (
                    <>
                      <button
                        onClick={() => setIsEditing(true)}
                        className="px-4 py-2 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium flex items-center gap-2"
                      >
                        <Edit3 className="w-4 h-4" />
                        Edit
                      </button>
                      <button
                        onClick={handleDelete}
                        disabled={loading}
                        className="px-4 py-2 rounded-lg bg-red-100 hover:bg-red-200 text-red-700 font-medium flex items-center gap-2"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={handleUpdate}
                        disabled={loading}
                        className="px-4 py-2 rounded-lg bg-green-100 hover:bg-green-200 text-green-700 font-medium flex items-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        Save
                      </button>
                      <button
                        onClick={() => {
                          setIsEditing(false);
                          setFormData(student);
                        }}
                        className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium"
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Full Name</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name || ""}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    />
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Student ID</label>
                    <input
                      type="text"
                      value={student.studentId}
                      disabled
                      className="w-full p-3 rounded-lg bg-gray-100 border border-gray-200 text-gray-600"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-gray-700 text-sm mb-2 block font-medium">Department</label>
                  <select
                    name="department"
                    value={formData.department || ""}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  >
                    {departments.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Year</label>
                    <select
                      name="year"
                      value={formData.year || ""}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    >
                      {years.map((y) => (
                        <option key={y} value={y}>
                          {y}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Division</label>
                    <select
                      name="division"
                      value={formData.division || ""}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    >
                      {divisions.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email || ""}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    />
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Phone</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone || ""}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full p-3 rounded-lg bg-white border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {status && (
            <div
              className={`mt-6 p-4 rounded-lg text-center ${
                status.includes("✅")
                  ? "bg-green-100 border border-green-300 text-green-700"
                  : "bg-red-100 border border-red-300 text-red-700"
              }`}
            >
              {status}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
