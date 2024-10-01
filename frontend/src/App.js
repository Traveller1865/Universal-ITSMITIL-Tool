import React, { useState } from 'react';
import Login from './components/Login';
import IncidentForm from './components/IncidentForm';
import IncidentList from './components/IncidentList';
import ServiceRequestStatus from './components/ServiceRequestStatus';
import SLAMonitoring from './components/SLAMonitoring';
import './Styles/App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogin = (newToken) => {
      localStorage.setItem('token', newToken);
      setToken(newToken);
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      setToken(null);
  };

  return (
      <div className="App">
          <h1>University IT Help Desk</h1>
          {!token ? (
              <Login setToken={handleLogin} />
          ) : (
              <>
                  <button onClick={handleLogout}>Logout</button>
                  <IncidentForm />
                  <IncidentList />
                  <ServiceRequestStatus />
                  <SLAMonitoring />
              </>
          )}
      </div>
  );
}

export default App;