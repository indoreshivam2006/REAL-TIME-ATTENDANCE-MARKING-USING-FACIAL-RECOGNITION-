"use client";

import React, { useRef, useEffect, useState } from "react";

export interface MultiCameraCaptureProps {
  onCaptureComplete: (images: string[]) => void; // Returns array of 5 captured images
  minImages?: number; // Optional minimum images required
}

const directions = [
  { name: "Front", instruction: "Look straight at the camera" },
  { name: "Left", instruction: "Turn your face slightly to the LEFT" },
  { name: "Right", instruction: "Turn your face slightly to the RIGHT" },
  { name: "Up", instruction: "Tilt your head slightly UP" },
  { name: "Down", instruction: "Tilt your head slightly DOWN" }
];

const MultiCameraCapture: React.FC<MultiCameraCaptureProps> = ({ onCaptureComplete, minImages = 5 }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [cameraStatus, setCameraStatus] = useState<"loading" | "active" | "stopped">("stopped");
  const [cameraError, setCameraError] = useState<string>("");
  const [currentStep, setCurrentStep] = useState(0);
  const [capturedImages, setCapturedImages] = useState<string[]>([]);
  const [captureMessage, setCaptureMessage] = useState<string>("");
  const [isCapturing, setIsCapturing] = useState(false);

  // Start camera
  const startCamera = async () => {
    try {
      setCameraStatus("loading");
      setCameraError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }
      });

      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraStatus("active");
    } catch (err) {
      console.error("Error accessing camera:", err);
      setCameraError("Failed to access camera. Please check permissions.");
      setCameraStatus("stopped");
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraStatus("stopped");
  };

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || cameraStatus !== "active" || isCapturing) return;

    setIsCapturing(true);

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      setIsCapturing(false);
      return;
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.8);

    const updatedImages = [...capturedImages, dataUrl];
    setCapturedImages(updatedImages);

    const capturedDirection = directions[currentStep].name;
    const nextStep = currentStep + 1;
    setCurrentStep(nextStep);

    // Show capture success message
    if (nextStep < directions.length) {
      setCaptureMessage(`✅ ${capturedDirection} side captured! (${nextStep}/5)`);
    } else {
      setCaptureMessage("🎉 All 5 sides of the face captured successfully!");
      onCaptureComplete(updatedImages); // Send all 5 images to parent
    }

    // Clear capturing state after short delay
    setTimeout(() => {
      setIsCapturing(false);
    }, 300);
  };

  const resetCapture = () => {
    setCapturedImages([]);
    setCurrentStep(0);
    setCaptureMessage("");
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      {/* Camera Status */}
      <div className="flex items-center space-x-2 text-sm">
        <div
          className={`w-3 h-3 rounded-full ${cameraStatus === "active"
            ? "bg-green-500"
            : cameraStatus === "loading"
              ? "bg-yellow-500 animate-pulse"
              : "bg-red-500"
            }`}
        ></div>
        <span className="text-gray-600">
          {cameraStatus === "active"
            ? "Camera Active"
            : cameraStatus === "loading"
              ? "Starting Camera..."
              : "Camera Stopped"}
        </span>
      </div>

      {/* Progress indicator */}
      <div className="flex space-x-2">
        {directions.map((dir, index) => (
          <div
            key={dir.name}
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${index < currentStep
              ? "bg-green-500 text-white"
              : index === currentStep
                ? "bg-blue-500 text-white animate-pulse"
                : "bg-gray-300 text-gray-600"
              }`}
          >
            {index < currentStep ? "✓" : index + 1}
          </div>
        ))}
      </div>

      {/* Video */}
      <div className="relative">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`rounded-lg shadow-md w-full max-w-md ${cameraStatus === "active" ? "block" : "hidden"
            }`}
          style={{ maxHeight: "360px" }}
        />

        {cameraStatus === "loading" && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-200 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600">Starting camera...</p>
            </div>
          </div>
        )}

        {cameraStatus === "stopped" && (
          <div className="flex items-center justify-center bg-gray-100 rounded-lg w-full max-w-md h-60">
            <p className="text-gray-600">Camera is stopped</p>
          </div>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />

      {cameraError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md">
          <p className="text-sm">{cameraError}</p>
          <button
            onClick={startCamera}
            className="mt-2 text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {cameraStatus === "active" && currentStep < directions.length && (
        <div className="text-center space-y-3">
          <div className="bg-blue-100 border border-blue-300 rounded-lg p-3 max-w-md">
            <p className="text-lg font-bold text-blue-800">
              Step {currentStep + 1}/5: {directions[currentStep].name}
            </p>
            <p className="text-sm text-blue-600">{directions[currentStep].instruction}</p>
          </div>
          <button
            onClick={captureImage}
            disabled={isCapturing}
            className={`px-8 py-3 rounded-lg font-semibold transition-all ${isCapturing
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
          >
            {isCapturing ? "Capturing..." : `📸 Capture ${directions[currentStep].name}`}
          </button>
        </div>
      )}

      {/* Capture feedback message */}
      {captureMessage && (
        <div className={`text-center p-3 rounded-lg max-w-md ${currentStep >= directions.length
          ? "bg-green-100 border border-green-400 text-green-700"
          : "bg-yellow-100 border border-yellow-400 text-yellow-700"
          }`}>
          <p className="font-semibold">{captureMessage}</p>
        </div>
      )}

      {currentStep >= directions.length && (
        <div className="text-center space-y-2">
          <p className="text-green-500 font-bold text-lg">✅ All 5 images captured successfully!</p>
          <p className="text-gray-400 text-sm">Submitting registration...</p>
        </div>
      )}

      {/* Reset button if user wants to recapture */}
      {currentStep > 0 && currentStep < directions.length && (
        <button
          onClick={resetCapture}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Start Over
        </button>
      )}
    </div>
  );
};

export default MultiCameraCapture;
