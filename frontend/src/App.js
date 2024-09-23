import React from 'react';
import './App.css';
import IncidentForm from './components/IncidentForm';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Universal ITSM/ITIL Tool</h1>
                <IncidentForm />
            </header>
        </div>
    );
}

export default App;
