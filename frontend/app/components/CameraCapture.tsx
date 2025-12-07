"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";

export interface FaceData {
  box: [number, number, number, number];
  match: { user_id: string; name: string } | null;
  confidence?: number;
}

interface CameraCaptureProps {
  onCapture: (dataUrl: string) => void;
  captureIntervalMs?: number | null;
  singleShot?: boolean;
  isLiveMode?: boolean;
  facesData?: FaceData[];
}

const CameraCapture: React.FC<CameraCaptureProps> = ({
  onCapture,
  captureIntervalMs = null,
  singleShot = false,
  isLiveMode = false,
  facesData = [],
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [cameraStatus, setCameraStatus] = useState<"loading" | "active" | "stopped">("stopped");
  const [cameraError, setCameraError] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);

  const startCamera = async () => {
    try {
      setCameraStatus("loading");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      });
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraStatus("active");
    } catch (err) {
      console.error("Camera error:", err);
      setCameraError("Failed to access camera.");
      setCameraStatus("stopped");
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());
    if (videoRef.current) videoRef.current.srcObject = null;
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    setCameraStatus("stopped");
  };

  // Draw face boxes on overlay canvas (separate from video)
  const drawFaceOverlay = useCallback(() => {
    const video = videoRef.current;
    const overlayCanvas = overlayCanvasRef.current;
    if (!video || !overlayCanvas || cameraStatus !== "active") return;

    const ctx = overlayCanvas.getContext("2d");
    if (!ctx) return;

    // Match canvas size to video
    overlayCanvas.width = video.videoWidth || 640;
    overlayCanvas.height = video.videoHeight || 480;

    // Clear previous drawings
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    // Draw face boxes
    facesData.forEach((face) => {
      const [x, y, w, h] = face.box;

      // Draw box with glow effect
      ctx.shadowColor = face.match ? "lime" : "red";
      ctx.shadowBlur = 10;
      ctx.strokeStyle = face.match ? "lime" : "red";
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);
      ctx.shadowBlur = 0;

      // Draw label background
      const label = face.match ? `${face.match.name} (${face.match.user_id})` : "Unknown";
      ctx.font = "bold 14px Arial";
      const textWidth = ctx.measureText(label).width;

      ctx.fillStyle = face.match ? "rgba(0, 255, 0, 0.8)" : "rgba(255, 0, 0, 0.8)";
      ctx.fillRect(x, y - 24, textWidth + 10, 22);

      ctx.fillStyle = face.match ? "#000" : "#fff";
      ctx.fillText(label, x + 5, y - 8);
    });

    // Continue animation loop
    if (isLiveMode && cameraStatus === "active") {
      animationFrameRef.current = requestAnimationFrame(drawFaceOverlay);
    }
  }, [facesData, cameraStatus, isLiveMode]);

  const capture = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || cameraStatus !== "active") return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // OPTIMIZED: Reduced quality to 0.6 for faster upload/processing
    const dataUrl = canvas.toDataURL("image/jpeg", 0.6);
    setIsProcessing(true);
    onCapture(dataUrl);

    // Reset processing indicator after a short delay
    setTimeout(() => setIsProcessing(false), 500);
  }, [cameraStatus, onCapture]);

  useEffect(() => {
    if (singleShot || isLiveMode) startCamera();
    return () => stopCamera();
  }, [singleShot, isLiveMode]);

  // Start face overlay animation when camera is active
  useEffect(() => {
    if (isLiveMode && cameraStatus === "active") {
      animationFrameRef.current = requestAnimationFrame(drawFaceOverlay);
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isLiveMode, cameraStatus, drawFaceOverlay]);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (captureIntervalMs && isLiveMode && cameraStatus === "active") {
      intervalRef.current = setInterval(capture, captureIntervalMs);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [captureIntervalMs, isLiveMode, cameraStatus, capture]);

  return (
    <div className="relative w-full max-w-md">
      {/* Hidden canvas for capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Video feed */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className={`rounded-lg shadow-md w-full ${cameraStatus === "active" ? "block" : "hidden"}`}
        style={{ maxHeight: "360px" }}
      />

      {/* Overlay canvas for face boxes */}
      <canvas
        ref={overlayCanvasRef}
        className={`absolute top-0 left-0 rounded-lg w-full pointer-events-none ${cameraStatus === "active" ? "block" : "hidden"}`}
        style={{ maxHeight: "360px" }}
      />

      {/* Processing indicator */}
      {isProcessing && cameraStatus === "active" && (
        <div className="absolute top-2 right-2 flex items-center gap-2 bg-blue-600/80 text-white px-3 py-1 rounded-full text-sm">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          Scanning...
        </div>
      )}

      {/* Camera status indicators */}
      {cameraStatus === "loading" && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Starting camera...</p>
        </div>
      )}

      {cameraStatus === "stopped" && !cameraError && (
        <button
          onClick={startCamera}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-2 rounded"
        >
          Start Camera
        </button>
      )}

      {cameraError && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-red-600 text-center">
          <p>{cameraError}</p>
          <button
            onClick={startCamera}
            className="mt-2 bg-blue-600 text-white px-4 py-2 rounded text-sm"
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
};

export default CameraCapture;
