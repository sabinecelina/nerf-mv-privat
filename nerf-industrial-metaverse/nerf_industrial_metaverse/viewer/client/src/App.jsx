import { useState, useEffect } from 'react';
import UploadForm from './components/UploadForm';
import CheckConnection from './components/CheckConnection';
import RenderedVideo from './components/RenderedVideo';
import Information from './components/Information';
import './App.css'; // Import the CSS file
import { socket } from './components/socket';
import ImageSlider from './components/ImageSlider';
const App = () => {
    const [isConnected, setIsConnected] = useState(socket.coonected);

    useEffect(() => {

        socket.connect()

        socket.on('connect', () => {
            setIsConnected(true);
        });

        socket.on('disconnect', () => {
            setIsConnected(false);
        });

        return () => {
            socket.disconnect(); // Disconnect the socket when the component unmounts
        };
    }, []);


    return (
        <div className="container my-5">
            <h1 className="text-center mb-4">NeRF Trainer</h1>
            <div className="row justify-content-center">
                <div className="col-lg-11">
                    <CheckConnection isConnected={isConnected} />
                    <Information />
                    <RenderedVideo />
                    <ImageSlider />
                    <div className="card my-5">
                        <div className="card-body">
                            <UploadForm />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default App;