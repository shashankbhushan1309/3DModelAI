import React, { Suspense, useRef, useEffect } from 'react';
import { Canvas, useLoader, useThree } from '@react-three/fiber';
import { OrbitControls, Stage, Grid, Environment, Bounds } from '@react-three/drei';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import * as THREE from 'three';
import { Maximize2, Layers } from 'lucide-react';

function Model({ url, wireframe }) {
    const geom = useLoader(STLLoader, url);

    useEffect(() => {
        geom.computeVertexNormals();
    }, [geom]);

    return (
        <mesh geometry={geom} castShadow receiveShadow>
            <meshStandardMaterial
                color="#3b82f6"
                metalness={0.6}
                roughness={0.4}
                wireframe={wireframe}
            />
        </mesh>
    );
}

export default function Viewer3D({ stlUrl, wireframe, onToggleWireframe }) {
    const controlsRef = useRef();

    const handleResetCamera = () => {
        if (controlsRef.current) {
            controlsRef.current.reset();
        }
    };

    return (
        <div className="relative w-full h-full rounded-2xl overflow-hidden glass-panel bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">

            {/* Overlay Controls */}
            <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
                <button
                    onClick={handleResetCamera}
                    className="p-2 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-lg backdrop-blur-sm border border-slate-600/50 shadow-lg transition-colors"
                    title="Reset View"
                >
                    <Maximize2 className="w-5 h-5" />
                </button>
                <button
                    onClick={onToggleWireframe}
                    className={`p-2 bg-slate-800/80 hover:bg-slate-700 rounded-lg backdrop-blur-sm border border-slate-600/50 shadow-lg transition-colors ${wireframe ? 'text-blue-400' : 'text-slate-300'}`}
                    title="Toggle Wireframe"
                >
                    <Layers className="w-5 h-5" />
                </button>
            </div>

            {!stlUrl && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <p className="text-slate-500 font-medium">Model viewer ready</p>
                </div>
            )}

            <Canvas shadows camera={{ position: [50, 50, 50], fov: 45 }}>
                <color attach="background" args={['#0f172a']} />

                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 20, 10]} intensity={1.5} castShadow shadow-mapSize={[1024, 1024]} />
                <pointLight position={[-10, -10, -10]} intensity={0.5} />

                <Suspense fallback={null}>
                    <Bounds fit clip observe margin={1.2}>
                        {stlUrl && <Model url={stlUrl} wireframe={wireframe} />}
                    </Bounds>
                </Suspense>

                <Grid
                    infiniteGrid
                    fadeDistance={200}
                    cellColor="#334155"
                    sectionColor="#475569"
                    sectionSize={10}
                    cellSize={1}
                />

                <OrbitControls ref={controlsRef} makeDefault />
                <Environment preset="city" />
                <axesHelper args={[20]} />
            </Canvas>
        </div>
    );
}
