import React, { useEffect, useState } from 'react';
import { socket } from './socket'

const ExportMesh = () => {

    const [meshExported, setMeshExported] = useState(false);
    const [meshFileURL, setMeshFileURL] = useState('');
    const [meshFileName, setMeshFileName] = useState('');
    const fetchMeshFilename = () => {
        fetch('/get-filename-mesh')
            .then((response) => response.json())
            .then((data) => {
                const { filename } = data;
                setMeshFileName(filename)
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    };
    const fetchMeshURL = () => {
        fetch('/api/mesh-url')
            .then((response) => response.blob())
            .then((blob) => {
                const meshFileURL = URL.createObjectURL(blob);
                setMeshFileURL(meshFileURL);
            });
    };
    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = meshFileURL;
        link.download = meshFileName;
        link.click();
    };
    const handleMesh = () => {
        // Send a request to Flask to start rendering the video
        fetch('/export-mesh')
            .then(response => {
                // Handle the response as needed
                console.log('Mesh export started');
            })
            .catch(error => {
                // Handle errors
                console.error('Error mesh export:', error);
            });
    };
    useEffect(() => {
        socket.on('export_mesh_complete', () => {
            setMeshExported(true);
            console.log('mesh export done');
            fetchMeshURL();
            fetchMeshFilename();
        });
    }, []);
    return (
        <div>
            <button className="mesh-button-container btn btn-primary my-3" onClick={handleMesh}>
                Export Mesh
            </button>
            {meshExported &&
                <button className="mesh-button-container btn btn-primary m-3" onClick={handleDownload}>
                    Download Mesh
                </button>
            }
        </div>
    );
}  
export default ExportMesh;