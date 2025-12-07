"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, UserPlus, ArrowLeft, CheckCircle2, AlertCircle } from "lucide-react";
import MultiCameraCapture from "@/app/components/MultiCameraCapture";

export default function StudentRegistrationPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    studentId: "",
    department: "",
    year: "",
    division: "",
    email: "",
    phone: "",
  });
  const [faceImages, setFaceImages] = useState<string[]>([]);
  const [status, setStatus] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const departments = ["Computer Science", "IT", "Electronics", "Mechanical", "Civil"];
  const years = ["1st Year", "2nd Year", "3rd Year", "4th Year"];
  const divisions = ["A", "B", "C", "D"];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleNext = () => {
    if (!formData.name || !formData.studentId || !formData.department || !formData.year || !formData.division) {
      setStatus("Please fill all required fields");
      return;
    }
    setStatus("");
    setStep(2);
  };

  const handleCaptureComplete = (images: string[]) => {
    setFaceImages(images);
    setStep(3);
  };

  const handleSubmit = async () => {
    if (faceImages.length < 3) {
      setStatus("Please capture at least 3 face images");
      return;
    }

    setIsSubmitting(true);
    setStatus("Registering student...");

    try {
      const res = await fetch("http://localhost:5000/api/students/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          faceImages: faceImages,
        }),
      });

      const data = await res.json();

      if (data.success) {
        setStatus("✅ Student registered successfully!");
        setTimeout(() => {
          router.push("/teacher/dashboard");
        }, 2000);
      } else {
        setStatus(`❌ ${data.error || "Registration failed"}`);
      }
    } catch (err) {
      console.error(err);
      setStatus("❌ Error connecting to server");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-white/20">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/teacher/dashboard")}
                className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors group"
              >
                <ArrowLeft className="w-6 h-6 text-gray-600 group-hover:text-gray-800 transition-colors" />
              </button>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg">
                  <UserPlus className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                    Student Registration
                  </h1>
                  <p className="text-gray-600 text-sm">Register new student with face recognition</p>
                </div>
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="flex items-center gap-2">
              {[1, 2, 3].map((s) => (
                <div
                  key={s}
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                    step >= s
                      ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {s}
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <div className="max-w-4xl mx-auto">
          {/* Step 1: Student Details */}
          {step === 1 && (
            <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-blue-200 p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Student Information</h2>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">
                      Full Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Enter full name"
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    />
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">
                      Student ID <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="studentId"
                      value={formData.studentId}
                      onChange={handleChange}
                      placeholder="Enter student ID"
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-gray-700 text-sm mb-2 block font-medium">
                    Department <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="department"
                    value={formData.department}
                    onChange={handleChange}
                    className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                  >
                    <option value="">Select Department</option>
                    {departments.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">
                      Year <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="year"
                      value={formData.year}
                      onChange={handleChange}
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    >
                      <option value="">Select Year</option>
                      {years.map((y) => (
                        <option key={y} value={y}>
                          {y}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">
                      Division <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="division"
                      value={formData.division}
                      onChange={handleChange}
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    >
                      <option value="">Select Division</option>
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
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Email (Optional)</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="Enter email"
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    />
                  </div>

                  <div>
                    <label className="text-gray-700 text-sm mb-2 block font-medium">Phone (Optional)</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="Enter phone number"
                      className="w-full p-3 rounded-lg bg-white/60 border border-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    />
                  </div>
                </div>

                <button
                  onClick={handleNext}
                  className="w-full py-3 px-4 rounded-lg font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white transition-all duration-300 flex items-center justify-center gap-3 mt-6 hover:shadow-lg hover:-translate-y-0.5"
                >
                  Next: Capture Face Images
                  <Camera className="w-5 h-5" />
                </button>

                {status && (
                  <div className="p-3 rounded-lg text-center bg-red-100 border border-red-300 text-red-700">
                    {status}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Face Capture */}
          {step === 2 && (
            <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-purple-200 p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Capture Face Images</h2>
              <p className="text-gray-600 mb-6">
                Capture at least 5 clear images of the student's face from different angles
              </p>

              <MultiCameraCapture onCaptureComplete={handleCaptureComplete} minImages={5} />

              <button
                onClick={() => setStep(1)}
                className="w-full py-3 px-4 rounded-lg font-semibold bg-gray-200 hover:bg-gray-300 text-gray-700 transition-all duration-300 flex items-center justify-center gap-3 mt-6"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Details
              </button>
            </div>
          )}

          {/* Step 3: Confirmation */}
          {step === 3 && (
            <div className="bg-white/70 backdrop-blur-lg rounded-xl border-2 border-green-200 p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Confirm Registration</h2>

              <div className="space-y-4 mb-6">
                <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                  <h3 className="font-semibold text-gray-800 mb-2">Student Details</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Name:</span>
                      <span className="ml-2 font-medium">{formData.name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Student ID:</span>
                      <span className="ml-2 font-medium">{formData.studentId}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Department:</span>
                      <span className="ml-2 font-medium">{formData.department}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Year:</span>
                      <span className="ml-2 font-medium">{formData.year}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Division:</span>
                      <span className="ml-2 font-medium">{formData.division}</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                  <h3 className="font-semibold text-gray-800 mb-2">Face Images Captured</h3>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="text-gray-700">{faceImages.length} images captured successfully</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 py-3 px-4 rounded-lg font-semibold bg-gray-200 hover:bg-gray-300 text-gray-700 transition-all duration-300"
                  disabled={isSubmitting}
                >
                  Recapture Images
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 py-3 px-4 rounded-lg font-semibold bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Registering...
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-5 h-5" />
                      Complete Registration
                    </>
                  )}
                </button>
              </div>

              {status && (
                <div
                  className={`p-3 rounded-lg text-center mt-4 ${
                    status.includes("✅")
                      ? "bg-green-100 border border-green-300 text-green-700"
                      : "bg-red-100 border border-red-300 text-red-700"
                  }`}
                >
                  {status}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
