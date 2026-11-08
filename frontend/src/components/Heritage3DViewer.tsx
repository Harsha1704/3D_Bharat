import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import {
  RotateCcw,
  Play,
  Pause,
  Maximize2,
  Minimize2,
  Sun,
  AlertTriangle,
  Loader2,
} from "lucide-react";

export type ViewMode = "realistic" | "wireframe" | "clay";

interface Heritage3DViewerProps {
  modelUrl: string;
  title: string;
  polyCount?: number | null;
  vertexCount?: number | null;
  onModelLoaded?: () => void;
  onError?: (err: string) => void;
}

export const Heritage3DViewer: React.FC<Heritage3DViewerProps> = ({
  modelUrl,
  title,
  polyCount,
  vertexCount,
  onModelLoaded,
  onError,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [loading, setLoading] = useState(true);
  const [loadProgress, setLoadProgress] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [autoRotate, setAutoRotate] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>("realistic");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [sunIntensity, setSunIntensity] = useState(1.8);

  // References for Three.js objects
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const loadedModelRef = useRef<THREE.Group | null>(null);
  const originalMaterialsRef = useRef<Map<THREE.Mesh, THREE.Material | THREE.Material[]>>(new Map());
  const sunLightRef = useRef<THREE.DirectionalLight | null>(null);
  const animFrameIdRef = useRef<number | null>(null);
  const defaultCameraStateRef = useRef<{ position: THREE.Vector3; target: THREE.Vector3 }>({
    position: new THREE.Vector3(0, 15, 45),
    target: new THREE.Vector3(0, 8, 0),
  });

  /* =========================================================
     INITIALIZE THREE.JS SCENE, CAMERA & LIGHTING
  ========================================================= */
  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 500;

    // 1. Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a1128); // Deep heritage midnight navy
    scene.fog = new THREE.FogExp2(0x0a1128, 0.008);
    sceneRef.current = scene;

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 15, 45);
    cameraRef.current = camera;

    // 3. Renderer with antialiasing and sRGB color space
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = true;
    controls.minDistance = 2;
    controls.maxDistance = 250;
    controls.maxPolarAngle = Math.PI / 2 + 0.05; // Prevent flipping below ground
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 1.0;
    controls.target.set(0, 8, 0);
    controlsRef.current = controls;

    // 5. Lighting System (Indian golden hour heritage lighting)
    // Warm Sun Directional Light (Surya)
    const sunLight = new THREE.DirectionalLight(0xffecd2, 1.8);
    sunLight.position.set(40, 50, 30);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 200;
    const d = 40;
    sunLight.shadow.camera.left = -d;
    sunLight.shadow.camera.right = d;
    sunLight.shadow.camera.top = d;
    sunLight.shadow.camera.bottom = -d;
    sunLight.shadow.bias = -0.0005;
    scene.add(sunLight);
    sunLightRef.current = sunLight;

    // Soft Sky & Ground Hemisphere Fill
    const hemiLight = new THREE.HemisphereLight(0xb1e1ff, 0x3d3020, 0.7);
    hemiLight.position.set(0, 50, 0);
    scene.add(hemiLight);

    // Subtle Front Ambient Fill
    const ambientLight = new THREE.AmbientLight(0xfff5e6, 0.4);
    scene.add(ambientLight);

    // Warm Antique Gold Accent Rim Light
    const rimLight = new THREE.DirectionalLight(0xd4af37, 0.6);
    rimLight.position.set(-30, 20, -30);
    scene.add(rimLight);

    // 6. Ground Grid & Subtle Circular Pedestal
    const grid = new THREE.GridHelper(120, 60, 0xd4af37, 0x1f293d);
    grid.position.y = -0.02;
    scene.add(grid);

    // 7. Render Loop
    const animate = () => {
      animFrameIdRef.current = requestAnimationFrame(animate);
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    animate();

    // 8. Resize Handler
    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
      }
      controls.dispose();
      renderer.dispose();
    };
  }, []);

  /* =========================================================
     LOAD GLB MODEL
  ========================================================= */
  useEffect(() => {
    const scene = sceneRef.current;
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    if (!scene || !camera || !controls || !modelUrl) return;

    // Remove existing model
    if (loadedModelRef.current) {
      scene.remove(loadedModelRef.current);
      loadedModelRef.current.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          mesh.geometry?.dispose();
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach((m) => m.dispose());
          } else {
            mesh.material?.dispose();
          }
        }
      });
      loadedModelRef.current = null;
    }

    originalMaterialsRef.current.clear();
    setLoading(true);
    setLoadProgress(10);
    setLoadError(null);

    const loader = new GLTFLoader();

    loader.load(
      modelUrl,
      (gltf) => {
        const model = gltf.scene;
        loadedModelRef.current = model;

        // Cache original materials and configure shadows
        model.traverse((child) => {
          if ((child as THREE.Mesh).isMesh) {
            const mesh = child as THREE.Mesh;
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            originalMaterialsRef.current.set(mesh, mesh.material);
          }
        });

        // Compute Bounding Box & Center Model
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        // Center model so its base is exactly on the ground plane (Y = 0)
        model.position.x = -center.x;
        model.position.y = -box.min.y;
        model.position.z = -center.z;

        scene.add(model);

        // Frame camera based on bounding sphere
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI / 180);
        let cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;
        cameraDistance = Math.max(cameraDistance, 10);

        const targetY = size.y * 0.4;
        camera.position.set(cameraDistance * 0.7, cameraDistance * 0.5, cameraDistance * 0.9);
        controls.target.set(0, targetY, 0);
        controls.update();

        // Save default camera state for reset
        defaultCameraStateRef.current = {
          position: camera.position.clone(),
          target: new THREE.Vector3(0, targetY, 0),
        };

        setLoading(false);
        setLoadProgress(100);
        if (onModelLoaded) onModelLoaded();
      },
      (xhr) => {
        if (xhr.total > 0) {
          const percent = Math.round((xhr.loaded / xhr.total) * 100);
          setLoadProgress(percent);
        }
      },
      (error) => {
        console.error("Error loading GLTF model:", error);
        const msg = "Failed to load 3D model. Please verify storage and network connectivity.";
        setLoadError(msg);
        setLoading(false);
        if (onError) onError(msg);
      }
    );
  }, [modelUrl]);

  /* =========================================================
     AUTO-ROTATE TOGGLE
  ========================================================= */
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate;
    }
  }, [autoRotate]);

  /* =========================================================
     SUN INTENSITY CONTROLLER
  ========================================================= */
  useEffect(() => {
    if (sunLightRef.current) {
      sunLightRef.current.intensity = sunIntensity;
    }
  }, [sunIntensity]);

  /* =========================================================
     SHADING VIEW MODES (Realistic, Wireframe, Clay)
  ========================================================= */
  useEffect(() => {
    if (!loadedModelRef.current) return;

    loadedModelRef.current.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        const origMat = originalMaterialsRef.current.get(mesh);

        if (viewMode === "realistic") {
          if (origMat) mesh.material = origMat;
        } else if (viewMode === "wireframe") {
          mesh.material = new THREE.MeshBasicMaterial({
            color: 0xd4af37, // Antique gold wireframe
            wireframe: true,
          });
        } else if (viewMode === "clay") {
          mesh.material = new THREE.MeshStandardMaterial({
            color: 0xcccccc,
            roughness: 0.9,
            metalness: 0.05,
            flatShading: true,
          });
        }
      }
    });
  }, [viewMode]);

  /* =========================================================
     CAMERA RESET
  ========================================================= */
  const handleResetCamera = () => {
    if (!cameraRef.current || !controlsRef.current) return;
    const { position, target } = defaultCameraStateRef.current;
    cameraRef.current.position.copy(position);
    controlsRef.current.target.copy(target);
    controlsRef.current.update();
  };

  /* =========================================================
     FULLSCREEN TOGGLE
  ========================================================= */
  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false)).catch(() => {});
    }
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-full bg-[#0a1128] overflow-hidden select-none ${
        isFullscreen ? "fixed inset-0 z-50" : ""
      }`}
      style={{ minHeight: "480px" }}
    >
      {/* Three.js Canvas */}
      <canvas ref={canvasRef} className="w-full h-full block cursor-grab active:cursor-grabbing" />

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-[#0a1128]/85 backdrop-blur-sm flex flex-col items-center justify-center z-20">
          <div className="relative flex items-center justify-center mb-4">
            <Loader2 className="w-12 h-12 text-[#d4af37] animate-spin" />
            <div className="absolute text-xs font-semibold text-[#d4af37]">{loadProgress}%</div>
          </div>
          <h4 className="text-white font-medium text-sm tracking-wide">Loading 3D Heritage Model</h4>
          <p className="text-xs text-slate-400 mt-1">{title}</p>
          <div className="w-48 h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-amber-300 transition-all duration-200"
              style={{ width: `${Math.max(loadProgress, 8)}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {loadError && (
        <div className="absolute inset-0 bg-[#0a1128]/90 flex flex-col items-center justify-center p-6 z-20 text-center">
          <AlertTriangle className="w-12 h-12 text-rose-400 mb-3" />
          <h4 className="text-white font-semibold text-base mb-1">Failed to Render 3D Model</h4>
          <p className="text-xs text-rose-300/80 max-w-md mb-4">{loadError}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded text-xs hover:bg-amber-500/30 transition-colors"
          >
            Retry Loading
          </button>
        </div>
      )}

      {/* Top Floating Control Bar */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between pointer-events-none z-10">
        <div className="pointer-events-auto flex items-center gap-2 bg-[#0c1836]/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#d4af37]/25 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-amber-200">{title}</span>
          {polyCount && (
            <span className="text-[10px] text-slate-400 border-l border-slate-700 pl-2">
              {polyCount.toLocaleString()} Polys {vertexCount ? `• ${vertexCount.toLocaleString()} Verts` : ""}
            </span>
          )}
        </div>

        {/* View Mode Switcher */}
        <div className="pointer-events-auto flex items-center gap-1 bg-[#0c1836]/80 backdrop-blur-md p-1 rounded-lg border border-[#d4af37]/25 shadow-lg">
          <button
            onClick={() => setViewMode("realistic")}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              viewMode === "realistic"
                ? "bg-[#d4af37] text-slate-950 font-medium"
                : "text-slate-300 hover:text-white"
            }`}
            title="Realistic PBR sandstone shading"
          >
            Realistic
          </button>
          <button
            onClick={() => setViewMode("wireframe")}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              viewMode === "wireframe"
                ? "bg-[#d4af37] text-slate-950 font-medium"
                : "text-slate-300 hover:text-white"
            }`}
            title="Geometric Wireframe wire mesh"
          >
            Wireframe
          </button>
          <button
            onClick={() => setViewMode("clay")}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              viewMode === "clay"
                ? "bg-[#d4af37] text-slate-950 font-medium"
                : "text-slate-300 hover:text-white"
            }`}
            title="Surface Clay / Normal Shading"
          >
            Clay
          </button>
        </div>
      </div>

      {/* Bottom Floating Control Ribbon */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-[#0c1836]/90 backdrop-blur-md px-4 py-2 rounded-xl border border-[#d4af37]/30 shadow-2xl z-10">
        {/* Reset Camera */}
        <button
          onClick={handleResetCamera}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-200 hover:text-[#d4af37] bg-slate-900/60 hover:bg-slate-800 rounded-md transition-colors"
          title="Reset camera viewpoint"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Camera</span>
        </button>

        {/* Auto Rotate Toggle */}
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md transition-colors ${
            autoRotate
              ? "bg-[#d4af37]/20 text-[#d4af37] border border-[#d4af37]/40"
              : "text-slate-300 hover:text-white bg-slate-900/60 hover:bg-slate-800"
          }`}
          title={autoRotate ? "Pause rotation" : "Start turntable rotation"}
        >
          {autoRotate ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          <span>{autoRotate ? "Pause" : "Rotate"}</span>
        </button>

        {/* Sun Lighting Boost */}
        <button
          onClick={() => setSunIntensity(sunIntensity === 1.8 ? 2.6 : 1.8)}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md transition-colors ${
            sunIntensity > 2.0
              ? "bg-amber-400/20 text-amber-300 border border-amber-400/40"
              : "text-slate-300 hover:text-white bg-slate-900/60 hover:bg-slate-800"
          }`}
          title="Toggle high midday Surya illumination"
        >
          <Sun className="w-3.5 h-3.5" />
          <span>Surya Light</span>
        </button>

        {/* Fullscreen Toggle */}
        <button
          onClick={toggleFullscreen}
          className="p-1.5 text-slate-300 hover:text-[#d4af37] bg-slate-900/60 hover:bg-slate-800 rounded-md transition-colors"
          title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
        >
          {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>
      </div>

      {/* Helpful Interaction Tip Overlay */}
      <div className="absolute bottom-4 right-4 text-[10px] text-slate-400 bg-slate-950/70 px-2.5 py-1 rounded border border-slate-800 pointer-events-none hidden sm:block">
        Left-click to Rotate • Scroll to Zoom • Right-click to Pan
      </div>
    </div>
  );
};

export default Heritage3DViewer;
